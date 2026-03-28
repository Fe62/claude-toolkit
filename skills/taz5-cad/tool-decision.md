# Tool Decision Guide: OpenSCAD vs CadQuery

## Default: OpenSCAD

Use OpenSCAD unless the part description triggers one or more CadQuery criteria below.

---

## Decision Table

| Use OpenSCAD when... | Use CadQuery when... |
|---|---|
| Part is geometric / prismatic | Part needs fillets, chamfers, or shells |
| Simple boolean ops (union, difference, intersection) | Engineering fit parts (threads, snap fits, press fits) |
| Readable, tweakable code is a priority | Python scripting, loops, or conditionals needed |
| Quick bracket, housing, flange, or mount | Complex sweeps, lofts, or organic geometry |
| Part will be shared / edited by others | Parametric families (one script, many variants) |
| No Python environment available | STEP export needed (e.g. for machining reference) |

---

## Signals in Part Description → CadQuery

Trigger words that suggest CadQuery:
- "fillet", "chamfer", "rounded edges", "blend"
- "thread", "threaded", "M3/M4/M6", "helix"
- "snap fit", "click in", "press fit", "interference"
- "swept", "lofted", "follows a path", "variable cross-section"
- "shell", "hollow with uniform wall"
- "multiple sizes", "parametric family", "variants"

---

## Installation

**OpenSCAD:** `/Applications/OpenSCAD.app` — must be installed separately
- Download: openscad.org (use snapshot/nightly on macOS Tahoe — stable has render issues)

**CadQuery:** Install on first use
```bash
pip install cadquery
```
Verify: `python3 -c "import cadquery; print(cadquery.__version__)"`

---

## Syntax Quick Reference

**OpenSCAD — parametric box:**
```scad
// Named variables
length = 50;
width  = 30;
height = 20;
wall   = 2;

module hollow_box(l, w, h, t) {
    difference() {
        cube([l, w, h]);
        translate([t, t, t])
            cube([l-2*t, w-2*t, h]);
    }
}

hollow_box(length, width, height, wall);
```

**CadQuery — same box with fillets:**
```python
import cadquery as cq

length = 50
width  = 30
height = 20
wall   = 2
fillet_r = 1.5

box = (
    cq.Workplane("XY")
    .box(length, width, height)
    .shell(-wall)
    .edges("|Z")
    .fillet(fillet_r)
)

box.val().exportStl("output.stl")
box.val().exportStep("output.step")
```
