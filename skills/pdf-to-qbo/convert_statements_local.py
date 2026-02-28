#!/usr/bin/env python3
"""
Wells Fargo PDF to QBO Converter
Usage: python3 convert_statements.py /path/to/statement/folder

Auto-detects account type from folder name:
  - Folder name containing '.cc', 'Signify', 'visa', or 'card' → CREDITCARD
  - Everything else → BANK (checking)

Output: writes [folder-name].qbo into the same folder.
"""

import pdfplumber
import re
import sys
import hashlib
from datetime import datetime
from pathlib import Path


# ── CONSTANTS ─────────────────────────────────────────────────────────────────

WF_BANK_ROUTING = "121042882"
WF_FID = "3000"

CREDITCARD_HINTS = ['.cc', 'signify', 'visa', 'card', 'credit']


# ── AUTO-DETECT FROM FOLDER NAME ─────────────────────────────────────────────

def detect_account_type(folder_name):
    lower = folder_name.lower()
    for hint in CREDITCARD_HINTS:
        if hint in lower:
            return "CREDITCARD"
    return "BANK"


# ── FILENAME DATE PARSING ─────────────────────────────────────────────────────

def parse_closing_date(filename):
    stem = Path(filename).stem
    match = re.match(r'^(\d{2})(\d{2})(\d{2})', stem)
    if not match:
        raise ValueError(f"Cannot parse date from filename: {filename}")
    mm, dd, yy = match.groups()
    return datetime(2000 + int(yy), int(mm), int(dd))


def infer_year(month, closing_date):
    if month > closing_date.month:
        return closing_date.year - 1
    return closing_date.year


# ── PDF PARSING: CREDIT CARD ──────────────────────────────────────────────────

def parse_creditcard_pdf(pdf_path, closing_date):
    transactions = []
    account_number = None

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            t = page.extract_text() or ""
            full_text += t + "\n"
            if not account_number:
                acct_match = re.search(r'Account Number\s+([\d\s]{16,25})', t)
                if acct_match:
                    account_number = re.sub(r'\s+', '', acct_match.group(1))

        # Extract new balance
        ending_balance = None
        balance_date = None
        bal_match = re.search(r'New Balance\s+\$([\d,]+\.\d{2})', full_text)
        if bal_match:
            ending_balance = float(bal_match.group(1).replace(',', ''))
            balance_date = closing_date

        lines = full_text.split('\n')
        in_transactions = False

        for line in lines:
            line = line.strip()

            if 'Transaction Details' in line:
                in_transactions = True
                continue

            if not in_transactions:
                continue

            if re.match(r'^(See reverse|DETACH|Make checks|Payment Remittance|Page \d+)', line, re.I):
                continue

            tx_match = re.match(
                r'^(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(\S{10,})\s+(.+?)\s+([\d,]+\.\d{2})\s*$',
                line
            )
            if tx_match:
                _, post_date_str, ref_num, description, amount_str = tx_match.groups()
                amount = float(amount_str.replace(',', ''))
                post_month, post_day = [int(x) for x in post_date_str.split('/')]
                year = infer_year(post_month, closing_date)
                post_date = datetime(year, post_month, post_day)

                is_credit = bool(re.search(
                    r'(ONLINE PAYMENT|PAYMENT.*THANK|CREDIT|REFUND|RETURN)',
                    description, re.I
                ))
                signed_amount = -amount if is_credit else amount

                transactions.append({
                    'date': post_date,
                    'ref': ref_num,
                    'description': description.strip(),
                    'amount': signed_amount,
                })

    return transactions, account_number, ending_balance, balance_date


# ── PDF PARSING: CHECKING ─────────────────────────────────────────────────────

