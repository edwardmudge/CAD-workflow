#!/usr/bin/env python3
"""Compare two STEP files: volume added and removed, where, and the change
in mass. This is how a one-off SolidWorks edit is re-expressed in code:
diff the STEP before and after, then change params or build() until the
diff between the SolidWorks STEP and the new export is empty.

    python code/scripts/step_diff.py OLD.step NEW.step
    python code/scripts/step_diff.py OLD.step NEW.step --material ABS --export exports/diff

Both files must share a coordinate frame; a moved part shows as a large
add plus remove.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

from build123d import Shape, export_step  # noqa: E402

from project_tools.geometry import load_step, mass_g  # noqa: E402

MIN_VOLUME_MM3 = 1e-6  # boolean slivers below this are numerical noise


def solids(shape: Shape | None) -> list[Shape]:
    if shape is None:
        return []
    return [s for s in shape.solids() if s.volume > MIN_VOLUME_MM3]


def describe(label: str, pieces: list[Shape]) -> float:
    total = sum(s.volume for s in pieces)
    print(f"{label}: {total:.3f} mm3 in {len(pieces)} region(s)")
    for s in pieces:
        box = s.bounding_box()
        lo = ", ".join(f"{v:.3f}" for v in box.min)
        hi = ", ".join(f"{v:.3f}" for v in box.max)
        print(f"    {s.volume:10.3f} mm3   bbox ({lo}) to ({hi}) mm")
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--material", default="ABS", help="material from params.yaml for the mass change")
    parser.add_argument("--export", type=Path, help="write added.step and removed.step to this folder")
    args = parser.parse_args()

    old, new = load_step(args.old), load_step(args.new)
    added, removed = solids(new - old), solids(old - new)
    add_v = describe("added", added)
    rem_v = describe("removed", removed)
    print(f"net volume change: {add_v - rem_v:+.3f} mm3")
    print(f"mass: {mass_g(old, args.material):.3f} g -> {mass_g(new, args.material):.3f} g "
          f"({mass_g(new, args.material) - mass_g(old, args.material):+.3f} g, {args.material})")

    if args.export:
        args.export.mkdir(parents=True, exist_ok=True)
        for name, pieces in (("added", added), ("removed", removed)):
            if pieces:
                export_step(Shape.fuse(*pieces) if len(pieces) > 1 else pieces[0], args.export / f"{name}.step")
                print(f"ok    {args.export / name}.step")
    if not added and not removed:
        print("identical within tolerance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
