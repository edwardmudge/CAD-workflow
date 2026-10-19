"""Sensor bracket (EXAMPLE): requirement and geometry checks on the exported STEP."""
import pytest
from build123d import Axis

from project_tools.geometry import bbox_size, hole_centres, mass_g
from project_tools.standards import iso_273_medium_size

PART = "sensor_bracket"
TOL_MM = 0.01


@pytest.fixture(scope="module")
def shape(exported_step):
    return exported_step(PART)


@pytest.fixture(scope="module")
def p(part_params):
    return part_params(PART)


def test_mass_within_limit(shape, p, requirement):
    req = requirement("R-01")
    mass = mass_g(shape, p["material"])
    assert mass <= req["max"], (
        f"{req['id']} breached: mass {mass:.2f} {req['unit']} > limit {req['max']} {req['unit']} "
        f"({req['text']})"
    )


def test_bounding_box_matches_params(shape, p):
    expected = (p["length"], p["width"], p["thickness"])
    assert bbox_size(shape) == pytest.approx(expected, abs=TOL_MM)


def test_two_holes_at_spacing(shape, p):
    holes = hole_centres(shape, Axis.Z)
    assert len(holes) == 2, f"expected 2 holes, found {len(holes)}: {holes}"
    for hole in holes:
        assert hole.diameter_mm == pytest.approx(p["hole_diameter"], abs=TOL_MM)
    (x1, y1, _), (x2, y2, _) = (hole.centre_mm for hole in holes)
    spacing = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    assert spacing == pytest.approx(p["hole_spacing"], abs=TOL_MM)


def test_holes_are_iso_273_medium(shape, requirement):
    req = requirement("R-02")
    for hole in hole_centres(shape, Axis.Z):
        assert iso_273_medium_size(hole.diameter_mm), (
            f"{req['id']}: hole diameter {hole.diameter_mm} mm is not an ISO 273 medium clearance size"
        )


def test_hole_edge_distance_meets_min_wall(shape, rules):
    """Hole edge to outer edge, measured on the bounding box. Adequate for a
    flat plate; a shaped part needs a distance query instead."""
    box = shape.bounding_box()
    for hole in hole_centres(shape, Axis.Z):
        x, y, _ = hole.centre_mm
        wall = min(x - box.min.X, box.max.X - x, y - box.min.Y, box.max.Y - y) - hole.diameter_mm / 2
        assert wall >= rules["min_wall"], f"wall {wall:.2f} mm < min_wall {rules['min_wall']} mm"
