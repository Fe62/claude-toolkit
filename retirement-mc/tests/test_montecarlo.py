import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine import montecarlo
from engine.spine import MonthFlow, SpineResult

EQUITY_ONLY = {"equity": {"return": 0.075, "vol": 0.15}}


def make_spine(n_months, retire_month, monthly_contribution=1000.0):
    months = []
    for t in range(n_months):
        phase = "working" if t < retire_month else "retired"
        months.append(
            MonthFlow(
                month=t, year=2026 + t // 12, cal_month=t % 12 + 1, phase=phase,
                pretax_contribution=0.0,
                roth_contribution=0.0,
                taxable_inflow=monthly_contribution if phase == "working" else 0.0,
                rental_net=0.0,
                ss_income=0.0,
                loan_payments={},
            )
        )
    return SpineResult(
        months=months, retire_month=retire_month,
        conversions={}, payoff_months={},
    )


# --- Common random numbers -----------------------------------------------------

def test_monthly_return_draws_are_deterministic_given_same_inputs():
    a = montecarlo.monthly_return_draws(EQUITY_ONLY, 24, 500, seed=42)
    b = montecarlo.monthly_return_draws(EQUITY_ONLY, 24, 500, seed=42)
    np.testing.assert_array_equal(a["equity"], b["equity"])


def test_return_types_get_independent_draw_streams():
    returns_cfg = {"equity": {"return": 0.075, "vol": 0.15}, "real_estate": {"return": 0.04, "vol": 0.08}}
    draws = montecarlo.monthly_return_draws(returns_cfg, n_months=24, paths=500, seed=42)
    assert not np.allclose(draws["equity"], draws["real_estate"])


def test_return_draws_independent_of_scenario_only_seed_and_assumptions_matter():
    # Two "scenarios" (different target income, different spine) but same
    # assumptions+seed must reuse the identical draw sequence.
    spine_a = make_spine(36, retire_month=12, monthly_contribution=500.0)
    spine_b = make_spine(36, retire_month=12, monthly_contribution=9000.0)

    result_a = montecarlo.run(
        spine_a, EQUITY_ONLY, 0.025, target_income_today=2000.0, draw_order="t-p-r",
        initial_buckets={"taxable": 10_000}, paths=200, seed=7,
    )
    result_b = montecarlo.run(
        spine_b, EQUITY_ONLY, 0.025, target_income_today=2000.0, draw_order="t-p-r",
        initial_buckets={"taxable": 10_000}, paths=200, seed=7,
    )
    draws = montecarlo.monthly_return_draws(EQUITY_ONLY, 36, 200, seed=7)
    assert result_a.buckets["taxable"].shape == result_b.buckets["taxable"].shape == (200, 37)
    assert draws["equity"].shape == (200, 36)


# --- Zero-vol parity (spec verification plan item 2) ---------------------------

def test_zero_vol_montecarlo_matches_deterministic_path():
    spine = make_spine(60, retire_month=24, monthly_contribution=1500.0)
    zero_vol = {"equity": {"return": 0.075, "vol": 0.0}}
    mc = montecarlo.run(
        spine, zero_vol, inflation=0.025,
        target_income_today=1000.0, draw_order="t-p-r",
        initial_buckets={"taxable": 5_000, "pretax": 2_000, "roth": 1_000},
        paths=200, seed=99,
    )
    det = montecarlo.run(
        spine, zero_vol, inflation=0.025,
        target_income_today=1000.0, draw_order="t-p-r",
        initial_buckets={"taxable": 5_000, "pretax": 2_000, "roth": 1_000},
        paths=1, seed=99, deterministic=True,
    )
    taxable = mc.buckets["taxable"]
    p10 = np.percentile(taxable[:, -1], 10)
    p50 = np.percentile(taxable[:, -1], 50)
    p90 = np.percentile(taxable[:, -1], 90)
    assert math.isclose(p10, p50, rel_tol=1e-9)
    assert math.isclose(p50, p90, rel_tol=1e-9)
    assert math.isclose(p50, det.buckets["taxable"][0, -1], rel_tol=1e-9)
    # All 200 zero-vol paths should be bit-identical to each other, month by month.
    np.testing.assert_allclose(taxable, np.tile(taxable[0], (200, 1)))


# --- Working-phase growth sanity -----------------------------------------------

