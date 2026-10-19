#!/usr/bin/env python3
"""Render isometric, top and front projections of STEP files to
exports/renders/, as SVG (for people) and PNG (for agents: Claude and Codex
can look at a PNG but only read an SVG as text).

    python code/scripts/render.py                       # every STEP in exports/
    python code/scripts/render.py cad/step/cover.step   # any STEP, e.g. a SolidWorks export

Views use build123d's frame (+Z up). SolidWorks parts are +Y up, so their
"top" view here is SolidWorks' front view.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from build123d import Edge, ExportSVG, GeomType, LineType, Shape, Vector  # noqa: E402

from project_tools import EXPORTS  # noqa: E402
from project_tools.geometry import bbox_size, load_step  # noqa: E402

# view name: (direction from the part towards the viewer, viewport up)
VIEWS = {
    "iso": ((1, -1, 1), (0, 0, 1)),
    "top": ((0, 0, 1), (0, 1, 0)),
    "front": ((0, -1, 0), (0, 0, 1)),
}
CURVE_SAMPLES = 48
VIEW_DISTANCE = 3  # bounding-box diagonals between the part and the viewport


def project(shape: Shape, direction: tuple, up: tuple) -> tuple[list[Edge], list[Edge]]:
    box = shape.bounding_box()
    centre = box.center()
    origin = centre + Vector(direction).normalized() * box.diagonal * VIEW_DISTANCE
    return shape.project_to_viewport(origin, up, centre)


def polyline(edge: Edge) -> tuple[list[float], list[float]]:
    count = 2 if edge.geom_type == GeomType.LINE else CURVE_SAMPLES
    points = [edge.position_at(i / (count - 1)) for i in range(count)]
    return [p.X for p in points], [p.Y for p in points]


def write_svg(visible: list[Edge], hidden: list[Edge], path: Path) -> None:
    svg = ExportSVG(margin=5)
    svg.add_layer("hidden", line_color="gray", line_type=LineType.ISO_DOT)
    svg.add_layer("visible")
    svg.add_shape(hidden, layer="hidden")
    svg.add_shape(visible, layer="visible")
    svg.write(path)


def write_png(visible: list[Edge], hidden: list[Edge], path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    for edges, style in ((hidden, {"color": "0.65", "lw": 0.6, "ls": "--"}), (visible, {"color": "k", "lw": 1.0})):
        for edge in edges:
            ax.plot(*polyline(edge), **style)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def render(step: Path, out_dir: Path) -> list[Path]:
    shape = load_step(step)
    size = " x ".join(f"{v:g}" for v in (round(s, 2) for s in bbox_size(shape)))
    written = []
    for view, (direction, up) in VIEWS.items():
        visible, hidden = project(shape, direction, up)
        base = out_dir / f"{step.stem}_{view}"
        write_svg(visible, hidden, base.with_suffix(".svg"))
        write_png(visible, hidden, base.with_suffix(".png"), f"{step.stem}: {view}, bbox {size} mm")
        written += [base.with_suffix(".svg"), base.with_suffix(".png")]
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("steps", nargs="*", type=Path, help="STEP files (default: every STEP in exports/)")
    args = parser.parse_args()
    steps = args.steps or sorted(EXPORTS.glob("*.step"))
    if not steps:
        print("skip  no STEP files in exports/; run code/scripts/export.py first")
        return 0
    out_dir = EXPORTS / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for step in steps:
        try:
            for path in render(step, out_dir):
                print(f"ok    {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        except Exception as exc:  # report every file, then fail once
            failures += 1
            print(f"FAIL  {step}: {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
