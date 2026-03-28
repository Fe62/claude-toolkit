# TAZ 5 CAD Generation Skill

## Purpose
Generate print-ready 3D parts for the LulzBot TAZ 5 from plain language descriptions.
Handles tool selection, code generation, iterative rendering, and STL export.

## Invocation
In Claude Code:
```
/taz5-cad
```
Claude reads this file, loads machine-config.md and material-profiles.md into context, then prompts:
> "Describe the part you want to make."

In Claude.ai:
- Paste SKILL.md + machine-config.md as a context block at session start
- Same conversational flow, but rendering hands off to Claude Code
- Claude writes .scad or .py code blocks — paste into local OpenSCAD to preview
- When shape is final, bring to Claude Code for clean STL export via render.sh

---

## Workflow

```
Describe part
     ↓
Recommend tool (OpenSCAD vs CadQuery) — see tool-decision.md
     ↓
Generate initial .scad or .py script
     ↓
── PASS 0: SANITY CHECK ────────────────────────
│  Single perspective render → PNG shown to Flint
│  "Does this look roughly right?"
│  Flint: yes / adjust description
────────────────────────────────────────────────
     ↓
── AUTONOMOUS LOOP (2–3 rounds) ────────────────
│  Render 4-view (front/side/top/perspective)
│  Review all 4 views against self-critique checklist
│  Rewrite code if any checklist item fails
│  Repeat until all items pass
────────────────────────────────────────────────
     ↓
── FINAL OUTPUT ────────────────────────────────
│  STL exported to ~/Desktop/taz5-renders/
│  Perspective PNG auto-opened
│  .scad/.py saved alongside STL
────────────────────────────────────────────────
     ↓
Manual: Cura LE → slice → upload to OctoPrint
```

---

## Self-Critique Checklist

Run this against every render before presenting output to Flint.
Do not show output until all items pass or are explicitly flagged with a note.

- [ ] Overhangs ≤45° (ABS) / ≤50° (PETG), or support requirement noted
- [ ] Wall thickness ≥2.0mm (ABS) / ≥1.6mm (PETG)
- [ ] No unsupported bridges >20mm
- [ ] Bottom edges chamfered (not filleted) for bed adhesion
- [ ] Geometry is manifold / watertight
- [ ] All holes include +0.3mm clearance for fit
- [ ] Part fits within 280×280×250mm build volume
- [ ] All dimensions are named variables (not magic numbers)
- [ ] ABS parts scaled up 0.8% in X/Y if tight tolerances required

---

## Code Style

**OpenSCAD:**
- All dimensions as named variables at top of file
- Comments explaining each major operation
- Modules for repeated geometry
- No nesting beyond 4 levels of boolean ops

**CadQuery:**
- All dimensions as named Python variables at top of file
- One operation per line where possible
- Export both STL and STEP

---

## Render Commands

```bash
# Pass 0 — single sanity check view
./render.sh path/to/file.scad partname --single

# Autonomous loop — 4-view
./render.sh path/to/file.scad partname
```

See render.sh for full detail.
