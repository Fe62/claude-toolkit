---
name: paychex-to-iif
description: Parse Paychex Payroll Journal, Cash Requirements, and Invoice PDFs from a Payroll.MMDD folder and generate a QuickBooks Desktop IIF file with 3 Write Checks. Use after paychex-download has run.
---

# paychex-to-iif Skill

Parses Paychex payroll PDFs and generates a QuickBooks Desktop `.iif` file containing 3 Write Checks ready for import. Run after `paychex-download` has populated the `Payroll.MMDD` folder.

---

## Prerequisites

```bash
pip install pdfplumber
```

---

## Input Files (in `Payroll.MMDD` folder)
| File | Used For |
|---|---|
| `*Payroll_Journal*` or similar | Direct Deposit check + Tax check (employee WH lines) |
| `*Cash_Requirements*` or similar | Tax check (employer liability lines) |
| `*Invoice*` or `*Statement*` PDF | Invoice check amount |

File naming from Paychex zip TBD — update `REPORT_PATTERNS` dict after first download.

---

## QB Account Reference

### Check 1 — Invoice (payroll date − 1 day)
```
DEBIT:  66700:66730 — Payroll Prep Fees     ← Invoice PDF total
CREDIT: 10100 - US Bank Checking
```

### Check 2 — Direct Deposit (payroll date − 1 day)
```
DEBIT:  65600:65620:65621 — Employee Wages  ← PJ Sec 300, Net Pay
DEBIT:  65600:65610:65611 — Officers Salaries ← PJ Sec 100, Net Pay
DEBIT:  63360:63301 — Juan Magadan HRA      ← PJ Sec 300, Juan Magadan, HRA (first payroll of month only)
DEBIT:  63360:63302 — Ricardo Quezada HRA   ← PJ Sec 300, Ricky Quezada, HRA (first payroll of month only)
CREDIT: 10100 - US Bank Checking
```

### Check 3 — Tax Check (payroll date)
```
From Cash Requirements — Employer Liabilities:
DEBIT:  65700:65710 — FICA                  ← Social Security
DEBIT:  65700:65720 — Medicare              ← Medicare
DEBIT:  65700:65730 — FUTA                  ← FUTA
DEBIT:  65700:65740 — CA ETT               ← CA ETT
DEBIT:  65700:65750 — CA State Unemployment ← CA Unemployment

From Payroll Journal — Section 100 Officers:
DEBIT:  65600:65610:65613 — Fed-WH Taxes    ← Fed Income Tax
DEBIT:  65600:65610:65616 — CASDI-WH Taxes  ← CA Disability
DEBIT:  65600:65610:65614 — FICA-WH Taxes   ← Social Security
DEBIT:  65600:65610:65615 — Medicare-WH Taxes ← Medicare

From Payroll Journal — Section 300 Staff:
DEBIT:  65600:65620:65623 — Fed-WH Taxes    ← Fed Income Tax
DEBIT:  65600:65620:65626 — CASDI-WH Taxes  ← CA Disability
DEBIT:  65600:65620:65627 — CA State-WH Taxes ← CA Income Tax
DEBIT:  65600:65620:65624 — FICA-WH Taxes   ← Social Security
DEBIT:  65600:65620:65625 — Medicare-WH Taxes ← Medicare

CREDIT: 10100 - US Bank Checking
```

---

## IIF Format Notes

QB Desktop Write Check IIF structure:
```
!TRNS	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	MEMO	CLEAR	TOPRINT
!SPL	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	MEMO	CLEAR
!ENDTRNS
TRNS	CHECK	MM/DD/YYYY	10100 - US Bank Checking	Paychex	-TOTAL	MEMO	N	N
SPL	CHECK	MM/DD/YYYY	EXPENSE_ACCOUNT	Paychex	LINE_AMOUNT	MEMO	N
...more SPL lines...
ENDTRNS
```

- TRNS `AMOUNT` = negative (money leaving checking)
- SPL `AMOUNT` = positive (expense debits)
- `MEMO` = payroll date formatted as `MM/DD/YYYY` on all lines
- Account names must match QB Desktop **exactly** — including colons, em-dashes, and spacing
- Date format: `MM/DD/YYYY`

