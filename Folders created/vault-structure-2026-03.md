# Vault Structure — Claude Code Work Order

**Document status:** Active  
**Date started:** 2026-03-06  
**Parent project:** personal-os-2026-03.md  
**Owner:** Flint  
**Executed by:** Claude Code on femacbook  

---

## One-Line Goal

Create the Personal OS vault folder structure in iCloud Drive, populate
each folder with a minimal README, and prepare for Obsidian initialization.

---

## Prerequisites

- [ ] iCloud Drive active and syncing on femacbook
- [ ] Claude Code running on femacbook (not SSH remote)
- [ ] Terminal access confirmed

Verify iCloud Drive path before starting:
```bash
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/
```
Should list existing iCloud folders including claude-toolkit.

---

## Vault Location

```
~/Library/Mobile Documents/com~apple~CloudDocs/vault/
```

All commands below use `$VAULT` as shorthand. Claude Code should set
this variable first:

```bash
VAULT=~/Library/Mobile\ Documents/com~apple~CloudDocs/vault
```

---

## Step 1 — Create Folder Structure

Run in one pass. Creates all folders including nested ones.

```bash
mkdir -p "$VAULT"/{inbox,daily/briefs,projects,resources/{templates,checklists}}
mkdir -p "$VAULT"/areas/{home,cabin,health,finance,business}
mkdir -p "$VAULT"/knowledge/{concepts,references,people}
mkdir -p "$VAULT"/archive/{legacy-evernote,legacy-notion,legacy-notes-app,legacy-scans}
mkdir -p "$VAULT"/assets/{documents,images}
mkdir -p "$VAULT"/assets/scans/{financial,legal,general}
```

Verify:
```bash
find "$VAULT" -type d | sort
```

Expected output: 27 folders total.

---

## Step 2 — Populate README.md in Each Folder

Each folder gets a minimal README that describes its purpose and agent
permissions. This serves two purposes: Obsidian shows it as a note,
and agents can read it to understand scope before acting.

Claude Code should create each file below exactly as specified.

---

### /vault/README.md
```markdown
# Vault

Personal OS knowledge vault. All content is plain markdown.
Format and storage are independent of any application.

## Structure
- inbox/ — unsorted captures, cleared daily
- daily/ — daily notes and morning briefs
- projects/ — active projects
- areas/ — ongoing life domains
- knowledge/ — permanent notes and reference
- resources/ — templates and checklists
- archive/ — completed, retired, and migrated content
- assets/ — original files (PDFs, scans, images)

## Agent Rules
- Agents are always folder-scoped — never granted full vault access
- /archive and /assets are read-only to agents by default
- /inbox is the only folder agents may write to without a specific task
- See connector-registry.md in /resources for active data paths
```

---

### /vault/inbox/README.md
```markdown
# Inbox

Unsorted captures land here. Cleared during daily triage.

## Agent permissions
- Read: yes
- Write: yes (agents may deposit items here)
- Delete: no (human only)

## Human workflow
- Review daily during triage session
- Route each item to /projects, /areas, /knowledge, or /archive
- Nothing lives here permanently
```

---

### /vault/daily/README.md
```markdown
# Daily

Daily notes and morning briefs. One file per day.

## Naming convention
YYYY-MM-DD.md — e.g. 2026-03-06.md

## Agent permissions
- Read: yes
- Write: /daily/briefs/ only (generated morning briefs)
- Daily note skeleton: agent may create YYYY-MM-DD.md stub only

## Subfolders
- briefs/ — generated morning briefs, read-only after creation
```

---

### /vault/daily/briefs/README.md
```markdown
# Morning Briefs

Auto-generated each morning by n8n workflow on Mac Mini.
Pulls from fepi41 (sensors, home automation) and brekpi41 (cabin status).

## Format
YYYY-MM-DD-brief.md

## Agent permissions
- Read: yes
- Write: yes (generation only — one write per day)
- Edit/delete: no
```

---

### /vault/projects/README.md
```markdown
# Projects

Active projects with defined start and end dates.
One subfolder per project.

## Naming convention
project-name/ (lowercase, hyphenated)

## Agent permissions
- Read: yes (scoped to specific project folder when tasked)
- Write: yes (scoped to specific project folder only)
- Cross-project write: no

## Template
See /resources/templates/project-template.md
```

---

### /vault/areas/README.md
```markdown
# Areas

Ongoing life domains with no end date.
Standards and context that apply continuously.

## Domains
- home/ — house systems, maintenance, improvement
- cabin/ — cabin systems, seasonal, improvements  
- health/ — medical, fitness, personal
- finance/ — accounts, planning (no raw statements — those go in /assets)
- business/ — operating notes, not projects

## Agent permissions
- Read: yes (scoped to specific area when tasked)
- Write: yes (scoped to specific area only)
```

