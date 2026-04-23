---
name: firmware-monitor
description: Monitor manufacturer websites for firmware updates and send alert emails. Use this skill when asked to check, run, update, configure, or troubleshoot the Direct Lighting firmware update monitor. Also triggers when adding a new manufacturer, investigating a missed alert, or suspecting a JS-rendering problem with ARRI or Aputure.
---

# Direct Lighting — Firmware Monitor Skill

Monitors 8 lighting manufacturer sources for firmware changes and sends email alerts to the Direct Lighting team.

## File locations

```
~/payroll/firmware-monitor/          ← install here, near payroll scripts
  check_firmware.py                  ← main script (run this)
  manufacturers.json                 ← config: one entry per source
  state.json                         ← auto-generated: last known fingerprints
  firmware_monitor.log               ← rolling log of all runs
  SKILL.md                           ← this file
  SETUP.md                           ← one-time setup instructions
```

---

## How it works

On each run, for each manufacturer:
1. Fetches the source (web page, iTunes API, or Google Drive API)
2. Extracts a **fingerprint** — either a version string (e.g. `V5.16.24`) or an MD5 hash of the page content
3. Compares against the last known fingerprint stored in `state.json`
4. If changed → sends email alert to all 4 recipients via `sendmail`
5. Updates `state.json` with the new fingerprint

On **first run**, no alerts are sent — it just records current state as baseline.

---

## Source types

### `static_html`
Plain HTTP fetch + BeautifulSoup. Works for Astera, Fiilex, Nanlux, Kino Flo.
- If `version_pattern` is set: extracts first regex match as fingerprint (more precise)
- If `null`: hashes the page text (catches any change, but noisier)

### `itunes`
Calls `https://itunes.apple.com/lookup?id=APP_ID` and uses the `version` field.
Used for Blackout (iPad app).

### `google_drive`
Calls Google Drive API v3 to list files in a public folder.
Fingerprints the combined `name:modifiedTime` of all files.
Used for Cerise (FTSLED) — requires API key in `manufacturers.json`.

---

## Manufacturer quick reference

| Name | Type | Notes |
|------|------|-------|
| Astera | static_html | `update.astera-led.com` — version string at top |
| Fiilex | static_html | `fiilex.com` — "LAST UPDATED" date extracted |
| Nanlux | static_html | `nanlux.com` — page hashed (no single version string) |
| Kino Flo | static_html | `kinoflo.com` — "True Match Firmware X.X" extracted |
| ARRI | static_html | ⚠️ May be JS-rendered — see Troubleshooting |
| Aputure | static_html | ⚠️ Shopify — may be JS-rendered — see Troubleshooting |
| Blackout | itunes | iTunes API — clean version string |
| Cerise (FTSLED) | google_drive | Google Drive folder — needs API key |

---

## Running manually

```bash
cd ~/payroll/firmware-monitor
python3 check_firmware.py
```

First run records baseline. Second run onward triggers alerts on changes.

---

## Cron setup (run daily at 8am)

```bash
crontab -e
```

Add:
```
0 8 * * * cd /Users/YOURUSERNAME/payroll/firmware-monitor && /usr/bin/python3 check_firmware.py >> firmware_monitor.log 2>&1
```

Replace `YOURUSERNAME` with your macOS username.

---

## Adding a new manufacturer

1. Open `manufacturers.json`
2. Add an entry to the `"manufacturers"` array:

```json
{
  "name": "NewBrand",
  "type": "static_html",
  "url": "https://newbrand.com/firmware",
  "selector": "body",
  "version_pattern": "Version ([\\d.]+)",
  "notes": "Optional notes"
}
```

3. Run `check_firmware.py` once to set baseline — no alert will fire.

To **disable** without deleting, add `"disabled": true` to the entry.

---

## Troubleshooting

### ARRI or Aputure never detect updates
These sites may be JavaScript-rendered, meaning `requests` gets the skeleton HTML
without the actual content. To verify:

```bash
python3 - <<'EOF'
import requests
from bs4 import BeautifulSoup
r = requests.get("https://www.arri.com/en/technical-service/firmware/firmware-updates-for-lighting-products",
    headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
print(soup.get_text()[:500])
EOF
```

If the output is nearly empty or contains no version numbers, install Playwright:

```bash
pip3 install playwright
playwright install chromium
```

Then update the affected entries in `manufacturers.json` to `"type": "playwright_html"`
and add the `check_playwright_html()` function to `check_firmware.py` — see the
Playwright upgrade section below.

### Playwright upgrade (when needed)

Add this function to `check_firmware.py`:

```python
def check_playwright_html(mfr: dict) -> tuple[str, str]:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(mfr["url"], wait_until="networkidle", timeout=30000)
        content = page.inner_text("body")
        browser.close()
    pattern = mfr.get("version_pattern")
    if pattern:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            return matches[0], content[:500]
    return hashlib.md5(content.encode()).hexdigest(), content[:500]
```

Change the affected entry's `"type"` to `"playwright_html"` and add a dispatch
branch in `check_all()`:

```python
elif mtype == "playwright_html":
    fingerprint, detail = check_playwright_html(mfr)
```

### Cerise Google Drive returns 403
The folder must be publicly shared ("Anyone with the link can view").
Also verify the API key has the Drive API enabled in Google Cloud Console.

### sendmail not delivering
Test with:
```bash
echo "Subject: test" | sendmail flint@directlighting.net
```
If it fails, check that Postfix is running: `sudo launchctl start org.postfix.master`
Or configure Postfix relay to use Gmail SMTP — see SETUP.md.

---

## Email recipients

Defined at the top of `check_firmware.py`:

```python
ALERT_EMAILS = [
    "flint@directlighting.net",
    "juan@directlighting.net",
    "ken@directlighting.net",
    "rickq89@gmail.com",
]
```

Edit that list to add or remove recipients.
