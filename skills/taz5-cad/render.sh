#!/usr/bin/env bash
# render.sh — TAZ 5 OpenSCAD headless render
#
# Outputs PNG previews + STL to ~/Desktop/taz5-renders/
# Perspective PNG auto-opens after render.
#
# Usage:
#   ./render.sh path/to/file.scad [output_name] [--single]
#
#   --single  renders one perspective view only (Pass 0 sanity check)
#   default   renders 4-view (front/side/top/perspective) + STL
#
# NOTES:
#   - Uses --autocenter --viewall so camera adapts to any part size/position
#   - Does NOT use --render flag (CGAL/F6 mode) — breaks on macOS Tahoe
#     F5 preview export works for most geometry; for complex booleans,
#     open in OpenSCAD GUI and run F6 render before slicing in Cura LE
#   - OpenSCAD must be installed at /Applications/OpenSCAD.app
#     Use snapshot/nightly build on macOS Tahoe (stable has Qt/GL issues)
#     Download: https://openscad.org/downloads.html#snapshots

set -e

OPENSCAD="/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
OUTDIR="$HOME/Desktop/taz5-renders"
mkdir -p "$OUTDIR"

SCAD="${1:?Usage: render.sh file.scad [output_name] [--single]}"
NAME="${2:-$(basename "$SCAD" .scad)}"
SINGLE=false

# Parse flags
for arg in "$@"; do
  [[ "$arg" == "--single" ]] && SINGLE=true
done

BASE_FLAGS="--autocenter --viewall --colorscheme=Tomorrow"

if [ "$SINGLE" = true ]; then
    echo "Pass 0: single perspective render..."
    "$OPENSCAD" $BASE_FLAGS \
        --camera=0,0,0,55,0,25,0 \
        --imgsize=1200,900 \
        -o "$OUTDIR/${NAME}-preview.png" \
        "$SCAD"
    echo "Done: $OUTDIR/${NAME}-preview.png"
    open "$OUTDIR/${NAME}-preview.png"
    exit 0
fi

echo "Rendering 4 views..."

"$OPENSCAD" $BASE_FLAGS \
    --camera=0,0,0,90,0,0,0 \
    --imgsize=900,900 \
    -o "$OUTDIR/${NAME}-front.png" \
    "$SCAD"

"$OPENSCAD" $BASE_FLAGS \
    --camera=0,0,0,90,0,90,0 \
    --imgsize=900,900 \
    -o "$OUTDIR/${NAME}-side.png" \
    "$SCAD"

"$OPENSCAD" $BASE_FLAGS \
    --camera=0,0,0,0,0,0,0 \
    --imgsize=900,900 \
    -o "$OUTDIR/${NAME}-top.png" \
    "$SCAD"

"$OPENSCAD" $BASE_FLAGS \
    --camera=0,0,0,55,0,25,0 \
    --imgsize=1200,900 \
    -o "$OUTDIR/${NAME}-perspective.png" \
    "$SCAD"

echo "Exporting STL..."
"$OPENSCAD" \
    -o "$OUTDIR/${NAME}.stl" \
    "$SCAD"

echo ""
echo "Output: $OUTDIR/"
echo "  ${NAME}-front.png"
echo "  ${NAME}-side.png"
echo "  ${NAME}-top.png"
echo "  ${NAME}-perspective.png"
echo "  ${NAME}.stl"

open "$OUTDIR/${NAME}-perspective.png"