---

### /vault/areas/home/README.md
```markdown
# Home

House systems, maintenance logs, improvement projects, and
ongoing operational notes.

Sensor data summaries from fepi41 (LoRaWAN, irrigation, sewer)
are written here by the morning brief agent.
```

---

### /vault/areas/cabin/README.md
```markdown
# Cabin

Cabin systems, seasonal notes, improvement projects, and
ongoing operational context.

Status summaries from brekpi41 (Starlink, solar) are written
here by the morning brief agent.
```

---

### /vault/areas/health/README.md
```markdown
# Health

Medical records summaries, fitness notes, personal health context.

## Note
Original medical documents are stored in /assets/documents or
/assets/scans/general — not here. This folder holds working notes
and summaries only.
```

---

### /vault/areas/finance/README.md
```markdown
# Finance

Financial planning notes, account summaries, tax context.

## Important
Raw statements and original financial documents are stored in
/assets/scans/financial — never in this folder.
This folder holds working notes, summaries, and planning only.
```

---

### /vault/areas/business/README.md
```markdown
# Business

Operating notes for active business entities.
Project-specific work lives in /projects — this folder holds
ongoing operational context, contacts, and reference.
```

---

### /vault/knowledge/README.md
```markdown
# Knowledge

Permanent notes. Content here does not expire.

## Subfolders
- concepts/ — atomic notes, one idea per file (Zettelkasten-style)
- references/ — summaries of books, articles, research
- people/ — contact context, relationship notes

## Agent permissions
- Read: yes
- Write: no (human-authored only, by default)
- Exception: agent may propose a note to /inbox for human review
```

---

### /vault/knowledge/concepts/README.md
```markdown
# Concepts

Atomic notes. One idea per file.
Files link to each other using [[note name]] syntax.

## Naming convention
idea-or-concept-name.md (lowercase, hyphenated)
```

---

### /vault/knowledge/references/README.md
```markdown
# References

Summaries of books, articles, research, and external sources.
Not the original source — a working summary in your own words.

## Naming convention
author-short-title.md or source-topic-YYYY.md
```

---

### /vault/knowledge/people/README.md
```markdown
# People

Notes on contacts, relationships, and relevant context.
One file per person or organization.

## Naming convention
firstname-lastname.md or organization-name.md
```

---

### /vault/resources/README.md
```markdown
# Resources

Reusable templates and checklists.

## Subfolders
- templates/ — note and document templates
- checklists/ — recurring process checklists

## Special files
- connector-registry.md — all active data paths into the system
```

---

### /vault/resources/templates/README.md
```markdown
# Templates

Reusable note templates. Copy to target folder, rename, fill in.

## Available templates (add as built)
- project-template.md
- daily-note-template.md
- area-note-template.md
- meeting-note-template.md
```

---

### /vault/resources/checklists/README.md
```markdown
# Checklists

Recurring process checklists. These are reference documents —
copy and use, do not edit the original.
```

---

### /vault/archive/README.md
```markdown
# Archive

Completed projects, retired notes, and migrated legacy content.

## Agent permissions
- Read: yes
- Write: no (by default — explicit task required)
- Delete: no (human only, never agent)

## Subfolders
- legacy-evernote/ — migrated Evernote content
- legacy-notion/ — migrated Notion content
- legacy-notes-app/ — migrated Apple Notes content
- legacy-scans/ — OCR output from scanned documents
```

---

### /vault/assets/README.md
```markdown
# Assets

Original files referenced by vault notes.
Binary files live here — PDFs, scans, images.

## Agent permissions
- Read: yes (for ingestion and indexing)
- Write: no (human places files here)
- Delete: no (never — originals are records)

## Subfolders
- documents/ — text-layer PDFs, directly extractable
- scans/ — original scan files
  - scans/financial/ — financial originals, permanent retention
  - scans/legal/ — legal originals, permanent retention
  - scans/general/ — all other scans
- images/ — photos, diagrams, reference images
```

---

### /vault/assets/scans/financial/README.md
```markdown
# Financial Scans

Original scan files for all financial documents.

## Retention
Permanent. These files are never deleted.
The corresponding extracted .md lives in /archive/legacy-scans.

## Naming convention
YYYY-MM-DD-institution-description.pdf (or original filename preserved)
```

---

### /vault/assets/scans/legal/README.md
```markdown
# Legal Scans

Original scan files for legal documents, contracts, and records.

## Retention
Permanent. These files are never deleted.
```

