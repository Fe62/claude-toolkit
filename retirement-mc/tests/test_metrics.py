import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine import metrics
from engine.montecarlo import PathResult
from engine.spine import MonthFlow, SpineResult


def make_spine(n_months, retire_month=0):
    months = [
        MonthFlow(
            month=t, year=2026 + t // 12, cal_month=t % 12 + 1,
            phase="working" if t < retire_month else "retired",
            pretax_contribution=0.0, roth_contribution=0.0, taxable_inflow=0.0,
            rental_net=0.0, ss_income=0.0, loan_a_payment=0.0, loan_b_payment=0.0,
        )
        for t in range(n_months)
    ]
    return SpineResult(
        months=months, retire_month=retire_month,
        conversion_balance=None, conversion_payment=None,
        payoff_month_a=None, payoff_month_b=None,
    )


def test_survival_probability_matches_failed_fraction():
    result = PathResult(
        taxable=np.zeros((4, 1)), pretax=np.zeros((4, 1)), roth=np.zeros((4, 1)),
        failed=np.array([True, False, False, True]), failed_month=np.array([1, -1, -1, 2]),
    )
    assert math.isclose(metrics.survival_probability(result), 0.5)


def test_real_total_path_deflates_correctly():
    result = PathResult(
        taxable=np.array([[100.0, 110.0]]), pretax=np.zeros((1, 2)), roth=np.zeros((1, 2)),
        failed=np.array([False]), failed_month=np.array([-1]),
    )
    real = metrics.real_total_path(result, inflation=0.12)
    assert math.isclose(real[0, 0], 100.0, rel_tol=1e-9)
    assert math.isclose(real[0, 1], 110.0 / (1.12 ** (1 / 12)), rel_tol=1e-9)


def test_percentile_bands_shape_and_ordering():
    taxable = np.array([[100.0], [200.0], [300.0], [400.0], [500.0]])
    result = PathResult(
        taxable=taxable, pretax=np.zeros((5, 1)), roth=np.zeros((5, 1)),
        failed=np.zeros(5, dtype=bool), failed_month=np.full(5, -1),
    )
    bands = metrics.percentile_bands(result, inflation=0.0, percentiles=(10, 50, 90))
    assert set(bands.keys()) == {10, 50, 90}
    assert bands[10][0] <= bands[50][0] <= bands[90][0]


def test_endowment_income_matches_fixed_point_formula():
    # Zero-vol, zero-inflation, immediate retirement, single taxable bucket.
    # The "endowment" withdrawal is the fixed point of B_{t+1} = (B_t - income)*(1+r_m),
    # which solves to income = B0 * r_m / (1 + r_m), independent of horizon length.
    equity_return = 0.05
    n_months = 240  # 20 years
    spine = make_spine(n_months, retire_month=0)
    b0 = 100_000.0

    income = metrics.endowment_income(
        spine, equity_return=equity_return, equity_vol=0.0, inflation=0.0,
        initial_buckets={"taxable": b0}, draw_order="t-p-r",
    )

    r_m = math.exp(math.log(1 + equity_return) / 12) - 1
    expected = b0 * r_m / (1 + r_m)
    assert math.isclose(income, expected, rel_tol=1e-4)


def test_endowment_income_zero_for_degenerate_balance_sheet():
    spine = make_spine(60, retire_month=0)
    income = metrics.endowment_income(
        spine, equity_return=0.05, equity_vol=0.0, inflation=0.0,
        initial_buckets={"taxable": 0.0}, draw_order="t-p-r",
    )
    assert math.isclose(income, 0.0, abs_tol=1e-5)


def test_compute_scenario_metrics_bundle_is_internally_consistent():
    spine = make_spine(120, retire_month=12)
    result = metrics.compute_scenario_metrics(
        "test scenario", spine, equity_return=0.06, equity_vol=0.1, inflation=0.02,
        initial_buckets={"taxable": 50_000, "pretax": 20_000, "roth": 10_000},
        draw_order="t-p-r", target_income_today=500.0, paths=200, seed=5,
    )
    assert result.name == "test scenario"
    assert 0.0 <= result.survival_pct <= 1.0
    assert result.endowment_income >= 0.0
    assert set(result.bands.keys()) == {10, 25, 50, 75, 90}
    assert math.isclose(
        sum(result.bucket_mix_real_at_horizon.values()),
        result.median_total_real_at_horizon,
        rel_tol=1e-9,
    )
    # No loans in this fixture -> no conversion/payoff data.
    assert result.conversion_balance is None
    assert result.payoff_year_a is None
    assert result.payoff_year_b is None
