#!/usr/bin/env python3
"""
paychex_login.py — Ensure Paychex Flex is logged in ahead of the Tuesday 8am download.

Schedule: launchd Tuesday 7:45am (15 min before paychex_download.py)

Login flow (all cards are in the DOM simultaneously, SPA shows/hides them):
  username → password → [security question OR OTP method → OTP entry] → dashboard

Notes:
  - All button clicks use JS (.click()) to bypass Proton Pass extension overlay.
  - #login-password is type="password" on index.html?oac=... (the post-username-step URL).
  - OTP method selection auto-picks Text; user must enter the code manually.
  - Security question requires manual completion; Discord alert sent with question text.

Prerequisites:
  - Brave running with --remote-debugging-port=9222 (or not running — script will launch it)
  - security add-generic-password -s "paychex" -a "username" -w "YOUR_USERNAME"
  - security add-generic-password -s "paychex" -a "password" -w "YOUR_PASSWORD"
  - security add-generic-password -s "discord-webhook" -a "paychex-download" -w "WEBHOOK_URL"
"""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request as _urllib
import ssl as _ssl

from playwright.sync_api import sync_playwright

CDP_URL             = "http://localhost:9222"
PAYCHEX_LOGIN_URL   = "https://login.flex.paychex.com/login_static/UsernameOnly.html"
DASHBOARD_INDICATOR = "landing_remote"  # URL fragment; validated with DOM check
MANUAL_WAIT_SECONDS = 600   # 10 min — wait for user to handle MFA / security question


# ---------------------------------------------------------------------------
# Credentials + Discord
# ---------------------------------------------------------------------------

def get_credential(service, account):
    r = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True, text=True,
    )
    val = r.stdout.strip()
    if not val:
        raise RuntimeError(f"Keychain: not found — service={service!r} account={account!r}")
    return val


def get_discord_webhook():
    r = subprocess.run(
        ["security", "find-generic-password", "-s", "discord-webhook",
         "-a", "paychex-download", "-w"],
        capture_output=True, text=True,
    )
    url = r.stdout.strip().strip("\"'")
    return url if url.startswith("http") else None


def send_discord(webhook_url, message):
    if not webhook_url:
        return
    try:
        import certifi
        data = json.dumps({"content": message}).encode("utf-8")
        req = _urllib.Request(
            webhook_url, data=data,
            headers={"Content-Type": "application/json", "User-Agent": "paychex-download/1.0"},
        )
        ctx = _ssl.create_default_context(cafile=certifi.where())
        _urllib.urlopen(req, timeout=10, context=ctx)
    except Exception as e:
        print(f"Discord failed (non-fatal): {e}")


# ---------------------------------------------------------------------------
# Brave
# ---------------------------------------------------------------------------

def is_port_open(port=9222, timeout=2):
    try:
        with socket.create_connection(("localhost", port), timeout=timeout):
            return True
    except OSError:
        return False


def ensure_brave_debug_port():
    if is_port_open():
        print("Port 9222 open.")
        return True
    print("Port 9222 not open — launching Brave with --remote-debugging-port=9222...")
    subprocess.Popen([
        "open", "-a", "Brave Browser", "--args",
        "--remote-debugging-port=9222",
        "--no-first-run",
    ])
    for _ in range(30):
        time.sleep(0.5)
        if is_port_open():
            print("Brave launched, port 9222 open.")
            time.sleep(2)
            return True
    return False


# ---------------------------------------------------------------------------
# Login helpers
# ---------------------------------------------------------------------------

# JS snippet: check which login card is currently visible.
# Returns the card name or null.
_DETECT_CARD_JS = """() => {
    // Check password BEFORE username: after clicking Continue on the username card,
    // the SPA navigates to index.html?oac=... where both #login-username (shown as
    // context) and #login-password (active input) are visible simultaneously.
    // Password is hidden (w=0) on the initial username-only step, so order matters.
    const cards = [
        ['password',  document.getElementById('login-password')],
        ['username',  document.getElementById('login-username')],
        ['security',  document.getElementById('security-answer')],
        ['otpMethod', document.getElementById('otp-text')],
        ['otpEntry',  document.getElementById('one-time-password')],
    ];
    for (const [name, el] of cards) {
        if (el) {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && r.height > 0) return name;
        }
    }
    return null;
}"""


def _js_fill(page, element_id, value):
    """Set an input value via JS and trigger React/Angular change events."""
    page.evaluate(
        """([id, val]) => {
            const el = document.getElementById(id);
            if (!el) return;
            const nativeInput = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            nativeInput.set.call(el, val);
            el.dispatchEvent(new Event('input',  {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
        }""",
        [element_id, value],
    )


def _js_click(page, element_id):
    """Click a button via JS, bypassing Proton Pass extension overlay."""
    page.evaluate(f"document.getElementById('{element_id}').click()")


