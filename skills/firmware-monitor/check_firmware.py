#!/usr/bin/env python3
"""
Direct Lighting — Firmware Update Monitor
Checks manufacturer pages for firmware updates and sends email alerts via Gmail SMTP.
Run via cron on the Direct Lighting iMac.
"""

import json
import hashlib
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re
import sys

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
STATE_FILE  = SCRIPT_DIR / "state.json"
CONFIG_FILE = SCRIPT_DIR / "manufacturers.json"
LOG_FILE    = SCRIPT_DIR / "firmware_monitor.log"

# ── Config (recipients, smtp, manufacturers all live in manufacturers.json) ────
_cfg      = json.loads((Path(__file__).parent / "manufacturers.json").read_text())
ALERT_EMAILS = _cfg["recipients"]
FROM_ADDRESS = _cfg["smtp"]["from"]
SMTP_USER    = _cfg["smtp"]["user"]
SMTP_PASS    = _cfg["smtp"]["pass"]

# ── State helpers ──────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_config() -> dict:
    return json.loads(CONFIG_FILE.read_text())

# ── HTTP fetch ─────────────────────────────────────────────────────────────────

def fetch_url(url: str, timeout: int = 20) -> requests.Response:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r

# ── Source-type checkers ───────────────────────────────────────────────────────

def check_static_html(mfr: dict) -> tuple[str, str]:
    """
    Fetch a static HTML page and return (fingerprint, detail_text).
    If version_pattern is set, extract the first match as the fingerprint.
    Otherwise, hash the visible text of the page (or a CSS selector subset).
    """
    r = fetch_url(mfr["url"])
    soup = BeautifulSoup(r.text, "html.parser")

    selector = mfr.get("selector")
    if selector:
        elements = soup.select(selector)
        content = " ".join(e.get_text(separator=" ", strip=True) for e in elements)
    else:
        content = soup.get_text(separator=" ", strip=True)

    pattern = mfr.get("version_pattern")
    if pattern:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # Use the first (latest) match as the fingerprint
            return matches[0], content[:500]

    # Fall back to MD5 of the content block
    fingerprint = hashlib.md5(content.encode()).hexdigest()
    return fingerprint, content[:500]


def check_itunes(mfr: dict) -> tuple[str, str]:
    """Return (version_string, release_notes) from iTunes lookup API."""
    r = fetch_url(f"https://itunes.apple.com/lookup?id={mfr['app_id']}")
    data = r.json()
    if not data.get("results"):
        raise ValueError("iTunes API returned no results")
    result = data["results"][0]
    version = result["version"]
    notes   = result.get("releaseNotes", "(no release notes)")[:300]
    return version, notes


def check_google_drive(mfr: dict) -> tuple[str, str]:
    """
    List files in a public Google Drive folder via Drive API v3.
    Returns (fingerprint, file_listing_text).
    Requires an API key with Drive API enabled.
    """
    api_key   = mfr["api_key"]
    folder_id = mfr["folder_id"]

    if api_key == "YOUR_GOOGLE_API_KEY_HERE":
        raise ValueError("Google API key not configured — edit manufacturers.json")

    url = (
        "https://www.googleapis.com/drive/v3/files"
        f"?q='{folder_id}'+in+parents"
        "&orderBy=modifiedTime+desc"
        "&pageSize=10"
        "&fields=files(name,modifiedTime,id)"
        f"&key={api_key}"
    )
    r = fetch_url(url)
    files = r.json().get("files", [])

    if not files:
        return "empty", "(no files found)"

    # Fingerprint: names + modification dates of all files
    fingerprint_str = "|".join(f"{f['name']}:{f['modifiedTime']}" for f in files)
    fingerprint = hashlib.md5(fingerprint_str.encode()).hexdigest()

    listing = "\n".join(
        f"  {f['name']}  (modified {f['modifiedTime'][:10]})" for f in files
    )
    return fingerprint, listing

# ── Email alert ────────────────────────────────────────────────────────────────

def send_alert(manufacturer: str, old_val: str, new_val: str, url: str, detail: str):
    subject = f"[Firmware Alert] {manufacturer} — update detected"
    body = (
        f"Firmware update detected for {manufacturer}\n"
        f"\n"
        f"Previous: {old_val}\n"
        f"Current:  {new_val}\n"
        f"\n"
        f"Check here: {url}\n"
        f"\n"
        f"--- Detail preview ---\n"
        f"{detail[:400]}\n"
        f"\n"
        f"— Direct Lighting firmware monitor\n"
        f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = FROM_ADDRESS
    msg["To"]      = ", ".join(ALERT_EMAILS)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.sendmail(SMTP_USER, ALERT_EMAILS, msg.as_string())
    except Exception as e:
        log(f"  WARNING — email failed: {e}")

# ── Logging ────────────────────────────────────────────────────────────────────

def log(msg: str):
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")

# ── Main check loop ────────────────────────────────────────────────────────────

def check_all() -> list[str]:
    config  = load_config()
    state   = load_state()
    changes = []

    for mfr in config["manufacturers"]:
        name = mfr["name"]

        if mfr.get("disabled"):
            log(f"  {name}: SKIPPED (disabled)")
            continue

        log(f"Checking {name} ...")

        try:
            mtype = mfr["type"]
            if mtype == "itunes":
                fingerprint, detail = check_itunes(mfr)
            elif mtype == "google_drive":
                fingerprint, detail = check_google_drive(mfr)
            elif mtype == "static_html":
                fingerprint, detail = check_static_html(mfr)
            else:
                log(f"  {name}: unknown type '{mtype}' — skipping")
                continue

            prev = state.get(name)

            if prev is None:
                log(f"  {name}: first run — recording '{fingerprint}'")
            elif prev != fingerprint:
                log(f"  {name}: CHANGED  {prev!r} → {fingerprint!r}")
                send_alert(name, prev, fingerprint, mfr["url"], detail)
                changes.append(name)
            else:
                log(f"  {name}: unchanged ({fingerprint})")

            state[name] = fingerprint

        except Exception as e:
            log(f"  {name}: ERROR — {e}")

    save_state(state)
    return changes


if __name__ == "__main__":
    log("=== Firmware Monitor started ===")
    changes = check_all()
    if changes:
        log(f"Alerts sent for: {', '.join(changes)}")
    else:
        log("No changes detected.")
    log("=== Done ===")
    sys.exit(0)
