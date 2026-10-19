"""Sensor bracket (EXAMPLE, fictional): a flat plate with two clearance holes
and filleted vertical edges. Owned by build123d.

Origin at the centre of the base face; the plate sits on z = 0, so it lands
on the Top plane when SolidWorks inserts the STEP. Every dimension comes from
params/params.yaml.
"""
from build123d import Align, Axis, Box, Cylinder, Part, Pos, fillet

PARAMS = ("length", "width", "thickness", "hole_diameter", "hole_spacing", "corner_radius")
ON_BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def build(params: dict) -> Part:
    thickness = params["thickness"]
    plate = Box(params["length"], params["width"], thickness, align=ON_BASE)

    vertical = plate.edges().filter_by(Axis.Z)
    assert len(vertical) == 4, f"expected 4 vertical edges, found {len(vertical)}"
    plate = fillet(vertical, radius=params["corner_radius"])

    hole = Cylinder(params["hole_diameter"] / 2, thickness, align=ON_BASE)
    offset = params["hole_spacing"] / 2
    return plate - Pos(-offset, 0, 0) * hole - Pos(offset, 0, 0) * hole


if __name__ == "__main__":
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root), str(root / "code" / "src")]
    from ocp_vscode import show
    from project_tools.params import load_part_params

    show(build(load_part_params("sensor_bracket", required=PARAMS)))
