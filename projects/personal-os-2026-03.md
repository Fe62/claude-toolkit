# Personal OS — Knowledge Vault, Agentic Infrastructure & Daily Interface

**Document status:** Active  
**Date started:** 2026-03-05  
**Date completed:**  
**Owner:** Flint  

---

## One-Line Goal

Build a software-agnostic, agent-ready personal operating system that consolidates
fragmented knowledge, automates daily situational awareness, and presents a unified
interface for triage, deep work, and life management.

---

## Design Principles

1. **Data is sovereign** — format and storage are independent of any UI or app.
   No data is ever orphaned by a software change.
2. **Structure enables agents** — folder layout gives agents bounded, logical scope.
   An agent always knows where to read, where to write, and what to leave alone.
3. **Simple over clever** — one layer of complexity at a time. No feature added
   until the layer below it is stable.
4. **Local first** — all data lives on your hardware. AI cloud APIs are called;
   your knowledge is never uploaded to one.
5. **Chores before chat** — the system serves triage and situational awareness
   first, deep work second. Automation does the chores so you don't have to.
6. **Build for extension** — every data path is a pipe with connectors, not a
   hard-wired integration. New sensors, workflows, data sources, or UI surfaces
   plug in without restructuring what already exists. The system anticipates
   growth; nothing needs to be rebuilt to accommodate it.

---

## Background & Context

Years of fragmented knowledge across Apple Notes, Evernote, Notion, plain text files,
PDFs, scanned documents, and photos. No single retrieval point. No daily intelligence
layer. Monitoring infrastructure already exists (fepi41 LoRaWAN/Node-RED, brekpi41
cabin monitoring) but produces data without reasoning. The goal is to add an AI
reasoning layer on top of existing infrastructure, consolidate legacy knowledge into
a durable format, and build a daily interface that reflects a specific workflow:
situational awareness → triage → deep work.

---

## Success Criteria

### Phase 1 — Vault Foundation
- [ ] Folder structure created in iCloud Drive
- [ ] Obsidian vault initialized pointing at that folder
- [ ] Structure validated: human-readable, agent-navigable, domain-separated
- [ ] Legacy source inventory complete (count by type and source)
- [ ] Migration pipeline designed (OCR strategy for scans decided)

### Phase 2 — Mac Mini + AI Layer
- [ ] Mac Mini online, on Tailscale
- [ ] Ollama running with chosen base model
- [ ] Vector DB (Chroma or Qdrant) ingesting vault .md files
- [ ] Conversational retrieval working: "find everything about X" returns useful results
- [ ] Ingestion pipeline handles PDF, TXT, MD natively
- [ ] OCR pipeline handles scanned PDFs and JPGs

### Phase 3 — Morning Brief + Situational Awareness
- [ ] fepi41 sensor data (soil, irrigation, sewer) flowing into daily brief
- [ ] brekpi41 cabin status (solar, Starlink, conditions) flowing into daily brief
- [ ] Morning brief generated automatically, available before 7am
- [ ] Brief accessible from femacbook browser via Tailscale

### Phase 4 — Triage Layer
- [ ] Email synopsis automated (Act / File / Trash framing)
- [ ] Open tasks surfaced and Eisenhower-sorted
- [ ] Daily brief + triage presented in unified UI
- [ ] Conversational window available in same interface

### Phase 5 — Deep Work Interface
- [ ] Sidebar navigation to major life domains
- [ ] "I want to work on X today" surfaces relevant notes, open threads, history
- [ ] Cross-domain linking visible (Zettelkasten connections)
- [ ] Agent can be given a domain and returns a structured work session

### Phase 6 — Full Personal OS
- [ ] All legacy data migrated and indexed
- [ ] 3-tier memory system operational (working memory / project memory / archive)
- [ ] Daily workflow: brief → triage → deep work — fully automated setup
- [ ] Thin client (travel laptop) accesses everything via Tailscale browser

---

## Scope

