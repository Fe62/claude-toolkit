# Session Context

_Tracks completions, open work, and active skill state across sessions._
_Updated at end of each session via the /update skill._

---

## Completions

| Date | What |
|---|---|
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

- [ ] iMac Pre-Retirement Checklist
- [ ] Install gh (GitHub CLI) via Homebrew
- [ ] Install jq via Homebrew
- [ ] Recover api-key-prompt skill
- [ ] Recover quickbooks skill
- [ ] Document pdfplumber as explicit dependency (requirements.txt or registry note)
- [ ] iCloud selective sync strategy (work/personal separation)
- [ ] Evaluate last30days for owned adaptation — set a review date
- [ ] Explore community skills: github.com/hesreallyhim/awesome-claude-code
- [ ] Evaluate market-snapshot.py from Nick's tools (hourly SPY/QQQ/VIX)
- [x] Add update and simplify to Active Skills table in session-context.md
- [x] Push toolkit updates to GitHub

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
