# Session Context: paychex-download skill
**Date:** 2026-04-14
**Status:** COMPLETE — end-to-end download working.

---

## What Works (as of 2026-04-14)

Full download pipeline is operational:

1. **CDP connection to Brave** ✅
2. **XHR interceptor captures OIDC Bearer token** ✅ — the key breakthrough
3. **loadPackageFolders** ✅ — 200 with Bearer token
4. **getDownloadFolderRequestURL** ✅ — 200 with Bearer token
5. **Playwright expect_download() zip handler** ✅
6. **Extract to NAS** ✅ — 16 files to `Q2/Payroll.0415`

---

## The Root Cause (resolved)

**The 401 mystery:** `reporting_remote` endpoints require `authorization: Bearer <JWT>` (OIDC access token). The `x-payx-sid` header is NOT the auth mechanism — it's a session correlation ID only. Apache/proxy-level 401 fires when the Bearer token is absent or invalid.

**Why we couldn't find the token:** It's held in Angular's in-memory auth service (AngularJS `$http` interceptor), not in localStorage, sessionStorage, cookies, or any window global.

**The fix:** Install an `XMLHttpRequest.setRequestHeader` interceptor via `page.evaluate()` BEFORE navigating to RPTCTR_HTML. Angular's own `getMostFrequentlyUsedReports` call on page load carries the Bearer token through XHR — we capture it from there and use it in our subsequent fetch calls.

---

## Key Architecture Facts

**Auth:** OIDC Bearer JWT (`authorization: Bearer eyJ...`) — required for all `reporting_remote` endpoints
- Token source: Angular in-memory (AngularJS `$http` interceptor)
- Token lifetime: ~30 minutes
- `x-payx-sid` is a landing session ID used for correlation only

**loadPackageFolders:** Never fires from Angular on hash re-navigation (cached). We call it ourselves using the captured Bearer token.

**Folder data structure (from HAR + confirmed live):**
```json
{"packageId":"1","caids":["00FWDQEWMMMARRL70TU6"],"name":null,"dateType":"CheckDate","ns":"com.paychex.reporting.dto.PackageFolderV2"}
```
`packageId` and `caids` are stable. Only `date` changes per payroll.

**URL structure:**
- Reports center: `#?mode=admin&app=RPTCTR_HTML&clients=00FWDQEWMMMARRL70TU6`
- Dashboard: `#?mode=admin&app=DASHBOARD_ADM&clients=00FWDQEWMMMARRL70TU6`
- Navigating via `window.location.href` (not `page.reload()` — that strips hash)

**Reports center tabs:** Overview (default), Report library, Labor cost
- `getMostFrequentlyUsedReports` fires on Overview load — this is what we wait for
- `loadPackageFolders` is NOT called by Angular on RPTCTR_HTML navigation

---

## What Doesn't Work in CDP Mode (still true, now irrelevant)

- `context.route()` — never intercepts
- `page.add_init_script()` — doesn't apply to existing pages
- `response.text()` in sync response handler — asyncio CancelledError
- Our own fetch WITHOUT Bearer token — Apache-level 401

---

## Phase 3 Remaining

- [ ] launchd plist (Tuesday 8am)
- [ ] Log file per run in output folder
- [ ] Discord webhook: error alert + success with check totals
- [ ] AppleScript: open QB Desktop, import IIF, close
- [ ] End-to-end test: download → IIF → QB import

---

## paychex-to-iif skill (Phase 2) — fully working

File: `skills/paychex payroll automation/paychex-to-iif-SKILL.md`
Tested against Payroll.0408. Outputs 3 Write Checks (Invoice, DD, Tax).
QB account format: name-only (no number prefix). Confirmed working in QB Desktop.
