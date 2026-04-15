# Skills Inventory

Last updated: 2026-04-14

---

## How to Read This Registry

**Status:**
- `borrowed` — someone else's code, dependency risk, do not modify original
- `adapted` — started from borrowed, now our own copy
- `built` — designed and owned entirely

**Health:**
- `active` — installed and working
- `needs-setup` — exists but requires installation on this machine
- `broken` — known issue, needs attention
- `retired` — no longer in use

---

## Active Skills

### paychex-download
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Location | `skills/paychex payroll automation/paychex_download.py` |
| Type | Standalone Python script |
| Dependencies | `playwright` + Chromium; macOS Keychain entries: `paychex`/`username`, `paychex-password`/`password`; DirectNAS mounted at `/Volumes/Public` |
| Purpose | Automates Paychex Flex weekly payroll zip download for Direct Lighting LLC. Connects to existing Brave session via CDP, installs XHR interceptor to capture OIDC Bearer JWT from Angular's in-memory auth service, calls `loadPackageFolders` + `getDownloadFolderRequestURL`, downloads zip, extracts to correct NAS folder (`Q{1-4}/Payroll.MMDD`). |
| Auth method | XHR monkey-patch captures `Authorization: Bearer <JWT>` from Angular's own `getMostFrequentlyUsedReports` page-load request. `x-payx-sid` is correlation only. |
| Brave requirement | Brave must be running with `--remote-debugging-port=9222` before script runs |
| NAS path | `/Volumes/Public/Direct Lighting/Direct Lighting LLC/1.Direct.Payroll/1.Payrolls/26.Payrolls/Q{n}/Payroll.MMDD/` |
| Usage | `python3 paychex_download.py` (uses today's date) or `python3 paychex_download.py 2026-04-15` |
| Phase 3 pending | launchd plist (Tuesday 8am), per-run log, Discord webhook, AppleScript QB import |
| Session context | `skills/paychex payroll automation/SESSION-CONTEXT-phase3.md` |
| Added | 2026-04-14 |

---

### ollama-ingest
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Location | `vault/scripts/ollama-ingest.py` |
| Type | Standalone Python script (not a slash command) |
| Dependencies | `ollama` + `mistral:7b`; `pdftotext` + `pdftoppm` (poppler); `tesseract` (brew); macOS `textutil` (built-in); optional: `pypdf`, `python-docx` (pip) |
| Purpose | Bulk legacy document cataloging into the vault wiki. Targets `archive/legacy-orgs/` (10,535 files). Extracts text via pdftotext → tesseract OCR fallback for image-based scanned PDFs. Sends financial-document-tuned prompt to Ollama/mistral:7b. Writes vault-schema reference pages, concept/person stubs, updates index.md and log.md. |
| Scheduling | Crontab: `0 2 * * *`, `--limit 50 --ocr`, output → `knowledge/.ollama-ingest.log` |
| Registry | `knowledge/.ollama-registry.json` — dedup + state; `no-text` skips auto-retried on `--ocr` runs |
| Key flags | `--target`, `--model`, `--limit`, `--ocr`, `--dry-run`, `--verbose`, `--ext` |
| Division of labor | Bulk/financial legacy docs → ollama-ingest (local, nightly, free); deep comprehension/articles → `/wiki-ingest` via Claude Code |
| Slug namespace | `legacy-*` prefix — isolated from Claude Code wiki-ingest pages |
| Common commands | `python3 scripts/ollama-ingest.py --dry-run` (progress check); `--limit 200 --ocr` (weekend catchup); `--target archive/legacy-orgs/efit --limit 50 --ocr` (subfolder sprint) |
| Added | 2026-04-12 |

---

### feops-openclaw
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Host | feair (100.127.24.95, user: feair) |
| Workspace | /Users/feair/.openclaw/workspace/ |
| Gateway | loopback port 18789; Tailscale Serve at https://feairs-macbook-air.tail4bfd96.ts.net |
| Channels | Telegram (bot, Flint only); iMessage +1 323-244-0868 (not yet paired) |
| Purpose | FeOps — ops manager agent monitoring fepi41, brekpi41, octopi. Orchestrator/Coordinator role. Checks node reachability and service health, alerts Flint via Telegram. Future: coordinates service agents per SERVICE_AGENT_MESSAGE_CONTRACT.md |
| Key files | SOUL.md (scope + web fetch policy), TOOLS.md (node inventory + thresholds), HEARTBEAT.md (ops checklist), AGENTS.md, MESSAGE_CONTRACT.md, SERVICE_AGENT_MESSAGE_CONTRACT.md, fepi41/brekpi41/octopi-openclaw-ops.md |
| Models | Primary: openai-codex/gpt-5.4; fallbacks: kimi-k2.5, qwen2.5, claude-sonnet-4-6, gemini-3.1-pro |
| SSH | ssh via sshpass: `sshpass -p '7787' ssh -o StrictHostKeyChecking=no -o IdentitiesOnly=yes feair@100.127.24.95` |
| Node connections | brekpi41: SSH tunnel pattern (Pi tunnels to Mac loopback); fepi41/octopi: not yet deployed |
| Skills installed | ssh-exec (ClawHub) |
| Operating mode | Solo mode — no service agents deployed yet; FeOps polls nodes directly |
| Open work | Pair iMessage; add Victron polling method; delete BOOTSTRAP.md; rotate exposed tokens; deploy nodes on fepi41 + octopi |
| Added | 2026-04-06 |

---

### last30days
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | active |
| Source | https://github.com/mvanhorn/last30days-skill |
| Installed | ~/.claude/skills/last30days |
| Dependencies | OpenAI API key, xAI API key (optional) |
| Purpose | Research agent — searches internet, Reddit, and other sources for information from the last 30 days. Use for staying current on Claude Code techniques, trends, best practices, any time-sensitive research query. |
| Risk | External dependency — if source repo changes or disappears, skill may break. |
| Output | Raw research saved to ~/Documents/Last30Days/ (via --save-dir flag) |
| Known issue | Reddit, HN, and Bluesky fail on macOS with CERTIFICATE_VERIFY_FAILED — Python macOS SSL cert issue, not skill bug. Fix: run /Applications/Python*/Install\ Certificates.command or pip install --upgrade certifi |
| Notes | API keys managed via prompt-on-entry skill (see below). Never hardcode. |
| Reinstalled | 2026-03-28 |

---
### api-key-prompt
| Field | Detail |
|---|---|
| Status | built (to be rebuilt) |
| Health | needs-setup |
| Source | Originally built, resides on iMac — needs recovery and documentation |
| Installed | Unknown — check ~/.claude/skills/ on iMac |
| Dependencies | None |
| Purpose | Prompts for API key entry at runtime rather than storing keys in plain text files. Used by last30days and any other skill requiring API authentication. |
| Priority | High — rebuild early, all other API-dependent skills depend on this |

### ai-hedge-fund
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | active |
| Source | https://github.com/virattt/ai-hedge-fund |
| Installed | fepi41 ~/ai-hedge-fund |
| Dependencies | Python 3.11.9 (via pyenv), Anthropic API key in .env, requirements-core.txt via pip, Node.js v20.19.2 |
| Purpose | Multi-agent AI hedge fund system. Analysts run against tickers and return signals; portfolio manager returns BUY/SELL/HOLD decisions. |
| Web UI | React/Vite frontend built to static files; served by FastAPI backend at http://100.72.119.28:8000 |
| Service | systemd ai-hedge-fund.service on fepi41 — enabled, auto-starts on reboot, Restart=on-failure |
| Access | http://100.72.119.28:8000 (Tailscale only — not public internet) |
| Install notes | Do NOT use Poetry on ARM — hangs. Generate requirements-core.txt from poetry.lock via toml script. Exclude: contourpy, matplotlib, pillow, tiktoken. Pre-install: libjpeg-dev zlib1g-dev libpng-dev rustc cargo. Install pyenv build deps first: libbz2-dev libncurses-dev libffi-dev libreadline-dev libsqlite3-dev liblzma-dev. |
| Frontend build | Use `npx vite build` (not `npm run build`) — upstream TypeScript errors fail tsc gate. Also fix case-sensitive import: App.tsx `./components/layout` → `./components/Layout`. |
| Service mgmt | `sudo systemctl [start\|stop\|restart\|status] ai-hedge-fund` |
| Known issues | Michael Burry agent has upstream parsing error — harmless, not Pi-related |
| Bug patched | 2026-03-04 — news_sentiment.py UnboundLocalError on empty company_news; add `sentiments_classified_by_llm = 0` before `if company_news:` block |
| CLI flags | `--tickers TICKER,... --analysts-all --model claude-sonnet-4-5-20250929 --start-date ... --end-date ...` — both --tickers and --analysts-all required for non-interactive scripting |
| API key gotcha | Key entered via web UI can be truncated (first char dropped). Verify: `grep ANTHROPIC ~/ai-hedge-fund/.env \| cut -c1-30` — should show `ANTHROPIC_API_KEY=sk-ant-` |
| Test run | 2026-03-01 — Growth Analyst bearish on AAPL, portfolio manager HOLD ✓ (CLI) |
| Added | 2026-03-01 |
| Web UI added | 2026-03-03 |

---

### nick-hedgefund-tools
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | active |
| Source | https://gitlab.com/nick.nemo/ai-hedgefund |
| Installed | fepi41: ~/hedge-fund/tools/ (adapted scripts); ~/nick-hedgefund-review (reference) |
| Purpose | Investment automation scripts. morning-briefing, news-alert, portfolio-tracker adapted and running on cron. Advanced tools (edgar-monitor, insider-clusters, econometrics) available for later phases. |
| Cost model | Tier 1 free (yfinance/FRED/EDGAR data), Tier 2 ~$0.05 (light Claude synthesis), Tier 3 ~$0.15-0.50 (deep research / virattt full run) |
| Notes | Not a virattt fork — standalone system. Discord-native. Python + shell scripts. 27 scheduled jobs on source repo. |
| Added | 2026-03-04 |

---

### discord-webhook-delivery
| Field | Detail |
|---|---|
| Status | custom |
| Health | active |
| Installed | fepi41: ~/.hedge-fund-discord.env (webhooks), ~/hedge-fund/tools/ (scripts) |
| Purpose | One-way Discord delivery via webhooks. No persistent bot process. Routes morning briefings, news alerts, portfolio snapshots, and agent run results to #research, #trade-alerts, #agent-runs channels in "Fe Trading" server. |
| Config | ~/.hedge-fund-discord.env — 4 webhook URLs, chmod 600, never git. Load with `set -a; source ~/.hedge-fund-discord.env; set +a` |
| Gotchas | Use discord.com not discordapp.com (legacy, returns 403). Always set `User-Agent: DiscordBot (url, version)` — Python default UA triggers Cloudflare 1010. yfinance pin to 0.2.54 on ARM (1.2.0 fails, curl_cffi no armhf prebuilt). |
| Watchlist | ~/hedge-fund/memory/watchlist.json on fepi41 — single source of truth for holdings; update when positions change; recalculate weights to sum to 100% after any add/remove |
| Added | 2026-03-04 |
| Updated | 2026-03-05 — real holdings loaded; costBasis → cost_basis key corrected; NaN guard added for mutual funds |

---

### simplify
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Source | ~/.claude/commands/simplify.md |
| Type | Custom slash command (`/simplify`) |
| Dependencies | None |
| Purpose | Post-change code review. Checks changed code for reuse (duplication, reinvented wheels), quality (over-engineering, dead code, unclear naming), and efficiency (unnecessary loops, redundant ops). Fixes issues directly rather than reporting them. Shows a summary of changes when done. |
| Added | 2026-03-02 |

---

### update
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Source | ~/.claude/commands/update.md |
| Type | Custom slash command (`/update`) |
| Dependencies | session-context.md, skills-inventory.md, bible/master-reference.md, CHANGELOG.md |
| Purpose | End-of-session toolkit documentation update. Works through 5 sequential questions with confirmation at each step (session summary, skill changes, open work resolved, new open items, lessons learned), then drafts targeted updates to all four files. Stages with `git add -A` but never commits. |
| Last revised | 2026-03-02 — rewrote from single-summary prompt to 5-step interactive flow |

---
## pdf-to-qbo
- **Status:** installed, tested
- **Location:** skills/pdf-to-qbo/convert_statements.py
- **Usage:** python3 convert_statements.py "/path/to/folder"
- **Auto-detects:** BANK vs CREDITCARD from folder name
- **Handles:** WF Signify (Format A) and WF Signature/FA (Format B) CC statements
- **Output:** [folder-name].qbo written into same folder
- **Tested:** WellsSignify.25 (455 txns), FA.cc (14 statements), checking (5 txns)
- **Notes:** Requires pdfplumber. PDF filenames must start with MMDDYY.

---

### obsidian-vault
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Installed | iCloud Drive/vault/ — syncs to all devices |
| Purpose | Personal OS knowledge vault and external brain. Plain markdown throughout. AI-maintained wiki in knowledge/; raw source intake in raw/; CLAUDE.md schema controls AI behaviour. |
| Opened in | Obsidian (free) — vault at ~/Library/Mobile Documents/com~apple~CloudDocs/vault |
| Agent rules | Always folder-scoped. /archive and /assets read-only by default. /inbox is the only open-write folder. /raw is read-only for AI. |
| Schema | CLAUDE.md at vault root — loads automatically when Claude Code opened from vault. Defines folder map, naming conventions, YAML frontmatter, and 4 operational cycles. |
| raw/ | Permanent source intake shelf: articles/, papers/, notes/, repos/. Files accumulate here, never deleted or moved by AI. |
| knowledge/ | AI-maintained wiki: concepts/, references/, people/, index.md, log.md. index.md is the master index; log.md is the append-only operation log. |
| Vault commands | vault/.claude/commands/: wiki-ingest (deduped ingest), import-last30days (pulls last30days dumps to raw/notes/), archive-conversation (saves Claude synthesis to raw/notes/) |
| Bulk ingest | vault/scripts/ollama-ingest.py — nightly Ollama/mistral:7b batch pipeline for legacy docs; see ollama-ingest skill entry |
| Plugins | Dataview (live YAML frontmatter queries); Web Clipper (browser extension → raw/articles/) |
| First ingested | 2026-04-07 — hooeem-2025-external-brain article: 6 concept pages, 1 reference, 1 person page |
| Seed files | resources/connector-registry.md, resources/templates/project-template.md |
| Added | 2026-03-06 |
| Updated | 2026-04-12 — ollama-ingest pipeline added; Dataview + Web Clipper installed; default save location confirmed raw/ |

---

### dot-notation-migration
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Source | skills/migrate-pass3/migrate-pass3-2026-03.md |
| Purpose | Template script for sorting files into a vault by dot-notation prefix and folder-override rules. Built for Pass 3 of personal data consolidation (33,238 files). Reusable pattern for future migrations. |
| Key patterns | DRY_RUN = True default; shutil.copy2 for metadata preservation; _review/ prefix for human-attention flags |
| Added | 2026-03-12 |

### node-red-irrigation
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Installed | fepi41: ~/.node-red/Flint.flows |
| Purpose | TTN v3 LoRaWAN irrigation control layer. Receives uplinks from relay node, soil sensors, and sewer sensor via MQTT. Controls valve open/close via TTN downlinks. Tracks soil moisture, relay port states, and water usage via NR context (file-backed). Exposes HTTP API at /api/status and /api/clear-daily-log for n8n oversight layer. Posts valve command and sewer alert events to n8n webhooks. |
| Devices | relay-node1 (4 valves, ports 6-9), ss1/ss2/ss3/ss5/ss6/ss7 (soil sensors), sew1 (sewer depth) |
| TTN app | 5571-258-irri @ nam1.cloud.thethings.network:8883 |
| Context storage | file-backed (localfilesystem) — survives restarts; set in settings.js contextStorage block |
| Migration note | If n8n moves to Mac Mini, update valve-webhook-req and sewer-webhook-req node URLs from localhost:5678 to Mac Mini Tailscale IP |
| Added | 2026-03-14 |

---

### n8n-oversight
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Installed | fepi41: ~/.local/lib/node_modules/n8n; systemd user service n8n.service; port 5678 |
| Purpose | Oversight and alerting layer above Node-RED irrigation system. 6 workflows: WF-1 heartbeat (offline/recovery alerts), WF-2 daily morning status, WF-3 daily water usage report + log clear, WF-4 valve command watchdog (90s ack check), WF-5 sewer emergency relay, WF-6 sewer polling backup. |
| Version | n8n 1.123.25 (Node 20 compatible; v2.x requires Node ≥22) |
| Install method | npm config set prefix ~/.local; npm install -g n8n@1.123.25 --ignore-scripts; npm rebuild sqlite3 (isolated-vm won't build on aarch64 Node 20) |
| Service | systemd --user; loginctl enable-linger required; N8N_SECURE_COOKIE=false required for HTTP access |
| API | http://127.0.0.1:5678/api/v1 (JWT auth); use 127.0.0.1 not localhost (Pi resolves IPv6 first) |
| Workflow IDs | WF-1: EkSdpiFTrkLqQAKj, WF-2: OKnkrHDXvwGxQ589, WF-3: r63ynZ01PjKziRYh, WF-4: WrPRl0Kbtu94cDen, WF-5: azvAZyFAuyXHva7m, WF-6: Ygcj18XrURvC8Vmf |
| Dedup method | $getWorkflowStaticData('global') persists between executions — tracks per-device state transitions without external DB |
| Future | Long-term host: Mac Mini (always-on). When migrating, update NR webhook URLs in valve-webhook-req and sewer-webhook-req nodes |
| Added | 2026-03-14 |

---

### octopi-n8n
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Installed | octopi: Docker container `n8n`, port 5678; volume `n8n_data` |
| Version | n8n 2.12.3 |
| Purpose | Print event automation for TAZ 5. OctoPrint-Webhooks plugin (v3.0.3, 2blane fork) fires on PrintStarted/Done/Failed/Error → n8n "TAZ 5 Print Events" workflow → Discord `#print-alerts` embed + GitHub commit to `Fe62/direct-lighting-print-log/print-log.md` |
| Local IP (WiFi) | 192.168.1.126 — normal operating address |
| Local IP (Ethernet) | 192.168.1.125 — used when moved to office for diagnostics/updates |
| Access | `http://100.82.140.84:5678` (Tailscale only); owner: flint@directlighting.com |
| Workflow ID | `aQxDfVn7PKw28Qhy` |
| OctoPrint plugin | OctoPrint-Webhooks v3.0.3; webhook target: `http://127.0.0.1:5678/webhook/print-event` (127.0.0.1 not localhost — Pi resolves IPv6 first) |
| Webcam | Suyin HD USB via mjpg-streamer, port 8080, all interfaces |
| Stream URL | `http://192.168.1.126:8080/?action=stream` |
| Snapshot URL | `http://192.168.1.126:8080/?action=snapshot` |
| Obico | Camera feed live and calibrated |
| OctoLapse | Configured |
| Docker | `--restart unless-stopped`, volume `n8n_data`, `N8N_SECURE_COOKIE=false` |
| Migration note | If n8n moves off octopi, update OctoPrint webhook URL in plugin settings |
| Added | 2026-03-23 |
| Updated | 2026-03-25 — webcam/Obico/OctoLapse added; dual local IPs documented |

---

### taz5-cad
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Installed | skills/taz5-cad/ (toolkit); ~/.claude/commands/taz5-cad.md (slash command — not in git, back up if machine rebuilt) |
| Type | Custom slash command (`/taz5-cad`) + skill files |
| Dependencies | OpenSCAD 2026.03.16 (`/Applications/OpenSCAD.app`) — snapshot build, Tahoe-compatible; CadQuery 2.7.0 under `/opt/homebrew/bin/python3.12` (python3/3.14 lacks OCP wheels) |
| Purpose | Generate print-ready parts for LulzBot TAZ 5 from plain language. Selects OpenSCAD vs CadQuery, generates parametric code, runs Pass 0 sanity render, then 2–3 autonomous 4-view render/critique/refine rounds before presenting final STL. ABS/PETG profiles and machine constraints baked in. |
| Output | ~/Desktop/taz5-renders/ — STL + 4 PNGs per part |
| Tested | 2026-03-28 — flange (2"×3", 1" center hole, 4×M4, 6mm boss); 4-view loop clean, STL manifold NoError |
| Render notes | --render flag (CGAL/F6) breaks on macOS Tahoe — render.sh uses F5 preview export. For complex booleans, run F6 manually in OpenSCAD GUI before slicing. |
| CadQuery notes | Always invoke with `/opt/homebrew/bin/python3.12`. Font permission warnings on import (WarnockPro) are harmless. |
| Phase 2 | Auto-upload STL to OctoPrint; slice profile selection; n8n → Discord print status |
| Added | 2026-03-28 |

---

### ghostty-terminal-env
| Field | Detail |
|---|---|
| Status | built |
| Health | active |
| Source | https://ghostty.org |
| Installed | femacbook — app via direct download; configs in dotfiles |
| Dependencies | Ghostty, tmux, Starship prompt (all via Homebrew); Tailscale for SSH shortcuts |
| Purpose | GPU-accelerated terminal host for tmux sessions. Runs as infrastructure dashboard via `control` alias — opens split panes SSHed into fepi41 and brekpi41. Session state persists via tmux-resurrect/continuum. |
| Config files | ~/.config/ghostty/config, ~/.tmux.conf, ~/.tmux/scripts/control-room.sh, ~/.ssh/config, ~/.zshrc |
| Shell | zsh + Starship prompt (fish installed but not active) |
| Key aliases | `control` (dashboard), `ta` (attach), `tn` (new session), `tl` (list) |
| Rebuild | See bible: "Ghostty Terminal Environment" |
| Added | 2026-03-12 |
---

## Planned / In Progress

---

## Retired Skills

### quickbooks-automation
| Field | Detail |
|---|---|
| Status | retired |
| Retired | 2026-02-28 |
| Notes | Superseded by pdf-to-qbo skill, which handles the WF statement import workflow that was originally planned here. |

---

## Community Resources to Monitor

Sources for new skills worth evaluating:

- https://github.com/hesreallyhim/awesome-claude-code — curated community list
- https://github.com/affaan-m/everything-claude-code — 13 agents, 43 skills
- https://github.com/VoltAgent/awesome-claude-code-subagents — 100+ subagents
- https://claudelog.com — community-tested techniques
- r/ClaudeAI — Reddit community

---

## Installation Notes by Machine

### MacBook Pro M1 (primary)
- last30days: installed ✓
- api-key-prompt: needs rebuild
- quickbooks: needs rebuild

### direct-lighting (terminal only)
- last30days: verify installation
- api-key-prompt: likely installed here — recover before machine is replaced
- quickbooks: likely installed here — recover before machine is replaced

---

## Recovery Checklist (iMac)

Before replacing the iMac, run the following in terminal:
```
ls ~/.claude/skills/
ls ~/.claude/agents/
cat ~/.claude/CLAUDE.md
```

Copy any files not already in the toolkit to this registry and 
document them before the machine is retired.
