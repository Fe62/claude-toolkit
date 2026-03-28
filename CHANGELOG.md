# Changelog

Format: [YYYY-MM-DD] — What changed and why (brief)

---

## 2026-03

### 2026-03-28 — taz5-cad skill built and tested
- Built taz5-cad skill (6 files: SKILL.md, machine-config.md, material-profiles.md, tool-decision.md, render.sh, CLAUDE.md) and /taz5-cad slash command
- Skill tested end-to-end: flange generated in OpenSCAD, Pass 0 sanity check + 4-view autonomous render loop, STL exported manifold/clean
- Installed OpenSCAD 2026.03.16 (snapshot, macOS Tahoe-compatible) and CadQuery 2.7.0 (under python3.12 — python3.14 lacks OCP wheels)
- Added OpenSCAD missing-binary guard to render.sh; documented python3.12 invocation requirement
- Added 3 lessons to master-reference.md (CadQuery python version, OpenSCAD Tahoe --render flag, --autocenter --viewall)
- Fixed last30days SSL cert errors (ran Install Certificates.command for Python 3.14)

### 2026-03-28 — last30days skill reinstalled
- Reinstalled /last30days skill at ~/.claude/skills/last30days; confirmed working with DMX lighting trends research run
- X (15 posts) and web (18 pages) returned results; Reddit/HN/Bluesky blocked by macOS SSL cert errors (CERTIFICATE_VERIFY_FAILED)
- ~/Documents/Last30Days/ established as canonical output folder for research summaries
- Updated skills-inventory.md with reinstall date, output folder, and SSL known issue

### 2026-03-26 — octopi TAZ 5 documentation suite
- Wrote taz5-admin-guide.docx — full system reference (network, plugins, Cura, Obico, n8n, multi-user, maintenance)
- Wrote taz5-user-guide.docx — print workflows, monitoring, filament loading, bed leveling, materials reference, troubleshooting
- Wrote taz5-new-user-setup.docx — 1-page onboarding sheet (software → account → Cura → API key → first print)
- Added three-tier doc pattern lesson to master-reference.md

### 2026-03-25 — octopi webcam, Obico, OctoLapse, test print
- Installed Suyin HD USB webcam via mjpg-streamer (port 8080, all interfaces); stream/snapshot URLs confirmed
- Obico camera feed live and calibrated; OctoLapse configured
- Heated bed enabled in OctoPrint printer profile; Cura reconnected at 192.168.1.126
- Test print complete — ABS 2.85mm on PEI, clean result
- Corrected octopi local IP: .126 WiFi (normal operation), .125 ethernet (office/diagnostics)
- Updated octopi-n8n skill entry with webcam/Obico/OctoLapse details and dual IP clarification
- Added two lessons to master-reference.md (dual local IPs, mjpg-streamer setup)

### 2026-03-23 — octopi setup: OctoPrint Pi for TAZ 5
- Set up Raspberry Pi 4 4GB (Argon ONE M.2, OctoPi 1.1.0, Kingston 128GB SSD) as always-on 3D print management node on Direct Lighting network
- Installed Tailscale; Pi now at 100.82.140.84; SSH over Tailscale confirmed
- Installed Docker 29.3.0; deployed n8n 2.12.3 as Docker container (persistent volume, --restart unless-stopped, port 5678)
- Installed OctoPrint-Webhooks plugin v3.0.3 (2blane fork); fires on PrintStarted/Done/Failed/Error
- Built "TAZ 5 Print Events" n8n workflow: OctoPrint webhook → Discord #print-alerts embed + GitHub commit to Fe62/direct-lighting-print-log
- All services (Tailscale, Docker/n8n, OctoPrint) survive reboot; webhook re-registers correctly
- Added octopi-n8n to skills-inventory; added octopi to machine inventory
- Added n8n v2 API lessons and OctoPi hardware lessons to master-reference.md

### 2026-03-14 — Node-RED irrigation audit + n8n oversight layer
- Audited Node-RED flows on fepi41 (TTN v3/LoRaWAN irrigation system); 87→94 nodes after 11 fixes
- Fixes: TLS linked to MQTT broker, sewer downlink topic corrected, file-backed context storage enabled, scheduler wiring and water journalling logic repaired, relay-state-parser added, sewer thresholds write to globals, HTTP API endpoints (/api/status, /api/clear-daily-log) added, valve and sewer webhook events wired to n8n
- Installed n8n 1.123.25 on fepi41 (port 5678) as systemd user service; overcame 5 ARM/Node 20 install obstacles
- Built and activated 6 n8n workflows: WF-1 heartbeat, WF-2 daily status, WF-3 water report, WF-4 valve watchdog, WF-5 sewer emergency relay, WF-6 sewer polling backup
- Email alerting confirmed working; ss4/ss8 removed from WF-1 (not yet deployed); ss7 flagged for battery check
- Added node-red-irrigation and n8n-oversight to skills-inventory.md
- Added 6 lessons to master-reference.md (IPv6, n8n ARM install, linger, API quirks, static data dedup, email formatting)

### 2026-03-12 — Data consolidation: Pass 3 & 4 migration
- Built and ran Pass 3 migration script — 33,238 files sorted into staging by dot-notation prefix + folder-override rules; vault now at 33,269 files
- Pass 4 (Media/) resolved: Camera Uploads → ~/Pictures/, Femusic FLAC → ~/Music/Femusic/, 8 PDFs rescued to vault (5 Flatiron → legacy-orgs/flatiron/, 3 FE personal → areas/personal/FE.pers/); Media/ folder removed from Documents
- QB entity map finalized (3 active: personal/P&A/Ellsworth; 8 legacy; 2 old Quicken); G&G = GAG = Garbage&Greed LLC confirmed equivalent
- Facebook export (76MB) preserved in vault/archive/ as authoritative copy; account data cleared
- Dot-notation naming convention confirmed sufficient — no second-level subfolder sort needed
- Registered dot-notation-migration as reusable skill template

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
