"""metrics.py -- endowment search, survival probability, percentile bands,
and the composite per-scenario metric bundle consumed by the CLI/report.
"""

from dataclasses import dataclass

import numpy as np

from engine.montecarlo import LIQUID_BUCKETS, PathResult
from engine.montecarlo import run as run_montecarlo
from engine.spine import SpineResult


def deflate(nominal: float, inflation: float, month: int) -> float:
    """Convert a nominal dollar amount at `month` into today's $ (real terms)."""
    return nominal / (1 + inflation) ** (month / 12)


def real_total_path(result: PathResult, inflation: float, bucket_names: tuple = LIQUID_BUCKETS) -> np.ndarray:
    """Real (deflated) combined value of `bucket_names`, shape (paths, n_months+1).

    Defaults to the liquid buckets (taxable/pretax/roth) -- the survival and
    endowment metrics are about sustaining spendable income, not net worth
    including illiquid assets like real estate.
    """
    present = [b for b in bucket_names if b in result.buckets]
    nominal_total = sum(result.buckets[b] for b in present)
    n_months = nominal_total.shape[1] - 1
    deflator = np.array([(1 + inflation) ** (t / 12) for t in range(n_months + 1)])
    return nominal_total / deflator


def percentile_bands(
    result: PathResult, inflation: float, percentiles: tuple = (10, 25, 50, 75, 90)
) -> dict:
    """Real (liquid) portfolio percentile trajectories, for fan-chart plotting."""
    real = real_total_path(result, inflation)
    return {p: np.percentile(real, p, axis=0) for p in percentiles}


def survival_probability(result: PathResult) -> float:
    """Fraction of paths that never failed to meet the retirement income need."""
    return float((~result.failed).mean())


def endowment_income(
    spine: SpineResult,
    returns_cfg: dict,
    inflation: float,
    initial_buckets: dict,
    draw_order: str,
    lo: float = 0.0,
    hi: float = 1_000_000.0,
    iterations: int = 40,
) -> float:
    """Max sustainable monthly income (today's $) on the median deterministic path,
    per spec section 5: real (liquid) total at horizon >= real total at retirement,
    no failure.
    """

    def holds(income: float) -> bool:
        det = run_montecarlo(
            spine, returns_cfg, inflation, income, draw_order,
            initial_buckets, paths=1, seed=0, deterministic=True,
        )
        if det.failed[0]:
            return False
        real = real_total_path(det, inflation)[0]
        retire_month = min(max(spine.retire_month, 0), len(spine.months))
        return real[-1] >= real[retire_month]

    if not holds(lo):
        return 0.0  # degenerate balance sheet: even zero income erodes principal

    for _ in range(iterations):
        mid = (lo + hi) / 2
        if holds(mid):
            lo = mid
        else:
            hi = mid
    return lo


@dataclass
class ScenarioMetrics:
    name: str
    endowment_income: float
    survival_pct: float
    conversions: dict            # loan name -> {"balance": float, "payment": float}
    payoff_years: dict           # loan name -> Optional[int]
    median_total_real_at_horizon: float
    bucket_mix_real_at_horizon: dict
    bands: dict


def compute_scenario_metrics(
    name: str,
    spine: SpineResult,
    returns_cfg: dict,
    inflation: float,
    initial_buckets: dict,
    draw_order: str,
    target_income_today: float,
    paths: int,
    seed: int,
) -> ScenarioMetrics:
    mc = run_montecarlo(
        spine, returns_cfg, inflation, target_income_today, draw_order,
        initial_buckets, paths=paths, seed=seed,
    )
    det = run_montecarlo(
        spine, returns_cfg, inflation, target_income_today, draw_order,
        initial_buckets, paths=1, seed=seed, deterministic=True,
    )

    endowment = endowment_income(spine, returns_cfg, inflation, initial_buckets, draw_order)
    survival = survival_probability(mc)
    bands = percentile_bands(mc, inflation)

    deflator = (1 + inflation) ** (len(spine.months) / 12)
    bucket_mix = {name_: det.buckets[name_][0, -1] / deflator for name_ in det.buckets}
    median_total = sum(bucket_mix.values())

    payoff_years = {
        loan_name: (spine.months[month].year if month is not None else None)
        for loan_name, month in spine.payoff_months.items()
    }

    return ScenarioMetrics(
        name=name,
        endowment_income=endowment,
        survival_pct=survival,
        conversions=spine.conversions,
        payoff_years=payoff_years,
        median_total_real_at_horizon=median_total,
        bucket_mix_real_at_horizon=bucket_mix,
        bands=bands,
    )
