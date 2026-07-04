# Retirement Monte Carlo Tool — Build Spec
**Project:** `retirement-mc` · **Date:** 2026-07-04 · **Status:** Phase 1 (pre-tax)
**Origin:** Shape validated in Claude.ai prototype (`retirement-monte-carlo.jsx`, kept as reference for UX and engine behavior)

## 1. Purpose

Monte Carlo retirement assessment with scenario comparison. Answers: given the real
balance sheet, which allocation of surplus (prepay loan A vs loan B vs invest),
retirement year, SS claim timing, and asset decisions best supports the two goals:

1. **Endowment income** — max sustainable monthly income (today's $) where the median
   path never erodes real principal after retirement, horizon 2061.
2. **Survival probability** — % of paths that fund the income target ($20,000/mo
   today's $, adjustable) through 2061 without exhausting all buckets.

Both metrics reported per scenario; comparisons are always A-vs-B(-vs-C) deltas.

## 2. Architecture (validated in prototype)

**Two layers, strictly separated:**

- **Layer 1 — Deterministic spine.** Loan amortization, contractual income/expenses,
  lever-driven allocations, one-time events. Produces monthly cash-flow schedule.
  No randomness. Comparing spines alone already shows payment relief, payoff dates,
  and the 2031 conversion payment.
- **Layer 2 — Stochastic overlay.** Applies random draws ONLY to market returns
  (and inflation if made stochastic later). Runs N paths over the same spine.
  **Common random numbers:** identical draw sequence (fixed seed) across scenarios so
  deltas are pure lever effects.

**Internal math is nominal; all reporting deflated to today's dollars.**

## 3. Project layout

```
retirement-mc/
├── data/
│   ├── baseline.yaml        # real balance sheet (gitignored if repo goes remote)
│   ├── assumptions.yaml     # returns, vol, inflation, correlations
│   └── scenarios/
│       ├── a-invest.yaml    # lever overlays only (deltas from baseline)
│       └── b-prepay.yaml
├── engine/
│   ├── spine.py             # Layer 1
│   ├── montecarlo.py        # Layer 2 (numpy, vectorized across paths)
│   ├── metrics.py           # endowment search, survival, percentile bands
│   └── loans.py             # amortization incl. IO→amortizing + recast
├── run.py                   # CLI: run.py compare scenarios/a.yaml scenarios/b.yaml
├── output/                  # fan charts (matplotlib), summary .md → Obsidian vault
└── tests/                   # spine math verified against known amortization tables
```

Build pattern: iterative phases with explicit confirmation between each (per toolkit
conventions). Suggested order: loans.py + tests → spine.py → montecarlo.py →
metrics.py → CLI/report → real data entry.

## 4. Data schema

### baseline.yaml
```yaml
timeline:
  start: 2026-07        # simulation start
  horizon: 2061         # expected-lifetime endpoint
  step: monthly

buckets:                # three tax categories; same growth in Phase 1
  taxable: 0            # brokerage + cash equivalents
  pretax: 0             # 401k / trad IRA
  roth: 0

contributions:          # monthly, pre-retirement, off the top of surplus
  pretax: 0
  roth: 0

income:
  surplus: 0            # monthly investable surplus while working (after living
                        # expenses and minimum debt service at ORIGINAL schedule)
  rental_net: 0         # monthly net rental income, tracks inflation

liabilities:
  loan_a:               # IO → amortizing (Shellpoint-style)
    balance: 0
    rate: 0.0
    io_until: 2031      # conversion year
    amort_years: 25     # recast term at conversion
  loan_b:               # standard amortizing
    balance: 0
    rate: 0.0
    years_left: 0

social_security:        # claim ladder, both people; today's $, COLA-flat in real terms
  person1:
    - {age: 62, year: 0000, monthly: 0}
    - {age: 65, year: 0000, monthly: 0}
    - {age: 67, year: 0000, monthly: 0}
    - {age: 70, year: 0000, monthly: 0}
  person2: [same shape]
```

### assumptions.yaml
```yaml
equity_return: 0.075    # nominal annual, lognormal monthly draws
equity_vol: 0.15        # annual sigma
inflation: 0.025        # deterministic in Phase 1
paths: 10000
seed: 42
```

### Scenario overlay (levers only)
```yaml
name: "Prepay A hard, claim late"
retire_year: 2032
alloc: {prepay_a: 30, prepay_b: 40}   # % of allocatable surplus; remainder → taxable
recovery: {amount: 0, year: 2027}     # Direct Lighting event → taxable
recast_a: false                       # post-conversion payment re-derives from balance
draw_order: t-p-r                     # t-p-r | p-t-r | proportional
sell_property: {enabled: false, year: 2035, proceeds: 0}
ss_claim: {person1: 67, person2: 67}  # ladder index by age label
```

## 5. Engine rules (validated behaviors — preserve exactly)

**Loan A (IO → amortizing):**
- IO phase: minimum payment = balance × rate/12, recomputed monthly. Prepay reduces
  payment immediately. Relief vs no-prepay schedule (orig balance × rate/12) is
  freed cash → taxable.
- At conversion: recast payment from ACTUAL remaining balance over amort_years.
  Report conversion balance and payment per scenario (key decision output).
- Post-conversion, recast_a=false: fixed payment, prepay shortens term only; freed
  cash = (no-prepay conversion payment − actual recast payment), plus full scheduled
  payment once paid off.
- recast_a=true: payment re-derives monthly from balance over remaining term.

**Loan B:** standard amortization; on payoff, minimum payment freed → taxable;
extra allocation reroutes → taxable.

**Cash flows, working phase:** allocatable = surplus − pretax_contrib − roth_contrib.
Levers split allocatable. Taxable receives: invest share + freed relief + rental + SS
(if claimed pre-retirement). Contributions → respective buckets.

**Cash flows, retired phase:** need = inflated target + remaining debt service −
rental − SS. Withdraw per draw_order (sequential drain, or pro-rata for
proportional). Failure = need unmet with all buckets empty. Negative need (income
exceeds spending) → surplus back to taxable.

**Events:** recovery amount and sale proceeds → taxable at event month. Sale kills
rental income permanently from sale month.

**Returns:** lognormal monthly, mu = ln(1+r)/12 − σ_m²/2, σ_m = σ/√12. Median
deterministic path uses geometric mean (exp(mu)−1).

**Endowment metric:** binary search (~40 iterations) on income over the median
deterministic path; condition = real total at 2061 ≥ real total at retirement,
no failure.

## 6. Outputs per comparison run

- Metric table: endowment income, survival %, conversion balance/payment, payoff
  years, median 2061 total + bucket mix — per scenario, with deltas.
- Fan chart per scenario: p10/p25/p50/p75/p90 real portfolio by year, retirement
  marker. PNG via matplotlib.
- Summary .md written to Obsidian vault (path TBD at build time).

## 7. Phase 2 backlog — taxes (do not start until Phase 1 verified with real data)

- Bucket taxation: pre-tax withdrawals as ordinary income (bracket table), taxable
  as cap gains with basis tracking, Roth free. This activates the draw_order lever
  (currently identical totals by design).
- SS taxation (provisional income rules) and IRMAA awareness.
- Roth conversion ladder lever: convert $X/yr from pretax→roth in the gap years
  (retirement → SS start), filling chosen bracket.
- RMDs on pretax from age 73/75.
- Mortgage interest / rental depreciation effects if material.
- Sale proceeds: cap gains + depreciation recapture vs 1031 option.

## 8. Deferred / explicitly out of scope for Phase 1

- Rental vacancy/expense risk (decided: deterministic).
- Stochastic inflation, return regime models, fat tails (assumptions.yaml leaves room).
- SS claim-age actuarial formula (manual ladder instead — by design, from SSA
  statements).
- Hand-built stress paths (2008-in-year-one, recovery-at-floor) — add after Phase 1
  as named deterministic overlays; cheap once spine exists.
- Direct Lighting recovery as three discrete presets (wind-down ~46% / scaled
  operator ~58–74% / merge-sale) rather than free slider — nice-to-have.

## 9. Verification plan (Phase 1 acceptance)

1. loans.py output matches an independent amortization table for both loan types,
   including a mid-IO prepay case and a recast case.
2. Zero-vol run: Monte Carlo p10 = p50 = p90 = deterministic spine.
3. Prototype parity: same placeholder inputs in the .jsx and Python produce matching
   metrics within Monte Carlo noise (validates the port).
4. Real data entered; sanity-check conversion payment against the actual Shellpoint
   note terms.

## 10. Disclaimers

Decision-support tool, pre-tax model in Phase 1. Not financial advice; outputs are
conditional on chosen assumptions, and the prepay-vs-invest answer is dominated by
the equity-return and rate inputs — the tool's value is quantifying the RISK
difference between strategies, not predicting the winner.
