import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.spine import build_spine


def base_inputs():
    baseline = {
        "timeline": {"start": "2026-01", "horizon": 2027, "step": "monthly"},
        "buckets": {"taxable": 0, "pretax": 0, "roth": 0},
        "contributions": {"pretax": 500.0, "roth": 200.0},
        "income": {"surplus": 3000.0, "rental_net": 1000.0},
        "liabilities": {
            "loan_a": {"balance": 0.0, "rate": 0.0, "io_until": 2026, "amort_years": 25},
            "loan_b": {"balance": 0.0, "rate": 0.0, "years_left": 0},
        },
        "social_security": {
            "person1": [{"age": 67, "year": 2030, "monthly": 2000.0}],
            "person2": [{"age": 67, "year": 2030, "monthly": 1500.0}],
        },
    }
    assumptions = {"equity_return": 0.075, "equity_vol": 0.15, "inflation": 0.0, "paths": 100, "seed": 1}
    scenario = {
        "name": "test",
        "retire_year": 2029,
        "alloc": {"prepay_a": 0, "prepay_b": 0},
        "recovery": {"amount": 0, "year": None},
        "recast_a": False,
        "draw_order": "t-p-r",
        "sell_property": {"enabled": False, "year": 2030, "proceeds": 0},
        "ss_claim": {"person1": 67, "person2": 67},
    }
    return baseline, assumptions, scenario


def test_timeline_length_and_phase_boundary():
    baseline, assumptions, scenario = base_inputs()
    scenario["retire_year"] = 2027  # month index 12 (Jan 2027) given start 2026-01
    result = build_spine(baseline, assumptions, scenario)
    # start 2026-01, horizon 2027 -> Jan2026..Dec2027 == 24 months
    assert len(result.months) == 24
    assert result.retire_month == 12
    assert all(m.phase == "working" for m in result.months[:12])
    assert all(m.phase == "retired" for m in result.months[12:])


def test_no_inflation_contributions_flat_and_taxable_matches_invest_share():
    baseline, assumptions, scenario = base_inputs()
    scenario["retire_year"] = 2030  # stays working the whole horizon
    result = build_spine(baseline, assumptions, scenario)
    m0 = result.months[0]
    assert math.isclose(m0.pretax_contribution, 500.0)
    assert math.isclose(m0.roth_contribution, 200.0)
    # allocatable = 3000 - 500 - 200 = 2300; no prepay levers -> all goes to invest share
    # taxable_inflow = invest_share + rental (SS not yet claimed)
    assert math.isclose(m0.taxable_inflow, 2300.0 + 1000.0, abs_tol=0.01)


def test_ss_income_turns_on_at_claim_month():
    baseline, assumptions, scenario = base_inputs()
    baseline["timeline"]["horizon"] = 2031  # extend past the 2030 SS claim year
    scenario["retire_year"] = 2032
    result = build_spine(baseline, assumptions, scenario)
    claim_month = 48  # Jan 2030, start Jan 2026 -> (2030-2026)*12 = 48
    before = result.months[claim_month - 1]
    at = result.months[claim_month]
    assert before.ss_income == 0.0
    assert math.isclose(at.ss_income, 3500.0, abs_tol=0.01)  # 2000 + 1500, zero inflation


def test_inflation_scales_recurring_amounts():
    baseline, assumptions, scenario = base_inputs()
    assumptions["inflation"] = 0.024  # 2%/yr in monthly-compounded terms roughly
    scenario["retire_year"] = 2030
    result = build_spine(baseline, assumptions, scenario)
    m12 = result.months[12]  # exactly one year in
    expected_rental = 1000.0 * (1.024) ** 1.0
    assert math.isclose(m12.rental_net, expected_rental, rel_tol=1e-9)


def test_sale_stops_rental_and_deposits_proceeds():
    baseline, assumptions, scenario = base_inputs()
    scenario["retire_year"] = 2032
    scenario["sell_property"] = {"enabled": True, "year": 2027, "proceeds": 50_000.0}
    result = build_spine(baseline, assumptions, scenario)
    sale_month = 12  # Jan 2027
    before = result.months[sale_month - 1]
    at = result.months[sale_month]
    after = result.months[sale_month + 1]
    assert before.rental_net > 0
    assert at.rental_net == 0.0
    assert after.rental_net == 0.0
    assert at.taxable_inflow >= 50_000.0


def test_recovery_event_lands_in_taxable_at_event_month():
    baseline, assumptions, scenario = base_inputs()
    scenario["retire_year"] = 2032
    scenario["recovery"] = {"amount": 25_000.0, "year": 2026}
    result = build_spine(baseline, assumptions, scenario)
    event_month = 0  # Jan 2026 == start
    other_month = 1
    assert result.months[event_month].taxable_inflow >= 25_000.0
    assert result.months[other_month].taxable_inflow < 25_000.0


def test_loan_a_conversion_reported_and_prepay_reduces_conversion_payment():
    baseline, assumptions, scenario = base_inputs()
    baseline["timeline"]["horizon"] = 2032
    baseline["liabilities"]["loan_a"] = {
        "balance": 300_000.0, "rate": 0.06, "io_until": 2027, "amort_years": 25,
    }
    scenario["retire_year"] = 2035  # stay working throughout
    scenario["alloc"] = {"prepay_a": 100, "prepay_b": 0}

    no_prepay_scenario = dict(scenario)
    no_prepay_scenario["alloc"] = {"prepay_a": 0, "prepay_b": 0}

    with_prepay = build_spine(baseline, assumptions, scenario)
    without_prepay = build_spine(baseline, assumptions, no_prepay_scenario)

    assert with_prepay.conversion_balance is not None
    assert with_prepay.conversion_balance < without_prepay.conversion_balance
    assert with_prepay.conversion_payment < without_prepay.conversion_payment

    # Dumping 100% of allocatable surplus into prepay diverts it away from taxable
    # investing during IO, so taxable_inflow is lower than the no-prepay case...
    assert with_prepay.months[11].taxable_inflow < without_prepay.months[11].taxable_inflow
    # ...but the interest-only payment itself is smaller because the balance is lower.
    extra_at_11 = 2300.0  # full allocatable, zero inflation, no roth/pretax siphon in this fixture
    with_prepay_scheduled = with_prepay.months[11].loan_a_payment - extra_at_11
    assert with_prepay_scheduled < without_prepay.months[11].loan_a_payment


def test_loan_b_payoff_redirects_allocation_to_taxable():
    baseline, assumptions, scenario = base_inputs()
    baseline["timeline"]["horizon"] = 2032
    baseline["liabilities"]["loan_b"] = {"balance": 10_000.0, "rate": 0.06, "years_left": 5}
    scenario["retire_year"] = 2035
    scenario["alloc"] = {"prepay_a": 0, "prepay_b": 100}  # dump all allocatable into loan B
    result = build_spine(baseline, assumptions, scenario)

    assert result.payoff_month_b is not None
    payoff = result.payoff_month_b
    before = result.months[payoff - 1]
    after = result.months[payoff + 1]
    # Once paid off, the loan payment drops to zero and the freed allocation
    # (minimum + redirected extra) shows up in taxable_inflow.
    assert result.months[payoff].loan_b_payment > 0
    assert after.loan_b_payment == 0.0
    assert after.taxable_inflow > before.taxable_inflow
