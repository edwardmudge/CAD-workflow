#!/usr/bin/env python3
"""Load the made-up "sensor mount" example for a dry run. From the repo root:

    python scripts/load_cad_example.py

Run it in a throwaway copy of the template, never in a real project: it adds
fictional parts, requirements, decisions and plan items, and every one of
them is labelled EXAMPLE. Sources live in examples/sensor_mount/.

What it installs:
- parts/sensor_bracket.py (build123d) and a SolidWorks-owned sensor_cover
  placeholder that depends on it
- params, requirements R-01 and R-02, and ownership entries
- tests for the bracket and for the cover-to-bracket interface
- D entries (objective, one parameter change), PLAN.md stage S1, a glossary
  term and a HARDWARE.md fabrication row

Idempotent: a second run changes nothing. Standard library only.
"""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "modules"))
from _common import (  # noqa: E402
    TODAY,
    add_glossary_rows,
    append_log_entry,
    read,
    repo_root,
    report,
    write,
)

ROOT = repo_root()
SRC = ROOT / "examples" / "sensor_mount"
changed = []


def copy(src_rel, dst_rel):
    src, dst = SRC / src_rel, ROOT / dst_rel
    if dst.exists():
        if read(dst) != read(src):
            sys.exit(f"{dst_rel} exists and differs from the example. Use a fresh copy of the template.")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    changed.append(f"{dst_rel} added")


def data(text):
    """YAML without its comment lines: the schema examples in the headers
    mention ids such as R-01 and must not count as entries."""
    return "\n".join(line for line in text.split("\n") if not line.lstrip().startswith("#"))


def merge_yaml_list(rel, key, fragment_rel, sentinel):
    """Append list items under `key:`; an empty `key: []` is opened first."""
    path = ROOT / rel
    text = read(path)
    if sentinel in data(text):
        return
    fragment = read(SRC / fragment_rel)
    if f"\n{key}: []" in "\n" + text:
        text = text.replace(f"\n{key}: []", f"\n{key}:", 1)
    elif f"\n{key}:" not in "\n" + text:
        sys.exit(f"{rel}: no '{key}:' list found. Edit the example in by hand.")
    write(path, text.rstrip("\n") + "\n" + fragment)
    changed.append(f"{rel}: example entries added")


def refuse_on_clash(rel, token, sentinel):
    text = data(read(ROOT / rel))
    if token in text and sentinel not in text:
        sys.exit(f"{rel} already uses {token}. Load the example into a fresh copy of the template.")


# Code side: part, tests and data.
refuse_on_clash("params/requirements.yaml", "id: R-01", "part: sensor_bracket")
copy("parts/sensor_bracket.py", "parts/sensor_bracket.py")
copy("tests/test_sensor_bracket.py", "code/tests/test_sensor_bracket.py")
copy("tests/test_sensor_mount_interface.py", "code/tests/test_sensor_mount_interface.py")

params = ROOT / "params" / "params.yaml"
if "\nsensor_bracket:" not in "\n" + data(read(params)):
    write(params, read(params).rstrip("\n") + "\n" + read(SRC / "params.yaml"))
    changed.append("params/params.yaml: sensor_bracket section added")
merge_yaml_list("params/requirements.yaml", "requirements", "requirements.yaml", "part: sensor_bracket")
merge_yaml_list("parts/ownership.yaml", "parts", "ownership.yaml", "id: sensor_bracket")

# Documentation side: decisions, plan, glossary, hardware.
objective = append_log_entry(ROOT, "DECISIONS.md", "D", lambda ref: f"""
## {ref} EXAMPLE: sensor mount objective (accepted) [decision]
- Context: EXAMPLE, fictional. A sensor must be held on a panel by two M6 screws, with a cover over it.
- Decision: We will make the bracket in build123d (prismatic, parametric) and the cover in SolidWorks (styled surfaces), joined by the hole pattern.
- Alternatives: both in SolidWorks, rejected because the bracket is the part most likely to change and code makes that change testable.
- Consequences: + bracket changes are checked by tests. - the cover must be re-exported by hand when it changes.
- Parameters changed: none; initial values set in params/params.yaml.
- Tests added or changed: code/tests/test_sensor_bracket.py, code/tests/test_sensor_mount_interface.py.
- Evidence: EXAMPLE, fictional brief. Requirements R-01 and R-02 in params/requirements.yaml.
- Supersedes: none.
- Verified on: TBC.
- Non-revertible unless: the cover geometry becomes simple enough to own in code.
""", changed, "EXAMPLE: sensor mount objective")

