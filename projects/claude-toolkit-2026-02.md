# Claude Toolkit Foundation

**Document status:** Active
**Date started:** 2026-02-23
**Date completed:** 
**Owner:** Flint

---

## One-Line Goal

Build a portable, version-controlled toolkit in iCloud Drive that 
serves as the foundation for all future Claude Code automations, 
skills, and workflows.

---

## Background & Context

Starting from scratch with Claude Code as a non-programmer. The goal 
is to build infrastructure first — before any specific automations or 
projects. Everything that follows (subagents, prompts, workflows, the 
bible) depends on this structure being in place and working consistently 
across two machines. The 2017 iMac is transitional; the system must 
work entirely from terminal on that machine and carry forward cleanly 
when it's replaced. One existing skill (last30days) is already in use 
and needs to be documented and integrated. Two skills on the iMac 
(api-key-prompt, quickbooks) need recovery before that machine retires.

---

## Success Criteria

- [ ] Folder structure created in iCloud Drive on MacBook Pro M1
- [ ] All 7 files created and in place
- [ ] Initialized as private GitHub repo
- [ ] First commit pushed to GitHub
- [ ] Claude Code reads CLAUDE.md correctly from toolkit root
- [ ] iCloud sync verified on iMac
- [ ] Skills on iMac identified and logged in registry
- [ ] New machine onboarding possible in under 15 minutes

---

## Scope

**In scope:**
- Folder structure design and creation
- All 7 foundation files (CLAUDE.md, README.md, CHANGELOG.md, 
  master-reference.md, skills-inventory.md, _project-template.md, 
  this file)
- GitHub private repo initialization
- iCloud Drive setup as working copy

**Out of scope:**
- iCloud selective sync strategy (separate mini-project)
- Populating prompts library (Phase 2)
- Building subagents (Phase 2)
- Rebuilding api-key-prompt skill (separate project)
- QuickBooks automation (separate project)
- Recovering iMac skills (separate checklist in skills-inventory.md)

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| Claude Code installed | ✓ Complete | Both machines |
| iCloud Drive active | ✓ Complete | MacBook Pro M1 |
| GitHub account | ✓ Complete | Fe62 |
| iCloud on iMac | Pending | Needs enabling for sync |

---

## Constraints

- Terminal-friendly throughout — no GUI dependencies
- Plain markdown only — no proprietary formats
- Must work identically on both machines
- Local-first — minimize API calls
- No auto-push to GitHub — all pushes deliberate
- Never store API keys in any file

---

## Plan

### Phase 1 — Create files (current)
- [x] Draft CLAUDE.md
- [x] Draft README.md
- [x] Draft CHANGELOG.md
- [x] Draft bible/master-reference.md
- [x] Draft skills-registry/skills-inventory.md
- [x] Draft projects/_project-template.md
- [x] Draft projects/claude-toolkit-2026-02.md

### Phase 2 — Build on machine
- [ ] Create folder structure in iCloud Drive
- [ ] Copy all 7 files into correct locations
- [ ] Initialize git repo inside claude-toolkit folder
- [ ] Create private GitHub repo (Fe62/claude-toolkit)
- [ ] Push first commit
- [ ] Open Claude Code from toolkit root, verify CLAUDE.md loads
- [ ] Test on iMac — verify iCloud sync, verify terminal access

### Phase 3 — Validate and hand off to Phase 2 projects
- [ ] Enable iCloud Drive on iMac
- [ ] Verify toolkit accessible on iMac via terminal
- [ ] Run iMac skills recovery checklist
- [ ] Log any recovered skills in skills-inventory.md
- [ ] Update CHANGELOG.md
- [ ] Push final commit for this project

---

## Open Questions

- [ ] iCloud selective sync — how to keep work/personal separated 
      on iMac (separate mini-project)
- [ ] last30days — adapt into owned version or keep borrowed for now?

---

## Outcomes & Lessons

_To be filled in on completion._

---

## Bible Entry

_To be filled in on completion and copied to master-reference.md._