---

## Script: `paychex_to_iif.py`

```python
#!/usr/bin/env python3
"""
paychex-to-iif: Parse Paychex PDFs and generate QuickBooks Desktop IIF.
Usage: python3 paychex_to_iif.py /path/to/Payroll.MMDD YYYY-MM-DD

PDF structure confirmed against 04/08/2026 payroll.
"""

import pdfplumber, os, re, sys
from datetime import date, timedelta, datetime
from pathlib import Path

REPORT_PATTERNS = {
    'payroll_journal':    'Payroll_Journal',
    'cash_requirements':  'Cash_Requirements',
    'invoice':            'Invoice',
}

QB_ACCOUNTS = {
    # Invoice
    'payroll_prep_fees': 'Legal & Professional Fees:Payroll Prep Fees',
    # Direct Deposit
    'employee_wages':    'Payroll Expenses:Employee Payroll Expenses:Employee Wages',
    'officers_salaries': 'Payroll Expenses:Officers Salaries:Officers Salaries',
    'hsa_juan':          'Health Insurance Reim:Juan Magadan',
    'hsa_ricky':         'Health Insurance Reim:Ricardo Quezada',
    # Tax — employer liabilities
    'fica_er':           'Payroll Tax Expense:FICA',
    'medicare_er':       'Payroll Tax Expense:Medicare',
    'futa':              'Payroll Tax Expense:FUTA',
    'ca_ett':            'Payroll Tax Expense:CA ETT',
    'ca_sui':            'Payroll Tax Expense:CA State Unemployment',
    # Tax — officers WH
    'off_fed_wh':        'Payroll Expenses:Officers Salaries:Fed-WH Taxes',
    'off_casdi':         'Payroll Expenses:Officers Salaries:CASDI-WH Taxes',
    'off_fica':          'Payroll Expenses:Officers Salaries:FICA-WH Taxes',
    'off_medicare':      'Payroll Expenses:Officers Salaries:Medicare -WH Taxes',
    # Tax — staff WH
    'ee_fed_wh':         'Payroll Expenses:Employee Payroll Expenses:Fed - WH Taxes',
    'ee_casdi':          'Payroll Expenses:Employee Payroll Expenses:CASDI-WH Taxes',
    'ee_ca_state':       'Payroll Expenses:Employee Payroll Expenses:CA State - WH Taxes',
    'ee_fica':           'Payroll Expenses:Employee Payroll Expenses:FICA- WH Taxes',
    'ee_medicare':       'Payroll Expenses:Employee Payroll Expenses:Medicare - WH Taxes',
    # Bank
    'checking':          'US Bank Checking',
}

PAYEE = 'Paychex'


def find_report(folder, pattern_key):
    pattern = REPORT_PATTERNS[pattern_key]
    for f in Path(folder).glob('*.pdf'):
        if pattern.lower() in f.name.lower():
            return str(f)
    raise FileNotFoundError(f"Could not find {pattern_key} PDF in {folder}")


def fmt_date(d):
    return d.strftime('%m/%d/%Y')


def get_amount(pattern, text, default=0.0):
    m = re.search(pattern, text)
    return float(m.group(1).replace(',', '')) if m else default


def parse_invoice(folder):
    """Returns: {'total': float}
    Looks for TotalNewCharges line. Paychex compresses spaces in PDF text,
    so we strip spaces before matching.
    """
    path = find_report(folder, 'invoice')
    with pdfplumber.open(path) as pdf:
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
    compact = text.replace(' ', '').replace('\n', '')
    match = re.search(r'TotalNewCharges([\d,]+\.\d{2})', compact)
    if not match:
        raise ValueError("Could not find TotalNewCharges in invoice PDF")
    return {'total': float(match.group(1).replace(',', ''))}


def parse_cash_requirements(folder):
    """Returns employer liability amounts from the EFT/Taxpay section.
    FUTA, CA ETT, CA SUI default to 0.0 when not charged (most weeks).
    Structure confirmed: EmployerLiabilities block ends at TotalLiabilities.
    """
    path = find_report(folder, 'cash_requirements')
    with pdfplumber.open(path) as pdf:
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
    compact = text.replace(' ', '').replace('\n', '')

    er_match = re.search(r'EmployerLiabilities(.*?)TotalLiabilities', compact, re.DOTALL)
    if not er_match:
        raise ValueError("Could not find Employer Liabilities section in Cash Requirements")
    section = er_match.group(1)

    return {
        'social_security': get_amount(r'SocialSecurity([\d,]+\.\d{2})', section),
        'medicare':        get_amount(r'Medicare([\d,]+\.\d{2})', section),
        'futa':            get_amount(r'FedUnemploy([\d,]+\.\d{2})', section),
        'ca_ett':          get_amount(r'CAEmpTrain([\d,]+\.\d{2})', section),
        'ca_unemployment': get_amount(r'CAUnemploy([\d,]+\.\d{2})', section),
    }


def parse_payroll_journal(folder):
    """Returns officers and staff current-period totals, plus HRA for Juan/Ricky.

    Section boundaries (confirmed PDF structure):
      Officers: 100OFFICERSTOTALS ... 100OFFICERSTOTAL<space>
      Staff:    300STAFFTOTALS    ... 300STAFFTOTAL<space>

    HRA detection: look for HRAReimbursement between employee name header
    and EMPLOYEEYTDTOTAL. Only appears in that block when HRA is paid this period.
    """
    path = find_report(folder, 'payroll_journal')
    with pdfplumber.open(path) as pdf:
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)

    off_match = re.search(r'100OFFICERSTOTALS(.*?)100OFFICERSTOTAL\b', text, re.DOTALL)
    if not off_match:
        raise ValueError("Could not find 100 Officers Totals in Payroll Journal")
    off_text = off_match.group(1)

    staff_match = re.search(r'300STAFFTOTALS(.*?)300STAFFTOTAL\b', text, re.DOTALL)
    if not staff_match:
        raise ValueError("Could not find 300 Staff Totals in Payroll Journal")
    staff_text = staff_match.group(1)

    officers = {
        'net_pay':  get_amount(r'DirDep\*\*\s+([\d,]+\.\d{2})', off_text),
        'fed_wh':   get_amount(r'Fed Income Tax\s+([\d,]+\.\d{2})', off_text),
        'casdi':    get_amount(r'CA Disability\s+([\d,]+\.\d{2})', off_text),
        'fica':     get_amount(r'Social Security\s+([\d,]+\.\d{2})', off_text),
        'medicare': get_amount(r'Medicare\s+([\d,]+\.\d{2})', off_text),
    }

    staff = {
        'net_pay':  get_amount(r'DirDep\*\*\s+([\d,]+\.\d{2})', staff_text),
        'fed_wh':   get_amount(r'Fed Income Tax\s+([\d,]+\.\d{2})', staff_text),
        'casdi':    get_amount(r'CA Disability\s+([\d,]+\.\d{2})', staff_text),
        'ca_state': get_amount(r'CA Income Tax\s+([\d,]+\.\d{2})', staff_text),
        'fica':     get_amount(r'Social Security\s+([\d,]+\.\d{2})', staff_text),
        'medicare': get_amount(r'Medicare\s+([\d,]+\.\d{2})', staff_text),
    }

    # HRA: present in current-period block only when paid this payroll
    juan_block  = re.search(r'Magadan,JuanT(.*?)EMPLOYEEYTDTOTAL',   text, re.DOTALL)
    ricky_block = re.search(r'Quezada,Ricardo(.*?)EMPLOYEEYTDTOTAL',  text, re.DOTALL)

    juan_hra  = get_amount(r'HRAReimbursement\s+([\d,]+\.\d{2})', juan_block.group(1))  if juan_block  else 0.0
    ricky_hra = get_amount(r'HRAReimbursement\s+([\d,]+\.\d{2})', ricky_block.group(1)) if ricky_block else 0.0

    return {
        'officers': officers,
        'staff':    staff,
        'juan_hra': juan_hra,
        'ricky_hra': ricky_hra,
    }


def iif_header():
    return (
        '!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tMEMO\tCLEAR\tTOPRINT\n'
        '!SPL\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tMEMO\tCLEAR\n'
        '!ENDTRNS\n'
    )


def iif_check(check_date, splits, memo):
    """splits: list of (account, amount) — amounts positive. TRNS line is negative."""
    total = sum(amt for _, amt in splits)
    d = fmt_date(check_date)
    lines = [f'TRNS\tCHECK\t{d}\t{QB_ACCOUNTS["checking"]}\t{PAYEE}\t-{total:.2f}\t{memo}\tN\tN']
    for account, amount in splits:
        lines.append(f'SPL\tCHECK\t{d}\t{account}\t{PAYEE}\t{amount:.2f}\t{memo}\tN')
    lines.append('ENDTRNS')
    return '\n'.join(lines) + '\n'


def generate_iif(folder, payroll_date):
    memo      = fmt_date(payroll_date)
    day_before = payroll_date - timedelta(days=1)

    invoice = parse_invoice(folder)
    pj      = parse_payroll_journal(folder)
    cr      = parse_cash_requirements(folder)

    iif = iif_header()

    # Check 1 — Invoice (day before payroll)
    iif += iif_check(day_before, [
        (QB_ACCOUNTS['payroll_prep_fees'], invoice['total']),
    ], memo)

    # Check 2 — Direct Deposit (day before payroll)
    dd_splits = [
        (QB_ACCOUNTS['employee_wages'],    pj['staff']['net_pay']),
        (QB_ACCOUNTS['officers_salaries'], pj['officers']['net_pay']),
    ]
    if pj['juan_hra']  > 0: dd_splits.append((QB_ACCOUNTS['hsa_juan'],  pj['juan_hra']))
    if pj['ricky_hra'] > 0: dd_splits.append((QB_ACCOUNTS['hsa_ricky'], pj['ricky_hra']))
    iif += iif_check(day_before, dd_splits, memo)

    # Check 3 — Tax (payroll date)
    tax_splits = [
        (QB_ACCOUNTS['fica_er'],     cr['social_security']),
        (QB_ACCOUNTS['medicare_er'], cr['medicare']),
    ]
    if cr['futa']            > 0: tax_splits.append((QB_ACCOUNTS['futa'],    cr['futa']))
    if cr['ca_ett']          > 0: tax_splits.append((QB_ACCOUNTS['ca_ett'],  cr['ca_ett']))
    if cr['ca_unemployment'] > 0: tax_splits.append((QB_ACCOUNTS['ca_sui'],  cr['ca_unemployment']))
    tax_splits += [
        (QB_ACCOUNTS['off_fed_wh'],  pj['officers']['fed_wh']),
        (QB_ACCOUNTS['off_casdi'],   pj['officers']['casdi']),
        (QB_ACCOUNTS['off_fica'],    pj['officers']['fica']),
        (QB_ACCOUNTS['off_medicare'],pj['officers']['medicare']),
        (QB_ACCOUNTS['ee_fed_wh'],   pj['staff']['fed_wh']),
        (QB_ACCOUNTS['ee_casdi'],    pj['staff']['casdi']),
        (QB_ACCOUNTS['ee_ca_state'], pj['staff']['ca_state']),
        (QB_ACCOUNTS['ee_fica'],     pj['staff']['fica']),
        (QB_ACCOUNTS['ee_medicare'], pj['staff']['medicare']),
    ]
    iif += iif_check(payroll_date, tax_splits, memo)

    out_path = os.path.join(folder, f"payroll_{payroll_date.strftime('%m%d')}.iif")
    with open(out_path, 'w') as f:
        f.write(iif)

    dd_total  = sum(a for _, a in dd_splits)
    tax_total = sum(a for _, a in tax_splits)
    print(f"\nPayroll {memo}")
    print(f"  Check 1 (Invoice)  {fmt_date(day_before)}: ${invoice['total']:.2f}")
    print(f"  Check 2 (DD)       {fmt_date(day_before)}: ${dd_total:.2f}")
    print(f"  Check 3 (Tax)      {memo}: ${tax_total:.2f}")
    if pj['juan_hra']  > 0: print(f"    HRA Juan:  ${pj['juan_hra']:.2f}")
    if pj['ricky_hra'] > 0: print(f"    HRA Ricky: ${pj['ricky_hra']:.2f}")
    print(f"\nIIF written to: {out_path}")
    return out_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 paychex_to_iif.py /path/to/Payroll.MMDD YYYY-MM-DD")
        sys.exit(1)
    folder       = sys.argv[1]
    payroll_date = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
    generate_iif(folder, payroll_date)
```

