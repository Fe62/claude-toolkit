# Session Plan Loader

## Step 1 — Find the PRD

List all `.md` files in the `projects/` folder. Show them as a numbered list and ask:

> Which project are we working on today? (enter number or name)

## Step 2 — Read and validate

Read the selected PRD. Check the **Document status** field first.

- If status is **Closed**: stop and say — "This PRD is marked Closed. Are you sure this is the right one, or do you want to pick a different project?"
- If status is **Open** or **In Progress**: continue.

## Step 3 — Extract the working brief

Pull the following fields and present them in this format:

---
**PROJECT:** [title from # heading]
**GOAL:** [One-Line Goal]
**MACHINES:** [Machine Inventory — list hostnames/IPs]
**CONSTRAINTS:** [Constraints]
**DEPENDENCIES:** [Dependencies — flag any that look unresolved]
**SUCCESS LOOKS LIKE:** [Success Criteria]

**PHASES:**
[List each phase with its name and checkbox state — use ✅ for checked/done, ⬜ for unchecked/open]

**ACTIVE PHASE (best guess):** [first unchecked phase]

**OPEN QUESTIONS:** [Open Questions — if none, omit this section]
---

## Step 4 — Confirm with Flint

After presenting the brief, ask:

> Does this match where you are? If the active phase is wrong or anything has changed since this was written, tell me now and I'll update my working context before we start.

Wait for confirmation before proceeding with any work.

## Notes

- Do not summarize or paraphrase the Goal or Success Criteria — copy them exactly.
- If a section is empty or missing, note it as "Not specified" rather than omitting the field.
- Do not begin any implementation work until Step 4 is confirmed.
