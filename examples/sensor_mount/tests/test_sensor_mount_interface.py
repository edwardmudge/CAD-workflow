"""Cover to bracket interface (EXAMPLE). The cover is owned by SolidWorks and
the bracket by build123d; the test reads both STEPs, so it holds whichever
tool changes. Each part keeps its own origin, so the hole patterns are
compared by spacing, not by absolute position."""
from itertools import combinations

import pytest
from build123d import Axis

from project_tools.geometry import hole_centres

TOL_MM = 0.05


def spacings(holes):
    return sorted(
        sum((a - b) ** 2 for a, b in zip(h1.centre_mm, h2.centre_mm)) ** 0.5
        for h1, h2 in combinations(holes, 2)
    )


def test_cover_holes_match_bracket(ownership, exported_step):
    if ownership["sensor_cover"]["status"] == "placeholder":
        pytest.skip(
            "sensor_cover is a placeholder: model it in SolidWorks, export STEP AP214 "
            "to cad/step/, run register_sw_step.py, then remove status: placeholder"
        )
    bracket = hole_centres(exported_step("sensor_bracket"), Axis.Z)
    cover = hole_centres(exported_step("sensor_cover"), Axis.Z)
    assert len(cover) == len(bracket), f"cover has {len(cover)} holes, bracket has {len(bracket)}"
    assert spacings(cover) == pytest.approx(spacings(bracket), abs=TOL_MM)
