"""spine.py -- Layer 1: deterministic monthly cash-flow schedule.

Combines the baseline balance sheet with a scenario's levers to produce a
month-by-month schedule of contributions, taxable inflows, loan payments,
rental income, and Social Security income. No randomness and no bucket
growth here -- that's Layer 2 (montecarlo.py). Recurring dollar figures in
baseline.yaml are "today's $" and are inflated forward to nominal terms;
loan balances/rates/payments are already nominal (contractual).

Liabilities are an arbitrarily-named dict in baseline.yaml, each with a
`type` of io_amortizing, standard_amortizing, or revolving_interest_only
(see engine/loans.py). Scenario `alloc` and `recast` levers are keyed by
the same loan names.

Simplifying convention: lever years (retire_year, io_until, recovery.year,
sell_property.year, and each SS ladder entry's year) are treated as landing
in January of that year, since the schema only carries year-level granularity.
"""

from dataclasses import dataclass
from typing import Optional

from engine.loans import (
    MonthResult,
    amortize_loan_a,
    amortize_loan_b,
    amortize_revolving,
    conversion_snapshot,
)


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
    loan_payments: dict          # loan name -> actual cash paid this month (0 once paid off)

    @property
    def total_debt_service(self) -> float:
        return sum(self.loan_payments.values())


@dataclass
class SpineResult:
    months: list[MonthFlow]
    retire_month: int
    conversions: dict            # loan name -> {"balance": float, "payment": float} (io_amortizing only)
    payoff_months: dict          # loan name -> month index or None


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


def _build_loan_schedules(
    loan_cfg: dict, start_year: int, start_month: int, n_months: int,
    extra_payments: list, recast: bool,
) -> tuple[list[MonthResult], list[MonthResult], Optional[dict]]:
    """Return (actual_schedule, no-prepay reference_schedule, conversion info or None)."""
    loan_type = loan_cfg["type"]
    balance = float(loan_cfg["balance"])
    rate = float(loan_cfg["rate"])

    if loan_type == "io_amortizing":
        io_until_month = _month_index(start_year, start_month, int(loan_cfg["io_until"]))
        amort_months = int(loan_cfg["amort_years"]) * 12
        actual = amortize_loan_a(
            balance, rate, io_until_month, amort_months, extra_payments=extra_payments, recast=recast,
        )
        reference = amortize_loan_a(balance, rate, io_until_month, amort_months)
        conversion = conversion_snapshot(actual, io_until_month)
        conversion_info = (
            {"balance": conversion.balance_start, "payment": conversion.scheduled_payment}
            if conversion is not None else None
        )
        return actual, reference, conversion_info

    if loan_type == "standard_amortizing":
        months_remaining = int(loan_cfg["years_left"]) * 12
        actual = amortize_loan_b(balance, rate, months_remaining, extra_payments=extra_payments)
        reference = amortize_loan_b(balance, rate, months_remaining)
        return actual, reference, None

    if loan_type == "revolving_interest_only":
        min_pct = float(loan_cfg.get("min_payment_pct", 0.0))
        actual = amortize_revolving(
            balance, rate, n_months, extra_payments=extra_payments, min_payment_pct=min_pct,
        )
        reference = amortize_revolving(balance, rate, n_months, min_payment_pct=min_pct)
        return actual, reference, None

    raise ValueError(f"Unknown loan type: {loan_type!r}")


def build_spine(baseline: dict, assumptions: dict, scenario: dict) -> SpineResult:
    start_year, start_month = (int(x) for x in str(baseline["timeline"]["start"]).split("-"))
    horizon_year = int(baseline["timeline"]["horizon"])
    n_months = _num_months(start_year, start_month, horizon_year)
    inflation = float(assumptions["inflation"])

    retire_month = _month_index(start_year, start_month, int(scenario["retire_year"]))
    working_months = max(retire_month, 0)

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

    # --- Working-phase allocatable surplus, constant in today's $ ---
    surplus_today = float(baseline["income"]["surplus"])
    pretax_contrib_today = float(baseline["contributions"]["pretax"])
    roth_contrib_today = float(baseline["contributions"]["roth"])
    allocatable_today = surplus_today - pretax_contrib_today - roth_contrib_today

    alloc = scenario.get("alloc", {})
    recast_flags = scenario.get("recast", {})

    loan_names = list(baseline.get("liabilities", {}).keys())
    loan_share_today = {
        name: allocatable_today * float(alloc.get(name, 0)) / 100 for name in loan_names
    }
    invest_share_today = allocatable_today - sum(loan_share_today.values())

    # Constant extra-payment streams (today's $, inflated to nominal) while working only.
    extra_nominal = {
        name: [
            _inflate(loan_share_today[name], inflation, t) if t < working_months else 0.0
            for t in range(n_months)
        ]
        for name in loan_names
    }

    actual_schedules: dict[str, list[MonthResult]] = {}
    reference_schedules: dict[str, list[MonthResult]] = {}
    conversions: dict[str, dict] = {}
    payoff_months: dict[str, Optional[int]] = {}
    for name in loan_names:
        loan_cfg = baseline["liabilities"][name]
        actual, reference, conversion_info = _build_loan_schedules(
            loan_cfg, start_year, start_month, n_months,
            extra_nominal[name], bool(recast_flags.get(name, False)),
        )
        actual_schedules[name] = actual
        reference_schedules[name] = reference
        if conversion_info is not None:
            conversions[name] = conversion_info
        payoff_months[name] = _payoff_month(actual, n_months)

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

        loan_payments = {name: _actual_payment(actual_schedules[name], t) for name in loan_names}

        pretax_contribution = 0.0
        roth_contribution = 0.0

        if phase == "working":
            pretax_contribution = _inflate(pretax_contrib_today, inflation, t)
            roth_contribution = _inflate(roth_contrib_today, inflation, t)

            freed_total = sum(
                _scheduled(reference_schedules[name], t) - _scheduled(actual_schedules[name], t)
                for name in loan_names
            )
            redirect_total = sum(
                extra_nominal[name][t]
                for name in loan_names
                if payoff_months[name] is not None and t > payoff_months[name]
            )

            taxable_inflow = (
                _inflate(invest_share_today, inflation, t)
                + redirect_total + freed_total + rental + ss_income
            )
        else:
            # Retirement has no surplus to allocate: rental/SS offset "need" directly in
            # Layer 2 (via the rental_net/ss_income fields) rather than depositing into
            # taxable here. Loan relief is already reflected in the lower actual
            # loan_payments feeding that same "need" calc.
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
                loan_payments=loan_payments,
            )
        )

    return SpineResult(
        months=months,
        retire_month=retire_month,
        conversions=conversions,
        payoff_months=payoff_months,
    )