def test_deterministic_growth_matches_hand_computed_compounding():
    spine = make_spine(12, retire_month=100, monthly_contribution=0.0)  # never retires
    zero_vol = {"equity": {"return": 0.06, "vol": 0.0}}
    det = montecarlo.run(
        spine, zero_vol, inflation=0.0,
        target_income_today=0.0, draw_order="t-p-r",
        initial_buckets={"taxable": 10_000}, paths=1, seed=1, deterministic=True,
    )
    mu, _ = montecarlo._monthly_mu_sigma(0.06, 0.0)
    expected = 10_000 * math.exp(mu) ** 12
    assert math.isclose(det.buckets["taxable"][0, -1], expected, rel_tol=1e-9)


def test_real_estate_bucket_grows_independently_and_ignores_failure():
    spine = make_spine(12, retire_month=0, monthly_contribution=0.0)
    returns_cfg = {"equity": {"return": 0.05, "vol": 0.0}, "real_estate": {"return": 0.10, "vol": 0.0}}
    det = montecarlo.run(
        spine, returns_cfg, inflation=0.0,
        target_income_today=100_000.0, draw_order="t-p-r",  # deliberately unaffordable -> failure
        initial_buckets={"taxable": 1_000, "real_estate": 50_000}, paths=1, seed=1, deterministic=True,
    )
    assert det.failed[0]
    assert det.buckets["taxable"][0, -1] == 0.0  # liquid bucket clamps to zero on failure
    # Illiquid real_estate keeps growing at its own rate regardless of the failure.
    mu, _ = montecarlo._monthly_mu_sigma(0.10, 0.0)
    expected = 50_000 * math.exp(mu) ** 12
    assert math.isclose(det.buckets["real_estate"][0, -1], expected, rel_tol=1e-9)


# --- Retirement withdrawal ordering --------------------------------------------

def test_sequential_draw_order_drains_taxable_before_pretax():
    spine = make_spine(6, retire_month=0)
    det = montecarlo.run(
        spine, {"equity": {"return": 0.0, "vol": 0.0}}, inflation=0.0,
        target_income_today=100.0, draw_order="t-p-r",
        initial_buckets={"taxable": 250, "pretax": 1_000, "roth": 1_000},
        paths=1, seed=1, deterministic=True,
    )
    taxable = det.buckets["taxable"]
    pretax = det.buckets["pretax"]
    # 250 taxable covers 2 full months (200) + 50 of month 3; pretax picks up the rest.
    assert taxable[0, 1] == 150
    assert taxable[0, 2] == 50
    assert taxable[0, 3] == 0
    assert pretax[0, 3] == 950  # month 3: 50 from taxable, 50 from pretax
    assert not det.failed[0]


def test_proportional_draw_order_splits_pro_rata():
    spine = make_spine(2, retire_month=0)
    det = montecarlo.run(
        spine, {"equity": {"return": 0.0, "vol": 0.0}}, inflation=0.0,
        target_income_today=100.0, draw_order="proportional",
        initial_buckets={"taxable": 300, "pretax": 100, "roth": 0},
        paths=1, seed=1, deterministic=True,
    )
    # 300:100 ratio -> taxable covers 75, pretax covers 25 of the 100 need.
    assert math.isclose(det.buckets["taxable"][0, 1], 225, abs_tol=1e-6)
    assert math.isclose(det.buckets["pretax"][0, 1], 75, abs_tol=1e-6)


def test_negative_need_deposits_surplus_into_taxable():
    spine = make_spine(2, retire_month=0)
    det = montecarlo.run(
        spine, {"equity": {"return": 0.0, "vol": 0.0}}, inflation=0.0,
        target_income_today=-500.0, draw_order="t-p-r",  # rental/SS exceed target -> negative need
        initial_buckets={"taxable": 0}, paths=1, seed=1, deterministic=True,
    )
    assert det.buckets["taxable"][0, 1] == 500


def test_failure_when_all_buckets_exhausted():
    spine = make_spine(12, retire_month=0)
    det = montecarlo.run(
        spine, {"equity": {"return": 0.0, "vol": 0.0}}, inflation=0.0,
        target_income_today=1000.0, draw_order="t-p-r",
        initial_buckets={"taxable": 2_500}, paths=1, seed=1, deterministic=True,
    )
    assert det.failed[0]
    assert det.failed_month[0] == 2  # months 0,1 fully covered (2000), month 2 short by 500
    # Once failed, balances stay clamped at zero for all subsequent months.
    assert det.buckets["taxable"][0, -1] == 0.0
