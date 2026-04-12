# Session Context

_Tracks completions, open work, and active skill state across sessions._
_Updated at end of each session via the /update skill._

--
##Machine Inventory

| Hostname | Tailscale IP | Username | Notes |
|---|---|---|---|
| femacbook | 100.72.76.32 | Flint | Primary dev machine (MacBook Pro M1) |
| fepi41 | 100.72.119.28 | flint | Raspberry Pi 8GB, Node-RED + ai-hedge-fund + n8n 1.x |
| octopi | 192.168.1.126 (WiFi) / 192.168.1.125 (eth) / 100.82.140.84 | pi | Raspberry Pi 4 4GB, Argon ONE M.2, OctoPi 1.1.0, TAZ 5, n8n 2.x Docker |
| brekpi41 | 100.77.133.46 | flint | Raspberry Pi — confirm IP when back online |
| direct-lighting | 100.110.71.33 | directlightingllc | Lighting controller (iMac) |
| feair | 100.127.24.95 | feair | MacBook Air — FeOps/OpenClaw gateway host; Tailscale Serve at feairs-macbook-air.tail4bfd96.ts.net |

> **femacbook terminal:** Ghostty + tmux + Starship (zsh). SSH shortcuts: `ssh fepi`, `ssh brek`, `ssh dl`. Infrastructure dashboard: `control` alias.
> Use Tailscale hostnames as canonical machine names. Always document usernames explicitly.

## Completions

