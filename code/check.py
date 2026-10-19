#!/usr/bin/env python3
"""The one command that verifies everything, in order:

1. doc checks (scripts/check_docs.py)
2. regenerate cad/equations.txt; fail if it was out of date (stage it, rerun)
3. export every build123d part (skipped with --fast)
4. pytest

    python code/check.py                  # everything; the pre-commit hook runs this
    python code/check.py --fast           # skip export; staleness tests still catch old exports
    python code/check.py --install-hooks  # once per clone, from the activated env

Exit 0 only if every step passed. CI will call this unchanged.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def environment_ok() -> bool:
    try:
        import build123d  # noqa: F401
        import yaml  # noqa: F401
        import pytest  # noqa: F401
    except ImportError as exc:
        print(f"ERROR {PY} cannot import {exc.name}: this is not the project environment.")
        print("      run python scripts/setup_env.py, or point the hook at the env once:")
        print("      git config hooks.python <path to the env's python.exe>")
        return False
    return True


def install_hooks() -> int:
    """Point git at .githooks and at this interpreter, so the hook runs in
    the project env even when git is started from outside it (VS Code)."""
    python = Path(PY).as_posix()
    for key, value in (("core.hooksPath", ".githooks"), ("hooks.python", python)):
        if subprocess.run(["git", "config", key, value], cwd=ROOT).returncode != 0:
            print(f"ERROR could not set git config {key}")
            return 1
        print(f"ok    git config {key} {value}")
    return 0


def step(title: str, *args: str) -> bool:
    print(f"\n== {title}", flush=True)
    return subprocess.run([PY, *args], cwd=ROOT).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fast", action="store_true", help="skip export; only run the tests")
    parser.add_argument("--install-hooks", action="store_true", help="enable .githooks with this interpreter")
    args = parser.parse_args()
    if not environment_ok():
        return 1
    if args.install_hooks:
        return install_hooks()

    results = {
        "docs": step("doc checks", "scripts/check_docs.py"),
        "equations": step("SolidWorks equations", "code/scripts/gen_sw_equations.py", "--check"),
    }
    if not args.fast:
        results["export"] = step("export", "code/scripts/export.py")
    results["tests"] = step("tests", "-m", "pytest", "-q")

    print("\n== summary")
    for name, ok in results.items():
        print(f"{'ok  ' if ok else 'FAIL'}  {name}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