**In scope:**
- Vault folder structure design and creation
- Legacy data inventory and migration pipeline
- Mac Mini setup as AI/orchestration server
- Ollama + vector DB for local AI retrieval
- Morning brief automation (house + cabin + business)
- Triage interface (email, tasks)
- Deep work interface (conversational + sidebar)
- Integration with existing fepi41/brekpi41 data streams

**Out of scope:**
- Modifying Node-RED or irrigation logic on fepi41
- Any live brokerage connection
- Public internet exposure of any service
- Mobile-native app (browser via Tailscale is sufficient for now)
- Real-time collaborative editing

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                       │
│   Sidebar UI   │   Dashboard   │   Conversational       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    AI LAYER (Mac Mini)                   │
│   Ollama (local model)   │   Vector DB   │   n8n        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    DATA LAYER                            │
│   /vault (iCloud)   │   fepi41 sensors  │  brekpi41    │
│   Plain .md files   │   Node-RED data   │  cabin data  │
└─────────────────────────────────────────────────────────┘
```

All layers communicate over Tailscale. Data layer is never dependent on AI or
interface layer — it remains readable and useful if either above it fails.

---

## Vault Folder Structure

### Design Constraints
- Every folder has a single, unambiguous purpose
- Agents are given folder-level scope — never "all of /vault"
- `/archive` is read-only to agents unless explicitly instructed otherwise
- `/inbox` is the only folder agents may write to without a specific task
- Depth is shallow — maximum 3 levels before files appear
- Names are lowercase, hyphenated — consistent with toolkit convention

### Structure

```
/vault
│
├── /inbox                    ← Unsorted captures land here. Daily triage clears it.
│                               Agents may write here. Humans clear it.
│
├── /daily                    ← Daily notes, morning briefs, journal entries
│   ├── YYYY-MM-DD.md         ← One file per day, auto-generated skeleton
│   └── /briefs               ← Generated morning briefs (read-only after generation)
│
├── /projects                 ← Active projects, one subfolder each
│   ├── /direct-lighting      ← Business project example
│   ├── /cabin-expansion      ← Physical project example
│   └── _project-template.md ← Same template as toolkit
│
├── /areas                    ← Ongoing life domains (no end date)
│   ├── /home                 ← House systems, maintenance, improvement
│   ├── /cabin                ← Cabin systems, seasonal, improvements
│   ├── /health               ← Medical, fitness, personal
│   ├── /finance              ← Accounts, tax, planning (no raw statements here)
│   └── /business             ← Operating notes, not projects
│
├── /knowledge                ← Permanent notes, ideas, reference material
│   ├── /concepts             ← Zettelkasten atomic notes — one idea per file
│   ├── /references           ← Summaries of books, articles, research
│   └── /people               ← Notes on contacts, relationships, context
│
├── /resources                ← Templates, checklists, reusable material
│   ├── /templates            ← Note templates by type
│   └── /checklists           ← Recurring process checklists
│
├── /archive                  ← Completed projects, retired notes, legacy migrations
│   ├── /legacy-evernote      ← Migrated Evernote content (post-OCR)
│   ├── /legacy-notion        ← Migrated Notion content
│   ├── /legacy-notes-app     ← Migrated Apple Notes content
│   └── /legacy-scans         ← OCR'd scanned documents
│
└── /assets                   ← Images, PDFs, attachments referenced by notes
    ├── /documents            ← PDFs with text — directly ingestible
    ├── /scans                ← Original scan files (pre-OCR)
    └── /images               ← Photos, diagrams, reference images
