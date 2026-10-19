#!/usr/bin/env python3
"""List every parameter and requirement changed since a git ref, and fail if
any change is not named by a DECISIONS.md entry added since that ref.

    python code/scripts/params_audit.py              # since the latest tag (or the first commit)
    python code/scripts/params_audit.py --since REF

A parameter is named as `part.param` on an entry's "Parameters changed:"
line; a requirement by its id anywhere in the entry. Run at release time,
not on every commit: exploration does not need a decision per tweak, a
release does.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "code" / "src")]

from project_tools import PARAMS_FILE, REQUIREMENTS_FILE  # noqa: E402
from project_tools.params import RESERVED  # noqa: E402


def git(*args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def default_ref() -> str | None:
    tag = git("describe", "--tags", "--abbrev=0")
    if tag:
        return tag.strip()
    roots = git("rev-list", "--max-parents=0", "HEAD")
    return roots.split()[0] if roots else None


def flat_params(text: str | None) -> dict[str, object]:
    raw = yaml.safe_load(text or "") or {}
    flat = {}
    for part_id, section in raw.items():
        if part_id in RESERVED or not isinstance(section, dict):
            continue
        for name, entry in section.items():
            flat[f"{part_id}.{name}"] = entry.get("value") if isinstance(entry, dict) else entry
    return flat


def requirements(text: str | None) -> dict[str, dict]:
    return {req["id"]: req for req in (yaml.safe_load(text or "") or {}).get("requirements") or []}


def entries(text: str | None) -> dict[str, str]:
    """D-NN -> entry text."""
    parts = re.split(r"^(?=## D-\d+)", text or "", flags=re.M)
    return {m.group(1): part for part in parts if (m := re.match(r"## (D-\d+)", part))}


def changed(old: dict, new: dict) -> list[str]:
    return sorted(key for key in old.keys() | new.keys() if old.get(key) != new.get(key))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", help="git ref to compare against (default: latest tag, else first commit)")
    args = parser.parse_args()
    ref = args.since or default_ref()
    if not ref:
        print("skip  no commits yet; nothing to audit")
        return 0

    def at_ref(path: Path) -> str | None:
        return git("show", f"{ref}:{path.relative_to(ROOT).as_posix()}")

    params = changed(flat_params(at_ref(PARAMS_FILE)), flat_params(PARAMS_FILE.read_text(encoding="utf-8")))
    reqs = changed(requirements(at_ref(REQUIREMENTS_FILE)), requirements(REQUIREMENTS_FILE.read_text(encoding="utf-8")))
    decisions_file = ROOT / "DECISIONS.md"
    old_entries = entries(at_ref(decisions_file))
    new_entries = {k: v for k, v in entries(decisions_file.read_text(encoding="utf-8")).items() if k not in old_entries}
    named = " ".join(
        line for text in new_entries.values() for line in text.splitlines() if line.startswith("- Parameters changed:")
    )
    everything = "\n".join(new_entries.values())

    print(f"since {ref}: {len(params)} parameter(s), {len(reqs)} requirement(s) changed; "
          f"new decisions: {', '.join(new_entries) or 'none'}")
    missing = []
    for key in params:
        ok = re.search(rf"(?<![\w.]){re.escape(key)}(?![\w])", named)
        print(f"{'ok  ' if ok else 'MISS'}  {key}")
        missing += [] if ok else [key]
    for rid in reqs:
        ok = re.search(rf"\b{re.escape(rid)}\b", everything)
        print(f"{'ok  ' if ok else 'MISS'}  {rid}")
        missing += [] if ok else [rid]
    if missing:
        print(f"FAIL  {len(missing)} change(s) with no decision entry: record them in DECISIONS.md")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