| Date | What |
|---|---|
| 2026-04-12 | Vault ollama-ingest pipeline — scripts/ollama-ingest.py built (batch PDF/doc cataloging via Ollama/mistral:7b, pdftotext + tesseract OCR fallback, JSON registry dedup, --limit/--ocr/--dry-run flags); mistral:7b pulled, tesseract installed; OCR fallback added after 80% image-PDF failure rate discovered in first test batch; crontab installed (2am daily, --limit 50 --ocr); conversation archived + /wiki-ingest run (6 new concept pages: ollama-ingest, local-llm-inference, ocr-pipeline, batch-processing-schedule, registry-pattern); Obsidian Web Clipper installed, Dataview plugin installed, default save location set to raw/ |
| 2026-04-07 | Vault external brain activation — CLAUDE.md schema written, raw/ intake folder created, knowledge/index.md + log.md added, 3 vault commands built (/wiki-ingest, /import-last30days, /archive-conversation), first INGEST pass run on hooeem external brain article (6 concepts, 1 reference, 1 person page) |
| 2026-04-06 | FeOps/OpenClaw workspace built on feair — SOUL.md (scope + operating mode), TOOLS.md (node inventory, thresholds, escalation map), HEARTBEAT.md (ops checklist), fepi41-openclaw-ops.md, octopi-openclaw-ops.md; openclaw.json gateway fixed (loopback + Tailscale Serve); ssh-exec skill installed; web fetch policy added; 5 config gaps resolved |
| 2026-03-28 | taz5-cad skill built (SKILL.md, machine-config.md, material-profiles.md, tool-decision.md, render.sh, CLAUDE.md); /taz5-cad slash command created; tested end-to-end with flange (4-view render loop, STL export clean); OpenSCAD 2026.03.16 + CadQuery 2.7.0 installed on femacbook |
| 2026-03-28 | last30days skill reinstalled at ~/.claude/skills/last30days; DMX lighting trends research confirmed working (X + web); SSL cert errors blocking Reddit/HN/Bluesky on macOS noted |
| 2026-03-26 | octopi TAZ 5 documentation suite — taz5-admin-guide.docx (full system reference), taz5-user-guide.docx (print workflows, materials, troubleshooting), taz5-new-user-setup.docx (1-page onboarding sheet) |
| 2026-03-25 | octopi webcam + Obico + OctoLapse — Suyin HD USB cam via mjpg-streamer port 8080; Obico camera feed live and calibrated; OctoLapse configured; heated bed enabled in OctoPrint profile; Cura reconnected at new IP; test print complete (ABS 2.85mm on PEI, clean) |
| 2026-03-23 | octopi setup — Pi 4 in Argon ONE M.2, OctoPi 1.1.0, Tailscale 100.82.140.84; Docker + n8n 2.12.3; OctoPrint-Webhooks plugin; "TAZ 5 Print Events" n8n workflow (Discord #print-alerts + GitHub job log); all services persist across reboot |
| 2026-03-14 | Node-RED irrigation audit (87→94 nodes), 11 fixes applied, HTTP API endpoints added, webhook events to n8n wired; n8n 1.123.25 installed on fepi41 (port 5678, systemd user service); 6 oversight workflows built and activated (WF-1 heartbeat, WF-2 daily status, WF-3 water report, WF-4 valve watchdog, WF-5 sewer relay, WF-6 sewer poll); email alerting confirmed working |
| 2026-03-12 | Data consolidation Pass 3 & 4 (fefamacbook) — vault at 33,269 files; QB entity map finalized; G&G = GAG = Garbage&Greed LLC; dot-notation convention confirmed sufficient |
| 2026-03-06 | Obsidian vault structure — 30 folders and 26 files created in iCloud Drive/vault/; README in every folder with purpose and agent permissions; seed files: connector-registry.md, project-template.md, daily note stub; vault live in Obsidian |
| 2026-03-05 | personal OS + data consolidation — created personal-os-2026-03.md PRD and data-consolidation-2026-03.md work order in /projects; Obsidian vault, OCR pipeline, and inventory agent identified as future skills |
| 2026-03-05 | portfolio-tracker real holdings — replaced placeholder tickers with real 14-position portfolio in watchlist.json on fepi41; removed JACTX (mutual fund, no yfinance data); recalculated weights to sum to 100%; fixed costBasis → cost_basis key mismatch; added NaN guard for unresolvable tickers |
| 2026-03-04 | ai-hedge-fund Discord comms layer — "Fe Trading" server, 4 webhook channels, morning-briefing/news-alert/portfolio-tracker on cron, agent-run.sh on-demand; nvm for Node.js v22 (NodeSource armhf blocked); yfinance pinned 0.2.54; Cloudflare DiscordBot User-Agent fix; news_sentiment.py upstream bug patched |
| 2026-03-03 | ai-hedge-fund web UI deployed on fepi41 — React/Vite frontend + FastAPI backend, systemd service, accessible at http://100.72.119.28:8000; three post-deploy bugs fixed (Vite URL baking, StaticFiles routing, Cache-Control) |
| 2026-03-02 | /update skill rewritten (5-step interactive flow), /simplify skill created, both added to skills-inventory; SSH remote setup completed for fepi41 and brekpi41 |
| 2026-03-01 | raspberry-pi-expansion — PRD created, fepi41 fully set up (Python 3.11.9 via pyenv, ai-hedge-fund installed and tested), machine inventory confirmed with Tailscale IPs |
| 2026-02-28 | pdf-to-qbo — local PDF-to-QBO converter for WF statements, dual CC format support, QB Desktop Mac import fixes (LEDGERBAL, INTU.BID) |
| 2026-02-24 | load-context — quick + full modes, clipboard copy, alias + keyboard shortcut |
| 2026-02-24 | api-key-prompt — rebuilt for zsh, session-only export, multi-service |
| 2026-02-23 | Toolkit foundation — folder structure, CLAUDE.md, README, registry, GitHub |

---

## Open Work

- [x] Check ss7 battery — replaced 2026-04-06
- [ ] When ss4/ss8 sensors deployed: add back to WF-1 THRESHOLDS in n8n heartbeat workflow
- [ ] Migrate n8n from fepi41 to Mac Mini when available — update NR webhook URLs in valve-webhook-req and sewer-webhook-req nodes
- [ ] Install n8n on brekpi41 — offline-capable config (no internet dependency, self-maintaining; brekpi cycles on battery + Starlink)
- [ ] iMac Pre-Retirement Checklist
- [ ] Install jq via Homebrew
- [ ] Recover api-key-prompt skill
- [ ] Recover quickbooks skill
- [ ] Document pdfplumber as explicit dependency (requirements.txt or registry note)
- [ ] iCloud selective sync strategy (work/personal separation)
- [ ] Back up ~/.claude/commands/taz5-cad.md to toolkit or dotfiles repo (not tracked in git)
- [ ] Install yt-dlp for last30days YouTube support (`brew install yt-dlp`)
- [x] Test taz5-cad skill with a CadQuery part — confirmed 2026-04-06
- [ ] Phase 2: auto-upload STL to OctoPrint after final taz5-cad render (n8n already on octopi)
- [ ] Explore community skills: github.com/hesreallyhim/awesome-claude-code
- [ ] Evaluate market-snapshot.py from Nick's tools (hourly SPY/QQQ/VIX)
- [ ] Data consolidation — direct-lighting (Pass 3 migration pending)
- [ ] _review/ triage — 8,852 files flagged, later session
- [ ] Ellsworth folder in _review → vault/areas/finance/ellsworth-trust/
- [ ] QB files → sort into active/legacy/old-quicken under assets/documents/quickbooks/
- [ ] Empty Trash — after all migration confirmed
- [ ] Delete ~/Documents originals — after Trash emptied
- [ ] Evaluate Pass 3 script as template for direct-lighting migration
- [x] Add update and simplify to Active Skills table in session-context.md
- [x] Push toolkit updates to GitHub
- [ ] octopi: confirm mjpg-streamer autostarts on boot (verify service configured)
- [ ] octopi: add `export TERM=xterm-256color` to ~/.bashrc on Pi (permanent fix for Ghostty SSH sessions)
- [ ] octopi: add octopi pane to Ghostty control-room dashboard
- [ ] octopi: store taz5-admin-guide.docx, taz5-user-guide.docx, taz5-new-user-setup.docx somewhere accessible (shared drive or vault)
- [ ] feair: pair iMessage +1 323-244-0868 with FeOps (`openclaw configure` on feair)
- [ ] feair: add brekpi41 Victron health endpoint or MQTT topic to TOOLS.md and HEARTBEAT.md (SOC polling method undefined)
- [ ] feair: delete BOOTSTRAP.md from FeOps workspace (bootstrap phase complete)
- [ ] feair: rotate Telegram bot token, gateway auth token, Brave API key (exposed in chat 2026-04-06)
- [ ] feair: add feair/FeOps to session-context.md machine inventory
- [ ] feair: deploy OpenClaw node on fepi41 (same SSH tunnel pattern as brekpi41)
- [ ] feair: deploy OpenClaw node on octopi (same SSH tunnel pattern as brekpi41)
- [ ] vault: delete stray file at vault root (`1. Which extensions are bulk-excludable?...md`)
- [x] vault: set up Obsidian Web Clipper browser extension — installed 2026-04-12
- [x] vault: install Dataview plugin in Obsidian — installed 2026-04-12
- [x] vault: verify Obsidian default save location routes new files to raw/ — confirmed 2026-04-12
- [ ] vault: tune ollama-ingest --limit once first nightly run completes (check knowledge/.ollama-ingest.log runtime)
- [ ] Push toolkit updates to GitHub

---

## Active Skills

| Skill | Location | Status |
|---|---|---|
| pdf-to-qbo | skills/pdf-to-qbo/convert_statements.py | active |
| load-context | skills/load-context/load-context.sh | active |
| api-key-prompt | skills/api-key-prompt/set-api-key.sh | active |
| last30days | ~/.claude/skills/last30days | active (borrowed) |
| ai-hedge-fund | fepi41 ~/ai-hedge-fund | active (borrowed) |
| update | ~/.claude/commands/update.md | active |
| simplify | ~/.claude/commands/simplify.md | active |
| node-red-irrigation | fepi41: ~/.node-red/Flint.flows | active |
| n8n-oversight | fepi41: ~/.n8n, port 5678 | active |
| octopi-n8n | octopi: Docker n8n, port 5678 | active |
| taz5-cad | skills/taz5-cad/ + ~/.claude/commands/taz5-cad.md | active |
| feops-openclaw | feair: /Users/feair/.openclaw/workspace/ | active |
| ollama-ingest | vault/scripts/ollama-ingest.py | active |