def parse_checking_pdf(pdf_path, closing_date):
    transactions = []
    account_number = None

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += (page.extract_text() or "") + "\n"

    acct_match = re.search(r'Account number:\s*(\d{8,12})', full_text)
    if acct_match:
        account_number = acct_match.group(1).strip()

    # Extract ending balance
    ending_balance = None
    balance_date = None
    bal_match = re.search(r'Ending balance on (\d{1,2}/\d{1,2})\s+([\d,]+\.\d{2})', full_text)
    if bal_match:
        bal_date_str, bal_amt = bal_match.groups()
        ending_balance = float(bal_amt.replace(',', ''))
        bal_month, bal_day = [int(x) for x in bal_date_str.split('/')]
        bal_year = infer_year(bal_month, closing_date)
        balance_date = datetime(bal_year, bal_month, bal_day)

    lines = full_text.split('\n')
    in_transactions = False
    cur_date = None
    cur_desc = None
    cur_amounts = None

    def commit(date_str, desc, amounts):
        month, day = [int(x) for x in date_str.split('/')]
        year = infer_year(month, closing_date)
        tx_date = datetime(year, month, day)
        tx_amount_raw = float(amounts[0].replace(',', ''))
        desc_upper = desc.upper()
        is_deposit = bool(re.search(
            r'(ZELLE|PAYPAL|DEPOSIT|TRANSFER.*FROM|RECEIVED|INCOMING)',
            desc_upper
        ))
        is_withdrawal = bool(re.search(
            r'(TRANSFER.*TO|CHECK|PAYMENT OUT|WITHDRAWAL)',
            desc_upper
        ))
        signed = tx_amount_raw if (is_deposit and not is_withdrawal) else -tx_amount_raw
        fitid = tx_date.strftime('%Y%m%d') + hashlib.md5(
            (desc + str(tx_amount_raw)).encode()
        ).hexdigest()[:10]
        return {
            'date': tx_date,
            'ref': fitid,
            'description': desc.strip(),
            'amount': signed,
        }

    result = []

    for line in lines:
        line_stripped = line.strip()

        if 'Transaction history' in line_stripped:
            in_transactions = True
            continue

        if not in_transactions:
            continue

        if re.match(r'^(Ending balance on|Totals \$|Summary of checks|Monthly service fee)', line_stripped, re.I):
            if cur_date:
                result.append(commit(cur_date, cur_desc, cur_amounts))
                cur_date = cur_desc = cur_amounts = None
            in_transactions = False
            continue

        if re.match(r'^(Date|Check|Deposits|Withdrawals|Number\s+Description)', line_stripped, re.I):
            continue

        tx_match = re.match(
            r'^(\d{1,2}/\d{1,2})\s+(?:\d{3,6}\s+)?(.+?)\s+([\d,]+\.\d{2})(?:\s+([\d,]+\.\d{2}))?\s*$',
            line_stripped
        )
        if tx_match:
            if cur_date:
                result.append(commit(cur_date, cur_desc, cur_amounts))
            date_str, description, amt1, amt2 = tx_match.groups()
            cur_date = date_str
            cur_desc = description
            cur_amounts = [amt1] + ([amt2] if amt2 else [])
            continue

        if cur_date and line_stripped and not re.match(r'^(The Ending|If you|©|IMPORTANT)', line_stripped, re.I):
            cur_desc = (cur_desc or "") + " " + line_stripped

    if cur_date:
        result.append(commit(cur_date, cur_desc, cur_amounts))

    return result, account_number, ending_balance, balance_date


# ── DEDUPLICATION ─────────────────────────────────────────────────────────────

def deduplicate(transactions):
    seen = set()
    unique = []
    for t in transactions:
        key = (t['date'].strftime('%Y%m%d'), f"{abs(t['amount']):.2f}", t['ref'][:15])
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique


# ── QBO BUILDER ───────────────────────────────────────────────────────────────

def build_transaction_block(t):
    trntype = "CREDIT" if t['amount'] > 0 else "DEBIT"
    dtposted = t['date'].strftime('%Y%m%d')
    amount = f"{t['amount']:.2f}"
    fitid = re.sub(r'[^A-Za-z0-9]', '', t['ref'])[:36]
    memo = re.sub(r'[<>&"\']', ' ', t['description'])[:255]
    return (f"<STMTTRN>\n<TRNTYPE>{trntype}</TRNTYPE>\n<DTPOSTED>{dtposted}</DTPOSTED>\n"
            f"<TRNAMT>{amount}</TRNAMT>\n<FITID>{fitid}</FITID>\n<MEMO>{memo}</MEMO>\n</STMTTRN>")


