# Session Context

_Tracks completions, open work, and active skill state across sessions._
_Updated at end of each session via the /update skill._

---

## Completions

| Date | What |
|---|---|
| 2026-03-01 | raspberry-pi-expansion — PRD created, fepi41 fully set up (Python 3.11.9 via pyenv, ai-hedge-fund installed and tested), machine inventory confirmed with Tailscale IPs |
| 2026-02-28 | pdf-to-qbo — local PDF-to-QBO converter for WF statements, dual CC format support, QB Desktop Mac import fixes (LEDGERBAL, INTU.BID) |
| 2026-02-24 | load-context — quick + full modes, clipboard copy, alias + keyboard shortcut |
| 2026-02-24 | api-key-prompt — rebuilt for zsh, session-only export, multi-service |
| 2026-02-23 | Toolkit foundation — folder structure, CLAUDE.md, README, registry, GitHub |

---

## Open Work

- [ ] Add fepi41 as SSH remote in Claude Code
- [ ] Power on brekpi41, confirm username, add as SSH remote in Claude Code
- [x] Sweep "iMac 2017" references → replace with "direct-lighting" across all toolkit files (CLAUDE.md, master-reference.md, skills-inventory.md, README.md, load-context.sh)
- [ ] Push toolkit updates to GitHub
- [x] Close raspberry-pi-expansion-2026-03.md PRD
- [ ] iMac Pre-Retirement Checklist
- [ ] Install gh (GitHub CLI) via Homebrew
- [ ] Install jq via Homebrew
- [ ] Recover api-key-prompt skill
- [ ] Recover quickbooks skill
- [ ] Document pdfplumber as explicit dependency (requirements.txt or registry note)
- [ ] iCloud selective sync strategy (work/personal separation)
- [ ] Evaluate last30days for owned adaptation — set a review date
- [ ] Explore community skills: github.com/hesreallyhim/awesome-claude-code

---

## Active Skills

| Skill | Location | Status |
|---|---|---|
| pdf-to-qbo | skills/pdf-to-qbo/convert_statements.py | active |
| load-context | skills/load-context/load-context.sh | active |
| api-key-prompt | skills/api-key-prompt/set-api-key.sh | active |
| last30days | ~/.claude/skills/last30days | active (borrowed) |
| ai-hedge-fund | fepi41 ~/ai-hedge-fund | active (borrowed) |
