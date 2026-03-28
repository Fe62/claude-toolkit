# TAZ 5 CAD Skill — Claude Context

At the start of every session in this directory, read:
- SKILL.md — workflow, invocation, self-critique checklist
- machine-config.md — TAZ 5 build volume, extruder, OctoPrint details
- material-profiles.md — ABS and PETG temps, design rules, shrinkage
- tool-decision.md — when to use OpenSCAD vs CadQuery

## Defaults
- Tool: OpenSCAD (unless part description triggers CadQuery criteria)
- Material: ABS (unless specified)
- Output: ~/Desktop/taz5-renders/
- Render: render.sh (see script for usage)

## Iteration Protocol
1. Generate initial code
2. Run render.sh --single → show perspective PNG → ask "does this look roughly right?"
3. On confirmation → run full 4-view render loop (2–3 autonomous rounds)
4. Apply self-critique checklist each round — do not surface output until checklist passes
5. Final: STL + perspective PNG in ~/Desktop/taz5-renders/

## Never
- Use magic numbers — all dimensions as named variables
- Exceed build volume (280×280×250mm)
- Forget +0.3mm hole clearance on fit-critical holes
- Use fillet on bottom edges (use chamfer for bed adhesion)
