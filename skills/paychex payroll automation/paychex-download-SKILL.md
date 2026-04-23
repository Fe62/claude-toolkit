---
name: paychex-download
description: Automate Paychex Flex portal login, payroll zip download, extraction to correct DirectNAS QX folder. Use when running or scheduling weekly payroll downloads for Direct Lighting LLC.
---

# paychex-download Skill

Automates Paychex Flex portal login and payroll report download for Direct Lighting LLC. Downloads the weekly payroll zip and extracts it to the correct folder on DirectNAS.

---

## Prerequisites

```bash
pip install playwright
playwright install chromium
pip install keyring
```

Paychex credentials must be stored in macOS Keychain:
```bash
security add-generic-password -s "paychex" -a "username" -w "YOUR_USERNAME"
security add-generic-password -s "paychex-password" -a "password" -w "YOUR_PASSWORD"
```

DirectNAS must be mounted at `/Volumes/Public` before running.

---

## Folder Naming

**Format:** `Payroll.MMDD` where MMDD is the payroll date (e.g., `Payroll.0413` for April 13)

**QX logic:**
- Q1: January–March
- Q2: April–June  
- Q3: July–September
- Q4: October–December

**Full path:**
```
/Volumes/Public/Direct Lighting/Direct Lighting LLC/1.Direct.Payroll/1.Payrolls/26.Payrolls/QX/Payroll.MMDD/
```

---

## Script: `paychex_download.py`

```python
import subprocess, sys, os, zipfile, shutil
from datetime import date
from playwright.sync_api import sync_playwright

def get_credential(service, account):
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', service, '-a', account, '-w'],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def get_quarter(month):
    return (month - 1) // 3 + 1

def get_output_folder(payroll_date):
    nas_base = "/Volumes/Public/Direct Lighting/Direct Lighting LLC/1.Direct.Payroll/1.Payrolls/26.Payrolls"
    quarter = get_quarter(payroll_date.month)
    folder_name = f"Payroll.{payroll_date.strftime('%m%d')}"
    return os.path.join(nas_base, f"Q{quarter}", folder_name)

def check_nas():
    if not os.path.exists("/Volumes/Public"):
        print("ERROR: DirectNAS not mounted at /Volumes/Public. Aborting.")
        sys.exit(1)

def download_payroll(payroll_date=None):
    if payroll_date is None:
        payroll_date = date.today()

    check_nas()

    username = get_credential("paychex", "username")
    password = get_credential("paychex-password", "password")
    output_folder = get_output_folder(payroll_date)
    os.makedirs(output_folder, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # LOGIN
        # NOTE: Update selectors after mapping Paychex Flex portal
        page.goto("https://myapps.paychex.com/landing_remote/client.html#/login")
        page.fill('[name="username"]', username)  # verify selector
        page.fill('[name="password"]', password)  # verify selector
        page.click('[type="submit"]')             # verify selector
        page.wait_for_load_state("networkidle")

        # NAVIGATE TO REPORTS
        # TODO: Map exact nav path after first login
        # Expected: Reports → Payroll Reports → select pay period → Download All
        page.goto("https://myapps.paychex.com/...")  # TODO: fill after portal mapping

        # DOWNLOAD ZIP
        with page.expect_download() as download_info:
            page.click("...")  # TODO: Download All button selector
        download = download_info.value
        zip_path = os.path.join(output_folder, "payroll_download.zip")
        download.save_as(zip_path)

        browser.close()

    # EXTRACT ZIP
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(output_folder)

    print(f"Downloaded and extracted to: {output_folder}")
    return output_folder

if __name__ == "__main__":
    # Optional: pass date as YYYY-MM-DD argument
    if len(sys.argv) > 1:
        from datetime import datetime
        payroll_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        payroll_date = date.today()
    download_payroll(payroll_date)
```

---

## launchd Plist: `com.directlighting.paychex-download.plist`

Save to `~/Library/LaunchAgents/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.directlighting.paychex-download</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/paychex_download.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>2</integer>  <!-- 2 = Tuesday; payroll pulls from checking Tuesday -->
    <key>Hour</key>
    <integer>8</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/tmp/paychex-download.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/paychex-download.error.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.directlighting.paychex-download.plist
```

---

## Discord Notifications

Add to `paychex_download.py` — use existing Fe Trading webhook:

```python
import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/TOKEN"  # store in env or keychain

def notify_discord(message, is_error=False):
    emoji = "🚨" if is_error else "✅"
    requests.post(DISCORD_WEBHOOK, json={"content": f"{emoji} **Paychex Download** | {message}"})
```

Call on success:
```python
notify_discord(f"Download complete → {output_folder}")
```

Call on any exception:
```python
except Exception as e:
    notify_discord(f"FAILED: {str(e)}", is_error=True)
    raise
```

---
1. Log into Paychex Flex manually and map exact nav path to reports
2. Identify correct download selectors (use browser devtools)
3. Update `Weekday` in plist to actual payroll run day
4. Confirm zip contains: Payroll Journal, Cash Requirements, Direct Deposit, Retirement Plan Summary, and 401k CSV
5. Run once manually with a known payroll date to verify folder naming

---

## Known Issues / Watch Points
- Paychex Flex may require MFA — if so, headless will need a workaround (cookie session reuse or TOTP)
- Portal nav selectors will need to be mapped manually on first run
- DirectNAS mount path is case-sensitive on macOS Sequoia+; confirm exact volume name
