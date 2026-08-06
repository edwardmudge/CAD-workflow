#!/usr/bin/env python3
"""Load the Fairino FR5 as worked example data. Run after the robotics pack:

    python scripts/add_hardware.py
    python scripts/add_robotics.py --dof 6
    python scripts/load_fr5_example.py

Fills HARDWARE.md with the real FR5 numbers, seeds one genuine postmortem (the
mesh double-transform fault), two decisions, a worked PLAN.md item showing what
a Verify clause looks like when it has actually been measured, the
mesh-convention terms, and example report nodes.

Log entries take the next free D and P numbers rather than assuming D-01, so
this can be run after you have already recorded your own day-one decision.
Idempotent.

Provenance, preserved because it matters more than the numbers:
  DH table       Huang et al. (2026), mm and radians
  Joint limits   measured from the teach pendant, 2026-04-25
  Mesh, TCP      FR5 FK kit OBJ export, zero-pose world frame
Verify against your own machine before any powered run. Another FR5 may
differ by tool, mounting, or controller configuration.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "modules"))
from _common import (  # noqa: E402
    add_glossary_rows,
    append_log_entry,
    read,
    repo_root,
    report,
    require_hardware_core,
    write,
)

ROOT = repo_root()
hw_path = require_hardware_core(ROOT)
changed = []

if "Kinematic parameters" not in read(hw_path):
    sys.exit("Robotics pack not installed. Run: python scripts/add_robotics.py --dof 6")


def sub(text, old, new, what):
    """Replace, or stop. A loader that silently skips leaves a half-filled file."""
    if old not in text:
        sys.exit(f"HARDWARE.md: expected placeholder for {what!r}. "
                 f"Has it been edited? Fill it in by hand instead.")
    return text.replace(old, new, 1)


# ------------------------------------------------------------------ log entries
# Allocated first: the numbers appear in HARDWARE.md, PLAN.md and the report
# nodes, so nothing may hard-code them.
P_MESH = append_log_entry(
    ROOT, "POSTMORTEMS.md", "P",
    lambda ref: f"""
## {ref} Mesh vertices are in world zero-pose frame, not link-local (severity: medium)
- Rule: never apply T_0_i(q) directly to OBJ vertices. Use the delta form
  Delta_i = T_0_i(q) @ inv(T_0_i(0)), and apply no transform at all to the
  static base mesh Robot0.obj. The nozzle and TCP use Delta_6.
- Event: the OBJ files were exported from a CAD assembly posed at zero, so each
  vertex already encodes T_0_i(q=0). Applying the current transform on top gave
  T_0_i(q) . T_0_i(0) . v, one transform too many, and the arm rendered as
  garbage that moved roughly correctly, which made it look like a scaling bug.
- Detection: visual, on first render. Not by a test. That is itself a finding:
  a numeric zero-pose assertion would have caught it in seconds.
- Impact: development time lost to debugging the wrong subsystem.
- Why this rule prevents recurrence: it names the frame the vertices live in.
  The fault was a frame assumption, not arithmetic, so the fix is a stated
  convention, recorded in HARDWARE.md under Frames.
- Actions: [x] convention recorded in HARDWARE.md (done)
- Actions: [ ] assert T_0_6(0) position equals [-820.0, -202.0, 50.0] mm in a
  runnable check (done when the check exists and has been seen to fail)
""",
    changed, "Mesh vertices are in world zero-pose frame")

D_DH = append_log_entry(
    ROOT, "DECISIONS.md", "D",
    lambda ref: f"""
## {ref} Use standard DH parameters for the FR5 kinematic model (accepted) [decision]
- Context: FK and IK both need a kinematic model. Standard and modified DH
  produce different tables and are not interchangeable.
- Decision: We will use standard DH, with the table from Huang et al. (2026),
  lengths in mm and angles in rad.
- Alternatives: modified DH (rejected, the available table is standard form);
  URDF from the vendor (rejected for now, not obtained; revisit if the
  zero-pose check fails).
- Consequences: + one published table, directly usable. - the numbers are from
  literature, not measured on this arm, so they carry unknown calibration
  error and must not be trusted for powered motion until verified.
