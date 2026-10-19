---
status: active
verified: 2026-10-13
---
# Hardware reference

The physical facts this project must not get wrong. Rung 1 of the truth
ladder: if this file and the code or CAD disagree, measure the thing and fix
both.

Item: TBC (what is being designed, and what it is for)
Revision: TBC (the release tag the physical parts were made from)
Units in this project: SolidWorks MMGS (mm, g, s), angles in degrees, force in N
Up axis: build123d +Z, SolidWorks +Y. STEP carries coordinates, not "up".
Last verified against a physical part: never

Every number below carries where it came from. A number with no source is a
rumour, and rumours are what this file exists to stop. Densities and driving
dimensions live in params/params.yaml, not here: this file gives their
specification and source.

Before every powered or energised run, work through the pre-flight checklist below.

## Agent Notes

### Identity and revision
The single most expensive hardware mistake is working from the wrong
revision. Record what is actually in front of you, not what was ordered.

| Field | Value | Source |
|---|---|---|
| Make and model | TBC | |
| Serial or build number | TBC | |
| Hardware revision (release tag) | TBC | |
| Firmware or controller version | TBC, or n/a | |
| Date this item was last changed | TBC | |

### Units and conventions
State once, obey everywhere. Every quantity crossing a boundary (an SDK call,
a file, a plot axis, a report figure, a drawing) carries these units or is
converted at the boundary and named accordingly (`length_mm`, `mass_g`).

| Quantity | Unit | Notes |
|---|---|---|
| Length | mm | params.yaml `units: mm`; STEP files in mm; SolidWorks MMGS |
| Angle | deg | params entries with `unit: deg`; build123d takes degrees |
| Mass | g | `mass_g()` in code/src/project_tools/geometry.py |
| Density | g/cm3 | params.yaml materials. SolidWorks shows g/mm3 (1 g/cm3 = 0.001 g/mm3). Converted only inside `mass_g()` |
| Time | s | |
| Force or torque | N, N mm | SolidWorks MMGS reports torque in N mm, not N m |
| Up axis | build123d +Z, SolidWorks +Y | A build123d part inserted in SolidWorks has its +Z towards the viewer in the Front view. Orient it with assembly mates; do not remodel it Y-up |

A unit-free number crossing a function signature is a defect, not a style
preference. Convert at one named place, never opportunistically.

### Provenance rule
Every quantity in this file is one of:
- **Manual**: from the manufacturer's documentation or a standard. Cite the
  document and page or clause.
- **Measured**: read off the physical item. Cite the instrument and the date.
- **Derived**: computed from the two above. Show which.
- **TBC**: not yet known. TBC is a stop sign, not a default.

Never promote a number up this list without doing the work. A measured value
that disagrees with the manual is a finding worth recording, not an error to
be quietly corrected toward the manual.

### Pre-flight checklist (every powered or energised run)
- [ ] Every energy source identified: electrical, pneumatic, hydraulic,
      stored (springs, capacitors, raised mass), thermal, chemical
- [ ] Stop or isolation within reach of the operator, and tested this session
- [ ] Nobody inside the hazard zone; someone else knows the item is live
- [ ] First run at reduced speed, power, or feed
- [ ] Checked in simulation, dry run, or on scrap first
- [ ] The numbers in this file match what is actually fitted
- [ ] Correct PPE for the energy sources listed above

A checklist that has never caught anything is either a perfect process or an
unread checklist. Assume the second and find out.

### Model to reality parity
Anything true in the model, the simulation, or the drawing but not on the
physical item, or the reverse, gets a row here. This is where hardware
surprises are recorded before they become postmortems.

| Assumption in the model | Reality on the item | Handled by |
|---|---|---|
| Solid material: `mass_g()` uses full density | Printed parts have infill and are lighter | Mass tests are an upper bound; weigh the first print |
| | | |

