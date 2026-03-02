# Toolkit End-of-Session Update

Read the following files before making any changes:
- `session-context.md`
- `skills-registry/skills-inventory.md`
- `bible/master-reference.md`
- `CHANGELOG.md`

Then work through these questions in order, waiting for my confirmation before moving to the next:

1. Review your tool calls, file changes, and commands from this session. Draft a summary 
   of what was built or changed. Show it to me and ask: "Does this look right, anything 
   to add or correct?"

2. Check if any skill files were created or modified this session. Draft what changed. 
   Show it to me and ask: "Anything to add or correct?"

3. Show me the current Open Work list from session-context.md and ask: "Which of these 
   got resolved today?"

4. Review this session for any unfinished threads, partial work, or decisions that were 
   deferred. Suggest new open items, then ask: "Anything else to add?"

5. Review this session for patterns, mistakes avoided, or wins worth repeating. Suggest 
   lessons, then ask: "I'll also check with Claude.ai — paste any additional lessons here, 
   or say none."

Once you have all my answers, draft the updates to all four files without asking further questions:

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