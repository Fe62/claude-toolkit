"""montecarlo.py -- Layer 2: stochastic overlay on top of the deterministic spine.

Vectorized across paths (numpy). Random draws apply ONLY to market returns.
Common random numbers: the return draws depend only on (equity_return,
equity_vol, n_months, paths, seed) -- never on scenario/lever data -- so
calling this with the same assumptions across two scenarios reuses the exact
same draw sequence and isolates lever effects in the comparison.

Convention: each month, external cash flows (contributions, taxable inflow,
retirement withdrawal/surplus) are applied first, then the resulting balance
is grown by that month's return. All three buckets share the same monthly
return draw (same growth in Phase 1 -- no tax differentiation yet).
"""

from dataclasses import dataclass

import numpy as np

from engine.spine import SpineResult

_ORDER_MAP = {
    "t-p-r": ("taxable", "pretax", "roth"),
    "p-t-r": ("pretax", "taxable", "roth"),
}


@dataclass
class PathResult:
    taxable: np.ndarray      # shape (paths, n_months+1) -- balance at START of each month
    pretax: np.ndarray
    roth: np.ndarray
    failed: np.ndarray        # shape (paths,) bool -- True if need ever went unmet
    failed_month: np.ndarray  # shape (paths,) int -- month of first failure, -1 if never


def _monthly_mu_sigma(equity_return: float, equity_vol: float) -> tuple[float, float]:
    sigma_m = equity_vol / np.sqrt(12)
    mu = np.log(1 + equity_return) / 12 - sigma_m ** 2 / 2
    return mu, sigma_m


def monthly_return_draws(equity_return: float, equity_vol: float, n_months: int, paths: int, seed: int) -> np.ndarray:
    """Common-random-number lognormal monthly return draws, shape (paths, n_months)."""
    rng = np.random.default_rng(seed)
    mu, sigma_m = _monthly_mu_sigma(equity_return, equity_vol)
    z = rng.standard_normal((paths, n_months))
    return np.exp(mu + sigma_m * z) - 1


def median_deterministic_return(equity_return: float, equity_vol: float, n_months: int) -> np.ndarray:
    """Median-path monthly return: exp(mu)-1, i.e. the geometric mean (includes vol drag)."""
    mu, _ = _monthly_mu_sigma(equity_return, equity_vol)
    return np.full(n_months, np.exp(mu) - 1)


def _apply_need(need: np.ndarray, buckets: dict, draw_order: str) -> tuple[dict, np.ndarray]:
    """Apply retirement `need` (can be negative) across buckets.

    Negative need (income exceeds spending) deposits the surplus into taxable.
    Positive need drains buckets per draw_order: sequential for "t-p-r"/"p-t-r",
    pro-rata (re-normalized each round as buckets empty) for "proportional".
    Returns (updated buckets, unmet) where unmet is the shortfall if all
    relevant buckets are exhausted before need is covered.
    """
    surplus = np.maximum(-need, 0.0)
    need = np.maximum(need, 0.0)
    buckets = dict(buckets)
    buckets["taxable"] = buckets["taxable"] + surplus

    if draw_order == "proportional":
        remaining = need.copy()
        for _ in range(3):  # at most 3 rounds to drain 3 buckets
            if not np.any(remaining > 1e-9):
                break
            total = sum(buckets.values())
            share = {k: np.where(total > 1e-9, v / np.maximum(total, 1e-12), 0.0) for k, v in buckets.items()}
            take = {k: np.minimum(buckets[k], remaining * share[k]) for k in buckets}
            buckets = {k: buckets[k] - take[k] for k in buckets}
            remaining = remaining - sum(take.values())
        unmet = np.maximum(remaining, 0.0)
    else:
        order = _ORDER_MAP[draw_order]
        remaining = need.copy()
        for name in order:
            take = np.minimum(buckets[name], remaining)
            buckets[name] = buckets[name] - take
            remaining = remaining - take
        unmet = np.maximum(remaining, 0.0)

    return buckets, unmet


def run(
    spine: SpineResult,
    equity_return: float,
    equity_vol: float,
    inflation: float,
    target_income_today: float,
    draw_order: str,
    initial_buckets: dict,
    paths: int,
    seed: int,
    deterministic: bool = False,
) -> PathResult:
    n_months = len(spine.months)
    if deterministic:
        n_paths = 1
        returns = median_deterministic_return(equity_return, equity_vol, n_months)[None, :]
    else:
        n_paths = paths
        returns = monthly_return_draws(equity_return, equity_vol, n_months, n_paths, seed)

    buckets = {
        "taxable": np.full(n_paths, float(initial_buckets.get("taxable", 0.0))),
        "pretax": np.full(n_paths, float(initial_buckets.get("pretax", 0.0))),
        "roth": np.full(n_paths, float(initial_buckets.get("roth", 0.0))),
    }
    history = {k: np.zeros((n_paths, n_months + 1)) for k in buckets}
    for k in buckets:
        history[k][:, 0] = buckets[k]

    failed = np.zeros(n_paths, dtype=bool)
    failed_month = np.full(n_paths, -1, dtype=int)

    for t, flow in enumerate(spine.months):
        buckets["pretax"] = buckets["pretax"] + flow.pretax_contribution
        buckets["roth"] = buckets["roth"] + flow.roth_contribution
        buckets["taxable"] = buckets["taxable"] + flow.taxable_inflow

        if flow.phase == "retired":
            target_nominal = target_income_today * (1 + inflation) ** (t / 12)
            debt_service = flow.loan_a_payment + flow.loan_b_payment
            need_value = target_nominal + debt_service - flow.rental_net - flow.ss_income
            need = np.full(n_paths, need_value)
            buckets, unmet = _apply_need(need, buckets, draw_order)
            newly_failed = (~failed) & (unmet > 1e-6)
            failed_month = np.where(newly_failed, t, failed_month)
            failed = failed | newly_failed

        growth = 1.0 + returns[:, t]
        for k in buckets:
            buckets[k] = np.where(failed, 0.0, buckets[k] * growth)
            history[k][:, t + 1] = buckets[k]

    return PathResult(
        taxable=history["taxable"], pretax=history["pretax"], roth=history["roth"],
        failed=failed, failed_month=failed_month,
    )
