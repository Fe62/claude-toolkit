#!/usr/bin/env python3
"""
paychex_download.py — Download Paychex payroll zip and extract to DirectNAS.

Requirements:
  - Brave must be running with remote debugging:
      open -a "Brave Browser" --args --remote-debugging-port=9222
  - User must be logged into Paychex Flex in that Brave window
  - Paychex username stored in macOS Keychain:
      security add-generic-password -s "paychex" -a "username" -w "YOUR_USERNAME"
  - DirectNAS mounted at /Volumes/Public
  - pip3 install playwright requests && python3 -m playwright install chromium

Usage:
  python3 paychex_download.py
"""

import subprocess, sys, os, zipfile, json, uuid, time, shutil, tempfile, re
import urllib.request as _urllib, ssl as _ssl
from datetime import date, datetime
from playwright.sync_api import sync_playwright

# ── Static company config ──────────────────────────────────────────────────────
CLIENT = {
    "id": "70353251",
    "companyId": "70353251",
    "caid": "00FWDQEWMMMARRL70TU6",
    "branchId": "0080",
    "displayName": "Direct Lighting LLC",
    "version": "V1",
    "ns": "com.paychex.reporting.dto.ReportingClient",
}
BASE_URL  = "https://reporting.flex.paychex.com/reporting_remote/do/json"
DL_BASE   = "https://reporting.flex.paychex.com/reporting_remote"
NAS_BASE  = "/Volumes/Public/Direct Lighting/Direct Lighting LLC/1.Direct.Payroll/1.Payrolls/26.Payrolls"
CDP_URL   = "http://localhost:9222"


# ── Helpers ────────────────────────────────────────────────────────────────────
def get_credential(service, account):
    r = subprocess.run(
        ['security', 'find-generic-password', '-s', service, '-a', account, '-w'],
        capture_output=True, text=True,
    )
    val = r.stdout.strip()
    if not val:
        raise RuntimeError(f"Keychain credential not found: service={service} account={account}")
    return val

def get_output_folder(payroll_date):
    q = (payroll_date.month - 1) // 3 + 1
    return os.path.join(NAS_BASE, f"Q{q}", f"Payroll.{payroll_date.strftime('%m%d')}")

def check_nas():
    if not os.path.exists("/Volumes/Public"):
        print("ERROR: DirectNAS not mounted at /Volumes/Public. Aborting.")
        sys.exit(1)


# ── Logging ────────────────────────────────────────────────────────────────────
def write_log(output_folder, payroll_date, files, error=None):
    """Append a run record to {output_folder}/download.log."""
    os.makedirs(output_folder, exist_ok=True)
    log_path = os.path.join(output_folder, 'download.log')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Run:     {ts}\n")
        f.write(f"Payroll: {payroll_date}\n")
        if error:
            f.write(f"Status:  ERROR\n")
            f.write(f"Error:   {error}\n")
        else:
            f.write(f"Status:  OK\n")
            f.write(f"Files:   {len(files)}\n")
            for fn in sorted(files):
                f.write(f"  {fn}\n")
    print(f"Log written: {log_path}")


# ── Discord ────────────────────────────────────────────────────────────────────
def get_discord_webhook():
    """Returns webhook URL from Keychain, or None if not configured."""
    r = subprocess.run(
        ['security', 'find-generic-password', '-s', 'discord-webhook',
         '-a', 'paychex-download', '-w'],
        capture_output=True, text=True,
    )
    url = r.stdout.strip().strip('"\'')  # strip accidental quotes from Keychain value
    return url if url.startswith('http') else None


def send_discord(webhook_url, message):
    """POST message to Discord webhook. Silent if webhook_url is None."""
    if not webhook_url:
        return
    data = json.dumps({"content": message}).encode('utf-8')
    req = _urllib.Request(
        webhook_url, data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'paychex-download/1.0'},
    )
    try:
        import certifi
        ctx = _ssl.create_default_context(cafile=certifi.where())
        _urllib.urlopen(req, timeout=10, context=ctx)
    except Exception as e:
        print(f"Discord notification failed (non-fatal): {e}")


def parse_check_totals(files):
    """Extract dollar amounts from pay stub filenames (e.g. $464.85)."""
    amounts = []
    for f in files:
        m = re.search(r'\$([\d,]+\.\d{2})', os.path.basename(f))
        if m:
            amounts.append(float(m.group(1).replace(',', '')))
    return amounts


