#!/usr/bin/env python3
"""Robotics pack. HARDWARE.md ships with the template; from the repo root:

    python scripts/add_robotics.py --dof 6

Extends HARDWARE.md with the things that go wrong on articulated machines:
frames and rotation conventions, kinematic parameters, joint limits and rates,
singularities, and stop behaviour. Seeds the glossary with the term pairs that
reliably cause robotics bugs, and adds a routing row to AGENTS.md.

--dof defaults to 6. It sizes the joint tables only; nothing else assumes a
particular arm, so a 7-axis arm, a 3-axis gantry, or a delta all fit.

Idempotent. Seeds no postmortems, because a rule without a real event behind
it does not get followed.
"""
import argparse
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

parser = argparse.ArgumentParser(description="Add the robotics pack to HARDWARE.md.")
parser.add_argument("--dof", type=int, default=6,
                    help="number of actuated joints; sizes the joint tables (default 6)")
args = parser.parse_args()
if not 1 <= args.dof <= 12:
    sys.exit("--dof must be between 1 and 12. Beyond that, write the table by hand.")

ROOT = repo_root()
HW = require_hardware_core(ROOT)
changed = []

joints = range(1, args.dof + 1)
dh_rows = "\n".join(f"| {j} | | | | |" for j in joints)
limit_rows = "\n".join(f"| {j} | | | | |" for j in joints)

append_section(HW, "Frames", """
| Frame | Origin | Axes | Defined by |
|---|---|---|---|
| World / base | TBC | TBC | |
| Flange | TBC | TBC | |
| TCP | TBC offset from flange | TBC | |
| Mesh / CAD | TBC | TBC | Note any offset from the kinematic frame |

Rotation convention: TBC (e.g. intrinsic XYZ, quaternion order wxyz).
Ambiguity here is the single most common source of silent pose errors, and it
is silent precisely because a wrong convention still produces a valid pose.

Mesh vertices exported from CAD are often already in the zero-pose world
frame, meaning they encode the zero-pose transform. Applying the full pose
transform on top double-transforms them. State which convention the meshes in
this project use, and how it was checked.
""", changed, "HARDWARE.md: frames section added")

append_section(HW, "Kinematic parameters", f"""
DH convention used: TBC (standard Denavit-Hartenberg or modified). State
which. The two are not interchangeable and produce different tables from the
same machine.

| Joint | a | alpha | d | theta offset |
|---|---|---|---|---|
{dh_rows}

Source of these numbers: TBC (manufacturer manual and page, or measured).
Numbers taken from a forum post are not a source.

Self-check: state one pose whose forward kinematics you have computed and
verified, with the joint values in and the position out. A kinematic model
with no worked example is a model nobody has run.
""", changed, f"HARDWARE.md: kinematics section added ({args.dof} joints)")

append_section(HW, "Joint limits and rates", f"""
| Joint | Min | Max | Max speed | Notes |
|---|---|---|---|---|
{limit_rows}

Software limits should sit inside hardware limits. Record both if they differ,
and record which one the code actually enforces: a conservative development
range left in place silently gates the solver and looks like an unreachable
workspace.

Check for asymmetry before assuming symmetry. An arm whose limits run -264 to
+84 will quietly break any code that stores a single magnitude per joint.
""", changed, "HARDWARE.md: joint limits section added")

append_section(HW, "Singularities and excluded regions", """
TBC. Known configurations to avoid, what the controller does on entering them,
and how close is too close. A singularity does not announce itself: it appears
as a joint rate demand going to infinity for a finite Cartesian speed.
""", changed)

append_section(HW, "Stop behaviour", """
Fill this in from the manual before the first powered run, not after.

| Command or event | What it does | Recovery | Holds brakes? |
|---|---|---|---|
| E-stop (physical) | | | |
| Protective stop | | | |
| SDK stop call 1: TBC name | | | |
| SDK stop call 2: TBC name | | | |

If two SDK calls have similar names and different semantics, add both to
GLOSSARY.md today, not after the first surprise.
""", changed)

add_glossary_rows(ROOT, [
    ("joint", "One actuated degree of freedom.", "link, axis (vendor UIs often number axes differently)", ""),
    ("link", "The rigid body between two joints.", "joint", ""),
    ("flange", "The mechanical mounting face at the end of the arm.", "TCP; they coincide only with no tool fitted", ""),
    ("TCP", "Tool centre point, the controlled point, offset from the flange.", "flange, end effector (the physical tool)", ""),
    ("pose", "Position and orientation together, 6 numbers.", "position (3 numbers only)", ""),
    ("home", "A named joint configuration, usually all zeros.", "zero position (may differ per vendor), park position", ""),
    ("FK", "Forward kinematics: joint angles to pose. One answer.", "IK, which may have many answers or none", ""),
    ("IK", "Inverse kinematics: pose to joint angles. Often several solutions.", "FK", ""),
    ("configuration", "Which IK branch is in use (elbow up or down, wrist flip).", "pose; several configurations reach the same pose", ""),
    ("standard DH", "Denavit-Hartenberg parameters, original convention.", "modified DH; the tables are not interchangeable", ""),
    ("workspace", "The set of poses the TCP can reach.", "reach (a scalar distance)", ""),
    ("payload", "Mass the arm can carry, at a stated centre of gravity.", "tool mass alone; the CoG offset matters", ""),
    ("user frame", "A named frame the operator works in, base to workpiece.", "TCP offset: flange to tool, opposite direction, same 6-vector shape", ""),
], changed, "robotics")

add_routing_row(
    ROOT,
    "| Motion or kinematics change | HARDWARE.md | POSTMORTEMS.md, DECISIONS.md | "
    "notes/, simulation-only reachability results | code/src/ |\n",
    "| Motion or kinematics change |",
    changed,
)

report_hint(
    ROOT,
    "# Robotics sections that usually need nodes: frames and conventions,\n"
    "# kinematic model, calibration, control approach, safety case,\n"
    "# simulation to hardware gap.\n",
    changed,
)

report(
    changed,
    [
        "Fill the TBC fields in HARDWARE.md from the manual. Cite the page.",
        "Compute one FK pose by hand and record it as the self-check.",
        "Record the stop behaviour before the first powered run.",
        "Run python scripts/check_docs.py, then commit.",
    ],
)
