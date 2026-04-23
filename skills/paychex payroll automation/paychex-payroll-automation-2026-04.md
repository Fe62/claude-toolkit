# PRD: Paychex Payroll Automation
**One-Line Goal:** Automate weekly Paychex report download and QuickBooks Desktop IIF import for Direct Lighting LLC.

---

## Success Criteria
- [ ] Paychex Flex portal login and zip download fully automated via Playwright
- [ ] Zip extracted to correct `Payroll.MMDD` folder under correct QX path on DirectNAS
- [ ] IIF generated with 3 Write Checks, correct account mapping, correct dates
- [ ] HSA lines (Juan Magadan, Ricardo Quezada) appear only on first payroll of the month
- [ ] Invoice amount parsed from PDF inside the zip
- [ ] launchd plist runs automatically on payroll day
- [ ] Errors surface visibly (log file minimum; Discord webhook optional)

---

## Constraints
- Runs on Direct Lighting iMac (upgrades to M4 — skill syncs via iCloud automatically)
- QuickBooks Desktop only — IIF format, no API
- DirectNAS must be mounted at `/Volumes/Public` at execution time
- Paychex credentials stored in macOS Keychain — never hardcoded
- Invoice amount comes from a separate PDF inside the Paychex zip
- No native QB Desktop export from Paychex — full custom parse required

---

## Dependencies
- Python 3.x (already on Direct iMac)
- Playwright + Chromium (headless)
- pdfplumber (PDF parsing — Payroll Journal, Cash Requirements, Invoice)
- launchd (macOS scheduler — runs Tuesday, payroll pulls from checking Tuesday)
- DirectNAS mounted at `/Volumes/Public`
- QB Desktop (IIF import automated via AppleScript)
- Discord webhook (existing Fe Trading infrastructure — errors + import confirmation)

---

## Machine Inventory
| Role | Machine | Access |
|---|---|---|
| Development | femacbook | Claude Code, iCloud sync |
| Execution | Direct Lighting iMac | launchd, QB Desktop, DirectNAS |
| Sync path | iCloud (claude-toolkit) | Auto on both machines |

Skill path: `~/Library/Mobile Documents/com~apple~CloudDocs/claude-toolkit/skills/paychex-payroll-automation/`
```
paychex-payroll-automation/
  paychex-download/
    SKILL.md
    paychex_download.py
  paychex-to-iif/
    SKILL.md
    paychex_to_iif.py
    import_iif.applescript
  401k/              ← separate skill, TBD
    SKILL.md
```

---

## Source Reports → QB Account Mapping

### Check 1 — Paychex Invoice (date: day before payroll)
| QB Account | Source |
|---|---|
| 66700:66730 — Payroll Prep Fees | Invoice PDF in zip, total amount |

Bank: `10100 - US Bank Checking` · Payee: `Paychex` · Type: Write Check

---

### Check 2 — Direct Deposit (date: day before payroll)
| QB Account | Source |
|---|---|
| 65600:65620:65621 — Employee Wages | Payroll Journal, Section 300 Staff totals, Net Pay |
| 65600:65610:65611 — Officers Salaries | Payroll Journal, Section 100 Officers totals, Net Pay |
| 63360:63301 — Juan Magadan HRA | Payroll Journal, Section 300, Juan Magadan, HRA Reimbursement *(first payroll of month only)* |
| 63360:63302 — Ricardo Quezada HRA | Payroll Journal, Section 300, Ricky Quezada, HRA Reimbursement *(first payroll of month only)* |

Bank: `10100 - US Bank Checking` · Payee: `Paychex` · Type: Write Check

---

### Check 3 — Tax Check (date: payroll date)
**From Cash Requirements — Employer Liabilities:**
| QB Account | Source |
|---|---|
| 65700:65710 — FICA | Cash Req, Employer Liabilities, Social Security |
| 65700:65720 — Medicare | Cash Req, Employer Liabilities, Medicare |
| 65700:65730 — FUTA | Cash Req, Employer Liabilities, FUTA |
| 65700:65740 — CA ETT | Cash Req, Employer Liabilities, CA ETT |
| 65700:65750 — CA State Unemployment | Cash Req, Employer Liabilities, CA Unemployment |

**From Payroll Journal — Section 100 Officers Totals:**
| QB Account | Source |
|---|---|
| 65600:65610:65613 — Fed-WH Taxes | Officers totals, Fed Income Tax |
| 65600:65610:65616 — CASDI-WH Taxes | Officers totals, CA Disability |
| 65600:65610:65614 — FICA-WH Taxes | Officers totals, Social Security |
| 65600:65610:65615 — Medicare-WH Taxes | Officers totals, Medicare |

**From Payroll Journal — Section 300 Staff Totals:**
| QB Account | Source |
|---|---|
| 65600:65620:65623 — Fed-WH Taxes | Staff totals, Fed Income Tax |
| 65600:65620:65626 — CASDI-WH Taxes | Staff totals, CA Disability |
| 65600:65620:65627 — CA State-WH Taxes | Staff totals, CA Income Tax |
| 65600:65620:65624 — FICA-WH Taxes | Staff totals, Social Security |
| 65600:65620:65625 — Medicare-WH Taxes | Staff totals, Medicare |

Bank: `10100 - US Bank Checking` · Payee: `Paychex` · Type: Write Check

---

## Folder Structure
```
/Volumes/Public/Direct Lighting/Direct Lighting LLC/1.Direct.Payroll/1.Payrolls/26.Payrolls/
  Q1/
    Payroll.MMDD/
      [extracted zip contents]
  Q2/
  Q3/
  Q4/
```
QX determined by payroll month: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec

---

## Plan

### Phase 1 — paychex-download skill
- [ ] Map Paychex Flex portal login and report download nav flow
- [ ] Build Playwright script: login → download zip
- [ ] Implement QX folder logic and `Payroll.MMDD` naming
- [ ] Extract zip, preserve all files
- [ ] Test with live payroll run

### Phase 2 — paychex-to-iif skill
- [ ] Parse Invoice PDF → extract total amount
- [ ] Parse Payroll Journal PDF → sections 100 and 300 totals
- [ ] Parse Cash Requirements PDF → employer liabilities section
- [ ] Implement HSA detection (check HRA > 0 for Juan/Ricky)
- [ ] Build IIF generator: 3 Write Checks, correct dates, memo = payroll date
- [ ] Validate output against a known-good manual payroll entry
- [ ] Test import into QB Desktop

### Phase 3 — Scheduling & Ops
- [ ] launchd plist — every Tuesday (payroll pulls from checking Tuesday, lands Wednesday)
- [ ] Mount check: abort with clear error if DirectNAS not mounted
- [ ] Log file per run in `Payroll.MMDD` folder
- [ ] AppleScript: open QB Desktop, import IIF, close
- [ ] Discord webhook: error alert on any failure
- [ ] Discord webhook: success alert after IIF import confirming check totals

### Phase 4 — 401k Skill (separate)
- [ ] Spec TBD — lives in `paychex-payroll-automation/401k/`

---

## Open Questions
- [ ] Paychex Flex portal: confirm report names match expected: "Payroll Journal", "Cash Requirements", "Direct Deposit", "Retirement Plan Summary"
