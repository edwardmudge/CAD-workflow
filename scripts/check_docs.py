#!/usr/bin/env python3
"""Doc checks: pointer sync, frontmatter, human-section cap, log numbering,
plan verify gates, cross-references, report_nodes lint, staleness warnings.
Exit 1 on errors; warnings never fail the build."""
import re
import sys
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Add ".cursorrules", "GEMINI.md", etc. here as you adopt vendors.
POINTER_FILES = ["CLAUDE.md"]
POINTER_TEXT = (
    "# Pointer only. Do not add rules here.\n"
    "All agent instructions for this repository live in AGENTS.md at the repo root.\n"
    "Read AGENTS.md and follow it as if it were this file.\n"
)

# Capped + "## Agent Notes" delimiter required. Absent files are skipped, so
# module documents (HARDWARE.md, VAULT.md) may be listed before they exist.
TWO_PART = [
    "AGENTS.md",
    "GLOSSARY.md",
    "README.md",
    "PLAN.md",
    "SETUP.md",
    "REFERENCES.md",
    "HARDWARE.md",
    "VAULT.md",
]
HUMAN_CAP = 25       # non-blank lines before the first "## " heading
STALE_DAYS = 90

SKIP_PREFIXES = ("notes/", "lessons/", ".github/", "scripts/")
SKIP_FILES = set(POINTER_FILES) | {"report/report_nodes.md"}
FRONTMATTER_EXEMPT = {"README.md"}

errors, warnings = [], []


def read(path):
    """Text with line endings normalised and any BOM stripped.

    Git on Windows may hand back CRLF, and several Windows editors write a
    UTF-8 BOM. Either one would otherwise fail the pointer comparison or the
    frontmatter regex with a message that explains nothing.
    """
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def strip_fences(text):
    """Blank out fenced code blocks, keeping line numbers intact.

    Examples inside fences are documentation, not entries: a template showing
    "Record: D-03" must not register as a reference to a decision D-03.
    """
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def md_files():
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES or rel.startswith(SKIP_PREFIXES):
            continue
        yield rel, read(p)


def norm(ref):
    """D-07 and D-7 are the same entry. Compare on the integer."""
    kind, num = ref.split("-")
    return f"{kind}-{int(num)}"


# 1. Pointer files match canonical text exactly.
for name in POINTER_FILES:
    p = ROOT / name
    if p.exists() and read(p) != POINTER_TEXT:
        errors.append(f"{name}: drifted from canonical pointer text")

# 2. Frontmatter present with status + verified; staleness warning.
today = datetime.date.today()
for rel, text in md_files():
    if rel in FRONTMATTER_EXEMPT:
        continue
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{rel}: missing frontmatter")
        continue
    fm = m.group(1)
    if not re.search(r"^status:\s*(active|superseded)\s*$", fm, re.M):
        errors.append(f"{rel}: frontmatter needs status: active|superseded")
    vm = re.search(r"^verified:\s*(\d{4}-\d{2}-\d{2})\s*$", fm, re.M)
    if not vm:
        errors.append(f"{rel}: frontmatter needs verified: YYYY-MM-DD")
    elif "status: active" in fm:
        age = (today - datetime.date.fromisoformat(vm.group(1))).days
        if age > STALE_DAYS:
            warnings.append(f"{rel}: not verified for {age} days")

# 3. Two-part files: human section cap and Agent Notes delimiter.
for name in TWO_PART:
    p = ROOT / name
    if not p.exists():
        continue
    text = read(p)
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    if "\n## Agent Notes" not in "\n" + body:
        errors.append(f"{name}: missing '## Agent Notes' section")
    human = []
    for line in body.splitlines():
        if line.startswith("## "):
            break
        if line.strip():
            human.append(line)
    if len(human) > HUMAN_CAP:
        errors.append(
            f"{name}: human section is {len(human)} non-blank lines "
            f"(cap {HUMAN_CAP}); move detail to Agent Notes"
        )

# 4. Logs: entry numbers are unique. A duplicate D-01 silently overwrites
#    history and breaks every reference to it.
defined = set()
for name, kind in (("DECISIONS.md", "D"), ("POSTMORTEMS.md", "P")):
    p = ROOT / name
    if not p.exists():
        continue
    seen = set()
    for i, line in enumerate(strip_fences(read(p)).splitlines(), 1):
        m = re.match(rf"^##\s+({kind}-\d+)\b", line)
        if not m:
            continue
        ref = norm(m.group(1))
        if ref in seen:
            errors.append(f"{name}:{i}: duplicate entry {m.group(1)}")
        seen.add(ref)
        defined.add(ref)

# 5. PLAN.md: work items carry a state, and a ticked item carries evidence.
plan = ROOT / "PLAN.md"
if plan.exists():
    lines = strip_fences(read(plan)).splitlines()
    items = []  # (line_no, title, state, start_index)
    for i, line in enumerate(lines):
        m = re.match(r"^#{2,6}\s+(S\d+(?:\.\d+)*)\s+(.*)$", line)
        if not m:
            continue
        state = re.search(r"\[([ ~x])\]\s*$", m.group(2))
        if not state:
            errors.append(
                f"PLAN.md:{i + 1}: item {m.group(1)} has no state marker; "
                f"end the heading with [ ], [~] or [x]"
            )
            continue
        items.append((i + 1, m.group(1), state.group(1), i))

    for n, (line_no, title, state, start) in enumerate(items):
        if state != "x":
            continue
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("#"):
                end = j
                break
        block = "\n".join(lines[start:end])
        if "**Verify:**" not in block:
            errors.append(f"PLAN.md:{line_no}: {title} is [x] with no '**Verify:**' clause")
            continue
        after = block.split("**Verify:**", 1)[1]
        if not re.search(r"\b(Measured|Result):", after):
            errors.append(
                f"PLAN.md:{line_no}: {title} is [x] but its Verify clause has no "
                f"'Measured:' or 'Result:' line"
            )
        if not re.search(r"\d{4}-\d{2}-\d{2}", after):
            errors.append(
                f"PLAN.md:{line_no}: {title} is [x] but its Verify clause has no date"
            )

# 6. Cross-references resolve. A bullet citing D-99 points at nothing.
for rel in ("PLAN.md", "HARDWARE.md", "report/report_nodes.md"):
    p = ROOT / rel
    if not p.exists():
        continue
    for i, line in enumerate(strip_fences(read(p)).splitlines(), 1):
        for ref in re.findall(r"\b([DP]-\d+)\b", line):
            if norm(ref) not in defined:
                errors.append(f"{rel}:{i}: references {ref}, which is not in the logs")

# 7. report_nodes.md: bullets only. Inert when the report module is absent.
rn = ROOT / "report" / "report_nodes.md"
if (ROOT / "report").is_dir() and rn.exists():
    for i, line in enumerate(read(rn).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not re.match(r"^- \[[DP]-\d+\]", line):
            errors.append(f"report/report_nodes.md:{i}: not a '- [D-NN]' bullet")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
