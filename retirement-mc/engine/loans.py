"""Loan amortization for the retirement-mc spine (Layer 1).

Three loan mechanics, matching the balance sheet:
- io_amortizing: interest-only until conversion, then amortizing (Shellpoint-style
  home mortgage). See amortize_loan_a.
- standard_amortizing: standard amortizing from the start (rental mortgage).
  See amortize_loan_b.
- revolving_interest_only: no fixed term; minimum payment each month is interest
  (margin loan, securities-based line) or interest-plus-a-minimum-principal-nibble
  (credit card style). See amortize_revolving.

All support a monthly extra-payment (prepay) stream. No randomness here —
this module is pure loan mechanics; cash routing (freed payments -> taxable)
is a spine.py concern.
"""

from dataclasses import dataclass
from typing import Sequence


@dataclass
class MonthResult:
    month: int                # 0-indexed month since loan start
    phase: str                 # "io" or "amortizing" (loan A only; loan B always "amortizing")
    balance_start: float
    scheduled_payment: float   # interest (IO) or amortizing payment for the month, excl. extra
    extra: float                # extra/prepay principal applied this month
    interest: float
    principal: float           # total principal paid (scheduled + extra), capped at balance
    balance_end: float
    payoff: bool                # True on the month the loan reaches zero balance


def amortize_payment(balance: float, annual_rate: float, term_months: int) -> float:
    """Standard fixed monthly payment to fully amortize `balance` over `term_months`."""
    if term_months <= 0:
        return balance
    r = annual_rate / 12
    if r == 0:
        return balance / term_months
    return balance * r / (1 - (1 + r) ** -term_months)


def amortize_loan_b(
    balance: float,
    annual_rate: float,
    months_remaining: int,
    extra_payments: Sequence[float] = (),
) -> list[MonthResult]:
    """Standard amortizing loan (Loan B).

    The fixed payment is computed once from the original balance/rate/term.
    Extra payments accelerate payoff; the loan simply stops once balance hits zero.
    """
    r = annual_rate / 12
    payment = amortize_payment(balance, annual_rate, months_remaining)
    results: list[MonthResult] = []

    month = 0
    while balance > 1e-9:
        interest = balance * r
        extra = extra_payments[month] if month < len(extra_payments) else 0.0
        scheduled_principal = payment - interest
        principal = min(balance, scheduled_principal + extra)
        balance_end = balance - principal
        payoff = balance_end <= 1e-9
        results.append(
            MonthResult(
                month=month,
                phase="amortizing",
                balance_start=balance,
                scheduled_payment=payment,
                extra=extra,
                interest=interest,
                principal=principal,
                balance_end=max(balance_end, 0.0),
                payoff=payoff,
            )
        )
        balance = max(balance_end, 0.0)
        month += 1

    return results


def amortize_loan_a(
    balance: float,
    annual_rate: float,
    io_until_months: int,
    amort_months: int,
    extra_payments: Sequence[float] = (),
    recast: bool = False,
) -> list[MonthResult]:
    """IO -> amortizing loan (Loan A), with optional recast at conversion.

    IO phase (month < io_until_months): scheduled payment = balance * rate/12,
    recomputed every month off the current (possibly prepaid-down) balance.
    Extra payments are pure prepay principal during this phase.

    At month == io_until_months, the payment is recast from the ACTUAL remaining
    balance over `amort_months`.

    Post-conversion:
      - recast=False: payment fixed at the conversion-month value; extra payments
        only shorten the remaining term.
      - recast=True: payment is re-derived every month from the current balance
        over the remaining term (amort_months - months since conversion).
    """
    r = annual_rate / 12
    results: list[MonthResult] = []

    month = 0
    fixed_payment: float | None = None  # set at conversion when recast=False

    while balance > 1e-9:
        interest = balance * r
        extra = extra_payments[month] if month < len(extra_payments) else 0.0

        if month < io_until_months:
            phase = "io"
            scheduled_payment = interest
            scheduled_principal = 0.0
        else:
            phase = "amortizing"
            months_since_conversion = month - io_until_months
            if recast:
                remaining_term = max(amort_months - months_since_conversion, 1)
                scheduled_payment = amortize_payment(balance, annual_rate, remaining_term)
            else:
                if fixed_payment is None:
                    # Conversion month: recast from actual balance, then hold fixed.
                    fixed_payment = amortize_payment(balance, annual_rate, amort_months)
                scheduled_payment = fixed_payment
            scheduled_principal = scheduled_payment - interest

        principal = min(balance, scheduled_principal + extra)
        balance_end = balance - principal
        payoff = balance_end <= 1e-9

        results.append(
            MonthResult(
                month=month,
                phase=phase,
                balance_start=balance,
                scheduled_payment=scheduled_payment,
                extra=extra,
                interest=interest,
                principal=principal,
                balance_end=max(balance_end, 0.0),
                payoff=payoff,
            )
        )

        balance = max(balance_end, 0.0)
        month += 1

    return results


def amortize_revolving(
    balance: float,
    annual_rate: float,
    n_months: int,
    extra_payments: Sequence[float] = (),
    min_payment_pct: float = 0.0,
) -> list[MonthResult]:
    """Revolving interest-only debt (margin loan, securities-based line, credit card).

    No fixed amortization term, so the loop is bounded by `n_months` rather than
    running to payoff. Minimum payment each month is max(interest, balance *
    min_payment_pct): margin loans/SBLs use min_payment_pct=0 (pure interest-only,
    balance never self-amortizes without extra payments); credit-card-style lines
    set min_payment_pct>0 for a minimum principal nibble even without extra.
    """
    r = annual_rate / 12
    results: list[MonthResult] = []

    month = 0
    while month < n_months and balance > 1e-9:
        interest = balance * r
        minimum_payment = max(interest, balance * min_payment_pct)
        scheduled_principal = minimum_payment - interest
        extra = extra_payments[month] if month < len(extra_payments) else 0.0
        principal = min(balance, scheduled_principal + extra)
        balance_end = balance - principal
        payoff = balance_end <= 1e-9

        results.append(
            MonthResult(
                month=month,
                phase="revolving",
                balance_start=balance,
                scheduled_payment=minimum_payment,
                extra=extra,
                interest=interest,
                principal=principal,
                balance_end=max(balance_end, 0.0),
                payoff=payoff,
            )
        )

        balance = max(balance_end, 0.0)
        month += 1

    return results


def conversion_snapshot(schedule: list[MonthResult], io_until_months: int) -> MonthResult | None:
    """Return the first amortizing-phase MonthResult (the conversion month), if present."""
    for result in schedule:
        if result.month == io_until_months and result.phase == "amortizing":
            return result
    return None