thickness = append_log_entry(ROOT, "DECISIONS.md", "D", lambda ref: f"""
## {ref} EXAMPLE: bracket plate thickness 5 to 6 mm (accepted) [decision]
- Context: EXAMPLE, fictional. The 5 mm bracket flexed visibly under the sensor cable in a hand test.
- Decision: We will make the plate 6 mm thick.
- Alternatives: a stiffening rib, rejected because it forces a worse print orientation.
- Consequences: + stiffer plate. - about 3 g heavier, still inside R-01.
- Parameters changed: sensor_bracket.thickness: 5 → 6
- Tests added or changed: none; test_mass_within_limit already covers R-01.
- Evidence: EXAMPLE, fictional hand test. Mass after the change in exports/manifest.json.
- Supersedes: none.
- Verified on: TBC. The dry run verifies it with python code/check.py.
- Non-revertible unless: a measured deflection at 5 mm is within the sensor's alignment tolerance.
""", changed, "EXAMPLE: bracket plate thickness")

plan = ROOT / "PLAN.md"
plan_text = read(plan)
if "S1 — Sensor mount (EXAMPLE" not in plan_text:
    refs = ", ".join(r for r in (objective, thickness) if r) or "TBC"
    stage = f"""**S1 — Sensor mount (EXAMPLE, fictional)**

#### S1.1 Bracket meets its requirements [ ]
Goal: the build123d bracket passes R-01 and R-02, checked on its exported STEP.
1. python code/scripts/export.py --part sensor_bracket
2. python -m pytest code/tests/test_sensor_bracket.py
**Verify:** every test in test_sensor_bracket.py passes and the mass in exports/manifest.json is at most 25 g.
Record: {refs}.

#### S1.2 Cover holes match the bracket [ ]
Goal: the SolidWorks cover and the build123d bracket agree on the hole pattern.
1. Model sensor_cover in SolidWorks; link its hole spacing to sensor_bracket_hole_spacing in cad/equations.txt.
2. Save As STEP AP214 to cad/step/sensor_cover.step, run code/scripts/register_sw_step.py sensor_cover, remove status: placeholder.
**Verify:** test_cover_holes_match_bracket passes rather than skips.
"""
    placeholder = "**S1 — Stage name**\n\n#### S1.1 First item [ ]\nGoal: TBC.\n1. TBC\n**Verify:** TBC — state the condition so that it could fail.\n"
    if placeholder in plan_text:
        plan_text = plan_text.replace(placeholder, stage, 1)
    elif "### Open questions" in plan_text:
        plan_text = plan_text.replace("### Open questions", stage + "\n### Open questions", 1)
    else:
        sys.exit("PLAN.md: no S1 placeholder or '### Open questions' heading found.")
    write(plan, plan_text)
    changed.append("PLAN.md: stage S1 added")

add_glossary_rows(ROOT, [
    ("hole spacing", "Centre-to-centre distance between the bracket's two mounting holes.",
     "edge distance, from a hole edge to the part edge", "sensor_bracket.hole_spacing"),
], changed, "EXAMPLE")

hardware = ROOT / "HARDWARE.md"
row_tbc = "| TBC | TBC | TBC | TBC | |\n"
example_row = f"| sensor_bracket (EXAMPLE) | FDM print | TBC | ABS, 0.2 mm layers, 4 walls, flat on its base | example, {TODAY} |\n"
hw_text = read(hardware)
if "sensor_bracket (EXAMPLE)" not in hw_text and row_tbc in hw_text:
    write(hardware, hw_text.replace(row_tbc, example_row, 1))
    changed.append("HARDWARE.md: example fabrication row added")

report(changed, [
    "python code/scripts/gen_sw_equations.py (the example adds SolidWorks globals)",
    "python code/check.py (exports the bracket, runs every check)",
    "Work through the dry run in WORKFLOW.md.",
])