```

### Agent Scope Map

| Agent Task | Permitted Folders | Write Access |
|---|---|---|
| Morning brief generation | /daily, /areas, /projects | /daily/briefs only |
| Inbox triage | /inbox | /inbox, /projects, /areas |
| Legacy migration | /archive, /assets | /archive only |
| Project research | /projects/[specific] | /projects/[specific] only |
| Knowledge retrieval | /knowledge, /areas, /projects | None — read only |
| Daily note skeleton | /daily | /daily only |

---

## 3-Tier Memory System

Mapped to vault structure:

| Tier | Description | Vault Location | Retention |
|---|---|---|---|
| **Working memory** | Current day, active tasks, open loops | /daily, /inbox | Days to weeks |
| **Project memory** | Active project context, decisions, history | /projects | Life of project |
| **Long-term memory** | Permanent knowledge, reference, archive | /knowledge, /archive | Permanent |

The AI layer maintains an index across all three tiers. Retrieval pulls from all
three but surfaces working memory first, then project, then long-term.

---

## Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| Storage format | Plain markdown (.md) | Durable, portable, agent-native |
| Human interface | Obsidian (minimal) | Best .md editor, local vault, no lock-in |
| Vault location | iCloud Drive /vault | Consistent with toolkit, syncs across machines |
| Local AI model | Ollama on Mac Mini | Apple Silicon, private, always-on |
| Vector DB | Chroma (start) → Qdrant (scale) | Chroma is simpler to start; Qdrant if needed |
| Orchestration | n8n on Mac Mini | Visual, self-hosted, connects everything |
| OCR pipeline | Tesseract + Apple Vision | Tesseract for flatbed scans; Apple Vision for photos of docs |
| UI shell | Node.js / React (TBD) | Clean, sidebar-capable, local |
| Network | Tailscale | Already live |

---

## Machine Roles (Updated)

| Machine | Location | Role |
|---|---|---|
| **Mac Mini M2** (planned) | Home | Brain — Ollama, Chroma, n8n, vault AI layer |
| **fepi41** | Home | Pipes — LoRaWAN, irrigation, sewer, Node-RED, financial data |
| **brekpi41** | Cabin | Edge — Starlink, solar, cabin sensors, Tailscale relay |
| **femacbook** | Primary | Workstation, vault editing via Obsidian |
| **Travel laptop** | Road | Thin client — browser + Tailscale only |

---

## Daily Workflow Design

```
MORNING (automated — no interaction required)
  brekpi41 → cabin status push to Mac Mini
  fepi41   → sensor summary push to Mac Mini
  n8n      → assembles morning brief .md → writes to /daily/briefs/
  Interface → brief available at browser open

TRIAGE (Act / File / Trash)
  Email synopsis surfaced in UI
  /inbox cleared — items routed to /projects, /areas, or /archive
  Eisenhower sort applied to open tasks

DEEP WORK
  "I want to work on [X] today"
  Agent scopes to /projects/[x] + relevant /areas + /knowledge
  Returns: open threads, last session summary, relevant notes
  Conversational window available throughout

END OF DAY (optional)
  Capture to /inbox or directly to /daily/YYYY-MM-DD.md
  /update equivalent for vault — close loops, file captures