- Verified on: 2026-04-25, by the zero-pose FK check reproducing
  [-820.0, -202.0, 50.0] mm. That validates the table's self-consistency, not
  its agreement with this physical arm, which remains unmeasured.
- Non-revertible unless: a measured calibration of this arm disagrees with the
  literature table by more than the application tolerance.
""",
    changed, "Use standard DH parameters")

D_MESH = append_log_entry(
    ROOT, "DECISIONS.md", "D",
    lambda ref: f"""
## {ref} Transform meshes by delta rather than re-authoring them link-local (accepted) [shortcut]
- Context: OBJ vertices are in the zero-pose world frame (see {P_MESH}). Either
  re-export each mesh in its own link frame, or apply a delta at run time.
- Decision: We will apply Delta_i = T_0_i(q) @ inv(T_0_i(0)) each frame.
- Alternatives: re-export from CAD in link-local frames (rejected, needs CAD
  access and repeats on every mesh revision).
- Consequences: + no CAD dependency, works with the meshes as supplied.
  - one matrix inverse per link per frame, and the convention must be
  explained to anyone reading the render code.
- Verified on: 2026-04-25, by visual comparison against the teach pendant pose.
- Non-revertible unless: mesh count or frame-rate target rises enough that the
  per-frame inverse shows up in a profile.
- Ceiling: fine at 7 meshes and interactive rates. Upgrade path: precompute
  inv(T_0_i(0)) once at init, then re-export link-local if it still matters.
  Marker: debt-01.
