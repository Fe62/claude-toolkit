# Master Reference — Claude Toolkit Bible

Last updated: 2026-03-26

---

## Purpose

This is the living manual for how Flint uses Claude Code. It captures 
skills developed, conventions established, lessons learned, and 
decisions made. Updated at the completion of every project via the 
Bible Entry section of each project file.

This document is also the first thing to paste into Claude Code as 
context when starting a new session on a new machine or project.

---



---

## Working Environment

| Item | Detail |
|---|---|
| Primary machine | MacBook Pro M1 |
| Secondary machine | direct-lighting (terminal only, transitional) |
| Claude Code | Installed on both |
| Working copy | iCloud Drive |
| Version control | GitHub (private, push deliberately) |
| File format | Plain markdown (.md) throughout |
| Naming convention | topic-YYYY-MM |

---

## Toolkit Structure

See README.md for full folder structure. Key locations:

- `/projects` — all PRDs and plans, one file per project
- `/skills-registry/skills-inventory.md` — every skill, its source and status
- `/prompts` — reusable prompt templates
- `/subagents` — specialist agent definitions
- `/claude-md-templates` — CLAUDE.md starters for new projects

---

## Skills Summary

_Populated as skills are built or adapted. One entry per skill._

### last30days (borrowed)
Research agent that searches internet, Reddit, and other sources for 
information from the last 30 days. Useful for staying current on Claude 
Code techniques, trends, and any time-sensitive query. Installed at 
~/.claude/skills/last30days. Requires OpenAI API key. Source: 
github.com/mvanhorn/last30days-skill. Candidate for adaptation into 
owned version.

### api-key-prompt (to be rebuilt)
Prompts for API key entry at runtime. Prevents keys from being stored 
in plain text. Required dependency for last30days and any future 
API-dependent skill. Originally built, currently on iMac — recovery 
and rebuild is early priority.

## QBO Import — QB Desktop Mac
- Format: OFX 1.x SGML only (not XML/OFX 2.x)
- Required: <INTU.BID>3000</INTU.BID> — Wells Fargo Intuit bank ID
- Required: <LEDGERBAL> block with ending balance and as-of date
- .qbo files may not download from Claude.ai — save as .txt and rename
- WF Signify format: "Transaction Details" section, no card prefix
- WF Signature/FA format: Payments/Credits/Purchases sections, 4-digit card prefix per line

### pdf-to-qbo (built)
Local Python script that converts Wells Fargo PDF bank and credit card statements
to QBO format for QB Desktop Mac import. Handles two CC statement layouts:
WF Signify (Format A) and WF Signature/FA (Format B). Installed at
skills/pdf-to-qbo/convert_statements.py. Requires pdfplumber.

### quickbooks-automation (retired)
Superseded by pdf-to-qbo (2026-02-28). The pdf-to-qbo skill handles
the WF statement import workflow that was originally planned here.

---

## Conventions Established

_Decisions we've made that future-me should know about._

### 2026-02-23 — Initial conventions
- File naming: topic-YYYY-MM
- PRDs and Plans live in single combined file in /projects
- Changelog lives at root, bible entry at end of every project file
- Skills have three statuses: borrowed / adapted / built
- GitHub pushes are deliberate, not automatic
- iCloud selective sync strategy to be handled as separate mini-project

### 2026-02-24 — Skill shortcut convention
When building a new skill, ask: does this warrant a terminal alias and/or
keyboard shortcut? If the skill will be run frequently or at the start of
sessions, add an alias to ~/.zshrc and consider an Automator Quick Action
for a keyboard shortcut. Document both in the skill's README.

### 2026-03-02 — Slash command design: interactive flows beat single prompts
When a skill requires gathering information before making changes, use a sequential
question flow with confirmation at each step rather than a single summary prompt.
Gaps and corrections surface earlier and updates are more accurate.

### 2026-03-02 — Register skill file and inventory entry together
When creating a new slash command, add its skills-inventory.md entry in the same
session. Don't leave skills undocumented — the registry becomes unreliable.

### 2026-02-24 — load-context maintenance convention
When any skill is completed or retired, update load-context.sh before
the final commit. Two sections to touch:
- Active Skills — add new skill with one-line description, alias, and shortcut if any
- Recent Completions — add one line summarizing what was done and when
Treat load-context.sh as a living document, not a snapshot.
---

## Raspberry Pi / ARM Python Installs

