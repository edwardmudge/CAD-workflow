"""Registry of build123d parts, derived from parts/ownership.yaml.

There is deliberately no second hand-kept list: every build123d entry in
ownership.yaml is loaded from its `source`, which must define

    PARAMS: tuple[str, ...]          # names required from params.yaml
    def build(params: dict) -> Part

code/tests/test_repository.py checks both directions: every build123d entry
loads, and every module in parts/ is listed in ownership.yaml.
"""
from __future__ import annotations

import importlib.util
from collections.abc import Callable
from types import ModuleType
from typing import Any

from project_tools import ROOT
from project_tools.ownership import load_ownership
from project_tools.params import load_part_params


def load_module(part_id: str, source: str) -> ModuleType:
    path = ROOT / source
    if not path.exists():
        raise FileNotFoundError(f"{part_id}: source {source} not found")
    spec = importlib.util.spec_from_file_location(f"parts.{part_id}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("build", "PARAMS"):
        if not hasattr(module, name):
            raise AttributeError(f"{part_id}: {source} does not define {name}")
    return module


def registry() -> dict[str, ModuleType]:
    return {
        part["id"]: load_module(part["id"], part["source"])
        for part in load_ownership()
        if part["owner"] == "build123d"
    }


def build_part(part_id: str) -> Any:
    module = registry()[part_id]
    build: Callable[[dict], Any] = module.build
    return build(load_part_params(part_id, required=module.PARAMS))
