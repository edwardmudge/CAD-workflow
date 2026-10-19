#!/usr/bin/env python3
"""Build every build123d part and export STEP (AP214) and STL to exports/,
recording provenance in exports/manifest.json.

    python code/scripts/export.py               # all build123d parts
    python code/scripts/export.py --part ID     # one part

Exit 1 if any part fails. Never edit exports/ by hand: rerun this.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

from build123d import export_step, export_stl  # noqa: E402

from parts import load_module  # noqa: E402
from project_tools import EXPORTS, MANIFEST_FILE  # noqa: E402
from project_tools.geometry import bbox_size, mass_g  # noqa: E402
from project_tools.ownership import load_ownership  # noqa: E402
from project_tools.params import load_part_params, params_hash  # noqa: E402
from project_tools.provenance import git_state, kernel_versions, read_json, text_sha256, write_json  # noqa: E402


def export_part(part: dict) -> dict:
    module = load_module(part["id"], part["source"])
    params = load_part_params(part["id"], required=module.PARAMS)
    shape = module.build(params)
    if not shape.is_valid:
        raise ValueError(f"{part['id']}: build() returned an invalid solid")
    step = ROOT / part["step"]
    step.parent.mkdir(parents=True, exist_ok=True)
    if not export_step(shape, step):
        raise RuntimeError(f"{part['id']}: STEP export failed")
    if not export_stl(shape, step.with_suffix(".stl")):
        raise RuntimeError(f"{part['id']}: STL export failed")
    return {
        **git_state(),
        "source_sha256": text_sha256(ROOT / part["source"]),
        "params_sha256": params_hash(part["id"]),
        "material": params["material"],
        "mass_g": round(mass_g(shape, params["material"]), 3),
        "bbox_mm": [round(v, 4) for v in bbox_size(shape)],
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": kernel_versions(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part", help="export only this part id")
    args = parser.parse_args()

    parts = [part for part in load_ownership() if part["owner"] == "build123d"]
    if args.part:
        parts = [part for part in parts if part["id"] == args.part]
        if not parts:
            print(f"ERROR {args.part} is not a build123d part in parts/ownership.yaml")
            return 1

    EXPORTS.mkdir(exist_ok=True)
    manifest = read_json(MANIFEST_FILE)
    known = {part["id"] for part in load_ownership()}
    manifest = {pid: entry for pid, entry in manifest.items() if pid in known}
    failures = 0
    for part in parts:
        try:
            manifest[part["id"]] = export_part(part)
            entry = manifest[part["id"]]
            print(f"ok    {part['id']}: {entry['mass_g']} g, bbox {entry['bbox_mm']} mm")
        except Exception:  # report every part, then fail once
            failures += 1
            print(f"FAIL  {part['id']}")
            traceback.print_exc()
    write_json(MANIFEST_FILE, manifest)
    if not parts:
        print("skip  no build123d parts in parts/ownership.yaml")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
