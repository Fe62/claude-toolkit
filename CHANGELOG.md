# Changelog

Format: [YYYY-MM-DD] — What changed and why (brief)

---

## 2026-03

### 2026-03-06 — Obsidian vault structure live
- Created 30 folders and 26 files in iCloud Drive/vault/ on femacbook
- README in every folder — purpose + agent permission model
- Seed files: connector-registry.md, project-template.md, today's daily note stub
- Vault opened in Obsidian and confirmed live
- Added obsidian-vault entry to skills-inventory.md
- Added two lessons to master-reference.md (shell path spaces, README-per-folder pattern)

### 2026-03-05 — personal OS + data consolidation PRDs
- Created personal-os-2026-03.md PRD in /projects — Obsidian vault, OCR pipeline, inventory agent identified as future skills
- Created data-consolidation-2026-03.md work order in /projects — human agent data pipeline, ready to start

### 2026-03-05 — portfolio-tracker real holdings
- Replaced placeholder tickers in watchlist.json on fepi41 with real 14-position portfolio
- Removed JACTX (mutual fund — no yfinance price data)
- Recalculated weights for remaining 14 positions to sum to 100%
- Fixed costBasis → cost_basis key mismatch in portfolio-tracker.sh
- Added math.isnan() guard so unpriceable tickers show N/A instead of corrupting portfolio totals
- Tracker confirmed working and posting to Discord #research

### 2026-03-04 — ai-hedge-fund Discord comms layer
- Created "Fe Trading" Discord server; configured webhooks for #research, #trade-alerts, #agent-runs
- Adapted three scheduled tools from Nick Nemo's repo: morning-briefing.sh (6:15 AM), news-alert.py (every 30 min market hours), portfolio-tracker.sh (1:15 PM)
- Built agent-run.sh wrapper for on-demand virattt runs
- Resolved ARM issues: nvm for Node.js v22 (NodeSource dropped armhf), yfinance pinned to 0.2.54 (curl_cffi no armhf prebuilt)
- Fixed Discord 403: Cloudflare requires DiscordBot User-Agent header; switched discordapp.com → discord.com
- Patched virattt news_sentiment.py UnboundLocalError upstream bug
- Added nick-hedgefund-tools and discord-webhook-delivery to skills-inventory.md
- Added Discord webhooks section and 5 new lessons to master-reference.md

### 2026-03-03 — ai-hedge-fund web UI deployed on fepi41
- Deployed React/Vite frontend + FastAPI backend as always-on service on fepi41
- Frontend built to static files, served by FastAPI backend; systemd service auto-starts on reboot
- Accessible at http://100.72.119.28:8000 over Tailscale from FeMacBook
- Post-deploy fixes: replaced localhost API URLs with relative paths (Vite bakes URLs at build time);
  replaced app.mount("/", StaticFiles(...)) with /{full_path:path} catch-all route (fixes redirect_slashes
  blocking); added Cache-Control: no-store on index.html (prevents stale asset hash caching)
- Updated master-reference.md with corrected FastAPI+Vite deployment patterns and three new lessons

### 2026-03-02 — Slash commands: update + simplify
- Rewrote /update skill to use 5-step interactive flow (was single-summary prompt)
- Created /simplify skill for post-change code review (reuse, quality, efficiency)
- Added inventory entries for both in skills-inventory.md
- Added SSH remote conventions to master-reference.md (Linux-only, ssh-copy-id first)
- Updated machine inventory with confirmed usernames (brekpi41: flint, direct-lighting: directlightingllc)

---

## 2026-02

### 2026-02-23 — Initial build
- Created claude-toolkit folder structure
- Added CLAUDE.md, README.md, CHANGELOG.md
- Added bible/master-reference.md stub
- Added projects/_project-template.md
- Added skills-registry/skills-inventory.md with last30days entry
- Initialized as private GitHub repo
- Working copy established in iCloud Drive
- Claude Code authenticated via API credits, Pro + API credits strategy confirmed


## How to Use This File

Add an entry whenever you:
- Complete or start a significant project
- Add, adapt, or retire a skill
- Change a working convention
- Learn something that changes how you use the toolkit

Keep entries short — one to three lines is enough. The bible is 
for detail; this is just the trail of breadcrumbs.

### 2026-02-24 — Phase 2 complete
- Verified folder structure in iCloud Drive on MacBook Pro M1
- Confirmed all files pushed to GitHub (Fe62/claude-toolkit)
- Added .gitignore to exclude .DS_Store
- Set git global identity (name + email)
- Verified Claude Code reads CLAUDE.md correctly from toolkit root

### 2026-02-24 — api-key-prompt skill rebuilt
- Created skills/api-key-prompt/set-api-key.sh
- Supports Anthropic, OpenAI, Schwab, QuickBooks, plus any new service on the fly
- Keys entered silently, exported to session only, never written to file
- Written for zsh (MacBook Pro M1)

### 2026-02-24 — load-context skill built
- Created skills/load-context/load-context.sh
- Two modes: Quick (orientation block) and Full (orientation + all project files)
- Copies to clipboard via pbcopy — paste into any new Claude conversation

### 2026-03-01 — Raspberry Pi expansion + ai-hedge-fund
- Created raspberry-pi-expansion-2026-03.md PRD
- Confirmed Tailscale machine inventory (fepi41, brekpi41, direct-lighting, femacbook)
- Installed Python 3.11.9 via pyenv on fepi41; ai-hedge-fund cloned and running
- Documented ARM Python install patterns and Poetry workaround in master-reference.md
- Added ai-hedge-fund to skills-inventory.md

### 2026-02-28 — pdf-to-qbo skill completed
- Built local PDF-to-QBO converter for Wells Fargo bank and credit card statements
- Added dual CC format support (WF Signify Format A, WF Signature/FA Format B)
- Fixed QB Desktop Mac import errors: LEDGERBAL block and INTU.BID required
- quickbooks-automation retired; replaced by pdf-to-qbo
- Created session-context.md for cross-session tracking