def build_qbo(transactions, account_number, account_type, ending_balance=None, balance_date=None):
    dates = [t['date'] for t in transactions]
    dt_start = min(dates).strftime('%Y%m%d')
    dt_end = max(dates).strftime('%Y%m%d')
    dt_server = datetime.now().strftime('%Y%m%d%H%M%S')
    tx_blocks = "\n".join(build_transaction_block(t) for t in sorted(transactions, key=lambda x: x['date']))

    ledger_block = ""
    if ending_balance is not None and balance_date is not None:
        ledger_block = (f"<LEDGERBAL>\n<BALAMT>{ending_balance:.2f}</BALAMT>\n"
                        f"<DTASOF>{balance_date.strftime('%Y%m%d')}</DTASOF>\n</LEDGERBAL>\n")

    header = ("OFXHEADER:100\nDATA:OFXSGML\nVERSION:102\nSECURITY:NONE\n"
              "ENCODING:USASCII\nCHARSET:1252\nCOMPRESSION:NONE\n"
              "OLDFILEUID:NONE\nNEWFILEUID:NONE\n\n")

    signon = (f"<OFX>\n<SIGNONMSGSRSV1>\n<SONRS>\n<STATUS>\n<CODE>0</CODE>\n"
              f"<SEVERITY>INFO</SEVERITY>\n</STATUS>\n<DTSERVER>{dt_server}</DTSERVER>\n"
              f"<LANGUAGE>ENG</LANGUAGE>\n<FI>\n<ORG>Wells Fargo</ORG>\n<FID>{WF_FID}</FID>\n"
              f"</FI>\n<INTU.BID>{WF_FID}</INTU.BID>\n</SONRS>\n</SIGNONMSGSRSV1>\n")

    if account_type == "CREDITCARD":
        body = (f"<CREDITCARDMSGSRSV1>\n<CCSTMTTRNRS>\n<TRNUID>1001</TRNUID>\n"
                f"<CCSTMTRS>\n<CURDEF>USD</CURDEF>\n<CCACCTFROM>\n<ACCTID>{account_number}</ACCTID>\n"
                f"</CCACCTFROM>\n<BANKTRANLIST>\n<DTSTART>{dt_start}</DTSTART>\n"
                f"<DTEND>{dt_end}</DTEND>\n{tx_blocks}\n</BANKTRANLIST>\n"
                f"{ledger_block}"
                f"</CCSTMTRS>\n</CCSTMTTRNRS>\n</CREDITCARDMSGSRSV1>\n")
    else:
        body = (f"<BANKMSGSRSV1>\n<STMTTRNRS>\n<TRNUID>1001</TRNUID>\n"
                f"<STMTRS>\n<CURDEF>USD</CURDEF>\n<BANKACCTFROM>\n"
                f"<BANKID>{WF_BANK_ROUTING}</BANKID>\n<ACCTID>{account_number}</ACCTID>\n"
                f"<ACCTTYPE>CHECKING</ACCTTYPE>\n</BANKACCTFROM>\n"
                f"<BANKTRANLIST>\n<DTSTART>{dt_start}</DTSTART>\n<DTEND>{dt_end}</DTEND>\n"
                f"{tx_blocks}\n</BANKTRANLIST>\n"
                f"{ledger_block}"
                f"</STMTRS>\n</STMTTRNRS>\n</BANKMSGSRSV1>\n")

    return header + signon + body + "</OFX>"


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_statements.py /path/to/folder")
        print("  Folder name auto-detects account type (BANK or CREDITCARD)")
        sys.exit(1)

    folder = Path(sys.argv[1]).expanduser().resolve()

    if not folder.exists():
        print(f"Folder not found: {folder}")
        sys.exit(1)

    folder_label = folder.name
    account_type = detect_account_type(folder_label)

    pdf_files = sorted(folder.glob('*_WellsFargo.pdf'))
    if not pdf_files:
        print(f"No *_WellsFargo.pdf files found in {folder}")
        sys.exit(1)

    print(f"Folder     : {folder_label}")
    print(f"Account    : {account_type}")
    print(f"Statements : {len(pdf_files)}\n")

    all_transactions = []
    account_number = None
    errors = []
    last_balance = None
    last_balance_date = None

    for pdf_path in pdf_files:
        try:
            closing_date = parse_closing_date(pdf_path.name)
            print(f"  {pdf_path.name}  (closing: {closing_date.strftime('%m/%d/%Y')})")

            if account_type == "CREDITCARD":
                txns, acct_num, bal, bal_date = parse_creditcard_pdf(pdf_path, closing_date)
            else:
                txns, acct_num, bal, bal_date = parse_checking_pdf(pdf_path, closing_date)

            if acct_num and not account_number:
                account_number = acct_num
            if bal is not None:
                last_balance = bal
                last_balance_date = bal_date

            bal_str = f"  |  ending balance: ${bal:,.2f}" if bal else ""
            print(f"    → {len(txns)} transactions{bal_str}")
            all_transactions.extend(txns)

        except Exception as e:
            import traceback; traceback.print_exc()
            errors.append(pdf_path.name)

    if not all_transactions:
        print("\nNo transactions extracted.")
        sys.exit(1)

    before = len(all_transactions)
    all_transactions = deduplicate(all_transactions)
    dupes = before - len(all_transactions)

    qbo_content = build_qbo(all_transactions, account_number, account_type, last_balance, last_balance_date)
    qbo_filename = f"{folder_label}.qbo"
    out_path = folder / qbo_filename
    out_path.write_text(qbo_content, encoding='ascii', errors='replace')

    dates = [t['date'] for t in all_transactions]
    print(f"\n{'='*50}")
    print(f"✓ Statements : {len(pdf_files)}")
    print(f"✓ Transactions: {len(all_transactions)}  ({dupes} dupes removed)")
    print(f"✓ Date range : {min(dates).strftime('%m/%d/%Y')} – {max(dates).strftime('%m/%d/%Y')}")
    print(f"✓ Account    : {account_number}")
    print(f"✓ QBO file   : {out_path}")
    if errors:
        print(f"⚠ Skipped    : {', '.join(errors)}")

    print(f"\nTransactions:")
    for t in sorted(all_transactions, key=lambda x: x['date']):
        sign = "+" if t['amount'] > 0 else ""
        print(f"  {t['date'].strftime('%m/%d/%Y')}  {sign}{t['amount']:.2f}  {t['description'][:60]}")


if __name__ == '__main__':
    main()