def get_visible_security_question(page):
    """Return the security question text from the visible card, or a fallback string."""
    return page.evaluate("""() => {
        const candidates = Array.from(document.querySelectorAll('p, label, h2, h3, span'));
        const visible = candidates.filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0
                && el.innerText.trim().length > 10
                && el.innerText.trim().length < 300;
        });
        // Look for something that resembles a question
        const q = visible.find(el => el.innerText.includes('?') || el.innerText.toLowerCase().includes('question'));
        return q ? q.innerText.trim() : (visible[0] ? visible[0].innerText.trim() : 'Security question (check Brave)');
    }""")


def get_ready_login_tab(ctx):
    """
    Return a tab ready for the login flow:
    1. Tab already at dashboard → return it (already done)
    2. Tab at login.flex.paychex.com → navigate within same domain to UsernameOnly.html
    3. No suitable tab → open a fresh one

    Deliberately avoids cross-origin goto (myapps → login.flex) which kills the CDP
    connection on attached browsers.
    """
    # 1. Dashboard already open (validate with DOM — URL alone isn't sufficient)
    for pg in ctx.pages:
        if is_dashboard_tab(pg):
            print(f"Dashboard tab found: {pg.url[:80]}")
            return pg

    # 2. Already on the login subdomain (same-domain navigation is safe)
    login_tab = next((pg for pg in ctx.pages if "login.flex.paychex.com" in pg.url), None)
    if login_tab:
        if "UsernameOnly.html" not in login_tab.url:
            print(f"login.flex tab at root — navigating to UsernameOnly.html")
            login_tab.goto(PAYCHEX_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
        else:
            print(f"login.flex tab at UsernameOnly.html — ready")
        return login_tab

    # 3. Open a brand new tab
    print("No suitable login tab — opening new one.")
    pg = ctx.new_page()
    pg.goto(PAYCHEX_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    return pg


# ---------------------------------------------------------------------------
# Main login loop
# ---------------------------------------------------------------------------

def is_dashboard_tab(pg):
    """
    Return True if this tab is showing the authenticated Paychex dashboard.

    After OIDC login, the dashboard lives at myapps.paychex.com/landing_remote/login.do
    (NOT landing_remote/html as one might expect). We disambiguate dashboard from
    security-question / MFA by checking that no form inputs are visible.
    """
    if DASHBOARD_INDICATOR not in pg.url:
        return False
    try:
        n = pg.evaluate("""() =>
            Array.from(document.querySelectorAll('input')).filter(i => {
                const r = i.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            }).length
        """)
        return n == 0
    except Exception:
        return False


def check_all_tabs_for_dashboard(ctx):
    """Return any tab that's reached the dashboard, or None."""
    for pg in ctx.pages:
        if is_dashboard_tab(pg):
            return pg
    return None


def run_login(page, username, password, webhook):
    """
    Complete the Paychex login flow.

    The flow has two distinct phases:
      Phase 1 — login.flex.paychex.com SPA cards (username → password)
                 All button clicks use JS to bypass Proton Pass overlay.
      Phase 2 — post-auth redirect (landing_remote/login.do or dashboard)
                 Watch the current page and ALL tabs for the dashboard.
                 Alert via Discord if security question or OTP appears.

    Returns True if any tab reaches the dashboard within MANUAL_WAIT_SECONDS.
    """
    ctx                   = page.context
    deadline              = time.time() + MANUAL_WAIT_SECONDS
    credentials_submitted = False
    otp_alerted           = False
    secq_alerted          = False

    while time.time() < deadline:

        # ── Check ALL tabs for dashboard ───────────────────────────────────
        if check_all_tabs_for_dashboard(ctx):
            return True

        # ── Phase 2: post-auth monitoring across ALL tabs ────────────────────
        if credentials_submitted:
            # After password submission, the login.flex `page` URL is stale —
            # the cross-domain OIDC redirect (login.flex → myapps.paychex.com)
            # breaks CDP URL tracking on the original page object.
            # Instead, scan ctx.pages directly for the landing_remote tab.

            landing_pages = [pg for pg in ctx.pages if DASHBOARD_INDICATOR in pg.url]

            if not landing_pages:
                print("  waiting for landing_remote redirect...")
                time.sleep(3)
                continue

            # Use the first landing_remote tab
            landing = landing_pages[0]
            url = landing.url
            print(f"  post-auth tab: {url[-60:]!r}")

            try:
                visible_inputs = landing.evaluate("""() =>
                    Array.from(document.querySelectorAll('input')).filter(i => {
                        const r = i.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }).length
                """)

                if visible_inputs == 0:
                    # No form inputs → dashboard is showing
                    return True

                # Has inputs → security question or OTP challenge
                inputs = landing.evaluate("""() =>
                    Array.from(document.querySelectorAll('input')).filter(i => {
                        const r = i.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }).map(i => ({id:i.id, name:i.name, type:i.type}))
                """)
                is_secq = any(
                    "security" in (i.get("id","") + i.get("name","")).lower()
                    for i in inputs
                )
                is_otp = any(
                    any(k in (i.get("id","") + i.get("name","")).lower()
                        for k in ("otp","code","factor","verify"))
                    for i in inputs
                )
                if is_secq and not secq_alerted:
                    q_text = get_visible_security_question(landing)
                    print(f"  Security question: {q_text!r}")
                    send_discord(webhook,
                        f"⚠️ **Paychex — Security Question**\n{q_text}\n"
                        f"Answer and click Continue in Brave before 8:00am."
                    )
                    secq_alerted = True
                elif is_otp and not otp_alerted:
                    print("  OTP required.")
                    send_discord(webhook,
                        "⚠️ **Paychex — OTP Required**\n"
                        "Verification code sent. Enter it in Brave before 8:00am."
                    )
                    otp_alerted = True

            except Exception:
                pass  # page still loading

            time.sleep(3)
            continue

        # ── Phase 1: login.flex SPA card handling ─────────────────────────
        try:
            card = page.evaluate(_DETECT_CARD_JS)
        except Exception as e:
            if "context was destroyed" in str(e) or "navigation" in str(e).lower():
                print("  Page navigating — waiting to settle...")
                time.sleep(3)
                try:
                    page.wait_for_load_state("load", timeout=15000)
                except Exception:
                    pass
                time.sleep(2)
                # After navigation, credentials may have been submitted if we
                # left login.flex — check URL to decide which phase we're in
                if "login.flex.paychex.com" not in page.url:
                    credentials_submitted = True
                continue
            raise

        print(f"  card={card!r}  url={page.url[-50:]!r}")

        if card == "username":
            _js_fill(page, "login-username", username)
            time.sleep(1.0)
            _js_click(page, "login-button")
            time.sleep(3)

        elif card == "password":
            _js_fill(page, "login-password", password)
            time.sleep(0.5)
            _js_click(page, "login-button")
            time.sleep(5)
            # Password submitted — next iteration will detect navigation
            credentials_submitted = True

        elif card == "otpMethod":
            print("  OTP delivery method — selecting Text.")
            page.evaluate("document.getElementById('otp-text').click()")
            time.sleep(0.5)
            _js_click(page, "login-button")
            time.sleep(3)

        elif card == "otpEntry" and not otp_alerted:
            print("  OTP entry card — sending Discord alert.")
            send_discord(webhook,
                "⚠️ **Paychex — OTP Required**\n"
                "Verification code sent to your phone. Enter it in Brave before 8:00am."
            )
            otp_alerted = True

        elif card == "security" and not secq_alerted:
            q_text = get_visible_security_question(page)
            print(f"  Security question: {q_text!r}")
            send_discord(webhook,
                f"⚠️ **Paychex — Security Question**\n{q_text}\n"
                f"Answer and click Continue in Brave before 8:00am."
            )
            secq_alerted = True

        time.sleep(2)

    return bool(check_all_tabs_for_dashboard(ctx))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    webhook = get_discord_webhook()

    try:
        username = get_credential("paychex", "username")
        password = get_credential("paychex", "password")
    except RuntimeError as e:
        send_discord(webhook, f"🚨 **Paychex Login** — Keychain error: {e}")
        sys.exit(1)

    if not ensure_brave_debug_port():
        send_discord(webhook,
            "🚨 **Paychex Login** — Brave debug port 9222 not open.\n"
            "Quit and relaunch Brave with `--remote-debugging-port=9222`, "
            "then log in manually before 8:00am."
        )
        sys.exit(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            ctx     = browser.contexts[0]
            page    = get_ready_login_tab(ctx)

            if is_dashboard_tab(page):
                print("Session already active.")
                send_discord(webhook,
                    "✅ **Paychex** — Session already active. Download runs at 8:00am."
                )
                browser.close()
                return

            print("Starting login flow...")
            success = run_login(page, username, password, webhook)

            if success:
                print(f"Logged in — dashboard: {page.url[:80]}")
                send_discord(webhook,
                    "✅ **Paychex** — Logged in successfully. Download runs at 8:00am."
                )
            else:
                raise RuntimeError(
                    f"Dashboard not reached within time limit. "
                    f"Final URL: {page.url}"
                )

            browser.close()

    except Exception as e:
        send_discord(webhook,
            f"🚨 **Paychex Login FAILED**\n"
            f"`{type(e).__name__}: {e}`\n"
            f"Log in manually before 8:00am."
        )
        raise


if __name__ == "__main__":
    main()
