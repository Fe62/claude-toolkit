# Toolkit End-of-Session Update

Read the following files before making any changes:
- `session-context.md`
- `skills-registry/skills-inventory.md`
- `bible/master-reference.md`
- `CHANGELOG.md`

Then ask me for the session summary using this structure:

> **Date:** (today's date)
> **Built or changed:** 
> **Skills added or modified:** 
> **Open items resolved:** 
> **New open items:** 
> **Lessons learned:** 

Once I provide the summary, make targeted updates to all four files:

1. **session-context.md** — add completions with today's date, update Open Work (remove resolved, add new), update Active Skills if needed
2. **skills-registry/skills-inventory.md** — add or update skill entries, update "Last updated" date
3. **bible/master-reference.md** — add genuine reusable lessons only, nothing session-specific
4. **CHANGELOG.md** — new entry at top, format:
   ```
   ## YYYY-MM-DD
   - item
   - item
   ```

After all updates:
- Show me a diff summary of every change made
- Run `git add -A`
- Do NOT commit — I will review and commit manually
