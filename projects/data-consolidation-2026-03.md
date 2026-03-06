# Data Consolidation — Human Agent Work Order

**Document status:** Active  
**Date started:** 2026-03-05  
**Parent project:** personal-os-2026-03.md  
**Owner:** Flint  
**Executed by:** Human agent (runs parallel to Phase 1 technical work)  

---

## One-Line Goal

Locate, consolidate, and triage all legacy data from four physical sources
into a single staging area on femacbook, ready for inventory and processing.

---

## Why This Is Parallel, Not Sequential

The vault structure and tooling (Phase 1 technical) can be built while this
work runs. Both tracks feed the same ingestion pipeline. Neither blocks the
other. The only dependency is that this work must be complete before bulk
OCR and migration begins.

---

## Success Criteria

- [ ] All four sources assessed
- [ ] Old hard drives tested — data recovered if accessible
- [ ] Single staging folder created on femacbook
- [ ] All legacy data copied into staging (not moved — originals untouched until confirmed)
- [ ] Obvious duplicates flagged
- [ ] Rough sort by domain completed (finance / business / home / personal)
- [ ] Inventory handoff file written — ready for automated inventory pass

---

## Staging Area

Create this folder on femacbook before starting:

```
~/Desktop/legacy-staging/
  /from-femacbook-local/
  /from-icloud/
  /from-dropbox/
  /from-harddrive-1/
  /from-harddrive-2/
  /duplicates-review/
  /unsortable/
  HANDOFF-NOTES.md         ← running notes as you go
```

Keep sources separated at this stage. Do not merge yet.
Source separation makes deduplication easier and traceable.

---

## Work Order by Source

---

### Source 1 — Old Hard Drives
**Do this first. Drives are the only non-recoverable risk.**

#### Step 1 — Physical assessment
- [ ] Locate all old hard drives
- [ ] Note in HANDOFF-NOTES.md: drive count, approximate age, last known machine
- [ ] Identify connection type needed (USB, USB-C, SATA adapter)
- [ ] Gather adapters or USB enclosure if needed

#### Step 2 — Test each drive
For each drive:
- [ ] Connect to femacbook
- [ ] Does it mount? (appears in Finder sidebar)
  - **Yes → proceed to Step 3**
  - **No → note in HANDOFF-NOTES.md, set aside for recovery decision**

#### Step 3 — Copy data off (if mounted)
- [ ] Open drive in Finder — note what's there in HANDOFF-NOTES.md
- [ ] Copy entire contents to staging:
  ```
  cp -R /Volumes/[drivename]/ ~/Desktop/legacy-staging/from-harddrive-1/
  ```
- [ ] Verify copy completed without errors
- [ ] Note: do NOT reformat or erase drive until vault migration is confirmed complete

#### Step 4 — Non-mounting drives
- [ ] List what you believe is on each non-mounting drive
- [ ] Decide: worth professional recovery? (typically $300-800)
- [ ] Note decision in HANDOFF-NOTES.md
- [ ] If recovery — set aside and continue with other sources

---

### Source 2 — femacbook Local
**Highest volume. Work methodically by folder.**

#### Step 1 — Identify candidate folders
Common locations to check:
- [ ] ~/Documents
- [ ] ~/Downloads (may have accumulated files)
- [ ] ~/Desktop (anything not already in Documents)
- [ ] ~/Pictures (if document images live here)
- [ ] Any project-specific folders in home directory
- [ ] ~/Library/Application Support/Notefile or similar note apps

#### Step 2 — Copy to staging
- [ ] Copy identified folders to:
  ```
  ~/Desktop/legacy-staging/from-femacbook-local/
  ```
- [ ] Do not delete originals yet
- [ ] Note any folders skipped and why in HANDOFF-NOTES.md

---

### Source 3 — iCloud Drive
**Likely overlaps with femacbook local. Keep separate for now.**

#### Step 1 — Confirm iCloud sync status
- [ ] Open Finder → iCloud Drive
- [ ] Confirm files are downloaded locally (not cloud-only icons)
- [ ] If cloud-only: right-click → Download — wait for completion

#### Step 2 — Identify legacy content
- [ ] Note which iCloud folders contain legacy documents vs. active working files
- [ ] Active toolkit folder (claude-toolkit/) — skip, already managed
- [ ] Everything else is a candidate

#### Step 3 — Copy to staging
- [ ] Copy legacy iCloud content to:
  ```
  ~/Desktop/legacy-staging/from-icloud/
  ```