# ── Main browser session ───────────────────────────────────────────────────────
def run(username):
    """
    1. Connects to existing Brave session via CDP.
    2. Installs XHR interceptor to capture the OIDC Bearer token from Angular's
       own requests (the token is held in-memory, not in storage).
    3. Navigates to RPTCTR_HTML so Angular makes getMostFrequentlyUsedReports,
       which exposes the Bearer token.
    4. Calls loadPackageFolders + getDownloadFolderRequestURL via page.evaluate()
       using the captured Bearer token for auth.
    5. Downloads zip via Playwright's download handler.
    Returns (payroll_date, zip_path, zip_name).
    """
    print("Connecting to Brave (CDP)...")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

        # ── Find Paychex tab ──────────────────────────────────────────────────
        paychex_page = None
        for pg in context.pages:
            if 'myapps.paychex.com' in pg.url:
                paychex_page = pg
                print(f"Found Paychex tab: {pg.url[:80]}")
                break
        if not paychex_page:
            raise RuntimeError(
                "No myapps.paychex.com tab found in Brave. "
                "Open Paychex Flex in Brave and log in first."
            )
        if 'login.do' in paychex_page.url or 'login' in paychex_page.url.split('?')[0].split('/')[-1]:
            raise RuntimeError(
                f"Paychex tab is at login page ({paychex_page.url[:60]}). "
                "Complete login to the Paychex Flex dashboard first."
            )

        # ── Install Playwright-level request listener to capture Bearer token ──
        # Angular holds the OIDC Bearer token in-memory; it's sent on every
        # reporting_remote request. Using page.on('request') (Playwright network
        # layer) instead of JS XHR patching so the listener survives full-page
        # navigations (e.g. when the tab is at login.do rather than the SPA).
        captured = {'token': None, 'sid': None}

        def handle_request(request):
            if 'reporting.flex.paychex.com' not in request.url:
                return
            hdrs = request.headers
            auth = hdrs.get('authorization', '')
            sid  = hdrs.get('x-payx-sid', '')
            if auth.startswith('Bearer ') and not captured['token']:
                captured['token'] = auth
            if sid and sid != '0' and not captured['sid']:
                captured['sid'] = sid

        paychex_page.on('request', handle_request)

        # ── Navigate to reports center to trigger Angular's reporting calls ───
        # Angular calls getMostFrequentlyUsedReports on RPTCTR_HTML load — that
        # request carries the Bearer token we need.
        REPORTS_URL   = ("https://myapps.paychex.com/landing_remote/html"
                         "?extoldlnk=true&lang=en&landingRedirect=true"
                         "#?mode=admin&app=RPTCTR_HTML&clients=00FWDQEWMMMARRL70TU6")
        DASHBOARD_URL = ("https://myapps.paychex.com/landing_remote/html"
                         "?extoldlnk=true&lang=en&landingRedirect=true"
                         "#?mode=admin&app=DASHBOARD_ADM&clients=00FWDQEWMMMARRL70TU6")

        current_url = paychex_page.url
        if 'RPTCTR_HTML' in current_url:
            print("Bouncing to dashboard first to force Angular re-init on return...")
            paychex_page.evaluate(f"() => {{ window.location.href = '{DASHBOARD_URL}'; }}")
            time.sleep(2)

        print("Navigating to reports center to trigger Angular Bearer token request...")
        paychex_page.evaluate(f"() => {{ window.location.href = '{REPORTS_URL}'; }}")

        # ── Wait for Bearer token ─────────────────────────────────────────────
        print("Waiting for Bearer token (up to 30s)...")
        deadline = time.time() + 30
        while time.time() < deadline:
            if captured['token']:
                break
            time.sleep(0.3)

        paychex_page.remove_listener('request', handle_request)

        if not captured['token']:
            raise RuntimeError(
                "Bearer token not captured. "
                "Check that Brave is open with Paychex Flex logged in and "
                "the tab can reach the reports center."
            )
        auth_header = captured['token']   # "Bearer eyJ..."
        session_id  = captured['sid'] or ""
        print(f"  Bearer token captured. Session: {session_id[:20]}...")

        # ── Call loadPackageFolders with real Bearer auth ─────────────────────
        print("Calling loadPackageFolders...")
        lpf_body = {
            "ns": "com.paychex.framework.remoting.dto.RemoteObjectRequest",
            "destination": "packagesRemoteV2",
            "operation": "loadPackageFolders",
            "params": [{"clients": [CLIENT], "packageId": "1",
                        "ns": "com.paychex.reporting.dto.GetPackageFolderRequest"}]
        }
        lpf_result = paychex_page.evaluate(
            """async ([body, sid, username, auth]) => {
                const r = await fetch(
                    'https://reporting.flex.paychex.com/reporting_remote/do/json/packagesRemoteV2/loadPackageFolders',
                    { method: 'POST', credentials: 'include',
                      headers: {
                        'content-type': 'application/json',
                        'accept': 'application/json, text/plain, */*',
                        'authorization': auth,
                        'x-payx-sid': sid, 'x-payx-cnsmr': 'PaychexFlex',
                        'x-payx-comp': 'PaychexFlex',
                        'x-payx-bizpn': '/reporting_remote/do/json/packagesRemoteV2/loadPackageFolders',
                        'x-payx-user-untrusted': username,
                      }, body: JSON.stringify(body) }
                );
                return { status: r.status, body: await r.text() };
            }""",
            [lpf_body, session_id, username, auth_header]
        )
        print(f"  status={lpf_result['status']}")
        if lpf_result['status'] != 200:
            print(f"  response={lpf_result['body'][:300]}")
            raise RuntimeError(f"loadPackageFolders failed: HTTP {lpf_result['status']}")
        lpf_data = json.loads(lpf_result['body'])
        folders  = lpf_data['data']['packageFolders']
        print(f"  Got {len(folders)} folders.")

        if not folders:
            raise RuntimeError("No payroll folders returned from Paychex.")

        folder = folders[0]
        d = folder['date']
        payroll_date = date(d['year'], d['month'], d['date'])
        print(f"Most recent payroll date: {payroll_date}")

        # ── getDownloadFolderRequestURL via in-browser fetch ──────────────────
        # Session is now valid (just made a live reporting call)
        print("Calling getDownloadFolderRequestURL...")
        gdu_body = {
            "ns": "com.paychex.framework.remoting.dto.RemoteObjectRequest",
            "destination": "downloadRemoteV2",
            "operation": "getDownloadFolderRequestURL",
            "params": [{
                "clients": [CLIENT],
                "folders": [{
                    "packageId": folder["packageId"],
                    "caids":     folder["caids"],
                    "name":      folder.get("name"),
                    "date":      folder["date"],
                    "dateType":  folder["dateType"],
                    "ns":        "com.paychex.reporting.dto.PackageFolderV2",
                }],
                "renditionIdFilter": [],
                "mergeOutput":       False,
                "reportAction":      "DOWNLOAD",
                "trackingId":        "DRSET",
                "ns":                "com.paychex.reporting.dto.DownloadFolderRequestV2",
            }]
        }
        gdu_result = paychex_page.evaluate(
            """async ([body, sid, username, auth]) => {
                const r = await fetch(
                    'https://reporting.flex.paychex.com/reporting_remote/do/json/downloadRemoteV2/getDownloadFolderRequestURL',
                    {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'content-type': 'application/json',
                            'accept': 'application/json, text/plain, */*',
                            'authorization': auth,
                            'x-payx-sid': sid,
                            'x-payx-cnsmr': 'PaychexFlex',
                            'x-payx-comp': 'PaychexFlex',
                            'x-payx-bizpn': '/reporting_remote/do/json/downloadRemoteV2/getDownloadFolderRequestURL',
                            'x-payx-user-untrusted': username,
                        },
                        body: JSON.stringify(body)
                    }
                );
                const text = await r.text();
                return { status: r.status, body: text };
            }""",
            [gdu_body, session_id, username, auth_header]
        )
        print(f"  status={gdu_result['status']}")
        if gdu_result['status'] != 200:
            print(f"  response={gdu_result['body'][:500]}")
            raise RuntimeError(f"getDownloadFolderRequestURL failed: HTTP {gdu_result['status']}")

        gdu_data = json.loads(gdu_result['body'])
        url_path = gdu_data['data']['urlInfo'][0]['url']
        download_url = f"{DL_BASE}/{url_path}"
        print(f"Download URL obtained.")

        # ── Download zip via Playwright ───────────────────────────────────────
        print("Downloading zip...")
        with tempfile.TemporaryDirectory() as tmp:
            with paychex_page.expect_download(timeout=60000) as dl_info:
                paychex_page.evaluate(
                    "url => { window.location.href = url; }",
                    download_url
                )
            download = dl_info.value
            zip_name = download.suggested_filename or "payroll.zip"
            zip_tmp  = os.path.join(tmp, zip_name)
            download.save_as(zip_tmp)
            print(f"Zip downloaded: {zip_name}")

            # Copy out before TemporaryDirectory cleans up
            final_tmp = f"/tmp/{zip_name}"
            shutil.copy2(zip_tmp, final_tmp)

        browser.close()
        return payroll_date, final_tmp, zip_name


