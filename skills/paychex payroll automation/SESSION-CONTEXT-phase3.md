# Session Context: paychex-download Phase 3
**Date:** 2026-04-15
**Status:** COMPLETE — end-to-end tested and working.

---

## What Was Completed

Full pipeline runs via `launchctl start com.directlighting.paychex-download`:

1. **Download** — Playwright CDP connects to Brave, captures Bearer token via `page.on('request')` listener, calls Paychex API, downloads zip, extracts 16 PDFs to `Q{n}/Payroll.MMDD/`
2. **IIF generation** — `paychex_to_iif.py` parses PDFs, writes 3 QB Write Checks to `payroll_MMDD.iif`
3. **QB import** — `import_iif.applescript` uses `open -a 'QuickBooks 2024'` (shell, not file dialog), dismisses backup warning + confirmation dialogs
4. **Log** — `{Payroll.MMDD}/download.log` written per run
5. **Discord** — success notification with check totals; error notification on failure

**Last successful run:** 2026-04-15
- Invoice: $38.59 | DD: $3,117.53 | Tax: $1,065.31
- 16 PDFs + IIF → `Q2/Payroll.0415/`
- QB checks confirmed clean

---

## Files

| File | Path (relative to `~/Library/Mobile Documents/com~apple~CloudDocs/claude-toolkit/`) |
|------|------|
| Download + orchestrator | `skills/paychex payroll automation/paychex_download.py` |
| IIF generator | `skills/paychex payroll automation/paychex_to_iif.py` |
| QB import AppleScript | `skills/paychex payroll automation/import_iif.applescript` |
| launchd plist | `~/Library/LaunchAgents/com.directlighting.paychex-download.plist` |
| IIF skill doc | `skills/paychex payroll automation/paychex-to-iif-SKILL.md` |
| Download skill doc | `skills/paychex payroll automation/paychex-download-SKILL.md` |

**python3:** `/usr/local/bin/python3`
**Keychain — Paychex username:** `security find-generic-password -s "paychex" -a "username" -w`
**Keychain — Discord webhook:** `security find-generic-password -s "discord-webhook" -a "paychex-download" -w`

---

## Known Gotchas

| Issue | Fix |
|-------|-----|
| Paychex tab at `login.do` | Script exits with clear error. Log into dashboard before 8am Tuesday. |
| QB can't open IIF path with spaces | IIF copied to `/private/tmp/payroll_MMDD.iif` before AppleScript call |
| Discord 403 Cloudflare block | `User-Agent: paychex-download/1.0` required; default Python UA is blocked |
| Discord SSL on macOS Python | Uses `certifi` CA bundle via `ssl.create_default_context(cafile=certifi.where())` |
| QB backup warning dialog | AppleScript clicks "No" button; loops 4 times to catch all dialogs |
| XHR interceptor killed by navigation | Fixed: use Playwright `page.on('request')` instead of JS monkey-patch |

---

## Schedule

- **launchd label:** `com.directlighting.paychex-download`
- **Schedule:** Tuesday 8:00am (Weekday=2)
- **Manual trigger:** `launchctl start com.directlighting.paychex-download`
- **System log:** `~/Library/Logs/paychex-download.log`
- **Per-run log:** `{NAS}/Q{n}/Payroll.MMDD/download.log`

---

## Prerequisites for Tuesday Run

1. Brave running with `--remote-debugging-port=9222`
2. Paychex Flex tab logged in to dashboard (URL contains `landing_remote/html`, not `login.do`)
3. QuickBooks Desktop open
4. DirectNAS mounted at `/Volumes/Public`
