# AI Hedge Fund Web UI — fepi41 Deployment

**Document status:** Complete
**Date started:** 2026-03-02
**Date completed:** 2026-03-03
**Owner:** Flint

---

## One-Line Goal

Deploy the ai-hedge-fund web application on fepi41 so it runs always-on and
is accessible from FeMacBook via browser over Tailscale.

---

## Background & Context

The ai-hedge-fund CLI is already installed and tested on fepi41 (Python 3.11.9
via pyenv, Anthropic API key in .env, test run confirmed 2026-03-01). The
upstream repo has since added a full web UI: a React/Vite frontend and
FastAPI/uvicorn backend. The goal is to complete that installation on fepi41
so the UI is always available without requiring FeMacBook to be awake or
running anything. FeMacBook accesses it via browser over Tailscale.

The frontend will be built into static files (not run as a dev server) and
served by the FastAPI backend — the correct approach for always-on use.

---

## Success Criteria

- [x] Node.js installed on fepi41
- [x] Backend dependencies installed (FastAPI, uvicorn, LangGraph)
- [x] Frontend built to static files
- [x] Backend configured to serve static frontend files
- [x] Backend and frontend listen on 0.0.0.0 (not localhost)
- [x] Both processes start automatically on fepi41 reboot (systemd service)
- [x] UI accessible from FeMacBook at http://100.72.119.28:8000
- [x] At least one agent run completed successfully through the UI
- [x] PRD closed, skills inventory and bible updated

---

## Scope

**In scope:**
- Node.js installation on fepi41 (ARM-compatible version)
- Backend dependency installation (app/backend)
- Frontend build (npm run build)
- FastAPI static file serving configuration
- Binding to 0.0.0.0 for Tailscale access
- systemd service for auto-start on reboot
- Firewall/port check (port 8000 open on fepi41)

**Out of scope:**
- Running a dev server (Vite dev mode) permanently — build only
- Exposing the UI to the public internet
- Any live brokerage connection
- Modifying agent logic or adding new agents
- Discord/Telegram notifications (not in main repo)
- brekpi41 setup

---

## Current State on fepi41

| Component | Status | Notes |
|---|---|---|
| Python 3.11.9 | ✓ Installed | Via pyenv, set local in project dir |
| ai-hedge-fund repo | ✓ Cloned | ~/ai-hedge-fund |
| CLI dependencies | ✓ Installed | requirements-core.txt via pip |
| .env with API key | ✓ Configured | Anthropic key, gitignored |
| CLI test run | ✓ Confirmed | 2026-03-01, AAPL, HOLD decision |
| Node.js | ✓ Installed | v20.19.2 LTS, aarch64, already present |
| FastAPI / uvicorn | ✓ Installed | fastapi 0.104.1, uvicorn 0.37.0 in pyenv 3.11.9 |
| LangGraph | ✓ Installed | langgraph 0.2.56 in pyenv 3.11.9 |
| systemd service | ✓ Configured | ai-hedge-fund.service, enabled, survives reboot |

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| fepi41 SSH access | ✓ Confirmed | flint@100.72.119.28 |
| Tailscale active | ✓ Confirmed | Both machines |
| Anthropic API key | ✓ Configured | In .env |
| Node.js (ARM) | ✓ Confirmed | v20.19.2 LTS, already installed |
| npm | ✓ Confirmed | 9.2.0, already installed |
| FastAPI + uvicorn | ✓ Confirmed | In pyenv 3.11.9 |
| Port 8000 open | ✓ Confirmed | Verified by successful FeMacBook curl |

---

## Constraints

- Never store API keys in any tracked file
- Do not modify Node-RED or irrigation config on fepi41
- No Poetry — use pip (Poetry hangs on Pi ARM, documented in bible)
- Build frontend to static files — do not run Vite dev server always-on
- All GitHub pushes deliberate

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| ARM-incompatible npm packages | Medium | Frontend is React/Vite — build deps only, not runtime. Lower risk than Python ARM issues. |
| Node.js version incompatibility | Low | Pin to LTS (Node 20). |
| Port 8000 blocked by ufw | Low | Check and open if needed. |
| Backend missing deps from ARM exclusions | Medium | Verify FastAPI + LangGraph install; may need additional exclusions. |
| Upstream repo changes break install | Low | Pin to current commit after confirmed working. |

---

## Plan

### Phase 1 — Backend web dependencies ✓ 2026-03-02
- [x] SSH into fepi41
- [x] Verify existing core deps include LangGraph (check pip list)
- [x] Install FastAPI, uvicorn: `pip install fastapi uvicorn`
- [x] Verify app/backend starts: `uvicorn main:app --reload` from app/backend
- [x] Confirm API responds at localhost:8000

### Phase 2 — Node.js and frontend build ✓ 2026-03-02
- [x] Install Node.js LTS on fepi41 (NodeSource ARM script or nvm)
      Note: Already installed — Node v20.19.2 LTS, npm 9.2.0, aarch64
