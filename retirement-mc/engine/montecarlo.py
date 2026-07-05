"""montecarlo.py -- Layer 2: stochastic overlay on top of the deterministic spine.

Vectorized across paths (numpy). Random draws apply ONLY to market returns.
Common random numbers: each return-type's draw depends only on (its own
return/vol, n_months, paths, seed) -- never on scenario/lever data -- so
calling this with the same assumptions across two scenarios reuses the exact
same draw sequence and isolates lever effects in the comparison. Return types
get independent draw streams (spawned from one seed), so equity and real
estate don't move in lockstep.

Convention: each month, external cash flows (contributions, taxable inflow,
retirement withdrawal/surplus) are applied first, then each bucket is grown
by its own return type's draw for that month. LIQUID_BUCKETS (taxable,
pretax, roth) are the ones retirement withdrawals draw from and the ones that
clamp to zero on failure; other buckets (e.g. real_estate) grow passively and
are not touched by the withdrawal machinery or the failure clamp -- an
illiquid asset doesn't vanish just because the liquid buckets ran dry.
"""

from dataclasses import dataclass

import numpy as np

from engine.spine import SpineResult

LIQUID_BUCKETS = ("taxable", "pretax", "roth")

BUCKET_RETURN_TYPE = {
    "taxable": "equity",
    "pretax": "equity",
    "roth": "equity",
    "real_estate": "real_estate",
}

_ORDER_MAP = {
    "t-p-r": ("taxable", "pretax", "roth"),
    "p-t-r": ("pretax", "taxable", "roth"),
}


@dataclass
class PathResult:
    buckets: dict             # bucket name -> ndarray, shape (paths, n_months+1)
    failed: np.ndarray         # shape (paths,) bool -- True if need ever went unmet
    failed_month: np.ndarray   # shape (paths,) int -- month of first failure, -1 if never


def _monthly_mu_sigma(annual_return: float, annual_vol: float) -> tuple[float, float]:
    sigma_m = annual_vol / np.sqrt(12)
    mu = np.log(1 + annual_return) / 12 - sigma_m ** 2 / 2
    return mu, sigma_m


def monthly_return_draws(returns_cfg: dict, n_months: int, paths: int, seed: int) -> dict:
    """Common-random-number lognormal monthly return draws per return-type.

    Each return-type (e.g. "equity", "real_estate") gets its own independent
    draw stream, shape (paths, n_months), spawned deterministically from `seed`.
    """
    names = sorted(returns_cfg.keys())
    child_seeds = np.random.SeedSequence(seed).spawn(len(names))
    draws = {}
    for name, child in zip(names, child_seeds):
        rng = np.random.default_rng(child)
        mu, sigma_m = _monthly_mu_sigma(returns_cfg[name]["return"], returns_cfg[name]["vol"])
        z = rng.standard_normal((paths, n_months))
        draws[name] = np.exp(mu + sigma_m * z) - 1
    return draws


def median_deterministic_return(returns_cfg: dict, n_months: int) -> dict:
    """Median-path monthly return per return-type: exp(mu)-1 (includes vol drag)."""
    draws = {}
    for name, cfg in returns_cfg.items():
        mu, _ = _monthly_mu_sigma(cfg["return"], cfg["vol"])
        draws[name] = np.full(n_months, np.exp(mu) - 1)
    return draws


def _apply_need(need: np.ndarray, buckets: dict, draw_order: str) -> tuple[dict, np.ndarray]:
    """Apply retirement `need` (can be negative) across the given (liquid) buckets.

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
        for _ in range(len(buckets)):  # enough rounds to drain every bucket in turn
            if not np.any(remaining > 1e-9):
                break
            total = sum(buckets.values())
            share = {k: np.where(total > 1e-9, v / np.maximum(total, 1e-12), 0.0) for k, v in buckets.items()}
            take = {k: np.minimum(buckets[k], remaining * share[k]) for k in buckets}
            buckets = {k: buckets[k] - take[k] for k in buckets}
            remaining = remaining - sum(take.values())
        unmet = np.maximum(remaining, 0.0)
    else:
        order = [name for name in _ORDER_MAP[draw_order] if name in buckets]
        remaining = need.copy()
        for name in order:
            take = np.minimum(buckets[name], remaining)
            buckets[name] = buckets[name] - take
            remaining = remaining - take
        unmet = np.maximum(remaining, 0.0)

    return buckets, unmet


def run(
    spine: SpineResult,
    returns_cfg: dict,
    inflation: float,
    target_income_today: float,
    draw_order: str,
    initial_buckets: dict,
    paths: int,
    seed: int,
    deterministic: bool = False,
) -> PathResult:
    n_months = len(spine.months)
    bucket_names = list(initial_buckets.keys())

    if deterministic:
        n_paths = 1
        returns = {k: v[None, :] for k, v in median_deterministic_return(returns_cfg, n_months).items()}
    else:
        n_paths = paths
        returns = monthly_return_draws(returns_cfg, n_months, n_paths, seed)

    buckets = {name: np.full(n_paths, float(initial_buckets.get(name, 0.0))) for name in bucket_names}
    history = {name: np.zeros((n_paths, n_months + 1)) for name in bucket_names}
    for name in bucket_names:
        history[name][:, 0] = buckets[name]

    failed = np.zeros(n_paths, dtype=bool)
    failed_month = np.full(n_paths, -1, dtype=int)

    for t, flow in enumerate(spine.months):
        if "pretax" in buckets:
            buckets["pretax"] = buckets["pretax"] + flow.pretax_contribution
        if "roth" in buckets:
            buckets["roth"] = buckets["roth"] + flow.roth_contribution
        if "taxable" in buckets:
            buckets["taxable"] = buckets["taxable"] + flow.taxable_inflow

        if flow.phase == "retired":
            target_nominal = target_income_today * (1 + inflation) ** (t / 12)
            need_value = target_nominal + flow.total_debt_service - flow.rental_net - flow.ss_income
            need = np.full(n_paths, need_value)
            liquid = {k: buckets[k] for k in LIQUID_BUCKETS if k in buckets}
            liquid, unmet = _apply_need(need, liquid, draw_order)
            buckets.update(liquid)
            newly_failed = (~failed) & (unmet > 1e-6)
            failed_month = np.where(newly_failed, t, failed_month)
            failed = failed | newly_failed

        for name in bucket_names:
            growth = 1.0 + returns[BUCKET_RETURN_TYPE[name]][:, t]
            grown = buckets[name] * growth
            if name in LIQUID_BUCKETS:
                grown = np.where(failed, 0.0, grown)
            buckets[name] = grown
            history[name][:, t + 1] = buckets[name]

    return PathResult(buckets=history, failed=failed, failed_month=failed_month)
