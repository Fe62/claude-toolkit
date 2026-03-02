# Master Reference — Claude Toolkit Bible

Last updated: 2026-03-01

---

## Purpose

This is the living manual for how Flint uses Claude Code. It captures 
skills developed, conventions established, lessons learned, and 
decisions made. Updated at the completion of every project via the 
Bible Entry section of each project file.

This document is also the first thing to paste into Claude Code as 
context when starting a new session on a new machine or project.

---

## Core Principles

These don't change project to project. They govern everything.

1. **Plan first** — no project starts without a PRD and plan in /projects
2. **Own your skills** — borrowed skills are a liability; adapt or rebuild over time
3. **Local first** — iCloud working copy, GitHub for backup, minimize API calls
4. **Simple over clever** — one layer of complexity at a time
5. **Never hardcode keys** — API keys always via prompt-on-entry or environment variables
6. **Keep the registry current** — log every skill immediately after installing

---

## Working Environment

| Item | Detail |
|---|---|
| Primary machine | MacBook Pro M1 |
| Secondary machine | iMac 2017 (terminal only, transitional) |
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

## Tailscale

### Tailscale CLI on macOS
The Tailscale CLI is not on the shell PATH by default on macOS.
Full path: `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
Example: `/Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4 hostname`

---

## Machine Inventory

| Hostname | Tailscale IP | Notes |
|---|---|---|
| femacbook | 100.74.137.113 | Primary dev machine (MacBook Pro M1) |
| fepi41 | 100.72.119.28 | Raspberry Pi, 8GB RAM, Python 3.11.9 via pyenv |
| brekpi41 | 100.77.133.46 | Raspberry Pi — offline as of 2026-03-01 |
| direct-lighting | 100.110.71.13 | Lighting controller |

Use Tailscale hostnames as canonical machine names throughout all toolkit files.

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

### 2026-02-28 — QB Desktop Mac QBO import requirements
QB Desktop Mac requires OFX 1.x SGML format — XML-based OFX 2.x is rejected silently.
Wells Fargo has at least two distinct CC statement layouts requiring separate parsers.
When QBO files won't download from Claude.ai, save as .txt and manually rename to .qbo.

---

## Open Mini-Projects

_Smaller items that don't warrant a full PRD but need to be done._

- [ ] Run pdf-to-qbo on full-year checking statements (P&A.checking.25)
- [ ] iCloud selective sync strategy — keep work/personal separated on iMac
- [ ] Recover skills from iMac before machine is retired
- [ ] Rebuild api-key-prompt skill
- [ ] Evaluate last30days for adaptation into owned version
- [ ] Explore Claude Code plugin marketplace for useful community skills

---

## Reference Links

- Claude Code docs: https://docs.claude.ai/claude-code
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Community skills: https://github.com/hesreallyhim/awesome-claude-code
- Community subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
- ClaudeLog: https://claudelog.com
