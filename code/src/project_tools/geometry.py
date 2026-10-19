"""Geometry helpers used by tests and scripts. They work on any STEP,
whichever tool made it, so the same checks apply to every owner.

Units: lengths in mm, volumes in mm3, masses in g, densities in g/cm3.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build123d import Axis, GeomType, Shape, import_step

from project_tools.params import density_g_cm3

MM3_PER_CM3 = 1000.0


@dataclass(frozen=True)
class Hole:
    centre_mm: tuple[float, float, float]  # axis point nearest the origin
    diameter_mm: float


def load_step(path: Path | str) -> Shape:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    return import_step(path)


def mass_g(shape: Shape, material: str) -> float:
    """Solid mass. For printed parts this is an upper bound: infill is not modelled."""
    return shape.volume / MM3_PER_CM3 * density_g_cm3(material)


def bbox_size(shape: Shape) -> tuple[float, float, float]:
    size = shape.bounding_box().size
    return (size.X, size.Y, size.Z)


def interference_volume(a: Shape, b: Shape) -> float:
    common = a & b
    return common.volume if common is not None else 0.0


def hole_centres(shape: Shape, axis: Axis = Axis.Z, tol: float = 1e-3) -> list[Hole]:
    """Holes parallel to axis: concave cylindrical faces, grouped by axis line
    and diameter.

    Concave means the surface normal points towards the cylinder axis, which
    excludes fillets and outside diameters. Grouping merges the half faces
    that SolidWorks writes for one hole when it splits periodic faces.
    """
    direction = axis.direction.normalized()
    found: dict[tuple, Hole] = {}
    for face in shape.faces().filter_by(GeomType.CYLINDER):
        face_axis = face.axis_of_rotation
        if face_axis is None or abs(abs(face_axis.direction.dot(direction)) - 1) > tol:
            continue
        point = face.position_at(0.5, 0.5)
        offset = point - face_axis.position
        radial = offset - direction * offset.dot(direction)
        if radial.dot(face.normal_at(0.5, 0.5)) >= 0:
            continue  # convex: a fillet or an outside diameter
        base = face_axis.position - direction * face_axis.position.dot(direction)
        centre = tuple(round(c, 3) + 0.0 for c in base)
        diameter = round(2 * radial.length, 3)
        key = (*(round(c / tol) for c in centre), round(diameter / tol))
        found.setdefault(key, Hole(centre, diameter))
    return sorted(found.values(), key=lambda h: (h.centre_mm, h.diameter_mm))
