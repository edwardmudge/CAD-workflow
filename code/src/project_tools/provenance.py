"""Hashes, versions and git state recorded with every export, so a test can
tell whether an export still matches the files it was made from."""
from __future__ import annotations

import hashlib
import json
import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from project_tools import ROOT


def text_sha256(path: Path) -> str:
    """Line endings normalised, so a CRLF checkout hashes like an LF one."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_state() -> dict[str, Any]:
    def git(*args: str) -> str:
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else ""

    return {"commit": git("rev-parse", "HEAD") or "none", "dirty": bool(git("status", "--porcelain"))}


def kernel_versions() -> dict[str, str]:
    """build123d and the OCCT wrapper it runs on; either can change geometry."""
    ocp = "unknown"
    for dist in ("cadquery-ocp-novtk", "cadquery-ocp"):
        try:
            ocp = version(dist)
            break
        except PackageNotFoundError:
            continue
    return {"build123d": version("build123d"), "ocp": ocp}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