### pyenv on Raspberry Pi
Install build dependencies BEFORE running `pyenv install` or compiled Python will be missing modules:
```
sudo apt install libbz2-dev libncurses-dev libffi-dev libreadline-dev libsqlite3-dev liblzma-dev
```
Set local Python version with `pyenv local X.X.X` — leaves global unchanged.

### Poetry on ARM — Do Not Use
Poetry install hangs indefinitely on Raspberry Pi ARM. Workaround:
1. Parse poetry.lock with a toml script to generate requirements-core.txt
2. Install with pip instead
Note: Poetry 2.x also removed the `export` command — the workaround is required regardless.

### ARM-Incompatible Packages
Exclude these when installing Python AI/data stacks on ARM:
`contourpy`, `matplotlib`, `pillow`, `tiktoken`

### System Deps to Pre-Install Before pip
```
sudo apt install libjpeg-dev zlib1g-dev libpng-dev rustc cargo
```

---

## Deploying FastAPI + Vite on Raspberry Pi (Always-On via Tailscale)

_Completed 2026-03-03. Source: ai-hedge-fund-ui-2026-03.md._

### Architecture
Build the Vite frontend to static files once; serve them from the FastAPI backend using
a `/{full_path:path}` catch-all route (not `app.mount("/", StaticFiles(...))`).
One process, one port, no dev server running permanently.

### Frontend Build
```bash
cd app/frontend
npm install
npx vite build          # NOT npm run build — upstream TS errors fail the tsc gate
```
- `npm run build` runs `tsc && vite build`. If upstream code has TypeScript errors, the
  whole build fails. `npx vite build` skips tsc — Vite transpiles TS itself. Use this
  for repos you don't fully own.
- Linux filesystems are case-sensitive. Imports that work on macOS may fail on Pi.
  Watch for errors like `Cannot find module './components/layout'` when the file is
  `Layout.tsx`. Fix the import, don't rename the file.

### Wiring dist/ into FastAPI
```python
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ... all routes and include_router() calls above this line ...

_dist_dir = Path(__file__).parent.parent / "frontend" / "dist"

if _dist_dir.exists():
    # Hashed assets: browsers may cache these (filename changes when content changes)
    app.mount("/assets", StaticFiles(directory=str(_dist_dir / "assets")), name="assets")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(str(_dist_dir / "favicon.ico"))

    # SPA catch-all: must be last — all API routes registered above take priority.
    # Serves index.html with no-store so browsers always re-fetch it.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = _dist_dir / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(
            str(_dist_dir / "index.html"),
            headers={"Cache-Control": "no-store"},
        )
```
- **Do NOT use `app.mount("/", StaticFiles(..., html=True))`** — Mount objects use partial-match
  priority and intercept before FastAPI's `redirect_slashes` can fire, causing trailing-slash
  routes to return 404 instead of redirecting. Use the catch-all route above instead.
- Use `Path(__file__)` not a relative path — safe regardless of working directory
- If any existing route uses `GET /`, rename it (e.g. `/health`) before adding the catch-all.
- Mount `/assets` separately for hashed asset files — these are safe to cache in the browser.

### systemd Service
```ini
[Unit]
Description=AI Hedge Fund Web UI
After=network.target

[Service]
Type=simple
User=flint
WorkingDirectory=/home/flint/ai-hedge-fund
EnvironmentFile=/home/flint/ai-hedge-fund/.env
ExecStart=/home/flint/.pyenv/versions/3.11.9/bin/python -m uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```
- `EnvironmentFile` loads `.env` key=value pairs directly — no export prefix needed.
  systemd ignores `#` comment lines.
- `WorkingDirectory` must be the repo root when the app uses package-level imports
  (`from app.backend.routes import ...`).
- Use absolute path to pyenv Python in `ExecStart`.
- flint has no passwordless sudo on fepi41. Stage the file as the user, then run
  `sudo mv ~/service-name.service /etc/systemd/system/` from an interactive session.

### Enabling and Starting
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-hedge-fund
sudo systemctl start ai-hedge-fund
sudo systemctl status ai-hedge-fund   # confirm active (running)
sudo reboot                            # confirm it survives reboot
```

### Key Gotchas
- Always bind uvicorn to `--host 0.0.0.0` — `127.0.0.1` is unreachable from other machines
  even on Tailscale.
- Kill any manually-started uvicorn process before starting the systemd service —
  port 8000 conflict will silently prevent the service from binding.
- **Vite bakes `VITE_API_URL` at build time.** If unset, your default fallback is embedded in the
  JS bundle. Always use `''` (empty string / relative URL) as the fallback — never `http://localhost:8000`.
  When the frontend is served by the same backend, relative URLs route correctly and no CORS config is needed.

