import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_module
from engine.metrics import ScenarioMetrics


def make_metrics(name, endowment, survival, taxable=1000.0, pretax=0.0, roth=0.0,
                  conversions=None, payoff_years=None):
    bands = {p: np.array([100.0, 200.0]) for p in (10, 25, 50, 75, 90)}
    return ScenarioMetrics(
        name=name, endowment_income=endowment, survival_pct=survival,
        conversions=conversions or {}, payoff_years=payoff_years or {},
        median_total_real_at_horizon=taxable + pretax + roth,
        bucket_mix_real_at_horizon={"taxable": taxable, "pretax": pretax, "roth": roth},
        bands=bands,
    )


def test_build_metric_table_shows_deltas_vs_first_scenario():
    a = make_metrics("Invest", endowment=1000.0, survival=0.8)
    b = make_metrics("Prepay", endowment=1200.0, survival=0.9)
    table = run_module.build_metric_table([a, b])
    assert "Invest" in table and "Prepay" in table
    assert "$1,000" in table
    assert "$1,200 (+$200)" in table
    assert "90.0% (+10.0%)" in table


def test_build_metric_table_handles_missing_loan_info():
    a = make_metrics("Baseline", endowment=500.0, survival=1.0)
    table = run_module.build_metric_table([a])
    assert "loan" not in table.lower()  # no loans in this fixture -> no loan rows at all


def test_build_metric_table_shows_loan_conversion_and_payoff_rows():
    a = make_metrics(
        "WithLoans", endowment=500.0, survival=1.0,
        conversions={"loan_a": {"balance": 200_000.0, "payment": 1_500.0}},
        payoff_years={"loan_a": None, "loan_c": 2035},
    )
    table = run_module.build_metric_table([a])
    assert "loan_a conversion balance" in table
    assert "$200,000" in table
    assert "loan_c payoff year" in table
    assert "2035" in table
    assert "n/a" in table  # loan_a has no payoff year, loan_c has no conversion


def test_plot_fan_chart_writes_png(tmp_path):
    bands = {p: np.linspace(100, 200, 13) for p in (10, 25, 50, 75, 90)}
    outpath = tmp_path / "fan.png"
    run_module.plot_fan_chart("Test", bands, start_year=2026, retire_month=6, outpath=outpath)
    assert outpath.exists()
    assert outpath.stat().st_size > 0


def test_write_summary_md_includes_table_and_chart_links(tmp_path):
    a = make_metrics("Invest", endowment=1000.0, survival=0.8)
    chart_path = tmp_path / "fan-invest.png"
    chart_path.write_bytes(b"fake-png")
    summary = run_module.write_summary_md([a], "TABLE_MARKDOWN", [chart_path], tmp_path)
    content = summary.read_text()
    assert "TABLE_MARKDOWN" in content
    assert "fan-invest.png" in content


def test_run_compare_end_to_end_against_example_data_files(tmp_path):
    # Uses baseline.example.yaml (checked into git) rather than the real, gitignored
    # baseline.yaml, so this test is reproducible from a fresh clone.
    repo_root = Path(__file__).resolve().parents[1]
    summary = run_module.run_compare(
        scenario_paths=[
            str(repo_root / "data/scenarios/a-invest.yaml"),
            str(repo_root / "data/scenarios/b-prepay.yaml"),
        ],
        baseline_path=str(repo_root / "data/baseline.example.yaml"),
        assumptions_path=str(repo_root / "data/assumptions.yaml"),
        target=20_000.0,
        outdir=str(tmp_path),
    )
    assert summary.exists()
    content = summary.read_text()
    assert "Invest surplus" in content
    assert "Prepay A hard" in content
    pngs = list(tmp_path.glob("fan-*.png"))
    assert len(pngs) == 2


def test_run_compare_with_nonzero_scenario_and_five_loans(tmp_path):
    baseline = {
        "timeline": {"start": "2026-01", "horizon": 2030, "step": "monthly"},
        "buckets": {"taxable": 50_000, "pretax": 20_000, "roth": 10_000, "real_estate": 100_000},
        "contributions": {"pretax": 300.0, "roth": 100.0},
        "income": {"surplus": 2000.0, "rental_net": 500.0},
        "liabilities": {
            "loan_a": {"type": "io_amortizing", "balance": 300_000.0, "rate": 0.06, "io_until": 2031, "amort_years": 25},
            "loan_b": {"type": "standard_amortizing", "balance": 40_000.0, "rate": 0.055, "years_left": 10},
            "loan_c": {"type": "revolving_interest_only", "balance": 15_000.0, "rate": 0.08},
            "loan_d": {"type": "revolving_interest_only", "balance": 25_000.0, "rate": 0.07},
            "loan_e": {"type": "revolving_interest_only", "balance": 5_000.0, "rate": 0.22, "min_payment_pct": 0.02},
        },
        "social_security": {
            "person1": [{"age": 67, "year": 2029, "monthly": 1800.0}],
            "person2": [{"age": 67, "year": 2029, "monthly": 1200.0}],
        },
    }
    assumptions = {
        "returns": {"equity": {"return": 0.06, "vol": 0.1}, "real_estate": {"return": 0.04, "vol": 0.08}},
        "inflation": 0.02, "paths": 300, "seed": 3,
    }
    scenario = {
        "name": "Simple Invest",
        "retire_year": 2029,
        "alloc": {"loan_a": 10, "loan_b": 10, "loan_c": 10, "loan_d": 10, "loan_e": 10},
        "recast": {"loan_a": False},
        "recovery": {"amount": 0, "year": None},
        "draw_order": "t-p-r",
        "sell_property": {"enabled": False, "year": 2030, "proceeds": 0},
        "ss_claim": {"person1": 67, "person2": 67},
    }
    baseline_path = tmp_path / "baseline.yaml"
    assumptions_path = tmp_path / "assumptions.yaml"
    scenario_path = tmp_path / "scenario.yaml"
    baseline_path.write_text(yaml.dump(baseline))
    assumptions_path.write_text(yaml.dump(assumptions))
    scenario_path.write_text(yaml.dump(scenario))

    summary = run_module.run_compare(
        scenario_paths=[str(scenario_path)],
        baseline_path=str(baseline_path),
        assumptions_path=str(assumptions_path),
        target=1000.0,
        outdir=str(tmp_path),
    )
    content = summary.read_text()
    assert "Simple Invest" in content
    assert "loan_a conversion balance" in content
    assert "real_estate (real $)" in content
    assert (tmp_path / "fan-simple-invest.png").exists()
