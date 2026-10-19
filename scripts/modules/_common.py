#!/usr/bin/env python3
"""Shared helpers for the hardware domain packs.

Every public function here is idempotent: running a pack twice leaves the repo
exactly as it was after the first run. That is not politeness, it is what lets
you add robotics today and mechanical next month without diffing by hand.

Standard library only, matching scripts/check_docs.py.
"""
import datetime
import pathlib
import re
import sys

TODAY = datetime.date.today().isoformat()


def repo_root():
    """The repo root, verified by AGENTS.md being in it."""
    root = pathlib.Path.cwd()
    if not (root / "AGENTS.md").exists():
        sys.exit("Run this from the repo root (AGENTS.md not found).")
    return root


def read(path):
    """utf-8-sig and CRLF normalisation, matching scripts/check_docs.py.

    Windows editors write BOMs. A pack that reads one back and writes it into
    the middle of a file makes the doc checks fail somewhere else entirely.
    """
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write(path, text):
    """LF on every platform: text mode on Windows would write CRLF."""
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def require_hardware_core(root):
    """Domain packs extend HARDWARE.md; they never create it.

    In the CAD template HARDWARE.md ships with the hardware core and the
    mechanical sections already in it, so a missing file means it was deleted.
    """
    hw = root / "HARDWARE.md"
    if not hw.exists():
        sys.exit("HARDWARE.md not found. Restore it from the template before adding a pack.")
    return hw


def append_section(path, heading, body, changed, label=None):
    """Append '### heading' plus body, unless that heading is already there."""
    text = read(path)
    if re.search(rf"^### {re.escape(heading)}\s*$", text, re.M):
        return False
    write(path, text.rstrip("\n") + f"\n\n### {heading}\n{body.strip()}\n")
    changed.append(label or f"{path.name}: '{heading}' added")
    return True


def insert_before(path, marker, block, sentinel, changed, label):
    """Insert block immediately before the first occurrence of marker.

    `sentinel` is a string unique to the block; if it is already present the
    insert is skipped. Fails loudly rather than silently doing nothing when
    the marker has been edited away, because a pack that quietly no-ops is
    worse than one that stops.
    """
    text = read(path)
    if sentinel in text:
        return False
    if marker not in text:
        sys.exit(f"{path.name}: expected to find {marker!r}. Edit it in by hand.")
    write(path, text.replace(marker, block + marker, 1))
    changed.append(label)
    return True


def add_routing_row(root, row, sentinel, changed):
    """Add one row to the AGENTS.md routing table, above 'Anything else'."""
    return insert_before(
        root / "AGENTS.md",
        "| Anything else |",
        row,
        sentinel,
        changed,
        f"AGENTS.md: routing row for {sentinel!r} added",
    )


def add_glossary_rows(root, rows, changed, label):
    """Seed GLOSSARY.md, skipping terms already defined.

    Only pairs that cause real bugs belong here. A full domain dictionary is
    noise, and noise is what makes the file stop being read.
    """
    gl = root / "GLOSSARY.md"
    text = read(gl)
    text = text.replace(
        "| example | Delete this row when the first real term arrives. | | |\n", ""
    )
    added = 0
    for term, definition, confuse, ident in rows:
        if re.search(rf"^\|\s*{re.escape(term)}\s*\|", text, re.M):
            continue
        text = text.rstrip("\n") + f"\n| {term} | {definition} | {confuse} | {ident} |"
        added += 1
    write(gl, text)
    if added:
        changed.append(f"GLOSSARY.md: {added} {label} terms added")
    return added


def next_free_number(root, name, kind):
    """The next unused D or P number, as an int.

    Hard-coding D-01 in a loader collides with the D-01 that SETUP.md tells
    you to write on day one, and check_docs.py now rejects the duplicate.
    """
    p = root / name
    if not p.exists():
        return 1
    used = [int(m) for m in re.findall(rf"^##\s+{kind}-(\d+)\b", read(p), re.M)]
    return max(used, default=0) + 1


def append_log_entry(root, name, kind, body_fn, changed, sentinel):
    """Append one numbered entry to DECISIONS.md or POSTMORTEMS.md.

    body_fn takes the allocated reference (e.g. 'D-03') and returns the entry
    text. `sentinel` is a phrase from the entry used to detect a prior run.
    """
    p = root / name
    text = read(p)
    if sentinel in text:
        return None
    ref = f"{kind}-{next_free_number(root, name, kind):02d}"
    write(p, text.rstrip("\n") + "\n\n" + body_fn(ref).strip())
    changed.append(f"{name}: {ref} added")
    return ref


def report_hint(root, hint, changed):
    """Add a section hint to report_nodes.md, if the report module exists."""
    rn = root / "report" / "report_nodes.md"
    if not rn.exists():
        return False
    text = read(rn)
    first = hint.strip().split("\n")[0]
    if first in text:
        return False
    write(rn, text.rstrip("\n") + "\n" + hint.strip())
    changed.append("report_nodes.md: section hints added")
    return True


def report(changed, next_steps):
    for c in changed:
        print("ok    " + c)
    if not changed:
        print("skip  nothing to do; already installed")
    if next_steps:
        print("\nNext, in this order:")
        for i, step in enumerate(next_steps, 1):
            print(f"{i}. {step}")