---

## Discord Webhooks for Scheduled Delivery (fepi41)

_Completed 2026-03-04. Source: ai-hedge-fund comms project._

### Why webhooks, not a bot
For scheduled one-way posting (briefings, alerts, snapshots), Discord webhooks are the correct tool.
Simple HTTP POST, no persistent process, no ARM compatibility issues. Bots add complexity only
needed for interactive/bidirectional communication.

### Cloudflare User-Agent requirement
Python's default User-Agent (`python-urllib/3.x` or `python-requests/x.x`) triggers Cloudflare
error 1010 (bot detection) on discord.com. Always set:
```python
headers={
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (https://github.com/Fe62/claude-toolkit, 1.0)"
}
```
Without this, all webhook POSTs return 403 Forbidden. Applies to both `urllib.request` and `requests`.

### Use discord.com, not discordapp.com
The legacy `discordapp.com` domain returns 403. Always use `discord.com`.

### Webhook URL security
Treat webhook URLs exactly like API keys:
- Store in `~/.hedge-fund-discord.env`, `chmod 600`, never git
- Load with `set -a; source ~/.hedge-fund-discord.env; set +a`
- Regenerate immediately if exposed in chat or logs

### Node.js on armhf — use nvm, not NodeSource
NodeSource dropped armhf (32-bit ARM) support. Installing via NodeSource returns
"Unsupported architecture: armhf". Fix:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 22
```

### yfinance on ARM
yfinance 1.2.0 fails on armhf — pulls in `curl_cffi` which has no armhf prebuilt and
fails to compile from source. Pin to last working version:
```bash
pip install "yfinance==0.2.54"
```

### yfinance batch download over per-ticker loop
Calling `yf.Ticker(ticker).fast_info` in a loop triggers rate limits. Use batch download:
```python
data = yf.download(" ".join(tickers), period="2d", progress=False, auto_adjust=True)
prices = data["Close"].iloc[-1]
prev_prices = data["Close"].iloc[-2]
```

---

## Tailscale

### Tailscale CLI on macOS
The Tailscale CLI is not on the shell PATH by default on macOS.
Full path: `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
Example: `/Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4 hostname`

## SSH Remotes (Claude Code)

### macOS hosts cannot be SSH remotes
Claude Code SSH remotes are Linux-only. macOS machines (including iMac/direct-lighting)
cannot be added as SSH remotes regardless of SSH connectivity. Use terminal SSH directly
for those machines — do not attempt to add them in Claude Code.

### SSH key auth before adding remotes
Always run `ssh-copy-id user@host` before adding a remote to Claude Code.
Password-based remotes prompt every session — key auth is required for friction-free use.

---



---

## Lessons Learned

_Hard-won insights. Updated as projects complete._

### 2026-02-23 — API key security
Never paste API keys into any conversation, file, or shared document. 
Keys should only exist in environment variables or be entered at 
runtime via prompt. If a key is accidentally exposed, revoke it 
immediately at the provider's API dashboard before doing anything else.

### 2026-03-01 — Raspberry Pi Python environment
Poetry hangs indefinitely on ARM — never use it. Use a toml script to extract requirements from poetry.lock and install with pip. Always install pyenv build deps before compiling Python. fepi41 has 8GB RAM — well-resourced for API-based workloads.

### 2026-03-01 — Tailscale CLI on macOS
Not on shell PATH. Always use full path: `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.

### 2026-03-02 — Claude Code SSH remotes are Linux-only
macOS hosts cannot be added as SSH remotes in Claude Code. Use terminal SSH directly
for macOS machines. For Linux remotes, run ssh-copy-id first — password-based remotes
add friction every session.

### 2026-03-02 — Document machine usernames explicitly
Usernames are not consistent across machines (brekpi41 uses `flint`, direct-lighting uses
`directlightingllc`). Always document the username in the machine inventory. Never assume.

### 2026-03-03 — FastAPI + Vite SPA deployment on Pi
`npm run build` fails on upstream TS errors; `npx vite build` bypasses tsc cleanly.
Linux case-sensitive imports will surface bugs that macOS dev masked.
Use `Path(__file__)` not CWD-relative paths.

### 2026-03-03 — Vite bakes API URLs into the JS bundle
`import.meta.env.VITE_API_URL` is resolved at build time, not runtime. If the env var is
not set, whatever the fallback string is (e.g. `http://localhost:8000`) gets embedded
permanently in the compiled JS. When that JS runs in a browser on a different machine,
all API calls go to localhost on the *browser's* machine. Always default to `''` (empty
string) so API calls are relative to wherever the page is served from.

