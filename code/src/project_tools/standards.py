"""Values taken from standards, kept in one place with their source.

ISO 273 clearance holes for metric fasteners, medium series, diameters in mm.
Check against your copy of the standard before relying on a size not used
here before.
"""

ISO_273_MEDIUM_MM: dict[str, float] = {
    "M2": 2.4,
    "M2.5": 2.9,
    "M3": 3.4,
    "M4": 4.5,
    "M5": 5.5,
    "M6": 6.6,
    "M8": 9.0,
    "M10": 11.0,
    "M12": 13.5,
    "M16": 17.5,
    "M20": 22.0,
}


def iso_273_medium_size(diameter_mm: float, tol: float = 0.01) -> str | None:
    """The thread size whose medium clearance hole matches, or None."""
    for size, hole in ISO_273_MEDIUM_MM.items():
        if abs(hole - diameter_mm) <= tol:
            return size
    return None
