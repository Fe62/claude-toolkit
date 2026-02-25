#!/bin/zsh

# load-context.sh
# Builds a context block from toolkit files and copies it to clipboard.
# Use at the start of any new Claude conversation to restore full project context.

TOOLKIT=~/Library/Mobile\ Documents/com~apple~CloudDocs/claude-toolkit

echo ""
echo "=== Load Context ==="
echo ""
echo "  1. Quick  — orientation block only (recommended)"
echo "  2. Full   — orientation + all active project files"
echo ""
read "CHOICE?Choice: "

# --- Build quick orientation block ---
QUICK=$(cat <<'ORIENTATION'
## Claude Toolkit — Session Context

**Owner:** Flint  
**Primary machine:** MacBook Pro M1  
**Secondary machine:** iMac 2017 (transitional, terminal only)  
**Working copy:** iCloud Drive → claude-toolkit/  
**GitHub:** github.com/Fe62/claude-toolkit (private, push deliberately)  
**File format:** Plain markdown throughout  
**Naming convention:** topic-YYYY-MM  

---

### Core Principles
1. Plan first — no project starts without a PRD in /projects
2. Own your skills — borrowed skills are a liability
3. Local first — iCloud working copy, GitHub for backup
4. Simple over clever — one layer of complexity at a time
5. Never hardcode keys — always via api-key-prompt or environment variables
6. Keep the registry current — log every skill immediately after installing

---

### Toolkit Structure
- `/projects` — PRDs and plans, one file per project
- `/skills-registry/skills-inventory.md` — every skill, source, and status
- `/skills` — installed skill scripts
- `/prompts` — reusable prompt templates
- `/subagents` — specialist agent definitions
- `/claude-md-templates` — CLAUDE.md starters for new projects
- `/bible/master-reference.md` — full conventions and lessons learned

---

### Active Skills
- **last30days** (borrowed) — research agent, searches last 30 days. Installed at ~/.claude/skills/last30days. Requires OpenAI API key.
- **api-key-prompt** (built) — secure runtime key entry, never stores keys. Located at skills/api-key-prompt/set-api-key.sh.

---

### Open Work
- [ ] iMac skills recovery (api-key-prompt, quickbooks) before machine retires
- [ ] iCloud selective sync strategy for iMac (work/personal separation)
- [ ] Rebuild quickbooks-automation with full PRD
- [ ] Evaluate last30days for adaptation into owned version
- [ ] Explore community skills: github.com/hesreallyhim/awesome-claude-code

---

### Recent Completions (2026-02-24)
- Toolkit Phase 2 complete — folder structure, GitHub, Claude Code verified
- api-key-prompt skill rebuilt for zsh, supports Anthropic/OpenAI/Schwab/QuickBooks/custom
- iCloud sync enabled on iMac, toolkit synced successfully

---

*To load full project file details, run load-context.sh and choose Full.*
ORIENTATION
)

if [[ "$CHOICE" == "1" ]]; then
  echo "$QUICK" | pbcopy
  echo ""
  echo "✓ Quick context copied to clipboard."
  echo "  Paste into any new Claude conversation to restore context."
  echo ""

elif [[ "$CHOICE" == "2" ]]; then
  # Start with quick block
  FULL="$QUICK"
  FULL+="\n\n---\n\n## Active Project Files\n"

  # Append all project files
  for f in "$TOOLKIT/projects/"*.md; do
    if [[ "$(basename $f)" != "_project-template.md" ]]; then
      FULL+="\n\n---\n\n### $(basename $f)\n\n"
      FULL+="$(cat $f)"
    fi
  done

  # Append skills inventory
  FULL+="\n\n---\n\n### Skills Inventory\n\n"
  FULL+="$(cat $TOOLKIT/skills-registry/skills-inventory.md)"

  echo "$FULL" | pbcopy
  echo ""
  echo "✓ Full context copied to clipboard."
  echo "  Includes orientation + all project files + skills inventory."
  echo ""

else
  echo "Invalid choice. Exiting."
  exit 1
fi