---

### Source 4 — Dropbox
**Treat like a remote folder once accessible.**

#### Step 1 — Confirm access
- [ ] Open Dropbox — confirm logged in and synced
- [ ] If not synced locally: sync needed folders first

#### Step 2 — Identify legacy content
- [ ] Note folder structure in HANDOFF-NOTES.md
- [ ] Identify which folders contain legacy documents

#### Step 3 — Copy to staging
- [ ] Copy legacy Dropbox content to:
  ```
  ~/Desktop/legacy-staging/from-dropbox/
  ```

---

## Deduplication Pass

Once all four sources are in staging:

#### Step 1 — Obvious duplicates
Run this command to find files with identical names across source folders:
```bash
find ~/Desktop/legacy-staging -type f -name "*.pdf" | \
  xargs -I{} basename {} | sort | uniq -d > ~/Desktop/legacy-staging/duplicates-review/duplicate-names.txt
```
- [ ] Review duplicate-names.txt
- [ ] For each duplicate: open both, confirm they are the same file
- [ ] Keep one copy, move other to /duplicates-review/ (do not delete yet)

#### Step 2 — Note unresolved duplicates
- [ ] List any same-name files that appear to be different versions in HANDOFF-NOTES.md
- [ ] These need human judgment — flag for Flint review

---

## Rough Domain Sort

After dedup, do a first-pass sort into broad domains.
This does not need to be perfect — it just reduces the inventory workload.

Create subfolders in staging:
```
~/Desktop/legacy-staging/sorted/
  /finance/       ← statements, tax docs, receipts, investments
  /business/      ← contracts, correspondence, project files
  /home/          ← property, maintenance, systems
  /cabin/         ← cabin-specific docs
  /personal/      ← health, personal records, other
  /unknown/       ← anything you can't quickly classify
```

**Rule of thumb:** 30 seconds per file maximum. If you can't tell in 30
seconds, it goes to /unknown. Speed matters more than precision here —
the AI handles fine-grained classification later.

---

## Proprietary Format Triage

While sorting, flag any files in unusual formats:

- [ ] Create a list in HANDOFF-NOTES.md: filename, format, estimated date
- Formats to flag: .wpd, .wps, .fp7, .fm, old .doc (pre-2007), .key (old), .pages (old), any format you can't open on femacbook

For each flagged file:
- [ ] Try opening on femacbook — does it open?
- [ ] If yes: note it opens, continue
- [ ] If no: add to proprietary-formats list for separate handling decision

---

## Handoff Notes File

Maintain HANDOFF-NOTES.md throughout. At minimum record:

```markdown
# Legacy Consolidation — Handoff Notes

## Hard Drives
- Drive 1: [description, mounted Y/N, contents summary]
- Drive 2: [description, mounted Y/N, contents summary]

## Source Summaries
- femacbook local: [rough file count, notable folders]
- iCloud: [rough file count, notable folders]
- Dropbox: [rough file count, notable folders]

## Duplicate Files
- [list of confirmed duplicates and which copy was kept]
- [list of version conflicts needing review]

## Proprietary Formats
- [filename, format, can-open Y/N]

## Domain Sort Summary
- Finance: ~[n] files
- Business: ~[n] files
- Home: ~[n] files
- Cabin: ~[n] files
- Personal: ~[n] files
- Unknown: ~[n] files

## Issues / Questions for Flint
- [anything that needs a decision]

## Estimated Total File Count
- [rough total across all sources post-dedup]
```

---

## Completion Criteria

This work order is complete when:
- [ ] All four sources assessed and copied to staging
- [ ] Hard drive situation resolved (data recovered or recovery decision made)
- [ ] Dedup pass complete
- [ ] Rough domain sort complete
- [ ] Proprietary formats listed
- [ ] HANDOFF-NOTES.md written and readable
- [ ] Staging folder handed back to Phase 1 technical track for automated inventory

**Estimated time:** 1-2 focused work sessions depending on drive count
and volume. Domain sort is the longest task — do it in passes, not
one sitting.

---

## What Happens Next

This staging folder and HANDOFF-NOTES.md become the input to the
automated inventory pass (Phase 1 technical). The agent reads the
staging folder, processes HANDOFF-NOTES.md for context, and generates
legacy-inventory.md — the master document that drives all subsequent
OCR and migration work.

Nothing in staging is deleted until legacy-inventory.md is reviewed
and approved by Flint.
