# End-of-Session Update Prompt

## How to use
1. Open Claude Code from toolkit root
2. Paste this prompt
3. Fill in the SESSION SUMMARY section
4. Claude will read current files, make targeted updates, stage for review

---

## PROMPT (paste into Claude Code)

I need you to update the toolkit documentation for today's session. 
Read the following files first, then make the updates described below.

**Files to read:**
- `session-context.md` (toolkit root)
- `skills-registry/skills-inventory.md`
- `bible/master-reference.md`
- `CHANGELOG.md`

**SESSION SUMMARY:**
<!-- Fill this in before running -->
Date: 
What we built or changed:
Skills added or modified:
Open items resolved:
New open items:
Lessons learned / bible-worthy notes:

---

**Update instructions:**

1. **session-context.md**
   - Add completed items to Recent Completions with today's date
   - Remove resolved open items from Open Work
   - Add any new open items to Open Work
   - Add new skills to Active Skills if any

2. **skills-registry/skills-inventory.md**
   - Add or update any skill entries based on SESSION SUMMARY
   - Update "Last updated" date at top

3. **bible/master-reference.md**
   - Add any lessons learned as new entries
   - Only add if genuinely reusable — don't add session-specific details

4. **CHANGELOG.md**
   - Add a new entry at the top in this format:
     ## YYYY-MM-DD
     - [what changed]
     - [what changed]

**After making all updates:**
- Show me a summary of every change made
- Stage all changed files with: git add -A
- Do NOT commit — I will review and commit manually

---
