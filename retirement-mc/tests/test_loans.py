import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.loans import amortize_loan_a, amortize_loan_b, amortize_payment, conversion_snapshot


def independent_payment(balance, annual_rate, term_months):
    """Reference fixed-payment formula, written independently of amortize_payment."""
    r = annual_rate / 12
    if r == 0:
        return balance / term_months
    return (balance * r * math.pow(1 + r, term_months)) / (math.pow(1 + r, term_months) - 1)


# --- Loan B: standard amortizing, no extra payments -------------------------

def test_loan_b_known_payment_300k_6pct_30yr():
    # Textbook value: $300,000 @ 6% / 30yr = $1,798.65/mo
    payment = amortize_payment(300_000, 0.06, 360)
    assert math.isclose(payment, 1798.65, abs_tol=0.01)
    assert math.isclose(payment, independent_payment(300_000, 0.06, 360), rel_tol=1e-9)


def test_loan_b_full_amortization_pays_off_at_term():
    schedule = amortize_loan_b(300_000, 0.06, 360)
    assert len(schedule) == 360
    assert schedule[-1].payoff
    assert schedule[-1].balance_end == 0.0
    total_principal = sum(m.principal for m in schedule)
    assert math.isclose(total_principal, 300_000, abs_tol=0.01)
    # Balance strictly decreasing
    balances = [m.balance_start for m in schedule]
    assert all(b1 > b2 for b1, b2 in zip(balances, balances[1:]))


def test_loan_b_extra_payments_shorten_term():
    baseline = amortize_loan_b(300_000, 0.06, 360)
    extra = [500.0] * 360
    accelerated = amortize_loan_b(300_000, 0.06, 360, extra)
    assert len(accelerated) < len(baseline)
    total_principal = sum(m.principal for m in accelerated)
    assert math.isclose(total_principal, 300_000, abs_tol=0.01)


# --- Loan A: IO -> amortizing, no prepay -------------------------------------

def test_loan_a_io_phase_is_interest_only_no_prepay():
    schedule = amortize_loan_a(300_000, 0.06, io_until_months=60, amort_months=300)
    io_months = schedule[:60]
    assert all(m.phase == "io" for m in io_months)
    # Interest-only: payment == interest, balance unchanged, no principal paid down
    for m in io_months:
        assert math.isclose(m.scheduled_payment, m.balance_start * 0.06 / 12, rel_tol=1e-9)
        assert math.isclose(m.scheduled_payment, m.interest, rel_tol=1e-9)
        assert m.balance_start == 300_000
        assert m.balance_end == 300_000


def test_loan_a_conversion_payment_matches_recast_formula():
    schedule = amortize_loan_a(300_000, 0.06, io_until_months=60, amort_months=300)
    conversion = conversion_snapshot(schedule, io_until_months=60)
    assert conversion is not None
    assert conversion.balance_start == 300_000
    expected = independent_payment(300_000, 0.06, 300)
    assert math.isclose(conversion.scheduled_payment, expected, rel_tol=1e-9)


# --- Loan A: mid-IO prepay ----------------------------------------------------

def test_loan_a_mid_io_prepay_reduces_conversion_balance():
    extra = [1_000.0] * 60  # $1k/mo extra throughout the 60-month IO phase
    schedule = amortize_loan_a(300_000, 0.06, io_until_months=60, amort_months=300, extra_payments=extra)
    conversion = conversion_snapshot(schedule, io_until_months=60)
    assert conversion is not None
    # Interest-only: every dollar of extra is pure principal reduction.
    assert math.isclose(conversion.balance_start, 300_000 - 60 * 1_000, abs_tol=0.01)


# --- Loan A: recast vs non-recast post-conversion -----------------------------

def test_loan_a_recast_false_holds_fixed_payment_after_conversion():
    extra = [0.0] * 60 + [2_000.0] * 240
    schedule = amortize_loan_a(
        300_000, 0.06, io_until_months=60, amort_months=300, extra_payments=extra, recast=False
    )
    post_conversion = [m for m in schedule if m.phase == "amortizing"]
    fixed_payment = post_conversion[0].scheduled_payment
    assert all(math.isclose(m.scheduled_payment, fixed_payment, rel_tol=1e-9) for m in post_conversion)
    # Extra payments still shorten the term vs the no-prepay case.
    no_prepay = amortize_loan_a(300_000, 0.06, io_until_months=60, amort_months=300)
    assert len(schedule) < len(no_prepay)


def test_loan_a_recast_true_payment_shrinks_as_balance_prepays():
    extra = [0.0] * 60 + [2_000.0] * 239
    schedule = amortize_loan_a(
        300_000, 0.06, io_until_months=60, amort_months=300, extra_payments=extra, recast=True
    )
    post_conversion = [m for m in schedule if m.phase == "amortizing"]
    payments = [m.scheduled_payment for m in post_conversion]
    # With recast, the derived payment should trend downward as balance shrinks faster
    # than the amortization schedule assumed.
    assert payments[-1] < payments[0]


def test_loan_a_total_principal_equals_original_balance():
    extra = [500.0] * 60 + [1_500.0] * 240
    schedule = amortize_loan_a(300_000, 0.06, io_until_months=60, amort_months=300, extra_payments=extra)
    total_principal = sum(m.principal for m in schedule)
    assert math.isclose(total_principal, 300_000, abs_tol=0.01)
