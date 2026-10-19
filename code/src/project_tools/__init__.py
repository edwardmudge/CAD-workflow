"""Shared helpers for the CAD scripts and tests. Paths are fixed here once."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PARAMS_FILE = ROOT / "params" / "params.yaml"
REQUIREMENTS_FILE = ROOT / "params" / "requirements.yaml"
OWNERSHIP_FILE = ROOT / "parts" / "ownership.yaml"
EXPORTS = ROOT / "exports"
MANIFEST_FILE = EXPORTS / "manifest.json"
SW_MANIFEST_FILE = ROOT / "cad" / "step" / "manifest.json"
EQUATIONS_FILE = ROOT / "cad" / "equations.txt"
