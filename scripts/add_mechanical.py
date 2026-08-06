#!/usr/bin/env python3
"""Mechanical pack. Run after add_hardware.py, from the repo root:

    python scripts/add_hardware.py
    python scripts/add_mechanical.py

Extends HARDWARE.md with the things that go wrong on made parts: which CAD
file is the source of truth and at what revision, what it is made of, how
tolerances stack, what the fabrication process actually produced, and what the
finished part measured. Seeds the glossary with the pairs that cause real
mechanical errors, and adds a routing row to AGENTS.md.

Idempotent. Seeds no postmortems, because a rule without a real event behind
it does not get followed.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "modules"))
from _common import (  # noqa: E402
    add_glossary_rows,
    add_routing_row,
    append_section,
    repo_root,
    report,
    report_hint,
    require_hardware_core,
)

ROOT = repo_root()
HW = require_hardware_core(ROOT)
changed = []

append_section(HW, "CAD and revision register", """
Name the source of truth once. A mesh export (STL, OBJ) is a derivative, never
the master: it has already lost the parametric history and usually the units.
If someone edits the export, that edit is lost at the next regeneration.

| Part | Master file and format | Revision | Derived exports | Last regenerated |
|---|---|---|---|---|
| TBC | TBC | TBC | TBC | TBC |

Rules that hold regardless of CAD package:
- The master is the native parametric file. STEP is the interchange format.
  Meshes are for visualisation and fabrication, not for dimensioning.
- A revision changes when the geometry changes, not when the file is opened.
- Every export records which revision it came from, in its filename or here.
- If the physical part was modified after fabrication (filed, drilled,
  shimmed), that is an as-built deviation. Record it below, do not
  retroactively edit the CAD to match and call it done.
""", changed, "HARDWARE.md: CAD revision register added")

append_section(HW, "Materials", """
| Part | Material and spec | Condition or temper | Density | Source |
|---|---|---|---|---|
| TBC | TBC | TBC | TBC | |

"Aluminium" is not a material specification; 6082-T6 is. "PLA" is not one
either: printed polymer properties depend on the print, not only the polymer,
so record the process parameters below alongside it. Anisotropy in printed and
laminated parts means a single stiffness or strength figure is a direction as
well as a number.
""", changed)

append_section(HW, "Tolerances, datums, and fits", """
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
""", changed, "HARDWARE.md: tolerances and datums added")

append_section(HW, "Fabrication process parameters", """
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
""", changed, "HARDWARE.md: fabrication parameters added")

append_section(HW, "Inspection and as-built record", """
The gap between as-designed and as-built is where assemblies fail. Measure the
features the design depends on, not every feature.

| Feature | Nominal | Measured | Instrument | Date | Within tolerance |
|---|---|---|---|---|---|
| TBC | | | | | |

Record the instrument and its resolution. A measurement quoted to more
decimal places than the instrument resolves is a fabrication of a different
kind. If a part was accepted outside tolerance, say so here and say why: an
undocumented concession is indistinguishable from an undetected defect.
""", changed, "HARDWARE.md: inspection record added")

add_glossary_rows(ROOT, [
    ("nominal dimension", "The intended size before tolerance is applied.", "basic dimension, which is theoretically exact and toleranced by a geometric frame", ""),
    ("tolerance", "Permitted deviation of one feature from nominal.", "clearance, which is the gap between two features", ""),
    ("clearance", "The gap between two mating features as assembled.", "allowance, the intended minimum clearance at worst case", ""),
    ("datum", "A referenced feature that measurement is taken from.", "origin, which is a coordinate system that need not touch the part", ""),
    ("as-designed", "The geometry in the master CAD file at a stated revision.", "as-built, the geometry actually produced and measured", ""),
    ("as-built", "The part as it physically exists, including rework.", "as-designed; the difference is a finding, not an error to be edited away", ""),
    ("master file", "The native parametric CAD file: the source of truth.", "STEP and mesh exports, which are derivatives and cannot be edited back", ""),
    ("worst-case stack", "Every tolerance at its least favourable limit.", "statistical stack, which allows a stated fraction of assemblies to fail", ""),
    ("build orientation", "How a part sits on the machine during fabrication.", "part orientation in the assembly; the first is a structural decision", ""),
], changed, "mechanical")

add_routing_row(
    ROOT,
    "| Mechanical or fabrication change | HARDWARE.md | DECISIONS.md, POSTMORTEMS.md | "
    "notes/, superseded CAD revisions, nominal values where as-built exists | none |\n",
    "| Mechanical or fabrication change |",
    changed,
)

report_hint(
    ROOT,
    "# Mechanical sections that usually need nodes: material and process\n"
    "# selection, datum scheme, tolerance stack-up, fabrication route,\n"
    "# and every as-designed to as-built deviation.\n",
    changed,
)

report(
    changed,
    [
        "Name the master CAD file and its revision in HARDWARE.md.",
        "State the datum scheme before dimensioning anything.",
        "Record process parameters at the time of fabrication, not from memory.",
        "Run python scripts/check_docs.py, then commit.",
    ],
)
