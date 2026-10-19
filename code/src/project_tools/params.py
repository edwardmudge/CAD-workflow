"""Load and validate params/params.yaml and params/requirements.yaml.

Parts get plain values (descriptions stripped). Every problem raises
ParamsError naming the file, section and key, because a vague YAML error is
the slowest kind to fix.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from project_tools import PARAMS_FILE, REQUIREMENTS_FILE

RESERVED = {"units", "materials", "design_rules"}
UNITS = {"mm", "deg", "count"}


class ParamsError(ValueError):
    pass


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ParamsError(f"{path.name}: top level must be a mapping")
    return data


def _check_entry(where: str, name: str, entry: Any) -> None:
    if not isinstance(entry, dict) or "value" not in entry:
        raise ParamsError(f"{where}.{name}: expected {{value: ..., description: ...}}")
    value = entry["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ParamsError(f"{where}.{name}: value must be a number, got {value!r}")
    if not str(entry.get("description", "")).strip():
        raise ParamsError(f"{where}.{name}: description is missing")
    if entry.get("unit", "mm") not in UNITS:
        raise ParamsError(f"{where}.{name}: unit must be one of {sorted(UNITS)}")


def load_raw(path: Path = PARAMS_FILE) -> dict[str, Any]:
    """The whole file, validated, with descriptions kept."""
    raw = _read_yaml(path)
    if raw.get("units") != "mm":
        raise ParamsError(f"{path.name}: units must be 'mm' (SolidWorks MMGS)")
    materials = raw.get("materials") or {}
    for name, density in materials.items():
        if isinstance(density, bool) or not isinstance(density, (int, float)) or density <= 0:
            raise ParamsError(f"{path.name}: materials.{name} must be a positive density in g/cm3")
    for name, entry in (raw.get("design_rules") or {}).items():
        _check_entry("design_rules", name, entry)
    for part_id in part_ids(raw):
        section = raw[part_id]
        if not isinstance(section, dict):
            raise ParamsError(f"{path.name}: {part_id} must be a mapping")
        material = section.get("material")
        if material not in materials:
            raise ParamsError(
                f"{path.name}: {part_id}.material {material!r} is not in materials "
                f"({', '.join(materials) or 'none defined'})"
            )
        for name, entry in section.items():
            if name != "material":
                _check_entry(part_id, name, entry)
    return raw


def part_ids(raw: dict[str, Any]) -> list[str]:
    return [key for key in raw if key not in RESERVED]


def load_part_params(
    part_id: str, required: Iterable[str] = (), path: Path = PARAMS_FILE
) -> dict[str, Any]:
    """Plain values for one part, plus its material name."""
    raw = load_raw(path)
    if part_id not in raw or part_id in RESERVED:
        raise ParamsError(f"{path.name}: no section for part {part_id!r}")
    section = raw[part_id]
    values: dict[str, Any] = {
        name: entry["value"] for name, entry in section.items() if name != "material"
    }
    values["material"] = section["material"]
    missing = [name for name in required if name not in values]
    if missing:
        raise ParamsError(f"{path.name}: {part_id} is missing {', '.join(missing)}")
    return values


def design_rules(path: Path = PARAMS_FILE) -> dict[str, float]:
    return {name: entry["value"] for name, entry in (load_raw(path).get("design_rules") or {}).items()}


def density_g_cm3(material: str, path: Path = PARAMS_FILE) -> float:
    materials = load_raw(path).get("materials") or {}
    if material not in materials:
        raise ParamsError(f"{path.name}: unknown material {material!r}")
    return float(materials[material])


def params_hash(part_id: str, path: Path = PARAMS_FILE) -> str:
    """Hash of everything in params.yaml that can change this part's export:
    its own section and the density of its material."""
    raw = load_raw(path)
    section = raw[part_id]
    payload = {"section": section, "density": raw["materials"][section["material"]]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def load_requirements(path: Path = REQUIREMENTS_FILE) -> list[dict[str, Any]]:
    reqs = _read_yaml(path).get("requirements") or []
    seen: set[str] = set()
    for req in reqs:
        rid = req.get("id", "?")
        for key in ("id", "part", "text", "source", "test"):
            if not str(req.get(key, "")).strip():
                raise ParamsError(f"{path.name}: {rid} is missing {key}")
        if rid in seen:
            raise ParamsError(f"{path.name}: duplicate id {rid}")
        seen.add(rid)
    return reqs


def requirement(rid: str, path: Path = REQUIREMENTS_FILE) -> dict[str, Any]:
    for req in load_requirements(path):
        if req["id"] == rid:
            return req
    raise ParamsError(f"{path.name}: no requirement {rid}")
