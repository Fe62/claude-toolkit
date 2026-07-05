"""spine.py -- Layer 1: deterministic monthly cash-flow schedule.

Combines the baseline balance sheet with a scenario's levers to produce a
month-by-month schedule of contributions, taxable inflows, loan payments,
rental income, and Social Security income. No randomness and no bucket
growth here -- that's Layer 2 (montecarlo.py). Recurring dollar figures in
baseline.yaml are "today's $" and are inflated forward to nominal terms;
loan balances/rates/payments are already nominal (contractual).

Simplifying convention: lever years (retire_year, io_until, recovery.year,
sell_property.year, and each SS ladder entry's year) are treated as landing
in January of that year, since the schema only carries year-level granularity.
"""

from dataclasses import dataclass
from typing import Optional

from engine.loans import MonthResult, amortize_loan_a, amortize_loan_b, conversion_snapshot


@dataclass
class MonthFlow:
    month: int                  # 0-indexed month since simulation start
    year: int
    cal_month: int              # calendar month, 1-12
    phase: str                   # "working" | "retired"
    pretax_contribution: float
    roth_contribution: float
    taxable_inflow: float        # net external cash landing in taxable this month
    rental_net: float
    ss_income: float             # combined SS benefit, both people, if claimed by now
    loan_a_payment: float        # total actual cash paid on loan A (0 once paid off)
    loan_b_payment: float


@dataclass
class SpineResult:
    months: list[MonthFlow]
    retire_month: int
    conversion_balance: Optional[float]
    conversion_payment: Optional[float]
    payoff_month_a: Optional[int]
    payoff_month_b: Optional[int]


def _month_index(start_year: int, start_month: int, year: int, month: int = 1) -> int:
    return (year - start_year) * 12 + (month - start_month)


def _num_months(start_year: int, start_month: int, horizon_year: int) -> int:
    return _month_index(start_year, start_month, horizon_year, 12) + 1


def _inflate(amount: float, inflation: float, month: int) -> float:
    return amount * (1 + inflation) ** (month / 12)


def _ss_lookup(ladder: list[dict], claim_age: int) -> dict:
    for entry in ladder:
        if entry["age"] == claim_age:
            return entry
    raise ValueError(f"No SS ladder entry for age {claim_age}")


def _scheduled(schedule: list[MonthResult], t: int) -> float:
    return schedule[t].scheduled_payment if t < len(schedule) else 0.0


def _actual_payment(schedule: list[MonthResult], t: int) -> float:
    if t >= len(schedule):
        return 0.0
    m = schedule[t]
    return m.scheduled_payment + m.extra


def _payoff_month(schedule: list[MonthResult], n_months: int) -> Optional[int]:
    if schedule and schedule[-1].payoff and schedule[-1].month < n_months:
        return schedule[-1].month
    return None


