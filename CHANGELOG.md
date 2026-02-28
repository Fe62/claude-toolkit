# Changelog

Format: [YYYY-MM-DD] — What changed and why (brief)

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

### 2026-02-28 — pdf-to-qbo skill completed
- Built local PDF-to-QBO converter for Wells Fargo bank and credit card statements
- Added dual CC format support (WF Signify Format A, WF Signature/FA Format B)
- Fixed QB Desktop Mac import errors: LEDGERBAL block and INTU.BID required
- quickbooks-automation retired; replaced by pdf-to-qbo
- Created session-context.md for cross-session tracking
