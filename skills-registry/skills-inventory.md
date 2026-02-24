# Skills Inventory

Last updated: 2026-02-23

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

## Planned / In Progress

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

### quickbooks-automation
| Field | Detail |
|---|---|
| Status | built (incomplete) |
| Health | needs-setup |
| Source | Originally built, resides on iMac — needs recovery |
| Installed | Unknown — check ~/.claude/skills/ on iMac |
| Dependencies | TBD — QuickBooks API credentials |
| Purpose | TBD — automation of QuickBooks workflows (details to be recovered from iMac and redeveloped) |
| Priority | Medium — revisit once toolkit foundation is stable |
| Notes | Was not fully worked out — will redesign from scratch with PRD |

---

## Retired Skills

_Nothing retired yet._

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

### iMac 2017 (terminal only)
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