```

---

## Document Inventory & Processing Strategy

### Principle
No processing begins until inventory is complete. The inventory is the
plan. Everything downstream — OCR tooling, conversion approaches, retention
decisions — is decided per document type, not per document. Work in batches
by type, not one file at a time.

### Phase 0 — Inventory First
Before any migration or OCR work, a full inventory pass is run across all
legacy sources. Output is a single inventory file:

```
/vault/inbox/legacy-inventory.md
```

The inventory captures:

| Field | Purpose |
|---|---|
| Filename | Identity |
| Source | Where it came from (Evernote, Notion, scan folder, etc.) |
| Format | .pdf, .jpg, .doc, .wpd, .txt, etc. |
| Estimated date | Age and likely relevance |
| Domain | finance / business / home / cabin / personal / unknown |
| Retention class | Keep-original / Extract-only / Discard-candidate |
| Processing type | See table below |
| Notes | Anything unusual |

This inventory is human-reviewed before any processing begins.
Discard candidates are confirmed by Flint before deletion.

---

### Document Type Classification

Every document falls into one of these types. Type determines the
processing path — nothing else does.

| Type | Examples | Processing Path |
|---|---|---|
| **A — Clean digital PDF** | Modern statements, contracts, exports | Direct text extract (pdfplumber). No OCR needed. |
| **B — Clean flatbed scan** | Good quality scanned docs | Tesseract OCR → .md |
| **C — Photo of document** | Phone/camera shots of paper | Apple Vision OCR → .md |
| **D — Poor quality scan** | Low res, skewed, faded | Triage: re-scan if original exists, else best-effort OCR + flag |
| **E — Proprietary format** | WordPerfect, old FileMaker, old Word | Convert to PDF first (print-to-PDF or conversion tool), then Type A or B path |
| **F — Difficult/unreadable** | Severely degraded, unusual format | Isolate for manual review. Options: re-scan original, print and re-scan, or discard |
| **G — Discard candidate** | Superseded, duplicate, zero current value | Human confirms → permanently deleted, never enters vault |

---

### Retention Classes

Not all documents are equal. Retention class determines what gets kept
and in what form.

| Class | Description | What's Kept |
|---|---|---|
| **Keep-original** | Legal, financial, medical, contracts | Original file preserved in /assets + .md extracted copy in /archive |
| **Extract-only** | Reference value only, original not needed | .md extracted copy in /archive, original discarded after extraction |
| **Discard-candidate** | Low or no value | Flagged for human confirmation, then deleted |

**Financial documents always use Keep-original.** The original scan is
the record of evidence. The .md is the searchable working copy.
Both are indexed. Neither replaces the other.

---

### Original File Preservation

For all Keep-original documents:

```
/assets/documents/          ← Type A (clean digital PDFs)
/assets/scans/              ← Type B/C/D (all scan originals)
  /assets/scans/financial/  ← Financial originals — never deleted
  /assets/scans/legal/      ← Legal originals — never deleted
  /assets/scans/general/    ← Everything else
```

The corresponding extracted .md lives in /archive with a header that
links back to the original:

```
---
source-file: /assets/scans/financial/original-filename.pdf
source-type: flatbed-scan
ocr-tool: tesseract
ocr-date: YYYY-MM-DD
ocr-confidence: high / medium / low
original-date: YYYY or estimated
domain: finance
retention: keep-original
---
```

This two-file pattern means:
- AI works with the .md (fast, searchable, no binary parsing)
- Original is always retrievable by filename link
- Audit trail is intact for financial/legal documents

---

### OCR Tool Selection

| Source Type | Tool | Rationale |
|---|---|---|
| Clean flatbed scans (.pdf, .tiff) | Tesseract | Open source, local, handles variable resolution |
| Photos of documents (.jpg, .png) | Apple Vision (macOS) | Significantly better on camera/phone photos |
| Old proprietary formats | Convert to PDF first, then above | Print-to-PDF on Mac handles most cases |
| Modern PDFs with text layer | pdfplumber (already in toolkit) | Direct extract, no OCR needed |

### Post-OCR Quality Check
After OCR, a confidence-scoring pass flags low-quality output before
it enters the vault. Low-confidence results are held in a review folder,
not committed to /archive, until spot-checked.

---

---

## Extensibility Design

Every data path into the system is built as a named, documented connector.
Adding a new source never requires modifying existing flows.

### Sensor / Data Source Connector Pattern
```
New LoRaWAN sensor added to fepi41
  → Node-RED flow created for that sensor (isolated, named)
  → Pushes to Mac Mini via standard endpoint
  → Mac Mini n8n picks it up and routes to correct handler
  → No existing flows touched
