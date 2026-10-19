"""Fixtures shared by every test. Geometry comes from exported STEP files,
never from build() directly, so a SolidWorks part and a build123d part are
checked the same way."""
from __future__ import annotations

from collections.abc import Callable
from functools import cache
from typing import Any

import pytest
from build123d import Shape

from parts import registry
from project_tools import ROOT
from project_tools.geometry import load_step
from project_tools.ownership import by_id
from project_tools.params import design_rules, load_part_params, requirement as find_requirement


@cache
def _modules() -> dict:
    return registry()


@cache
def _shape(part_id: str) -> Shape:
    part = by_id()[part_id]
    path = ROOT / part["step"]
    if not path.exists():
        if part["owner"] == "build123d":
            hint = f"run: python code/scripts/export.py --part {part_id}"
        else:
            hint = "export it from SolidWorks as STEP AP214, then run code/scripts/register_sw_step.py"
        pytest.fail(f"{part['step']} is missing; {hint}", pytrace=False)
    return load_step(path)


@pytest.fixture(scope="session")
def ownership() -> dict[str, dict[str, Any]]:
    return by_id()


@pytest.fixture(scope="session")
def part_params() -> Callable[[str], dict[str, Any]]:
    def load(part_id: str) -> dict[str, Any]:
        return load_part_params(part_id, required=_modules()[part_id].PARAMS)

    return load


@pytest.fixture(scope="session")
def exported_step() -> Callable[[str], Shape]:
    return _shape


@pytest.fixture(scope="session")
def requirement() -> Callable[[str], dict[str, Any]]:
    return find_requirement


@pytest.fixture(scope="session")
def rules() -> dict[str, float]:
    return design_rules()
