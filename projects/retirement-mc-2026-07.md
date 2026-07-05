# Retirement Monte Carlo Tool

**Document status:** Active
**Date started:** 2026-07-04
**Date completed:**
**Owner:** Flint

---

## One-Line Goal

Build a Python Monte Carlo retirement engine that compares lever-driven scenarios (prepay vs. invest, retirement year, SS claim timing) on endowment income and survival probability, porting the validated logic from the `retirement-monte-carlo.jsx` Claude.ai prototype.

---

## Background & Context

Shape and engine behavior were already validated in a Claude.ai prototype (`retirement-monte-carlo.jsx`), kept as UX/behavior reference. This project ports that to a local, owned Python tool so it runs against the real balance sheet without depending on a hosted artifact. Full build spec: `53cd8493-retirementmcspec.md` (uploaded by Flint 2026-07-04), reproduced in the Plan/Constraints sections below.

---

## Success Criteria

- [ ] `loans.py` matches an independent amortization table for both loan types (incl. mid-IO prepay + recast cases)
- [x] Zero-vol Monte Carlo run collapses to the deterministic spine (p10 = p50 = p90)
- [ ] Python port matches prototype `.jsx` metrics within Monte Carlo noise on placeholder inputs
- [x] Real data entered; loan_a conversion payment ($7,447/mo @ 3.60% over 30yr on $1,638,000) sanity-checked against the amortization formula 2026-07-05 (still worth confirming against the actual Shellpoint note once available)
- [x] `run.py compare` produces metric table + fan charts + Obsidian summary for at least 2 scenarios (Obsidian vault path still TBD -- writes to `--outdir`, default `output/`)

---

## Scope

**In scope (Phase 1 — pre-tax):**
- Deterministic spine: loan amortization (named loans: io_amortizing, standard_amortizing, revolving_interest_only), contractual income/expenses, lever-driven allocations, one-time events
- Stochastic overlay: lognormal monthly returns per return-type (equity, real_estate), common random numbers across scenarios, fixed seed
- Endowment income metric (binary search on median deterministic path) + survival probability metric — liquid buckets only (taxable/pretax/roth)
- CLI scenario comparison with fan charts + markdown summary
- 5 named liabilities (home mortgage, rental mortgage, Schwab margin loan, RJ SBL, credit card) and a 4th real_estate/private-investment bucket with its own return assumption (2026-07-05 addendum — see SPEC.md section 11)

**Out of scope (Phase 1):**
- All taxation (bracket tables, cap gains/basis, Roth conversion ladder, RMDs, IRMAA) — Phase 2 backlog
- Rental vacancy/expense risk, stochastic inflation, regime models, fat tails
- SS claim-age actuarial formula (manual ladder from SSA statements instead, by design)
- Hand-built stress paths, three-preset Direct Lighting recovery slider

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| numpy, matplotlib, pyyaml | Installed (this session) | Need to persist via requirements.txt |
| Real balance sheet data | Not yet entered | baseline.yaml stays placeholder/zeroed until real data step |
| retirement-monte-carlo.jsx prototype | Reference only | Used for parity check in verification plan |

---

## Constraints

- Internal math nominal; all reporting deflated to today's dollars
- Two layers strictly separated: deterministic spine (Layer 1) never touches randomness; stochastic overlay (Layer 2) applies draws only to market returns
- Common random numbers (fixed seed) across scenarios so comparisons isolate lever effects
- `data/baseline.yaml` gitignored once real numbers are entered (financial data)
- Build pattern: iterative phases with explicit confirmation between each phase before moving on

---

## Plan

- [x] Phase 0 — scaffold `retirement-mc/` project layout + placeholder data files
- [x] Phase 1 — `loans.py` + tests (IO→amortizing, standard amortizing, recast)
- [x] Phase 2 — `spine.py` (deterministic cash-flow schedule)
- [x] Phase 3 — `montecarlo.py` (vectorized stochastic overlay)
- [x] Phase 4 — `metrics.py` (endowment search, survival, percentile bands)
- [x] Phase 5 — `run.py` CLI + report/fan-chart output
- [x] Phase 5.5 — generalize loans (named, 3 mechanics) + assets (real_estate bucket, own return assumption) ahead of real data entry
- [x] Phase 6 — real data entered (all 5 loans, all 4 buckets, surplus, rental_net); first real `run.py compare` produced sensible output 2026-07-05
- [ ] Update load-context.sh (Active Skills + Recent Completions)
- [ ] Commit load-context.sh with final project commit

---

## Open Questions

- [ ] Exact Obsidian vault path for summary .md output (deferred to build time per spec)
- [x] SS ladder (both people, ages 62/65/67/70) — entered from SSA statements 2026-07-05
- [x] Real loan balances/rates (all 5), bucket values (all 4), surplus ($300/mo), rental_net ($8,100/mo combined) — entered 2026-07-05
- [x] Loan E minimum payment % (2%) — confirmed 2026-07-05
- [x] Monthly pretax/roth contribution amounts (pretax $19.80, roth $132) — entered 2026-07-05
- [x] Real estate taxable/pretax split — staying summed into one bucket, confirmed 2026-07-05 (revisit only if Phase 2 tax modeling needs it split)
- [x] Loan list confirmed (A home mortgage, B rental mortgage, C Schwab margin, D RJ SBL, E credit card) and asset structure (taxable/pretax/roth + real_estate) — 2026-07-05

---

## Outcomes & Lessons

_Filled in on completion._

---

## Bible Entry

_Filled in on completion._