```

### Connector Registry
A small registry file tracks all active data paths:
```
/vault/resources/connector-registry.md
```

| Connector | Source | Destination | Type | Status |
|---|---|---|---|---|
| soil-moisture | fepi41 LoRaWAN | Mac Mini n8n | push / cron | active |
| sewer-level | fepi41 LoRaWAN | Mac Mini n8n | push / alert | active |
| cabin-solar | brekpi41 | Mac Mini n8n | push / cron | active |
| cabin-starlink | brekpi41 | Mac Mini n8n | push / cron | active |
| financial-data | fepi41 cron | Mac Mini n8n | push / scheduled | active |

New rows are added when new sensors or data paths are wired in.
Nothing is removed — retired connectors are marked inactive.

### UI Extensibility
The sidebar is data-driven, not hardcoded. Each sidebar entry maps to
a config entry, not a code change. Adding a new domain (e.g. a new
business, a new property) means adding a folder to /vault and a line
to the sidebar config. No UI rebuild required.

### Phase 1 — Vault Foundation (now, no Mac Mini needed)

**Two parallel tracks. Neither blocks the other.**

#### Track A — Technical (Claude Code)
- Create folder structure in iCloud Drive
- Initialize Obsidian vault
- Build automated inventory tooling
- Test OCR pipeline on sample batch
- Design ingestion pipeline for Phase 2

#### Track B — Human Agent (parallel)
- Full data consolidation work order: **data-consolidation-2026-03.md**
- Covers: femacbook local, iCloud, Dropbox, old hard drives
- Output: ~/Desktop/legacy-staging/ + HANDOFF-NOTES.md
- Hard drives addressed first — only non-recoverable risk
- Completes with staging folder ready for automated inventory pass

#### Track convergence
When both tracks are complete:
- Automated inventory agent reads staging folder + HANDOFF-NOTES.md
- Generates /vault/inbox/legacy-inventory.md
- Flint reviews — confirms discards, resolves version conflicts
- Processing batches defined by document type (A through G)
- Phase 2 ingestion begins

### Phase 2 — Mac Mini + AI Layer (on Mac Mini arrival)
- Tailscale, Ollama, Chroma, n8n install
- Point vector DB at /vault — test retrieval quality
- OCR pipeline for /assets/scans
- Automated ingestion of new .md files

### Phase 3 — Automation Layer
- Morning brief pipeline (fepi41 + brekpi41 → Mac Mini → /daily/briefs)
- n8n workflows for inbox triage
- Email synopsis integration

### Phase 4 — Interface
- UI shell: sidebar + main panel + conversational window
- Sidebar wired to vault domains
- Conversational window wired to vector DB

### Phase 5 — Migration Complete
- All legacy sources processed and in /archive
- /knowledge populated with permanent notes
- Full 3-tier memory operational

---

## Open Questions

- [ ] Old proprietary formats — full list of formats found during inventory
- [ ] Type E/F document count — how many need conversion or re-scan?
- [ ] Financial document scope — how many years, which institutions?
- [ ] Which Ollama model is best for retrieval/synthesis vs. reasoning tasks?
- [ ] n8n vs. alternative for orchestration on Mac Mini?
- [ ] Email integration — which client/API for synopsis automation?
- [ ] Obsidian plugins — which minimal set is worth enabling?
- [ ] brekpi41 data push mechanism — cron + curl to Mac Mini, or Node-RED relay?

---

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| iCloud Drive active | ✓ | femacbook |
| Tailscale network | ✓ | All nodes live |
| fepi41 sensor data | ✓ | Node-RED, LoRaWAN |
| brekpi41 cabin data | ✓ | Starlink, solar |
| Mac Mini M2 | ❌ Planned | Brain layer depends on this |
| Obsidian | ❌ Install needed | Free, local |
| Ollama | ❌ Planned | On Mac Mini |
| Chroma / Qdrant | ❌ Planned | On Mac Mini |
| n8n | ❌ Planned | On Mac Mini |
| OCR tool | ❌ TBD | Depends on scan inventory |

---

## Constraints

- Never store API keys in any tracked file
- /archive is read-only to agents by default
- Vault format stays plain markdown — no proprietary formats enter /vault
- Obsidian is an interface only — no features that create vendor lock-in
- All agent tasks are folder-scoped — no agent has unrestricted vault access
- Mac Mini services stay on Tailscale — nothing exposed to public internet

---

## Outcomes & Lessons

_To be filled in on completion._

---

## Bible Entry

_To be filled in on completion and copied to master-reference.md._

---

## Skills Inventory Entry

_To be added on close._
