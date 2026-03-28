# TAZ 5 Material Profiles

## ABS

| Setting | Value |
|---|---|
| Nozzle temp | 230°C |
| Bed temp | 110°C |
| Min wall thickness | 2.0mm |
| Recommended infill | 30–40% |
| Support threshold | >45° overhangs |
| Shrinkage | 0.8% in X/Y |
| Enclosure | Required (warping risk without) |
| Retraction | 1.0mm / 45mm/s |
| Cooling fan | Off or minimal |

**Shrinkage compensation in code:**
```scad
// OpenSCAD — apply to final part before export
scale([1.008, 1.008, 1]) { your_part(); }
```
```python
# CadQuery
part = part.val().scale(1.008)  # uniform; or apply X/Y only
```

**ABS tips:**
- First layer extra slow (20–25mm/s) for adhesion to PEI
- Reduce perimeter speed to 50% of infill to avoid layer separation
- Combing enabled reduces stringing on complex geometry
- Retraction: 1.0–1.5mm if stringing occurs (adjust up in 0.1mm steps)

---

## PETG

| Setting | Value |
|---|---|
| Nozzle temp | 238°C |
| Bed temp | 80°C |
| Min wall thickness | 1.6mm |
| Recommended infill | 20–30% |
| Support threshold | >50° overhangs |
| Shrinkage | Minimal — no compensation needed |
| Enclosure | Not required |
| Retraction | 1.0mm / 45mm/s |
| Cooling fan | 50% after first layer |

**PETG tips:**
- PETG bonds aggressively to PEI — apply glue stick or PEI release agent
- Slightly lower print speed vs ABS improves layer adhesion
- Stringing common — increase retraction to 1.2mm if needed
- Avoid over-cooling — artifacts appear if fan >75%

---

## Design Rules Summary (apply regardless of material)

| Rule | Value |
|---|---|
| Hole clearance (fit) | +0.3mm on radius |
| Bottom edge treatment | Chamfer (not fillet) |
| Max unsupported bridge | 20mm |
| Minimum feature size | 1.0mm (nozzle is 0.5mm) |
| Thread engagement | ≥3 thread pitches |
| Snap fit deflection | Design for ABS: 2–4% strain; PETG: 3–5% |