def build_spine(baseline: dict, assumptions: dict, scenario: dict) -> SpineResult:
    start_year, start_month = (int(x) for x in str(baseline["timeline"]["start"]).split("-"))
    horizon_year = int(baseline["timeline"]["horizon"])
    n_months = _num_months(start_year, start_month, horizon_year)
    inflation = float(assumptions["inflation"])

    retire_month = _month_index(start_year, start_month, int(scenario["retire_year"]))

    # --- Social Security: resolve claim month + today's-$ monthly benefit per person ---
    ss_events = []  # (claim_month, today_dollar_monthly)
    for person_key in ("person1", "person2"):
        claim_age = scenario["ss_claim"][person_key]
        entry = _ss_lookup(baseline["social_security"][person_key], claim_age)
        claim_month = _month_index(start_year, start_month, int(entry["year"]))
        ss_events.append((claim_month, float(entry["monthly"])))

    # --- Rental income / property sale ---
    sell = scenario.get("sell_property", {"enabled": False})
    sale_month = (
        _month_index(start_year, start_month, int(sell["year"])) if sell.get("enabled") else None
    )
    rental_today = float(baseline["income"]["rental_net"])

    # --- Loan A: IO -> amortizing ---
    loan_a = baseline["liabilities"]["loan_a"]
    io_until_month = _month_index(start_year, start_month, int(loan_a["io_until"]))
    amort_months_a = int(loan_a["amort_years"]) * 12
    balance_a = float(loan_a["balance"])
    rate_a = float(loan_a["rate"])

    # --- Loan B: standard amortizing ---
    loan_b = baseline["liabilities"]["loan_b"]
    months_remaining_b = int(loan_b["years_left"]) * 12
    balance_b = float(loan_b["balance"])
    rate_b = float(loan_b["rate"])

    # --- Working-phase allocatable surplus, constant in today's $ ---
    surplus_today = float(baseline["income"]["surplus"])
    pretax_contrib_today = float(baseline["contributions"]["pretax"])
    roth_contrib_today = float(baseline["contributions"]["roth"])
    allocatable_today = surplus_today - pretax_contrib_today - roth_contrib_today

    alloc = scenario.get("alloc", {"prepay_a": 0, "prepay_b": 0})
    prepay_a_share_today = allocatable_today * float(alloc.get("prepay_a", 0)) / 100
    prepay_b_share_today = allocatable_today * float(alloc.get("prepay_b", 0)) / 100
    invest_share_today = allocatable_today - prepay_a_share_today - prepay_b_share_today

    working_months = max(retire_month, 0)

    # Constant extra-payment streams (today's $, inflated to nominal) while working only.
    extra_a_nominal = [
        _inflate(prepay_a_share_today, inflation, t) if t < working_months else 0.0
        for t in range(n_months)
    ]
    extra_b_nominal = [
        _inflate(prepay_b_share_today, inflation, t) if t < working_months else 0.0
        for t in range(n_months)
    ]

    schedule_a = amortize_loan_a(
        balance_a, rate_a, io_until_month, amort_months_a,
        extra_payments=extra_a_nominal, recast=bool(scenario.get("recast_a", False)),
    )
    reference_a = amortize_loan_a(balance_a, rate_a, io_until_month, amort_months_a)
    schedule_b = amortize_loan_b(balance_b, rate_b, months_remaining_b, extra_payments=extra_b_nominal)
    reference_b = amortize_loan_b(balance_b, rate_b, months_remaining_b)

    conversion = conversion_snapshot(schedule_a, io_until_month)
    payoff_month_a = _payoff_month(schedule_a, n_months)
    payoff_month_b = _payoff_month(schedule_b, n_months)

    recovery = scenario.get("recovery", {"amount": 0, "year": None})
    recovery_month = (
        _month_index(start_year, start_month, int(recovery["year"])) if recovery.get("amount") else None
    )

    months: list[MonthFlow] = []
    for t in range(n_months):
        year = start_year + (start_month - 1 + t) // 12
        cal_month = (start_month - 1 + t) % 12 + 1
        phase = "working" if t < retire_month else "retired"

        sold = sale_month is not None and t >= sale_month
        rental = 0.0 if sold else _inflate(rental_today, inflation, t)

        ss_income = sum(
            _inflate(monthly, inflation, t) for claim_month, monthly in ss_events if t >= claim_month
        )

        freed_a = _scheduled(reference_a, t) - _scheduled(schedule_a, t)
        freed_b = _scheduled(reference_b, t) - _scheduled(schedule_b, t)

        pretax_contribution = 0.0
        roth_contribution = 0.0

        if phase == "working":
            pretax_contribution = _inflate(pretax_contrib_today, inflation, t)
            roth_contribution = _inflate(roth_contrib_today, inflation, t)

            redirect_a = extra_a_nominal[t] if payoff_month_a is not None and t > payoff_month_a else 0.0
            redirect_b = extra_b_nominal[t] if payoff_month_b is not None and t > payoff_month_b else 0.0

            taxable_inflow = (
                _inflate(invest_share_today, inflation, t)
                + redirect_a + redirect_b + freed_a + freed_b + rental + ss_income
            )
        else:
            # Retirement has no surplus to allocate: rental/SS offset "need" directly in
            # Layer 2 (via the rental_net/ss_income fields) rather than depositing into
            # taxable here. Loan relief is already reflected in the lower actual
            # loan_a_payment/loan_b_payment feeding that same "need" calc.
            taxable_inflow = 0.0

        if recovery_month is not None and t == recovery_month:
            taxable_inflow += float(recovery["amount"])
        if sale_month is not None and t == sale_month:
            taxable_inflow += float(sell.get("proceeds", 0))

        months.append(
            MonthFlow(
                month=t, year=year, cal_month=cal_month, phase=phase,
                pretax_contribution=pretax_contribution,
                roth_contribution=roth_contribution,
                taxable_inflow=taxable_inflow,
                rental_net=rental,
                ss_income=ss_income,
                loan_a_payment=_actual_payment(schedule_a, t),
                loan_b_payment=_actual_payment(schedule_b, t),
            )
        )

    return SpineResult(
        months=months,
        retire_month=retire_month,
        conversion_balance=conversion.balance_start if conversion else None,
        conversion_payment=conversion.scheduled_payment if conversion else None,
        payoff_month_a=payoff_month_a,
        payoff_month_b=payoff_month_b,
    )
