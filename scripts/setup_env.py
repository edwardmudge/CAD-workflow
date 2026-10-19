#!/usr/bin/env python3
"""Set up this copy of the repo in one command. From the repo root:

    python scripts/setup_env.py            # create or repair the env, wire hooks
    python scripts/setup_env.py --check    # then run code/check.py as well
    python scripts/setup_env.py --update   # re-sync the env with environment.yml

What it does:
1. creates the conda env named in environment.yml if it is missing, or updates
   it when the project packages fail to import (or --update is given)
2. runs code/check.py --install-hooks from that env, so the pre-commit hook
   uses the right interpreter
3. points VS Code at the env (.vscode/settings.json, gitignored, per machine)
4. runs code/check.py when the env was just created, or with --check

Idempotent and quick when everything is already in place, so the VS Code
folder-open task in .vscode/tasks.json can run it on every open. Standard
library only: any python on PATH can run it.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "environment.yml"
VSCODE_SETTINGS = ROOT / ".vscode" / "settings.json"
PACKAGES = ("build123d", "yaml", "pytest")
# find_spec, not import: importing build123d takes seconds, and this runs on
# every folder open. A broken install still fails code/check.py.
FIND = "import importlib.util as u, sys; sys.exit(any(u.find_spec(m) is None for m in {!r}))"


def env_name(text: str) -> str:
    """The env's `name:` from environment.yml text."""
    m = re.search(r"^name:\s*([^\s#]+)", text, re.M)
    if not m:
        sys.exit("ERROR environment.yml has no 'name:' line")
    return m.group(1)


def find_conda() -> str:
    """conda is often not on PATH on Windows, so look in the usual places."""
    home = pathlib.Path.home()
    exe = "Scripts/conda.exe" if os.name == "nt" else "bin/conda"
    candidates = [os.environ.get("CONDA_EXE")]
    candidates += [str(home / base / exe) for base in ("miniconda3", "anaconda3", "miniforge3")]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).is_file():
            return candidate
    on_path = shutil.which("conda")
    if on_path:
        return on_path
    sys.exit("ERROR conda not found. Install Miniconda, or set CONDA_EXE to conda's full path.")


def env_python(conda: str, name: str) -> pathlib.Path | None:
    out = subprocess.run([conda, "env", "list", "--json"], capture_output=True, text=True, check=True)
    for prefix in json.loads(out.stdout)["envs"]:
        prefix = pathlib.Path(prefix)
        if prefix.name == name:
            return prefix / ("python.exe" if os.name == "nt" else "bin/python")
    return None


def packages_ok(python: pathlib.Path) -> bool:
    return subprocess.run([str(python), "-c", FIND.format(PACKAGES)], capture_output=True).returncode == 0


def conda_env(conda: str, action: str) -> None:
    print(f"\n== conda env {action} -f environment.yml (a few minutes the first time)", flush=True)
    args = [conda, "env", action, "-f", str(ENV_FILE)] + (["--prune"] if action == "update" else [])
    if subprocess.run(args, cwd=ROOT).returncode != 0:
        sys.exit(f"ERROR conda env {action} failed; see the output above")


def in_git_repo() -> bool:
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True)
    return result.returncode == 0


def install_hooks(python: pathlib.Path) -> bool:
    """Same keys as code/check.py --install-hooks, set directly so this script
    does not pay for that script's build123d import."""
    for key, value in (("core.hooksPath", ".githooks"), ("hooks.python", python.as_posix())):
        if subprocess.run(["git", "config", key, value], cwd=ROOT).returncode != 0:
            print(f"ERROR could not set git config {key}")
            return False
        print(f"ok    git config {key} {value}")
    return True


def set_vscode_interpreter(python: pathlib.Path) -> None:
    key, value = "python.defaultInterpreterPath", python.as_posix()
    settings = {}
    if VSCODE_SETTINGS.exists():
        try:
            settings = json.loads(VSCODE_SETTINGS.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            print(f"WARN  {VSCODE_SETTINGS.relative_to(ROOT)} is not plain JSON; set {key} to {value} by hand")
            return
    if settings.get(key) != value:
        settings[key] = value
        VSCODE_SETTINGS.parent.mkdir(exist_ok=True)
        VSCODE_SETTINGS.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print(f"ok    VS Code interpreter {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="run code/check.py afterwards")
    parser.add_argument("--update", action="store_true", help="re-sync the env with environment.yml")
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # keep order with conda's output

    name = env_name(ENV_FILE.read_text(encoding="utf-8"))
    conda = find_conda()
    python = env_python(conda, name)
    created = python is None
    if created:
        conda_env(conda, "create")
        python = env_python(conda, name)
        if python is None:
            sys.exit(f"ERROR env {name} still not found after creating it")
    elif args.update or not packages_ok(python):
        conda_env(conda, "update")
    if not packages_ok(python):
        sys.exit(f"ERROR {python} is missing one of {', '.join(PACKAGES)} even after setup")
    print(f"ok    conda env {name} ({python})")

    if in_git_repo():
        if not install_hooks(python):
            return 1
    else:
        print("WARN  not a git repository yet: run git init, then this script again to enable the hooks")
    if subprocess.run(["git", "lfs", "version"], capture_output=True).returncode != 0:
        print("WARN  git-lfs not found: install it before committing SolidWorks files")
    set_vscode_interpreter(python)

    if created or args.check:
        return subprocess.run([str(python), "code/check.py"], cwd=ROOT).returncode
    print("ok    setup complete; run with --check to run code/check.py too")
    return 0


if __name__ == "__main__":
    sys.exit(main())
