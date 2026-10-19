#!/usr/bin/env python3
"""Register a STEP exported from SolidWorks, so tests can tell when the
SLDPRT changes and the STEP goes stale.

In SolidWorks: File > Save As > STEP AP214, to the `step` path given in
parts/ownership.yaml (under cad/step/). Then:

    python code/scripts/register_sw_step.py PART_ID

Records the SLDPRT and STEP hashes in cad/step/manifest.json and prints the
bounding box, volume and holes, so you can sanity-check the export. Commit
the SLDPRT, the STEP and the manifest together.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

from build123d import Axis  # noqa: E402

from project_tools import SW_MANIFEST_FILE  # noqa: E402
from project_tools.geometry import bbox_size, hole_centres, load_step  # noqa: E402
from project_tools.ownership import by_id  # noqa: E402
from project_tools.provenance import file_sha256, git_state, read_json, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("part_id")
    args = parser.parse_args()

    part = by_id().get(args.part_id)
    if not part or part["owner"] != "solidworks":
        print(f"ERROR {args.part_id} is not a solidworks part in parts/ownership.yaml")
        return 1
    source, step = ROOT / part["source"], ROOT / part["step"]
    for path in (source, step):
        if not path.exists():
            print(f"ERROR {path.relative_to(ROOT)} not found")
            return 1

    shape = load_step(step)
    print(f"bbox   {' x '.join(f'{v:.3f}' for v in bbox_size(shape))} mm")
    print(f"volume {shape.volume:.3f} mm3")
    for axis_name, axis in (("X", Axis.X), ("Y", Axis.Y), ("Z", Axis.Z)):
        holes = hole_centres(shape, axis)
        if holes:
            sizes = sorted({h.diameter_mm for h in holes})
            print(f"holes  {len(holes)} along {axis_name}, diameters {sizes} mm")

    manifest = read_json(SW_MANIFEST_FILE)
    manifest[args.part_id] = {
        "source_sha256": file_sha256(source),
        "step_sha256": file_sha256(step),
        "registered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": git_state()["commit"],
    }
    write_json(SW_MANIFEST_FILE, manifest)
    print(f"ok    {args.part_id} registered in {SW_MANIFEST_FILE.relative_to(ROOT)}")
    if part["status"] == "placeholder":
        print(f"next  remove `status: placeholder` from {args.part_id} in parts/ownership.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