""",
    changed, "Transform meshes by delta")

if not (P_MESH and D_DH and D_MESH):
    print("skip  example log entries already present; re-reading their numbers")
    dec, pm = read(ROOT / "DECISIONS.md"), read(ROOT / "POSTMORTEMS.md")
    P_MESH = P_MESH or re.search(r"^## (P-\d+) Mesh vertices", pm, re.M).group(1)
    D_DH = D_DH or re.search(r"^## (D-\d+) Use standard DH", dec, re.M).group(1)
    D_MESH = D_MESH or re.search(r"^## (D-\d+) Transform meshes", dec, re.M).group(1)

# ------------------------------------------------------------------ HARDWARE.md
hw = read(hw_path)
if "Fairino FR5" in hw:
    print("skip  HARDWARE.md already carries FR5 data")
else:
    hw = sub(hw, "Item: TBC (what it is, make, model, serial or build number)",
             "Item: Fairino FR5, 6R serial collaborative arm", "item identity")
    hw = sub(hw, "Revision fitted: TBC (hardware revision, firmware or controller version)",
             "Revision fitted: TBC, controller and SDK version not yet recorded", "revision")
    hw = sub(hw, "Units in this project: TBC, one line, no exceptions (see Agent Notes)",
             "Units: lengths mm, angles rad internally, deg at every UI and limits table",
             "units line")
    hw = sub(hw, "Last verified against the physical item: never",
             "Last verified against the physical item: limits 2026-04-25 (teach "
             "pendant); DH from literature, never measured", "last verified")

    hw = sub(hw, "| Make and model | TBC | |",
             "| Make and model | Fairino FR5 | vendor datasheet |", "make and model")
    hw = sub(hw, "| Length | TBC mm or m | CAD is usually mm; physics and kinematics usually m |",
             "| Length | mm | DH table, meshes, and TCP are all mm. Do not mix in m |",
             "length units")
    hw = sub(hw, "| Angle | TBC deg or rad | State which appears in code and which in the UI |",
             "| Angle | rad internally, deg at boundaries | Limits and sliders are deg; "
             "DH theta is rad. Name every variable `_deg` or `_rad` |", "angle units")

    # Frames
    hw = sub(hw, "| World / base | TBC | TBC | |",
             "| World / base | Robot base, static | Per Robot0.obj export | "
             "CAD assembly at zero pose |", "world frame")
    hw = sub(hw, "| Flange | TBC | TBC | |",
             "| Flange | T_0_6 | Standard DH chain | DH table below |", "flange frame")
    hw = sub(hw, "| TCP | TBC offset from flange | TBC | |",
             "| TCP | [-798.137, -228.017, -109.903] mm | Zero-pose world frame, "
             "not a local offset | TCP.txt |", "TCP frame")
    hw = sub(hw, "| Mesh / CAD | TBC | TBC | Note any offset from the kinematic frame |",
             f"| Mesh / CAD | Zero-pose WORLD frame | Same as world | OBJ vertices "
             f"already encode T_0_i(q=0). See {P_MESH} |", "mesh frame")
    hw = sub(hw, "Rotation convention: TBC (e.g. intrinsic XYZ, quaternion order wxyz).",
             "Rotation convention: 4x4 homogeneous transforms throughout, standard DH form.",
             "rotation convention")

    # Kinematics
    hw = sub(hw, "DH convention used: TBC (standard Denavit-Hartenberg or modified). State",
             "DH convention used: STANDARD Denavit-Hartenberg (not modified). State",
             "DH convention")
    dh_old = re.search(
        r"\| Joint \| a \| alpha \| d \| theta offset \|\n\|---\|---\|---\|---\|---\|\n"
        r"(?:\| \d+ \| \| \| \| \|\n)+", hw)
    if not dh_old:
        sys.exit("HARDWARE.md: DH table not found. Was add_robotics.py run with --dof 6?")
    hw = hw.replace(dh_old.group(0),
                    "| Joint | a (mm) | alpha (rad) | d (mm) | theta offset |\n"
                    "|---|---|---|---|---|\n"
                    "| 1 | 0 | +pi/2 | 152 | 0 |\n"
                    "| 2 | -425 | 0 | 0 | 0 |\n"
                    "| 3 | -395 | 0 | 0 | 0 |\n"
                    "| 4 | 0 | +pi/2 | 102 | 0 |\n"
                    "| 5 | 0 | -pi/2 | 102 | 0 |\n"
                    "| 6 | 0 | 0 | 100 | 0 |\n")
    hw = sub(hw,
             "Source of these numbers: TBC (manufacturer manual and page, or measured).\n"
             "Numbers taken from a forum post are not a source.",
             "Source of these numbers: Huang et al. (2026). Literature, NOT measured on\n"
             "this machine. Treat as provisional until the zero-pose check below passes.\n\n"
             "theta_i = deg2rad(joint_angle_deg) + offset. Chain: T_0_6 = T_0_1 ... T_5_6.",
             "DH source")
    hw = sub(hw,
             "Self-check: state one pose whose forward kinematics you have computed and\n"
             "verified, with the joint values in and the position out. A kinematic model\n"
             "with no worked example is a model nobody has run.",
             "Self-check: joints [0,0,0,0,0,0] deg give T_0_6 position\n"
             "[-820.0, -202.0, 50.0] mm, verified 2026-04-25. This is the one runnable\n"
             "check the kinematics must leave behind. If it fails, the DH table or the\n"
             "convention is wrong.", "FK self-check")

    # Limits
    lim_old = re.search(
        r"\| Joint \| Min \| Max \| Max speed \| Notes \|\n\|---\|---\|---\|---\|---\|\n"
        r"(?:\| \d+ \| \| \| \| \|\n)+", hw)
    if not lim_old:
        sys.exit("HARDWARE.md: joint limits table not found.")
    hw = hw.replace(lim_old.group(0),
                    "| Joint | Min (deg) | Max (deg) | Max speed | Slider range (deg) |\n"
                    "|---|---|---|---|---|\n"
                    "| J1 | -174 | +174 | TBC | -170 to 170 |\n"
                    "| J2 | -264 | +84 | TBC | -130 to 80 (avoid deep negative, collision) |\n"
                    "| J3 | -159 | +159 | TBC | -155 to 155 |\n"
                    "| J4 | -264 | +84 | TBC | -170 to 80 |\n"
                    "| J5 | -174 | +174 | TBC | -170 to 170 |\n"
                    "| J6 | -174 | +174 | TBC | -170 to 170 |\n")
    hw = sub(hw, "Check for asymmetry before assuming symmetry. An arm whose limits run -264 to\n"
                 "+84 will quietly break any code that stores a single magnitude per joint.",
             "J2 and J4 ARE asymmetric on this arm (-264 to +84). Any code storing a single\n"
             "magnitude per joint is wrong for it. Source: teach pendant, 2026-04-25.\n\n"
             "Home = [0, 0, 0, 0, 90, 0] deg. J5 = 90 points the tool down (-Z). Home is\n"
             "NOT the zero configuration; the DH zero-pose check uses all zeros.",
             "asymmetry note")

    hw = sub(hw,
             "| Assumption in the model | Reality on the item | Handled by |\n|---|---|---|\n| | | |",
             "| Assumption in the model | Reality on the item | Handled by |\n|---|---|---|\n"
             "| DH from literature is exact | Real arm has manufacturing tolerance and "
             "calibration offsets | TBC, measure before powered runs |\n"
             "| Joint moves instantly to slider value | Rates, acceleration limits, and "
             "latency apply | TBC |\n"
             "| No self-collision | Deep negative J2 can collide | Slider ranges above |\n"
             "| No payload | Tool mass shifts CoG and reachable speed | TBC |",
             "parity table")
    write(hw_path, hw)
    changed.append("HARDWARE.md: FR5 data loaded")

# ------------------------------------------------------------------------ PLAN
plan_path = ROOT / "PLAN.md"
plan = read(plan_path)
if "Kinematic model reproduces the zero pose" in plan:
    print("skip  PLAN.md example item already present")
else:
    used = [int(m) for m in re.findall(r"^#{2,6}\s+S1\.(\d+)\b", plan, re.M)]
    item = f"""#### S1.{max(used, default=0) + 1} Kinematic model reproduces the zero pose [x]
