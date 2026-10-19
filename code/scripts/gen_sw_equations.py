#!/usr/bin/env python3
"""Generate cad/equations.txt from params/params.yaml for SolidWorks.

One global variable per numeric part parameter, named <part id>_<param>:

    "sensor_bracket_thickness"= 6mm

Link a SolidWorks part to the file (Tools > Equations > Link to external
file) and drive its dimensions from these globals. The file is written with
CRLF line endings for SolidWorks. Never edit it by hand.

    python code/scripts/gen_sw_equations.py           # write the file
    python code/scripts/gen_sw_equations.py --check   # also exit 1 if it was out of date
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

from project_tools import EQUATIONS_FILE  # noqa: E402
from project_tools.params import load_raw, part_ids  # noqa: E402

HEADER = [
    "' GENERATED from params/params.yaml by code/scripts/gen_sw_equations.py.",
    "' Do not edit: change params.yaml and rerun. Units: mm unless stated.",
]
SW_UNIT = {"mm": "mm", "deg": "deg", "count": ""}


def format_value(value: float) -> str:
    return f"{value:.10g}"


def equation(name: str, value: float, unit: str) -> str:
    """The SolidWorks global-variable line. Syntax lives only here, so a
    correction from a SolidWorks export is a one-line change.

    Verified 2026-10-19 in SolidWorks 2025: a linked CRLF file with this
    header read 6mm, 30deg and unitless 4 as global variables, and skipped
    the ' comment lines."""
    return f'"{name}"= {format_value(value)}{SW_UNIT[unit]}'


def render() -> str:
    raw = load_raw()
    lines = list(HEADER)
    for part_id in part_ids(raw):
        for name, entry in raw[part_id].items():
            if name != "material":
                lines.append(equation(f"{part_id}_{name}", entry["value"], entry.get("unit", "mm")))
    return "\r\n".join(lines) + "\r\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 if the file was out of date")
    args = parser.parse_args()
    new = render()
    old = EQUATIONS_FILE.read_bytes().decode("utf-8") if EQUATIONS_FILE.exists() else None
    if old == new:
        print("ok    cad/equations.txt is up to date")
        return 0
    EQUATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    EQUATIONS_FILE.write_bytes(new.encode("utf-8"))
    print("ok    cad/equations.txt regenerated")
    if args.check:
        print("FAIL  it was out of date: stage cad/equations.txt and rerun")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