---

### /vault/assets/scans/general/README.md
```markdown
# General Scans

Original scan files for all non-financial, non-legal documents.

## Retention
Retained unless explicitly marked for disposal after extraction.
```

---

## Step 3 — Create Seed Files

These are not READMEs — they are the first real working files in the vault.

### Connector Registry
```bash
cat > "$VAULT/resources/connector-registry.md" << 'EOF'
# Connector Registry

All active data paths into the Personal OS system.
Update this file when any connector is added, changed, or retired.

Last updated: 2026-03-06

---

| Connector | Source | Destination | Type | Status |
|---|---|---|---|---|
| soil-moisture | fepi41 LoRaWAN | Mac Mini n8n | push/cron | planned |
| sewer-level | fepi41 LoRaWAN | Mac Mini n8n | push/alert | planned |
| irrigation-relay | fepi41 LoRaWAN | Mac Mini n8n | push/cron | planned |
| cabin-solar | brekpi41 | Mac Mini n8n | push/cron | planned |
| cabin-starlink | brekpi41 | Mac Mini n8n | push/cron | planned |
| financial-data | fepi41 cron | Mac Mini n8n | push/scheduled | planned |

---

## Adding a New Connector
1. Add a row to the table above
2. Status: planned → active when wired and tested
3. Note the data format and push mechanism in a separate row if complex
EOF
```

### Project Template
```bash
cat > "$VAULT/resources/templates/project-template.md" << 'EOF'
# [Project Name]

**Status:** Active / Complete  
**Started:** YYYY-MM-DD  
**Completed:**  
**Area:** home / cabin / business / personal  

---

## One-Line Goal

---

## Background

---

## Success Criteria

- [ ] 

---

## Open Questions

- [ ] 

---

## Notes & Decisions

---

## Outcomes & Lessons

EOF
```

### Today's Daily Note Stub
```bash
TODAY=$(date +%Y-%m-%d)
cat > "$VAULT/daily/${TODAY}.md" << EOF
# ${TODAY}

## Morning Brief
_See briefs/${TODAY}-brief.md when available_

## Today's Focus

## Inbox
_Items to triage_

## Notes

## End of Day
EOF
```

---

## Step 4 — Verify Structure

```bash
echo "=== Vault folder count ==="
find "$VAULT" -type d | wc -l

echo "=== All folders ==="
find "$VAULT" -type d | sort

echo "=== All files ==="
find "$VAULT" -type f | sort
```

Expected: 27 folders, 22+ files (READMEs + seed files + today's daily note).

---

## Step 5 — Obsidian Initialization

Obsidian does not need a script — it is configured by opening the vault folder.

1. Download and install Obsidian from obsidian.md (free)
2. Open Obsidian → "Open folder as vault"
3. Navigate to: `~/Library/Mobile Documents/com~apple~CloudDocs/vault`
4. Select folder → Open

### Minimal Settings (apply immediately, nothing else)
- **Files & Links → Default location for new notes:** Same folder as current file
- **Files & Links → Use [[Wikilinks]]:** On
- **Editor → Spell check:** On or off per preference
- **No plugins enabled at this stage** — keep it minimal

### Verify
- [ ] Obsidian opens vault and shows folder tree in left sidebar
- [ ] README.md visible in root
- [ ] Today's daily note visible in /daily/
- [ ] No errors or warnings on open

---

## Completion Criteria

- [ ] All 27 folders created in iCloud Drive
- [ ] README.md in every folder
- [ ] Connector registry created in /resources
- [ ] Project template created in /resources/templates
- [ ] Today's daily note stub created in /daily
- [ ] Obsidian opens vault cleanly
- [ ] Structure visible and navigable in Obsidian sidebar
- [ ] iCloud sync confirmed (files visible on another device or iCloud.com)

---

## What Comes Next

With vault structure in place:

1. **Track B handoff** — when legacy-staging is ready, automated
   inventory agent reads it and writes to /vault/inbox/legacy-inventory.md
2. **Daily note automation** — n8n on Mac Mini generates daily stub each morning
3. **Morning brief pipeline** — fepi41 + brekpi41 data flows to /daily/briefs/
4. **Vector DB ingestion** — Mac Mini points Chroma at /vault, indexes all .md files

---

## Notes for Claude Code

- Use `$VAULT` variable throughout — do not hardcode the path
- iCloud Drive path has a space: `Mobile\ Documents` — escape it or quote it
- Create all folders before creating any files
- If any mkdir fails, stop and report — do not continue with partial structure
- Verify step (Step 4) must pass before marking complete
- Do not modify claude-toolkit/ or any existing iCloud content
