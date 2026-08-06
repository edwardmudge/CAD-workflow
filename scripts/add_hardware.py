#!/usr/bin/env python3
"""Hardware core for the project template. Run once from the repo root:

    python scripts/add_hardware.py

Creates HARDWARE.md with the parts every physical project needs regardless of
domain: what the thing is, what units this project speaks, where its numbers
came from, what to check before energising it, and where the model and reality
disagree. Adds a routing row to AGENTS.md.

Domain packs (add_robotics.py, add_mechanical.py) extend this file; run this
one first. Idempotent. Seeds no postmortems, because a rule without a real
event behind it does not get followed.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "modules"))
from _common import (  # noqa: E402
    TODAY,
    add_routing_row,
    repo_root,
    report,
    report_hint,
    write,
)

ROOT = repo_root()
changed = []

HARDWARE = f"""---
status: active
verified: {TODAY}
---
# Hardware reference

The physical facts this project must not get wrong. Rung 1 of the truth
ladder: if this file and the code disagree, measure the thing and fix both.

Item: TBC (what it is, make, model, serial or build number)
Revision fitted: TBC (hardware revision, firmware or controller version)
Units in this project: TBC, one line, no exceptions (see Agent Notes)
Last verified against the physical item: never

Every number below carries where it came from. A number with no source is a
rumour, and rumours are what this file exists to stop.

Before every powered run, work through the pre-flight checklist below.

## Agent Notes

### Identity and revision
The single most expensive hardware mistake is working from the wrong
revision. Record what is actually in front of you, not what was ordered.

| Field | Value | Source |
|---|---|---|
| Make and model | TBC | |
| Serial or build number | TBC | |
| Hardware revision | TBC | |
| Firmware or controller version | TBC | |
| Date this item was last changed | TBC | |

### Units and conventions
State once, obey everywhere. Every quantity crossing a boundary (an SDK call,
a file, a plot axis, a report figure, a drawing) carries these units or is
converted at the boundary and named accordingly (`length_mm` vs `length_m`).

| Quantity | Unit | Notes |
|---|---|---|
| Length | TBC mm or m | CAD is usually mm; physics and kinematics usually m |
| Angle | TBC deg or rad | State which appears in code and which in the UI |
| Mass | TBC kg | |
| Time | TBC s | |
| Force or torque | TBC N, Nm | |
| Temperature | TBC degC or K | |

A unit-free number crossing a function signature is a defect, not a style
preference. Convert at one named place, never opportunistically.

### Provenance rule
Every quantity in this file is one of:
- **Manual**: from the manufacturer's documentation. Cite the document and page.
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
| | | |
"""

hw = ROOT / "HARDWARE.md"
if hw.exists():
    print("skip  HARDWARE.md already exists")
else:
    write(hw, HARDWARE)
    changed.append("HARDWARE.md created")

add_routing_row(
    ROOT,
    "| Hardware change | HARDWARE.md | POSTMORTEMS.md, DECISIONS.md | "
    "notes/, any TBC field, model-only results | code/src/ |\n",
    "| Hardware change |",
    changed,
)

report_hint(
    ROOT,
    "# Hardware sections that usually need nodes: what the item is and its\n"
    "# revision, units and conventions, where the numbers came from, the\n"
    "# safety case, and every place the model and the item disagree.\n",
    changed,
)

report(
    changed,
    [
        "Fill the identity and units tables in HARDWARE.md. Cite the manual page.",
        "Record D-01: what the item is, the task, and the safety envelope.",
        "Add a domain pack if one fits: add_robotics.py, add_mechanical.py.",
        "Run python scripts/check_docs.py, then commit.",
    ],
)