# ── Extract zip ────────────────────────────────────────────────────────────────
def extract_zip(zip_path, zip_name, output_folder):
    """Extract zip to output_folder. Returns list of extracted filenames."""
    os.makedirs(output_folder, exist_ok=True)
    dest = os.path.join(output_folder, zip_name)
    shutil.copy2(zip_path, dest)
    with zipfile.ZipFile(dest, 'r') as z:
        z.extractall(output_folder)
        extracted = z.namelist()
    print(f"Extracted {len(extracted)} files to: {output_folder}")
    os.remove(zip_path)  # clean up /tmp copy
    return extracted


# ── Main ───────────────────────────────────────────────────────────────────────
IMPORT_TO_QB = True   # set False to skip the AppleScript QB import step

def main():
    check_nas()
    username = get_credential("paychex", "username")
    webhook  = get_discord_webhook()

    script_dir    = os.path.dirname(os.path.abspath(__file__))
    iif_script    = os.path.join(script_dir, 'paychex_to_iif.py')
    as_script     = os.path.join(script_dir, 'import_iif.applescript')
    python3       = '/usr/local/bin/python3'

    payroll_date  = None
    output_folder = None

    try:
        payroll_date, zip_tmp, zip_name = run(username)
        output_folder = get_output_folder(payroll_date)

        if os.path.exists(output_folder) and any(
            f.endswith('.pdf') for f in os.listdir(output_folder)
        ):
            print(f"Already downloaded: {output_folder} — skipping.")
            os.remove(zip_tmp)
            return

        files = extract_zip(zip_tmp, zip_name, output_folder)

        # ── IIF generation ────────────────────────────────────────────────────
        print("\nGenerating IIF...")
        iif_result = subprocess.run(
            [python3, iif_script, output_folder, payroll_date.isoformat()],
            capture_output=True, text=True,
        )
        if iif_result.returncode != 0:
            raise RuntimeError(f"IIF generation failed:\n{iif_result.stderr.strip()}")
        print(iif_result.stdout.strip())
        iif_path = os.path.join(output_folder, f"payroll_{payroll_date.strftime('%m%d')}.iif")

        # ── QuickBooks import (optional) ──────────────────────────────────────
        if IMPORT_TO_QB:
            print("\nImporting IIF into QuickBooks...")
            # Copy IIF to a path with no spaces — QB's open command is finicky
            iif_tmp = f"/private/tmp/payroll_{payroll_date.strftime('%m%d')}.iif"
            shutil.copy2(iif_path, iif_tmp)
            as_result = subprocess.run(
                ['osascript', as_script, iif_tmp],
                capture_output=True, text=True,
            )
            os.remove(iif_tmp)
            if as_result.returncode != 0:
                raise RuntimeError(f"QB import failed:\n{as_result.stderr.strip()}")
            print("QuickBooks import complete.")

        # ── Log ───────────────────────────────────────────────────────────────
        write_log(output_folder, payroll_date, files)

        # ── Discord success ───────────────────────────────────────────────────
        totals    = parse_check_totals(files)
        total_sum = sum(totals)
        checks_str = ', '.join(f'${t:.2f}' for t in sorted(totals, reverse=True))
        qb_status  = 'QB imported' if IMPORT_TO_QB else 'IIF ready (QB import disabled)'
        msg = (
            f"✅ **Paychex Payroll — {payroll_date}**\n"
            f"Files: {len(files)} | {qb_status}\n"
            f"Folder: `{output_folder}`"
        )
        if totals:
            msg += f"\nChecks: {checks_str}\nNet pay total: ${total_sum:.2f}"
        send_discord(webhook, msg)

        print(f"\nDone → {output_folder}")

    except Exception as e:
        ts  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = (
            f"🚨 **Paychex Download FAILED**\n"
            f"Time: {ts}\n"
            f"Error: {type(e).__name__}: {e}"
        )
        send_discord(webhook, msg)
        if output_folder:
            write_log(output_folder, payroll_date, [], error=str(e))
        raise


if __name__ == '__main__':
    main()