Goal: a forward-kinematics chain that can be trusted before anything moves.
1. Enter the standard DH table from Huang et al. (2026) — done
2. Compute T_0_6 with all joints at zero — done
**Verify:** FK of joints [0,0,0,0,0,0] deg puts the flange origin within 0.1 mm
of [-820.0, -202.0, 50.0] mm.
Measured: [-820.0, -202.0, 50.0] mm, exact to the quoted precision, 2026-04-25.
Record: {D_DH}.

"""
    write(plan_path, plan.replace("### Open questions", item + "### Open questions", 1))
    changed.append("PLAN.md: worked example item added")

# -------------------------------------------------------------------- GLOSSARY
add_glossary_rows(ROOT, [
    ("zero pose", "All six joints at 0 deg. The frame the OBJ meshes were exported in.",
     "home, which is [0,0,0,0,90,0] deg on this arm", "zero_joints"),
    ("delta transform", "Delta_i = T_0_i(q) @ inv(T_0_i(0)), applied to rest vertices.",
     f"T_0_i itself; applying that directly double-transforms. See {P_MESH}", "Delta"),
    ("rest verts", "Mesh vertices as loaded, in zero-pose world frame.",
     "link-local vertices, which these are not", "rest_verts"),
    ("Robot0.obj", "The static base mesh. Never transformed.",
     "Robot1.obj to Robot6.obj, which all move", ""),
], changed, "FR5")

# ---------------------------------------------------------------------- report
rn_path = ROOT / "report" / "report_nodes.md"
if rn_path.exists():
    rn = read(rn_path)
    if f"[{D_DH}]" in rn:
        print("skip  report nodes already present")
    else:
        write(rn_path, rn.rstrip("\n") + "\n" + "\n".join([
            f"- [{D_DH}] 2026-04-25 | standard DH chosen, table from Huang et al. (2026) | "
            f"alt: modified DH, vendor URDF | evidence: DECISIONS.md {D_DH}, HARDWARE.md | "
            f"section: Method",
            f"- [{D_MESH}] 2026-04-25 | mesh delta transform rather than link-local re-export | "
            f"alt: re-export from CAD | evidence: DECISIONS.md {D_MESH}, debt-01 | section: Method",
            f"- [{P_MESH}] 2026-04-25 | mesh frame assumption caused double transform | "
            f"alt: n/a | evidence: POSTMORTEMS.md {P_MESH} | section: Discussion",
        ]))
        changed.append("report_nodes.md: 3 example nodes added")

report(changed, [
    "Re-verify joint limits on your own teach pendant, and update the date.",
    "Run the FK zero-pose check. Literature DH is provisional until it passes.",
    "Fill the stop behaviour table from the manual. It is still TBC.",
    "Run python scripts/check_docs.py, then commit.",
])
print("\nThis is EXAMPLE data from a previous FR5 project. Another FR5 may differ by")
print("tool, mounting, or controller configuration. Verify before any powered run.")
