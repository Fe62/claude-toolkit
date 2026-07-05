"""metrics.py -- endowment search, survival probability, percentile bands,
and the composite per-scenario metric bundle consumed by the CLI/report.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from engine.montecarlo import PathResult
from engine.montecarlo import run as run_montecarlo
from engine.spine import SpineResult


def deflate(nominal: float, inflation: float, month: int) -> float:
    """Convert a nominal dollar amount at `month` into today's $ (real terms)."""
    return nominal / (1 + inflation) ** (month / 12)


def real_total_path(result: PathResult, inflation: float) -> np.ndarray:
    """Real (deflated) combined portfolio value, shape (paths, n_months+1)."""
    nominal_total = result.taxable + result.pretax + result.roth
    n_months = nominal_total.shape[1] - 1
    deflator = np.array([(1 + inflation) ** (t / 12) for t in range(n_months + 1)])
    return nominal_total / deflator


def percentile_bands(
    result: PathResult, inflation: float, percentiles: tuple = (10, 25, 50, 75, 90)
) -> dict:
    """Real portfolio percentile trajectories, for fan-chart plotting."""
    real = real_total_path(result, inflation)
    return {p: np.percentile(real, p, axis=0) for p in percentiles}


def survival_probability(result: PathResult) -> float:
    """Fraction of paths that never failed to meet the retirement income need."""
    return float((~result.failed).mean())


def endowment_income(
    spine: SpineResult,
    equity_return: float,
    equity_vol: float,
    inflation: float,
    initial_buckets: dict,
    draw_order: str,
    lo: float = 0.0,
    hi: float = 1_000_000.0,
    iterations: int = 40,
) -> float:
    """Max sustainable monthly income (today's $) on the median deterministic path,
    per spec section 5: real total at horizon >= real total at retirement, no failure.
    """

    def holds(income: float) -> bool:
        det = run_montecarlo(
            spine, equity_return, equity_vol, inflation, income, draw_order,
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
    conversion_balance: Optional[float]
    conversion_payment: Optional[float]
    payoff_year_a: Optional[int]
    payoff_year_b: Optional[int]
    median_total_real_at_horizon: float
    bucket_mix_real_at_horizon: dict
    bands: dict


def compute_scenario_metrics(
    name: str,
    spine: SpineResult,
    equity_return: float,
    equity_vol: float,
    inflation: float,
    initial_buckets: dict,
    draw_order: str,
    target_income_today: float,
    paths: int,
    seed: int,
) -> ScenarioMetrics:
    mc = run_montecarlo(
        spine, equity_return, equity_vol, inflation, target_income_today, draw_order,
        initial_buckets, paths=paths, seed=seed,
    )
    det = run_montecarlo(
        spine, equity_return, equity_vol, inflation, target_income_today, draw_order,
        initial_buckets, paths=1, seed=seed, deterministic=True,
    )

    endowment = endowment_income(spine, equity_return, equity_vol, inflation, initial_buckets, draw_order)
    survival = survival_probability(mc)
    bands = percentile_bands(mc, inflation)

    deflator = (1 + inflation) ** (len(spine.months) / 12)
    bucket_mix = {
        "taxable": det.taxable[0, -1] / deflator,
        "pretax": det.pretax[0, -1] / deflator,
        "roth": det.roth[0, -1] / deflator,
    }
    median_total = sum(bucket_mix.values())

    payoff_year_a = spine.months[spine.payoff_month_a].year if spine.payoff_month_a is not None else None
    payoff_year_b = spine.months[spine.payoff_month_b].year if spine.payoff_month_b is not None else None

    return ScenarioMetrics(
        name=name,
        endowment_income=endowment,
        survival_pct=survival,
        conversion_balance=spine.conversion_balance,
        conversion_payment=spine.conversion_payment,
        payoff_year_a=payoff_year_a,
        payoff_year_b=payoff_year_b,
        median_total_real_at_horizon=median_total,
        bucket_mix_real_at_horizon=bucket_mix,
        bands=bands,
    )
