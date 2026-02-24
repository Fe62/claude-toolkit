# Claude Toolkit

A portable, private library of skills, prompts, subagents, and project 
documents for working effectively with Claude Code.

## Quick Setup on a New Machine

1. **Verify Claude Code is installed**
```
   claude --version
```
   If not installed: https://docs.claude.ai/claude-code

2. **Confirm iCloud Drive is syncing this folder**
```
   ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit
```
   You should see this README. If not, wait for iCloud to sync or 
   check iCloud Drive settings.

3. **Clone the GitHub backup (if iCloud isn't available)**
```
   git clone https://github.com/Fe62/claude-toolkit.git
```

4. **Point Claude Code to this toolkit**
```
   cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit
   claude .
```
   Claude Code will automatically read CLAUDE.md on launch.

5. **Check your skills**
   Open /skills-registry/skills-inventory.md and reinstall any 
   skills marked as requiring local setup.

6. **Set up API keys**
   Never stored here. See the API key management skill in 
   /skills-registry/skills-inventory.md for instructions.

---

## How to Use This Toolkit Day-to-Day

**Starting a new project**
Copy /projects/_project-template.md, rename it topic-YYYY-MM.md, 
fill in the PRD and Plan sections before writing a single line of 
instructions to Claude Code.

**Adding a new skill**
Install or build the skill, then immediately log it in 
/skills-registry/skills-inventory.md. Don't let the registry 
fall behind.

**Updating the bible**
After completing any project or learning something worth keeping, 
add a synopsis to /bible/master-reference.md. Keep entries brief — 
one paragraph per skill or lesson.

**Pushing to GitHub**
Push deliberately after meaningful changes — not after every edit.
```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit
git add .
git commit -m "brief description of what changed"
git push
```

---

## Folder Structure
```
claude-toolkit/
├── CLAUDE.md                    ← Claude Code reads this first
├── README.md                    ← you are here
├── CHANGELOG.md                 ← log of meaningful changes
├── bible/
│   └── master-reference.md     ← living manual
├── projects/
│   ├── _project-template.md    ← blank template
│   └── [topic-YYYY-MM].md      ← one file per project
├── skills-registry/
│   └── skills-inventory.md     ← all skills, sources, status
├── prompts/
│   └── _readme.md              ← reusable prompt templates
├── claude-md-templates/
│   └── _readme.md              ← CLAUDE.md starters
└── subagents/
    └── _readme.md              ← specialist agent definitions
```

---

## Machines

| Machine | Role | Claude Code | Notes |
|---|---|---|---|
| MacBook Pro M1 | Primary | Full | Main working machine |
| iMac 2017 | Secondary | Terminal only | Transitional, replacing soon |

---

## Repository

- **Working copy:** iCloud Drive (local-first, always current)
- **Backup/version control:** GitHub private repo (push deliberately)
- **Do not** set up auto-sync or auto-push — keep pushes intentional
