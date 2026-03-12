# Vault Migration — Pass 3 Execution Script

**Document status:** Active  
**Date started:** 2026-03-11  
**Parent project:** personal-os-2026-03.md  
**Owner:** Flint  
**Executed by:** Claude Code on femacbook  

---

## One-Line Goal

Sort Documents into vault-ready folder structure using the existing
dot-notation naming convention. Flag non-conforming files for later review.
No files deleted — Trash not emptied until Pass 4 confirms.

---

## Prerequisites

- [ ] Pass 2 complete and reviewed
- [ ] Vault structure live in iCloud Drive
- [ ] Trash not emptied
- [ ] Python 3 available

---

## What This Script Does

1. Creates entity folders in a staging area (not vault yet — confirm first)
2. Sorts files by dot-notation prefix into entity folders
3. Moves QuickBooks files to dedicated location
4. Flags non-conforming files to `_review/` subfolders
5. Writes a migration report for human review before anything touches the vault

---

## Step 1 — Create the Script

Claude Code should create this file at:
```
~/Documents/migrate-pass3.py
```

```python
#!/usr/bin/env python3
"""
Vault Migration — Pass 3
Sorts files by dot-notation prefix into entity folders.
Flags non-conforming files to _review/.
Writes report before moving anything.
DRY RUN by default — set DRY_RUN = False to execute.
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────
DRY_RUN     = True   # ← CHANGE TO False TO EXECUTE
SOURCE      = Path("/Users/Flint/Documents")
STAGING     = Path("/Users/Flint/Documents/_pass3-staging")
REPORT      = Path("/Users/Flint/Documents/migrate-pass3-report.md")

# QuickBooks extensions — special handling
QB_EXTS = {'.qb2019', '.qb2020', '.qb2021', '.qb2022', '.qb2023',
           '.qbw', '.qdf', '.qdfm', '.qb', '.dmg'}

QB_DEST = STAGING / "assets/documents/quickbooks"

# Prefix → destination folder mapping
# Format: prefix (lowercase) → relative path under STAGING
PREFIX_MAP = {
    # Personal
    'fe':       'areas/personal/FE.pers',
    'fa':       'areas/personal/FA.pers',
    'fefa':     'areas/personal/FeFa.pers',
    'fanae':    'areas/personal/FA.pers',
    'fanee':    'areas/personal/FA.pers',
    'fedl':     'areas/personal/FE.pers',
    'fechase':  'areas/personal/FE.pers',
    'fewells':  'areas/personal/FE.pers',
    'fefalt':   'areas/finance/fefalt',
    'fefallc':  'areas/finance/fefalt',

    # Business — active
    'p&a':      'areas/business/parts-assembly',
    'pa':       'areas/business/parts-assembly',

    # Finance
    'itasca':   'areas/finance/itasca',

    # Legacy archive
    'flat':     'archive/legacy-orgs/flatiron',
    'pce':      'archive/legacy-orgs/pce',
    'gag':      'archive/legacy-orgs/gag',
    'efit':     'archive/legacy-orgs/efit',
    'cli':      'archive/legacy-orgs/cli',
    'bootstrap':'archive/legacy-orgs/bootstrap',
    'ironlight':'archive/legacy-orgs/ironlight',
    'brek':     'areas/cabin',
    'cody':     'areas/personal/FE.pers',
}

# Folders to process (top-level under SOURCE)
# Each entry: (folder_path, default_prefix_override or None)
FOLDERS_TO_PROCESS = [
    SOURCE / "Personal/docs",
    SOURCE / "Orgs/Parts & Assembly",
    SOURCE / "Orgs/FeFa",
    SOURCE / "Orgs/FeFaLT",
    SOURCE / "Orgs/Flatiron",
    SOURCE / "Orgs/Itasca Properties, LLC",
    SOURCE / "Orgs/Breckenridge",
    SOURCE / "Orgs/Cody",
    SOURCE / "Orgs/Flint",
    SOURCE / "Orgs/Fanae",
    SOURCE / "Orgs/GAG",
    SOURCE / "Orgs/PCE",
    SOURCE / "Orgs/EFIT",
    SOURCE / "Orgs/CLI",
    SOURCE / "Orgs/Bootstrap",
    SOURCE / "Orgs/Bootstrap Brewing LLC",
    SOURCE / "Orgs/Bootstrap LLC dba Ironlight labels",
    SOURCE / "Orgs/Ironlight",
    SOURCE / "Orgs/Ellsworth Trust",
    SOURCE / "Orgs/First Stampede, LLC",
    SOURCE / "Orgs/GE",
    SOURCE / "Orgs/Misc",
    SOURCE / "Tax",
    SOURCE / "Investments",
    SOURCE / "Financial",
    SOURCE / "Legal",
    SOURCE / "Medical",
    SOURCE / "Vehicles",
    SOURCE / "Real-Estate",
    SOURCE / "QuickBooks",
    SOURCE / "scans.012919",
    SOURCE / "Misc",
]

# Folder-level overrides — when whole folder has a known destination
FOLDER_DEST_OVERRIDE = {
    SOURCE / "Tax":                             "areas/finance/tax",
    SOURCE / "Investments":                     "areas/finance/investments",
    SOURCE / "Financial":                       "areas/finance",
    SOURCE / "Legal":                           "archive/legal",
    SOURCE / "Medical":                         "areas/health",
    SOURCE / "Vehicles":                        "areas/home/vehicles",
    SOURCE / "Real-Estate":                     "areas/finance/real-estate",
    SOURCE / "QuickBooks":                      "areas/finance/quickbooks",
    SOURCE / "scans.012919":                    "archive/legacy-scans",
    SOURCE / "Misc":                            "archive/misc",
    SOURCE / "Orgs/Ellsworth Trust":            "areas/finance/ellsworth-trust",
    SOURCE / "Orgs/First Stampede, LLC":        "areas/finance/first-stampede",
    SOURCE / "Orgs/GE":                         "archive/legacy-orgs/ge",
    SOURCE / "Orgs/Misc":                       "archive/legacy-orgs/misc",
    SOURCE / "Orgs/Breckenridge":               "areas/cabin/breckenridge",
    SOURCE / "Orgs/Cody":                       "areas/personal/FE.pers/cody",
    SOURCE / "Orgs/Fanae":                      "areas/personal/FA.pers",
    SOURCE / "Orgs/Flint":                      "areas/personal/FE.pers",
    SOURCE / "Orgs/Bootstrap":                  "archive/legacy-orgs/bootstrap",
    SOURCE / "Orgs/Bootstrap Brewing LLC":      "archive/legacy-orgs/bootstrap",
    SOURCE / "Orgs/Bootstrap LLC dba Ironlight labels": "archive/legacy-orgs/bootstrap",
    SOURCE / "Orgs/Ironlight":                  "archive/legacy-orgs/ironlight",
    SOURCE / "Orgs/EFIT":                       "archive/legacy-orgs/efit",
    SOURCE / "Orgs/CLI":                        "archive/legacy-orgs/cli",
    SOURCE / "Orgs/GAG":                        "archive/legacy-orgs/gag",
    SOURCE / "Orgs/PCE":                        "archive/legacy-orgs/pce",
    SOURCE / "Orgs/Flatiron":                   "archive/legacy-orgs/flatiron",
    SOURCE / "Orgs/Itasca Properties, LLC":     "areas/finance/itasca",
    SOURCE / "Orgs/FeFaLT":                     "areas/finance/fefalt",
    SOURCE / "Orgs/FeFa":                       "areas/personal/FeFa.pers",
    SOURCE / "Orgs/Parts & Assembly":           "areas/business/parts-assembly",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_prefix(filename):
    """Extract dot-notation prefix from filename. Returns lowercase prefix or None."""
    name = Path(filename).stem.lower()
    # Match fe., fa., fefa., p&a., flat. etc.
    m = re.match(r'^([a-z0-9&+]+)[\.,]', name)
    if m:
        return m.group(1)
    return None

def is_qb_file(filepath):
    return filepath.suffix.lower() in QB_EXTS

def get_dest(filepath, folder_override=None):
    """Determine destination for a file."""
    if is_qb_file(filepath):
        return QB_DEST, "quickbooks"

    if folder_override:
        return STAGING / folder_override, "folder-override"

    prefix = get_prefix(filepath.name)
    if prefix and prefix in PREFIX_MAP:
        return STAGING / PREFIX_MAP[prefix], f"prefix:{prefix}"

    # No match — goes to _review under its source folder
    return None, "review"

# ── Scan and plan ─────────────────────────────────────────────────────────────
plan        = []   # (source, dest, reason)
review      = []   # (source, review_folder)
stats       = defaultdict(int)

for folder in FOLDERS_TO_PROCESS:
    if not folder.exists():
        print(f"  SKIP (not found): {folder}")
        continue

    folder_override = FOLDER_DEST_OVERRIDE.get(folder)

    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        rel_root = Path(root).relative_to(folder)

        for filename in files:
            if filename.startswith('.'):
                continue

            src = Path(root) / filename
            dest_base, reason = get_dest(src, folder_override)

            if dest_base is None:
                # Route to _review under source folder name
                review_dest = STAGING / "_review" / folder.name / rel_root / filename
                review.append((src, review_dest, "no-prefix-match"))
                stats["review"] += 1
            else:
                dest = dest_base / rel_root / filename
                plan.append((src, dest, reason))
                stats[reason.split(':')[0]] += 1

# ── Write report ──────────────────────────────────────────────────────────────
now = datetime.now().strftime("%Y-%m-%d %H:%M")
lines = []
lines.append("# Vault Migration — Pass 3 Report")
lines.append(f"\nGenerated: {now}")
lines.append(f"Mode: {'DRY RUN — no files moved' if DRY_RUN else '⚠️  LIVE RUN — files moved'}\n")
lines.append("---\n")

lines.append("## Summary\n")
lines.append("| Category | File Count |")
lines.append("|---|---|")
total = sum(stats.values()) + len(review)
for k, v in sorted(stats.items()):
    lines.append(f"| {k} | {v:,} |")
lines.append(f"| review (no match) | {len(review):,} |")
lines.append(f"| **Total** | **{total:,}** |\n")

lines.append("---\n")
lines.append("## QuickBooks Files\n")
lines.append("| File | Source |")
lines.append("|---|---|")
for src, dest, reason in plan:
    if reason == "quickbooks":
        lines.append(f"| {src.name} | {src.parent.relative_to(SOURCE)} |")

lines.append("\n---\n")
lines.append("## Files Routed to _review/ (sample — first 50)\n")
lines.append("| File | Source Folder | Reason |")
lines.append("|---|---|---|")
for src, dest, reason in review[:50]:
    lines.append(f"| {src.name} | {src.parent.relative_to(SOURCE)} | {reason} |")
if len(review) > 50:
    lines.append(f"\n_...and {len(review) - 50} more_")

lines.append("\n---\n")
lines.append("## Destination Summary\n")
dest_summary = defaultdict(int)
for src, dest, reason in plan:
    rel = dest.relative_to(STAGING)
    top = '/'.join(rel.parts[:3])
    dest_summary[top] += 1
lines.append("| Destination | File Count |")
lines.append("|---|---|")
for dest, count in sorted(dest_summary.items(), key=lambda x: x[1], reverse=True):
    lines.append(f"| {dest} | {count:,} |")

lines.append("\n---\n")
lines.append("## Next Steps\n")
lines.append("""1. Review this report
2. Check QuickBooks files list — confirm all accounted for
3. Check _review sample — does the routing logic look correct?
4. Check destination summary — any surprises?
5. If satisfied: set DRY_RUN = False and re-run to execute
6. After execution: verify staging, then copy to vault
""")

REPORT.write_text("\n".join(lines))
print(f"✓ Report written to: {REPORT}")

# ── Execute (if not dry run) ──────────────────────────────────────────────────
if not DRY_RUN:
    print("\nExecuting moves...")
    moved = 0
    errors = 0

    all_moves = plan + [(s, d, r) for s, d, r in
                        [(s, d, r) for s, d, r in
                         [(s, d, "review") for s, d, _ in review]]]

    for src, dest, reason in plan:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            moved += 1
        except Exception as e:
            print(f"  ERROR: {src.name} → {e}")
            errors += 1

    for src, dest, reason in review:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            moved += 1
        except Exception as e:
            print(f"  ERROR: {src.name} → {e}")
            errors += 1

    print(f"\n✓ Done — {moved:,} files copied, {errors} errors")
    print(f"  Staging: {STAGING}")
    print(f"  Originals untouched in {SOURCE}")
    print(f"\n  Review staging, then copy to vault.")
else:
    print(f"\nDRY RUN complete — no files moved")
    print(f"Review {REPORT}")
    print(f"Set DRY_RUN = False to execute")
```

