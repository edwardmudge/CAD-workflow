"""Repository consistency: ownership, registry, params, requirements and
export freshness agree with each other. Works with zero parts, so a clean
copy of the template passes."""
from __future__ import annotations

import re

import pytest

from parts import load_module
from project_tools import MANIFEST_FILE, ROOT, SW_MANIFEST_FILE
from project_tools.ownership import load_ownership
from project_tools.params import load_part_params, load_raw, load_requirements, params_hash, part_ids
from project_tools.provenance import file_sha256, kernel_versions, read_json, text_sha256

PARTS = load_ownership()
IDS = [part["id"] for part in PARTS]
BUILD123D = [part for part in PARTS if part["owner"] == "build123d"]
ACTIVE = [part for part in PARTS if part["status"] == "active"]
SOLIDWORKS = [part for part in ACTIVE if part["owner"] == "solidworks"]


def ids(parts):
    return [part["id"] for part in parts]


@pytest.mark.parametrize("part", ACTIVE, ids=ids(ACTIVE))
def test_source_exists(part):
    assert (ROOT / part["source"]).exists(), f"{part['id']}: source {part['source']} not found"


@pytest.mark.parametrize("part", ACTIVE, ids=ids(ACTIVE))
def test_step_exists(part):
    hint = "run code/scripts/export.py" if part["owner"] == "build123d" else "export it from SolidWorks"
    assert (ROOT / part["step"]).exists(), f"{part['id']}: {part['step']} not found; {hint}"


def test_placeholders_are_listed():
    placeholders = [part["id"] for part in PARTS if part["status"] == "placeholder"]
    if placeholders:
        pytest.skip(f"placeholders, not yet modelled: {', '.join(placeholders)}")


def test_depends_on_ids_exist():
    for part in PARTS:
        for dep in part["depends_on"]:
            assert dep in IDS, f"{part['id']} depends on unknown part {dep!r}"
            assert dep != part["id"], f"{part['id']} depends on itself"


@pytest.mark.parametrize("part", BUILD123D, ids=ids(BUILD123D))
def test_build123d_part_loads_with_its_params(part):
    module = load_module(part["id"], part["source"])
    load_part_params(part["id"], required=module.PARAMS)


def test_every_part_module_is_owned():
    owned = {part["source"] for part in BUILD123D}
    modules = {p.relative_to(ROOT).as_posix() for p in (ROOT / "parts").glob("*.py")}
    orphans = modules - owned - {"parts/__init__.py"}
    assert not orphans, f"modules in parts/ not in ownership.yaml: {sorted(orphans)}"


def test_every_params_section_has_an_owner():
    orphans = set(part_ids(load_raw())) - set(IDS)
    assert not orphans, f"params.yaml sections with no ownership.yaml entry: {sorted(orphans)}"


def test_requirements_trace_to_parts_and_tests():
    for req in load_requirements():
        assert req["part"] in IDS, f"{req['id']}: unknown part {req['part']!r}"
        path, _, name = req["test"].partition("::")
        test_file = ROOT / path
        assert test_file.exists(), f"{req['id']}: test file {path} not found"
        assert re.search(rf"^def {re.escape(name)}\(", test_file.read_text(encoding="utf-8"), re.M), (
            f"{req['id']}: {req['test']} not found"
        )


def test_materials_documented_in_hardware():
    hardware = (ROOT / "HARDWARE.md").read_text(encoding="utf-8")
    for material in load_raw().get("materials") or {}:
        assert re.search(rf"^\|\s*{re.escape(material)}\s*\|", hardware, re.M), (
            f"material {material} has no row in the HARDWARE.md materials table"
        )


@pytest.mark.parametrize("part", BUILD123D, ids=ids(BUILD123D))
def test_build123d_export_is_current(part):
    entry = read_json(MANIFEST_FILE).get(part["id"])
    rerun = f"run: python code/scripts/export.py --part {part['id']}"
    assert entry, f"{part['id']}: not in exports/manifest.json; {rerun}"
    assert entry["source_sha256"] == text_sha256(ROOT / part["source"]), f"{part['id']}: source changed since export; {rerun}"
    assert entry["params_sha256"] == params_hash(part["id"]), f"{part['id']}: params changed since export; {rerun}"
    assert entry["versions"] == kernel_versions(), f"{part['id']}: build123d/OCP version changed since export; {rerun}"


@pytest.mark.parametrize("part", SOLIDWORKS, ids=ids(SOLIDWORKS))
def test_solidworks_step_is_current(part):
    entry = read_json(SW_MANIFEST_FILE).get(part["id"])
    rerun = f"re-export STEP AP214 from SolidWorks, then run code/scripts/register_sw_step.py {part['id']}"
    assert entry, f"{part['id']}: not registered in cad/step/manifest.json; {rerun}"
    assert entry["source_sha256"] == file_sha256(ROOT / part["source"]), f"{part['id']}: SLDPRT changed since its STEP was exported; {rerun}"
    assert entry["step_sha256"] == file_sha256(ROOT / part["step"]), f"{part['id']}: STEP changed since it was registered; {rerun}"