### 2026-03-03 — Do not use app.mount("/", StaticFiles(...)) for SPA serving
`app.mount()` creates a Mount object that uses partial-match routing. A mount at `"/"`
matches every path before FastAPI's `redirect_slashes` mechanism can fire, so routes like
`GET /api-keys` (which the router would redirect to `/api-keys/`) return 404 instead.
Fix: replace the mount with an explicit `@app.get("/{full_path:path}")` catch-all Route.
Route objects do full matching and don't block redirect_slashes. Register it last.

### 2026-03-03 — Always serve index.html with Cache-Control: no-store
After a Vite rebuild, asset filenames change (content-hashed). If the browser has cached
the old index.html, it will reference the old (now deleted) JS filename and fail silently.
The catch-all route must set `headers={"Cache-Control": "no-store"}` on index.html
responses. Hashed asset files under /assets/ are safe to cache (filename changes = cache bust).

### 2026-03-03 — systemd EnvironmentFile for .env
systemd's EnvironmentFile directive reads key=value pairs directly from a .env file.
No export prefixes needed. Comment lines (#) are ignored. Cleaner than baking env
vars into the service file or wrapper script.

### 2026-03-04 — NodeSource dropped armhf; use nvm on 32-bit ARM
NodeSource v22+ does not support armhf (armv7l). Use nvm to install Node.js on Raspberry Pi with 32-bit userland.

### 2026-03-04 — Discord webhooks require DiscordBot User-Agent
Python's default User-Agent triggers Cloudflare 1010 on discord.com. Always set `User-Agent: DiscordBot (url, version)` or webhook POSTs return 403. Also: use discord.com, not discordapp.com.

### 2026-03-04 — yfinance 1.2.0 breaks on armhf; pin to 0.2.54
curl_cffi (a 1.2.0 dependency) has no armhf prebuilt and fails to compile. Pin yfinance to 0.2.54 on ARM.

### 2026-03-04 — yfinance batch download avoids rate limits
Calling fast_info per ticker in a loop triggers rate limits. Use `yf.download()` for multi-ticker data fetches.

### 2026-03-05 — watchlist.json is the single source of truth for portfolio-tracker
No script changes needed when holdings change — edit watchlist.json only. Recalculate weights to sum to 100% after any add/remove. Mutual funds (e.g. JACTX) have no intraday price data in yfinance — exclude them. Guard against NaN prices with `math.isnan()` before accumulating totals, or one bad ticker poisons all portfolio math.

### 2026-03-06 — Shell variables with spaces in paths fail silently on macOS
Setting `VAULT=~/Library/Mobile\ Documents/...` and then using `"$VAULT/subfolder"` in the
same shell block produces empty expansions — the variable appears set but mkdir receives
a blank prefix and tries to create `/subfolder` at root (read-only on macOS). Fix: use the
explicit full path with double-quotes throughout, e.g. `"/Users/Flint/Library/Mobile Documents/..."`.
Alternatively, assign with `$HOME`: `VAULT="$HOME/Library/Mobile Documents/..."` works if
`$HOME` is set, but verify before relying on it in non-interactive shells.

### 2026-03-06 — README in every vault folder serves dual purpose
A README.md in each folder is visible as a note in Obsidian and readable by agents before
they act. Include: folder purpose, what lives here, and explicit agent permissions (read/write/delete).
This pattern makes agent scope self-documenting and prevents accidental cross-folder writes.

### 2026-03-05 — yfinance rate limits on repeated manual runs
Running portfolio-tracker.sh multiple times in a session triggers `YFRateLimitError`. The scheduled cron job (once daily) is fine; ad-hoc reruns in the same hour are not. Wait 15–30 minutes between manual test runs.

### 2026-03-04 — virattt CLI requires --analysts-all for non-interactive scripting
Without `--analysts-all`, the upstream script prompts interactively and can't be run from cron or shell wrappers.

### 2026-03-03 — Kill orphan processes before starting systemd service
If uvicorn was started manually for testing, kill it before enabling the systemd service.
A process already bound to port 8000 will silently prevent systemd from binding —
the service may show `active (running)` while the old process is actually serving traffic.

### 2026-02-28 — QB Desktop Mac QBO import requirements
QB Desktop Mac requires OFX 1.x SGML format — XML-based OFX 2.x is rejected silently.
Wells Fargo has at least two distinct CC statement layouts requiring separate parsers.
When QBO files won't download from Claude.ai, save as .txt and manually rename to .qbo.

### 2026-03-12 — shutil.copy2 preserves file metadata in migrations
`shutil.copy2` copies both file content and metadata (creation/modified dates). Prefer it
over `shutil.copy` for any file migration where timestamp preservation matters.

### 2026-03-12 — DRY_RUN = True as default in migration scripts
Set `DRY_RUN = True` at the top of any migration script. This makes it safe to run and review
before committing actual file moves. Flip to False only when dry run output looks correct.

### 2026-03-12 — Underscore prefix sorts to top in Finder for human-attention folders
Name folders requiring human review with a leading underscore (e.g. `_review/`). On macOS,
underscore sorts before letters — these folders appear at the top of Finder, a natural
visual signal that human attention is needed.

### 2026-03-14 — Pi localhost resolves IPv6 first; use 127.0.0.1 explicitly
On Raspberry Pi, `localhost` resolves to `::1` (IPv6) before `127.0.0.1` (IPv4). Services that
bind IPv4-only (e.g. Node-RED default config) will refuse connections. Always use `127.0.0.1`
not `localhost` in URLs on the Pi — this applies to n8n HTTP request nodes, curl, and any
service-to-service communication.

### 2026-03-14 — n8n on aarch64 with Node 20: install in two steps
n8n 2.x requires Node ≥22. Use n8n 1.x (1.123.25) for Node 20 compatibility.
isolated-vm (a dev dependency) fails to build from source on aarch64 with Node 20. Fix:
```bash
npm config set prefix ~/.local
npm install -g n8n@1.123.25 --ignore-scripts   # skip native module builds
cd ~/.local/lib/node_modules/n8n
npm rebuild sqlite3                              # sqlite3 must be built; n8n won't start without it
```
Do NOT rebuild isolated-vm — it's not required at runtime.

### 2026-03-14 — systemd user services require loginctl enable-linger
User-level systemd services (`systemctl --user`) stop when the user's session ends (SSH logout).
To make them persist after logout (survive reboots, run headlessly):
```bash
loginctl enable-linger flint
```
Without this, the service disappears the moment the SSH session closes.
Use `WantedBy=default.target` (not `multi-user.target`) in the `[Install]` section of user services.

### 2026-03-14 — n8n API: strip active and tags from workflow POST body
POST /api/v1/workflows rejects requests that include `active` or `tags` fields — both are
read-only on creation. Strip them from the body before posting. Activate separately:
```bash
PUT /api/v1/workflows/{id}/activate
```

### 2026-03-14 — n8n static workflow data for stateful dedup
`$getWorkflowStaticData('global')` returns a persistent object that survives between workflow
executions. Use it to track state transitions (e.g. device online→offline) without an external
database. Reliable for dedup logic where you only want to alert on state *changes*, not every poll.

### 2026-03-14 — Email formatting: use \r\n and ASCII separators
Some email clients (including Apple Mail) don't render `\n`-only line breaks in plain-text emails,
and Unicode box/line characters (─, │) display as garbage. For reliable cross-client rendering:
- Use `\r\n` for line breaks in email body strings
- Use plain ASCII `---` as section separators

### 2026-03-23 — n8n v2 webhook nodes require a webhookId UUID
Without a `webhookId` field in the webhook node object, n8n v2 never registers the webhook
even when the workflow is active and `POST /api/v1/workflows/{id}/activate` returns 200.
Symptom: `{"code":404,"message":"The requested webhook ... is not registered."}`.
Fix: add `"webhookId": "<uuid>"` to the webhook node before activating. If the workflow was
already created without it, use: deactivate → PUT (with webhookId added) → activate.

### 2026-03-23 — n8n v2 PUT /api/v1/workflows rejects extra fields
Fetching a workflow via GET and PUT-ting it back as-is returns 400 "must NOT have additional
properties". Only these fields are accepted: `name`, `nodes`, `connections`, `settings`.
Strip everything else (`active`, `tags`, `createdAt`, `updatedAt`, `versionId`, `staticData`,
`pinData`, `meta`, `shared`, etc.) before PUT.

### 2026-03-23 — n8n v2 first-run setup and API key creation
Owner account: `POST /rest/owner/setup` (not `/api/v1/`).
API key: `POST /rest/api-keys` — requires `scopes: [...]` array and `expiresAt: null` explicitly.
JWT session cookie from login does NOT work as Bearer token for `/api/v1/` — must use
`X-N8N-API-KEY` header with the `rawApiKey` value returned at key creation time.

### 2026-03-23 — OctoPi: cloud-init overrides hostname on every boot
Editing `/etc/hostname` or `/etc/hosts` directly does not survive reboot on OctoPi.
cloud-init resets both files. Fix: set `preserve_hostname: true` in `/etc/cloud/cloud.cfg`.

### 2026-03-23 — Ghostty TERM over SSH to Raspberry Pi
Ghostty's terminal type is not recognized by Debian. Sessions opened from Ghostty show
rendering issues. Fix: add `export TERM=xterm-256color` to `~/.bashrc` on the Pi.
Without this, must run it manually at the start of every SSH session.

### 2026-03-23 — Argon ONE M.2 board needs Pi attached for USB flashing
The M.2 board does not receive enough power from Mac USB alone when the Pi is detached.
Attempting to flash the SSD via Mac appears to work but produces a non-bootable result.
Correct method: boot a temp SD card on the Pi → flash SSD from within the running Pi using `dd`.

### 2026-03-23 — LulzBot dropped from Ultimaker Cura ~v5.x
LulzBot printer profiles (including TAZ 5) were removed from Ultimaker Cura around v5.
Use LulzBot's own Cura fork from lulzbot.com/software for native TAZ profiles and
built-in OctoPrint integration.

### 2026-03-26 — Three-tier doc set for shared lab/shop equipment
For equipment used by multiple people with different skill levels, a three-tier documentation
set reduces friction and support burden:
1. **Admin guide** — full system reference (network, accounts, services, plugins, maintenance)
2. **User guide** — operational workflows (print setup, monitoring, materials, troubleshooting)
3. **Onboarding sheet** — 1-page linear flow: software downloads → account → connection → first use
The onboarding sheet has the highest ROI — it eliminates the most common first-day friction.

### 2026-03-25 — octopi has two local IPs
192.168.1.126 is the WiFi address (normal operating address).
192.168.1.125 is the ethernet address (used when moved to office for diagnostics/updates).
Tailscale 100.82.140.84 is the canonical remote address regardless of which LAN interface is active.

### 2026-03-25 — mjpg-streamer for OctoPrint webcam on Raspberry Pi
Suyin HD USB webcam works via mjpg-streamer on port 8080, bound to all interfaces.
Stream URL: `http://<ip>:8080/?action=stream`
Snapshot URL: `http://<ip>:8080/?action=snapshot`
Both Obico and OctoLapse consume these URLs. Bind to all interfaces (not just localhost) so
OctoPrint and Obico can reach the stream from different processes/contexts.

### 2026-03-14 — zsh strips inline # comments from pasted command lines
zsh does not accept inline `#` comments on the same line as a command. When pasting
multi-line commands from notes or scripts, strip all `#` comments before running —
they will be interpreted as part of the argument, not ignored.

## Ghostty Terminal Environment (femacbook)

**Purpose:** GPU-accelerated terminal, always-on tmux sessions, multi-node SSH dashboard.

**Install (new machine):**
```bash
brew install tmux starship
brew install --cask ghostty
```
Then install tmux plugin manager (TPM) and plugins:
- tmux-resurrect (manual save/restore)
- tmux-continuum (auto background saves)

Activate plugins: `Ctrl+b Shift+i`

**Config files to copy from dotfiles:**
- `~/.config/ghostty/config`
- `~/.tmux.conf`
- `~/.tmux/scripts/control-room.sh` (chmod +x)
- `~/.ssh/config`
- `~/.zshrc` (Starship init + aliases)

**Shell:** zsh + Starship. Fish installed but not active — evaluate later.

**SSH shortcuts** (via ~/.ssh/config + Tailscale):
- `ssh fepi` → fepi41 (100.72.119.28)
- `ssh brek` → brekpi41 (100.77.133.46)
- `ssh dl` → direct-lighting (100.110.71.33)

**Dashboard:** `control` alias runs `~/.tmux/scripts/control-room.sh` — creates split panes SSHed into fepi and brek. Session persists across restarts via continuum.

**Key aliases:** `control`, `ta` (attach), `tn` (new), `tl` (list)

**Note:** Ghostty config is minimal — it's mainly a fast host for tmux. All session management is tmux's job, not Ghostty's.



---

## Reference Links

- Claude Code docs: https://docs.claude.ai/claude-code
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Community skills: https://github.com/hesreallyhim/awesome-claude-code
- Community subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
- ClaudeLog: https://claudelog.com