---

## Step 2 — Run Dry Run First

```bash
python3 ~/Documents/migrate-pass3.py
```

Open the report:
```bash
open ~/Documents/migrate-pass3-report.md
```

Review:
- QuickBooks files list — all accounted for?
- _review sample — routing logic correct?
- Destination summary — any surprises?

---

## Step 3 — Execute (after dry run review)

Edit the script — change line:
```python
DRY_RUN = True
```
to:
```python
DRY_RUN = False
```

Re-run:
```bash
python3 ~/Documents/migrate-pass3.py
```

Script uses `shutil.copy2` — **originals are untouched**.
Everything lands in `~/Documents/_pass3-staging/`.

---

## Step 4 — Verify Staging

```bash
ls ~/Documents/_pass3-staging/
find ~/Documents/_pass3-staging -type d | sort | head -40
find ~/Documents/_pass3-staging -type f | wc -l
```

Spot-check a few folders to confirm files landed correctly.

---

## Step 5 — Copy to Vault

Once staging looks correct, copy to iCloud vault:

```bash
# Areas
cp -R ~/Documents/_pass3-staging/areas/ \
  ~/Library/Mobile\ Documents/com~apple~CloudDocs/vault/areas/

# Archive  
cp -R ~/Documents/_pass3-staging/archive/ \
  ~/Library/Mobile\ Documents/com~apple~CloudDocs/vault/archive/

# Assets (QuickBooks files)
cp -R ~/Documents/_pass3-staging/assets/ \
  ~/Library/Mobile\ Documents/com~apple~CloudDocs/vault/assets/
```

---

## Step 6 — Verify Vault

```bash
find ~/Library/Mobile\ Documents/com~apple~CloudDocs/vault -type f | wc -l
```

---

## Completion Criteria

- [ ] Dry run report reviewed and approved
- [ ] Live run executed cleanly
- [ ] Staging verified
- [ ] Files copied to vault
- [ ] Vault file count confirmed
- [ ] Originals still intact in ~/Documents
- [ ] _review folders noted for future triage session
- [ ] Ready for Pass 4 (Media, remaining folders, final cleanup)

---

## Notes for Claude Code

- Script copies, never moves — originals always intact
- DRY_RUN = True is the safe default — must be explicitly changed
- Staging goes to ~/Documents/_pass3-staging/ not vault directly
- QuickBooks files always route to assets/documents/quickbooks/
- `_review/` uses underscore prefix — sorts to top in Finder
- shutil.copy2 preserves file metadata (creation date, modified date)
- If a folder in FOLDERS_TO_PROCESS doesn't exist, it's skipped silently
