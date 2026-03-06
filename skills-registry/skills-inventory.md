# Skills Inventory

Last updated: 2026-03-06

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

### last30days
| Field | Detail |
|---|---|
| Status | borrowed |
| Health | active |
| Source | https://github.com/mvanhorn/last30days-skill |
| Installed | ~/.claude/skills/last30days |
| Dependencies | OpenAI API key, xAI API key (optional) |
| Purpose | Research agent — searches internet, Reddit, and other sources for information from the last 30 days. Use for staying current on Claude Code techniques, trends, best practices, any time-sensitive research query. |
| Risk | External dependency — if source repo changes or disappears, skill may break. Candidate for adaptation into owned version. |
| Notes | API keys managed via prompt-on-entry skill (see below). Never hardcode. |

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
| Purpose | Personal OS knowledge vault. Plain markdown throughout. Folders: inbox, daily, projects, areas, knowledge, resources, archive, assets. Every folder has a README with purpose and agent permission model. |
| Opened in | Obsidian (free) — vault at ~/Library/Mobile Documents/com~apple~CloudDocs/vault |
| Agent rules | Always folder-scoped. /archive and /assets read-only by default. /inbox is the only open-write folder. connector-registry.md in /resources tracks all active data paths. |
| Seed files | resources/connector-registry.md, resources/templates/project-template.md |
| Added | 2026-03-06 |

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