---

## QB Desktop Import — AppleScript

Save as `import_iif.applescript` in the skill folder:

```applescript
on importIIF(iifPath)
    tell application "QuickBooks"
        activate
        delay 2
        -- Open IIF import dialog
        -- File → Utilities → Import → IIF Files
        tell application "System Events"
            tell process "QuickBooks"
                click menu item "File" of menu bar 1
                click menu item "Utilities" of menu "File" of menu bar 1
                click menu item "Import" of menu "Utilities" of menu "File" of menu bar 1
                click menu item "IIF Files..." of menu "Import" of menu "Utilities" of menu "File" of menu bar 1
                delay 1
                -- Type file path in Open dialog
                keystroke "g" using {command down, shift down}
                delay 0.5
                keystroke iifPath
                keystroke return
                delay 0.5
                keystroke return  -- Open
                delay 2
                -- Dismiss confirmation dialog if present
                try
                    keystroke return
                end try
            end tell
        end tell
    end tell
end importIIF
```

Call from Python:
```python
import subprocess

def import_to_quickbooks(iif_path):
    script = f'osascript import_iif.applescript "{iif_path}"'
    result = subprocess.run(script, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript import failed: {result.stderr}")
    return True
```

> **Note:** AppleScript selectors are approximate — QB Desktop menu structure needs to be verified on first run. QB must be open and on the home screen before import runs.

