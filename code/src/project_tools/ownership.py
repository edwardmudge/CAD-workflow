"""Load and validate parts/ownership.yaml: one owner per part."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from project_tools import OWNERSHIP_FILE

OWNERS = {"build123d", "solidworks", "vendor"}
STEP_DIRS = {"build123d": "exports/", "solidworks": "cad/step/", "vendor": "cad/vendor/"}
STATUSES = {"active", "placeholder"}


class OwnershipError(ValueError):
    pass


def load_ownership(path: Path = OWNERSHIP_FILE) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    parts = data.get("parts") or []
    seen: set[str] = set()
    for part in parts:
        pid = part.get("id")
        if not pid or pid in seen:
            raise OwnershipError(f"{path.name}: missing or duplicate id {pid!r}")
        seen.add(pid)
        owner = part.get("owner")
        if owner not in OWNERS:
            raise OwnershipError(f"{path.name}: {pid}.owner must be one of {sorted(OWNERS)}")
        for key in ("source", "step"):
            if not part.get(key):
                raise OwnershipError(f"{path.name}: {pid} is missing {key}")
        if not part["step"].startswith(STEP_DIRS[owner]):
            raise OwnershipError(f"{path.name}: {pid}.step must be under {STEP_DIRS[owner]}")
        part.setdefault("depends_on", [])
        part.setdefault("status", "active")
        if part["status"] not in STATUSES:
            raise OwnershipError(f"{path.name}: {pid}.status must be one of {sorted(STATUSES)}")
    return parts


def by_id(path: Path = OWNERSHIP_FILE) -> dict[str, dict[str, Any]]:
    return {part["id"]: part for part in load_ownership(path)}


def dependents(part_id: str, path: Path = OWNERSHIP_FILE) -> list[str]:
    """Every part that depends on part_id, directly or through others."""
    parts = load_ownership(path)
    found: list[str] = []
    frontier = [part_id]
    while frontier:
        current = frontier.pop()
        for part in parts:
            if current in part["depends_on"] and part["id"] not in found:
                found.append(part["id"])
                frontier.append(part["id"])
    return found