- [x] Confirm: `node --version`, `npm --version`
- [x] `cd app/frontend && npm install` — 433 packages, exit 0
- [x] `npm run build` — upstream TypeScript errors bypassed; fixed one real bug
      (App.tsx case-sensitive import: `./components/layout` → `./components/Layout`);
      ran `npx vite build` directly to skip tsc type-check gate on upstream code
- [x] Confirm dist/ folder exists with index.html — dist/index.html + assets/ confirmed

### Phase 3 — Wire frontend into backend ✓ 2026-03-03
- [x] Configure FastAPI to serve dist/ as static files
      Changes: health.py GET / → GET /health (freed root for SPA);
      main.py: added StaticFiles import + Path-based dist mount at "/" with html=True, registered last
- [x] Change uvicorn bind from localhost to 0.0.0.0 (--host 0.0.0.0 --port 8000)
- [x] Test from fepi41 locally: curl localhost:8000 → returns index.html; /health → JSON; /language-models/ → API JSON
- [x] Test from FeMacBook browser: curl http://100.72.119.28:8000 → returns index.html ✓
      ufw: non-interactive sudo not available; port confirmed open by successful curl from FeMacBook

### Phase 4 — Always-on service ✓ 2026-03-03
- [x] Check ufw: port 8000 confirmed open (no rule blocking; ufw non-interactive sudo not available)
- [x] Write systemd service file for uvicorn
      File: /etc/systemd/system/ai-hedge-fund.service
      User=flint, WorkingDirectory=/home/flint/ai-hedge-fund,
      EnvironmentFile=/home/flint/ai-hedge-fund/.env, Restart=on-failure
      Note: flint has no passwordless sudo; file staged to ~/ai-hedge-fund.service, user ran sudo mv + enable + start
- [x] Enable and start service: systemctl enable + start — active (running) confirmed
- [x] Reboot fepi41, confirm UI comes back automatically — ✓ UI back at http://100.72.119.28:8000 post-reboot
- [x] Test from FeMacBook after reboot — ✓ confirmed

### Phase 5 — Validate and close ✓ 2026-03-03
- [x] Run at least one agent analysis through the UI — confirmed by user
- [x] Update skills-inventory.md — ai-hedge-fund entry updated with web UI, access URL, service, build notes
- [x] Write bible entry — added to master-reference.md: FastAPI+Vite on Pi, systemd patterns, key gotchas
- [x] Commit toolkit updates to GitHub — staged, committed and pushed by Flint
- [x] Mark PRD complete — Document status: Complete, Date completed: 2026-03-03

---

## Open Questions

- [x] Does LangGraph survive the ARM exclusions already in place, or does it need separate install?
      Answer: Already installed and working (langgraph 0.2.56 in pyenv 3.11.9). No ARM issues.
- [x] Does the app/backend have its own requirements.txt, or does it use the root pyproject.toml?
      Answer: No separate backend requirements.txt. Root requirements-core.txt covers everything.
- [x] Which port does FeMacBook browser use — 8000 (backend serves all) or 5173 (separate frontend)?
      Answer: 8000 only, once frontend is built and served by FastAPI.

---

## Outcomes & Lessons

- All phases completed across two sessions (2026-03-02 and 2026-03-03), plus post-close fixes 2026-03-03
- No ARM-incompatible packages encountered — all Python and Node deps installed cleanly
- Node.js v20.19.2 LTS was already on fepi41 — no install needed
- `npm run build` fails due to upstream TypeScript debt; `npx vite build` is the correct approach
- Case-sensitive import bug in upstream App.tsx: `./components/layout` → `./components/Layout`
- **Vite bakes API URLs at build time** — always use relative URLs (`''` not `'http://localhost:8000'`)
  as the default; otherwise API calls go to localhost on the *browser's* machine, not the server
- **StaticFiles mount at `"/"` blocks FastAPI's redirect_slashes** — the mount's partial-match
  priority intercepts requests before trailing-slash redirects can fire; replace with an explicit
  `@app.get("/{full_path:path}")` catch-all route instead
- **`index.html` must be served with `Cache-Control: no-store`** — without it, browsers cache
  the old index.html (referencing old asset hashes) and load stale JS after a rebuild
- Frontend root endpoint calls need trailing slashes: `/api-keys` → `/api-keys/`
- systemd EnvironmentFile is the right pattern for .env-based secrets
- flint has no passwordless sudo on fepi41; stage files as user, sudo mv from interactive session
- Always check `ss -tlnp` first — three separate incidents traced back to server not running

---

## Bible Entry

Copied to master-reference.md 2026-03-03. See section:
"Deploying FastAPI + Vite on Raspberry Pi (Always-On via Tailscale)"

---

## Skills Inventory Update

Updated 2026-03-03. Added to ai-hedge-fund entry: Web UI, Access URL, Service,
frontend build notes, service management commands.
