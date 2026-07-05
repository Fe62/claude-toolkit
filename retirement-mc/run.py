#!/usr/bin/env python3
"""CLI entry point: run.py compare scenarios/a.yaml scenarios/b.yaml [...]

Loads a shared baseline + assumptions, builds the spine and runs the Monte
Carlo comparison for each scenario, then writes a metric table (with deltas
vs. the first scenario), a fan chart PNG per scenario, and a markdown summary.
Output location defaults to ./output; point --outdir at your Obsidian vault
once that path is decided (spec section 6 -- TBD at build time).
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

from engine.metrics import ScenarioMetrics, compute_scenario_metrics
from engine.spine import build_spine

def load_yaml(path: str) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def _money(v) -> str:
    return f"${v:,.0f}" if v is not None else "n/a"


def _add_numeric_row(lines: list, all_metrics: list, baseline: "ScenarioMetrics", label: str, getter, fmt) -> None:
    base_val = getter(baseline)
    cells = []
    for i, m in enumerate(all_metrics):
        value = getter(m)
        cell = fmt(value)
        if i > 0 and len(all_metrics) > 1:
            delta = value - base_val
            sign = "+" if delta >= 0 else ""
            cell = f"{cell} ({sign}{fmt(delta)})"
        cells.append(cell)
    lines.append("| " + label + " | " + " | ".join(cells) + " |")


def build_metric_table(all_metrics: list[ScenarioMetrics]) -> str:
    baseline = all_metrics[0]
    lines = [
        "| Metric | " + " | ".join(m.name for m in all_metrics) + " |",
        "|" + "---|" * (len(all_metrics) + 1),
    ]

    _add_numeric_row(lines, all_metrics, baseline, "Endowment income ($/mo)",
                      lambda m: m.endowment_income, lambda v: f"${v:,.0f}")
    _add_numeric_row(lines, all_metrics, baseline, "Survival probability",
                      lambda m: m.survival_pct * 100, lambda v: f"{v:.1f}%")
    _add_numeric_row(lines, all_metrics, baseline, "Median total at horizon (real $)",
                      lambda m: m.median_total_real_at_horizon, lambda v: f"${v:,.0f}")

    bucket_names = sorted({b for m in all_metrics for b in m.bucket_mix_real_at_horizon})
    for bucket in bucket_names:
        _add_numeric_row(
            lines, all_metrics, baseline, f"  {bucket} (real $)",
            lambda m, b=bucket: m.bucket_mix_real_at_horizon.get(b, 0.0), lambda v: f"${v:,.0f}",
        )

    loan_names = sorted({loan for m in all_metrics for loan in set(m.conversions) | set(m.payoff_years)})
    for loan in loan_names:
        cells = [_money((m.conversions.get(loan) or {}).get("balance")) for m in all_metrics]
        lines.append(f"| {loan} conversion balance | " + " | ".join(cells) + " |")
        cells = [_money((m.conversions.get(loan) or {}).get("payment")) for m in all_metrics]
        lines.append(f"| {loan} conversion payment | " + " | ".join(cells) + " |")
        cells = [str(m.payoff_years.get(loan)) if m.payoff_years.get(loan) is not None else "n/a" for m in all_metrics]
        lines.append(f"| {loan} payoff year | " + " | ".join(cells) + " |")

    return "\n".join(lines)


def plot_fan_chart(name: str, bands: dict, start_year: int, retire_month: int, outpath: Path) -> None:
    n_months = len(next(iter(bands.values()))) - 1
    x = [start_year + i / 12 for i in range(n_months + 1)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(x, bands[10], bands[90], alpha=0.2, label="p10-p90", color="steelblue")
    ax.fill_between(x, bands[25], bands[75], alpha=0.35, label="p25-p75", color="steelblue")
    ax.plot(x, bands[50], label="median", linewidth=2, color="steelblue")
    ax.axvline(start_year + retire_month / 12, linestyle="--", color="gray", label="retirement")
    ax.set_title(f"{name} — real portfolio value")
    ax.set_xlabel("Year")
    ax.set_ylabel("Real portfolio value (today's $)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def write_summary_md(all_metrics: list[ScenarioMetrics], table_md: str, chart_paths: list[Path], outdir: Path) -> Path:
    lines = ["# Retirement Monte Carlo Comparison", "", table_md, "", "## Fan charts", ""]
    for m, chart_path in zip(all_metrics, chart_paths):
        lines.append(f"### {m.name}")
        lines.append(f"![{m.name}]({chart_path.name})")
        lines.append("")
    outpath = outdir / "summary.md"
    outpath.write_text("\n".join(lines))
    return outpath


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def run_compare(scenario_paths: list[str], baseline_path: str, assumptions_path: str, target: float, outdir: str) -> Path:
    baseline = load_yaml(baseline_path)
    assumptions = load_yaml(assumptions_path)
    start_year = int(str(baseline["timeline"]["start"]).split("-")[0])

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    all_metrics = []
    chart_paths = []
    for scenario_path in scenario_paths:
        scenario = load_yaml(scenario_path)
        spine = build_spine(baseline, assumptions, scenario)
        m = compute_scenario_metrics(
            scenario["name"], spine, assumptions["returns"],
            assumptions["inflation"], baseline["buckets"], scenario["draw_order"],
            target, assumptions["paths"], assumptions["seed"],
        )
        all_metrics.append(m)

        chart_path = out / f"fan-{_slug(scenario['name'])}.png"
        plot_fan_chart(m.name, m.bands, start_year, spine.retire_month, chart_path)
        chart_paths.append(chart_path)

    table_md = build_metric_table(all_metrics)
    print(table_md)
    summary_path = write_summary_md(all_metrics, table_md, chart_paths, out)
    print(f"\nSummary written to {summary_path}")
    return summary_path


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="run.py")
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser("compare", help="Compare 1+ scenarios against a shared baseline/assumptions")
    compare.add_argument("scenarios", nargs="+", help="Scenario YAML files")
    compare.add_argument("--baseline", default="data/baseline.yaml")
    compare.add_argument("--assumptions", default="data/assumptions.yaml")
    compare.add_argument("--target", type=float, default=20_000.0, help="Target monthly income, today's $")
    compare.add_argument("--outdir", default="output")

    args = parser.parse_args(argv)
    run_compare(args.scenarios, args.baseline, args.assumptions, args.target, args.outdir)


if __name__ == "__main__":
    main()