---

## Discord Notifications

```python
import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/TOKEN"  # store in env or keychain

def notify_discord(message, is_error=False):
    emoji = "🚨" if is_error else "✅"
    requests.post(DISCORD_WEBHOOK, json={"content": f"{emoji} **Paychex IIF** | {message}"})
```

Call after successful import:
```python
notify_discord(
    f"IIF imported | Payroll {fmt_date(payroll_date)} | "
    f"Invoice: ${invoice_total:.2f} | DD: ${dd_total:.2f} | Tax: ${tax_total:.2f}"
)
```

Call on any failure:
```python
except Exception as e:
    notify_discord(f"FAILED: {str(e)}", is_error=True)
    raise
```

---

## QB Desktop Import — Manual Fallback
If AppleScript import fails:
1. File → Utilities → Import → IIF Files
2. Select the `.iif` file from the `Payroll.MMDD` folder
3. Verify 3 checks appear in the check register for `10100 - US Bank Checking`
4. Confirm dates: Invoice and DD = day before payroll; Tax = payroll date

---

## TODOs Before First Run
1. Download and open each PDF manually — map exact text structure for parsers
2. Update `REPORT_PATTERNS` dict with actual zip filenames
3. Implement the 3 parser functions (`parse_invoice`, `parse_payroll_journal`, `parse_cash_requirements`)
4. Validate `QB_ACCOUNTS` strings against actual QB Desktop chart of accounts (spacing/dash style must match exactly)
5. Run against first Paychex payroll and compare IIF output to manual entry
6. Confirm `is_first_of_month` logic matches actual HSA schedule

---

## Known Issues / Watch Points
- QB Desktop is sensitive to account name formatting — if import fails silently, compare account strings character by character
- IIF `AMOUNT` on TRNS line must be negative; SPL lines must be positive
- If Paychex adds/removes a line in a report (e.g., no FUTA some weeks), parser must handle gracefully — treat missing lines as 0.0, not crash
- HRA detection: using `> 0` is reliable; confirm whether "0.00" appears in report or line is omitted entirely
