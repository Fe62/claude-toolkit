# TAZ 5 Machine Configuration

## Printer
- **Model:** LulzBot TAZ 5
- **Build volume:** 280 × 280 × 250mm (X / Y / Z)
- **Bed surface:** PEI sheet
- **Bed leveling:** Manual + washers (no auto-level probe on TAZ 5)

## Extruder
- **Tool head:** Aerostruder
- **Nozzle diameter:** 0.5mm
- **Filament diameter:** 2.85mm
- **Drive type:** Direct drive
- **Retraction:** 1.0mm / 45mm/s

## Layer Heights
| Mode | Layer Height |
|---|---|
| Draft | 0.35–0.40mm |
| Standard | 0.20–0.25mm |
| Fine | 0.10–0.15mm |
| Ultra-fine | 0.075mm (temp-sensitive — ±5°C causes blobbing) |

Practical sweet spot for functional parts: **0.2mm**

## Print Speed
- Practical max: 80–100mm/s
- Better speed strategy: raise layer height, not mm/s
- Perimeter speed: 50% of infill speed recommended

## Overhang Limits
- ABS: ≤45° without support
- PETG: ≤50° without support

## Max Bridge Span (unsupported)
- 20mm

## Slicer
- **Required:** Cura LulzBot Edition (Cura LE) v21.08
- Do NOT use standard UltiMaker Cura — bed probing G-code uses variable substitution not supported outside Cura LE
- Pre-slice in Cura LE, upload .gcode to OctoPrint

## OctoPrint
- **Host:** octopi (Raspberry Pi 4)
- **Local (WiFi):** 192.168.1.126
- **Tailscale:** 100.82.140.84
- **API key:** stored in Claude memory (octopi entry) — do not hardcode in files
- **Baud rate:** 115200 (RAMBo board)
- **Webcam stream:** http://192.168.1.126:8080/?action=stream
- **Webcam snapshot:** http://192.168.1.126:8080/?action=snapshot
- **Failure detection:** Obico (active)

## Output Directory
`~/Desktop/taz5-renders/` — STL and PNGs land here for direct Cura LE access