### CAD and revision register
The master of every part is named once, in parts/ownership.yaml (owner,
source file, STEP). Export provenance (commit, hashes, mass, bounding box,
kernel versions) is in exports/manifest.json for build123d parts and
cad/step/manifest.json for SolidWorks parts. Do not copy either here. This
table records what those files cannot: releases and who received them.

| Release tag | Date | Parts released | Sent to | Notes |
|---|---|---|---|---|
| none yet | | | | |

Rules that hold regardless of CAD package:
- The master is the native parametric source: the .py for build123d parts,
  the .SLDPRT for SolidWorks parts. STEP (AP214) is the interchange format.
  Meshes (STL) are for visualisation and printing, never for dimensioning.
- A revision changes when the geometry changes, not when the file is opened.
- Only exports from a tagged commit leave the project.
- If the physical part was modified after fabrication (filed, drilled,
  shimmed), that is an as-built deviation. Record it below; do not
  retroactively edit the CAD to match and call it done.

### Materials
Each material in params/params.yaml needs a row here
(code/tests/test_repository.py::test_materials_documented_in_hardware checks
it). Its density lives only in params.yaml.

| Material | Specification and grade | Condition or process | Source |
|---|---|---|---|
| ABS | TBC: grade and supplier | Density in params.yaml is for solid ABS | Project brief, 2026-10-13; confirm against the supplier datasheet |

"Aluminium" is not a material specification; 6082-T6 is. "PLA" is not one
either: printed polymer properties depend on the print, not only the polymer,
so record the process parameters below alongside it. Anisotropy in printed and
laminated parts means a single stiffness or strength figure is a direction as
well as a number.

### Tolerances, datums, and fits
Design rules every part is checked against. The numbers live in
params/params.yaml `design_rules`; the hole table in
code/src/project_tools/standards.py.

| Rule | Value | Source |
|---|---|---|
| Minimum wall thickness | design_rules.min_wall | Project brief, 2026-10-13 |
| Minimum internal corner radius | design_rules.min_internal_radius | Project brief, 2026-10-13 |
| Clearance holes | ISO 273 medium series | ISO 273; table in standards.py |

Datum scheme: TBC. Name the datum features and their order (primary,
secondary, tertiary). A dimension with no stated datum is measured from
wherever the inspector chose, which is why the same part passes and fails.

| Feature | Nominal | Tolerance | Datum | Why this tolerance |
|---|---|---|---|---|
| TBC | | | | |

Stack-up: TBC. For any assembly where clearances matter, record the worst-case
and the statistical stack separately, and say which one the design relies on.
Worst-case that closes is safe; statistical that closes means some fraction of
assemblies will not.

Fits: state the intent, not just the numbers. "Clearance", "transition", and
"interference" are design decisions; the millimetres are their consequence.
Record the assembly temperature if a fit depends on it.

### Fabrication process parameters
The process is part of the part. Two identical CAD files made different ways
are different components, and the difference is usually discovered in test.

| Part | Process | Machine | Key parameters | Operator and date |
|---|---|---|---|---|
| TBC | TBC | TBC | TBC | |

Key parameters worth recording, by process:
- Additive: material and batch, layer height, wall count, infill and pattern,
  nozzle and bed temperature, build orientation. Orientation is a structural
  decision, not a packing decision.
- Subtractive: tool, speeds and feeds, workholding, number of setups. Each
  extra setup adds a datum transfer and its own error.
- Laser and waterjet: kerf width and which side of the line it was taken from.
- Joining: fastener spec and torque, adhesive and cure schedule, weld process.

Record what the machine actually did, not what the CAM file requested, when
they differ.

### Inspection and as-built record
The gap between as-designed and as-built is where assemblies fail. Measure the
features the design depends on, not every feature.

| Feature | Nominal | Measured | Instrument | Date | Within tolerance |
|---|---|---|---|---|---|
| TBC | | | | | |

Record the instrument and its resolution. A measurement quoted to more
decimal places than the instrument resolves is a fabrication of a different
kind. If a part was accepted outside tolerance, say so here and say why: an
undocumented concession is indistinguishable from an undetected defect.
