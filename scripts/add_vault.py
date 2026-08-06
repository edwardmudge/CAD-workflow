#!/usr/bin/env python3
"""Vault module for the project template. Run once from the repo root:

    python scripts/add_vault.py

Creates VAULT.md, the contract between this repository and an Obsidian vault
holding the project's reading. Adds a routing row, three glossary terms, a
truth-ladder amendment and the vault module section to AGENTS.md.

The boundary is one-directional and manual: source notes and annotations live
in the vault, the written literature review is report prose, and nothing is
copied by machine. There is deliberately no sync script — an exporter would
need the vault path committed in the repo and can silently pollute a vault
that a git plugin is already auto-pulling and merging.

Do NOT run this in the template repository itself. Leaving VAULT.md absent
there keeps the module inert, so the design document in the vault stays
maintainable from that repo without the read-only rule needing a carve-out.
Install this on project clones only. Idempotent.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "modules"))
from _common import (  # noqa: E402
    TODAY,
    add_glossary_rows,
    add_routing_row,
    append_section,
    read,
    repo_root,
    report,
    report_hint,
    write,
)

ROOT = repo_root()
AGENTS = ROOT / "AGENTS.md"
changed = []

OLD_RUNG_5 = "5. notes/ (working notes, low authority, may be stale)."
NEW_RUNG_5 = (
    "5. notes/ and the Obsidian vault (working notes and reference, low\n"
    "   authority, may be stale)."
)


def rung_5_needs_amending():
    """Pre-flight: can rung 5 be widened to name the vault?

    Checked before anything is written. A run that creates VAULT.md and then
    dies leaves the worst state available: the artefact exists, so the module
    reads as installed and its section is expected, while AGENTS.md carries
    none of its rules. Verify first, write second.
    """
    text = read(AGENTS)
    if "and the Obsidian vault" in text:
        return False
    if OLD_RUNG_5 not in text:
        sys.exit(
            "AGENTS.md: truth ladder rung 5 is not the expected text. Add the "
            "vault to it by hand, then re-run. Nothing has been written."
        )
    return True


needs_rung_5 = rung_5_needs_amending()

VAULT = f"""---
status: active
verified: {TODAY}
---
# Vault reference

Where this project's reading lives. The vault holds the source notes and the
annotations, this repository holds the project, and the report holds the
argument. Each boundary is crossed once, by hand, at a named moment.

Vault path: TBC (absolute path, in backticks, never a markdown link)
Project folder in the vault: TBC (e.g. `04. Dissertations/01. Something`)

Three things to remember:
- The agent reads the vault and never writes to it. Every vault edit is
  yours, made in Obsidian.
- A vault note is rung 5. It is reference, never fact. A number does not
  become true by being quoted out of one.
- The written literature review is report prose, so the agent never drafts
  it. The reading is yours and the writing is yours; the gap between them
  is not the agent's to fill.

The citekey is the one string tying it together: the same text in the vault
source note, in report/refs.bib, and in the Typst citation call.

## Agent Notes

### Paths
Fill both before using this module. Write them as plain text in backticks,
never as a markdown link: the CI links job runs lychee over every .md file,
and a link pointing outside the repository fails the build.

| Field | Value |
|---|---|
| Vault root | TBC |
| This project's folder in the vault | TBC |

### What crosses, and how
Manual in both senses: a human moves it, and a human decides it is worth
moving. Nothing here is automated, and nothing flows back into the vault.

| What | Direction | Means | Who |
|---|---|---|---|
| Source notes, annotations | vault to thinking | read in place | human |
| Bibliographic fields | vault to report/refs.bib | manual, keyed by citekey | human; agent may transcribe |
| Literature review prose | none | written straight into report.typ | human only |
| Project front door | vault to repo | a link, not content | human |

### Source notes
One vault note per external work, filed in this project's vault folder, each
carrying a citekey in its frontmatter. The note records what the work claims
and what it is worth; the report records what you concluded from it. Keep
those two jobs apart and neither one degrades into the other.

Citekey convention: TBC (`authorYEARword`, e.g. `craig2005introduction`, is
the usual default). Whatever is chosen, the same string appears in the vault
note, in report/refs.bib and in the report, or the trail breaks silently.

### Provenance
A source note is not evidence about the physical item. It is evidence about
what somebody published. When the two disagree, rung 1 wins and the
disagreement is worth recording rather than quietly resolving toward print.
"""

vault = ROOT / "VAULT.md"
if vault.exists():
    print("skip  VAULT.md already exists")
else:
    write(vault, VAULT)
    changed.append("VAULT.md created")


if needs_rung_5:
    # The ladder is core text, not a module section, so it is edited in place
    # rather than appended to. Pre-flighted above.
    write(AGENTS, read(AGENTS).replace(OLD_RUNG_5, NEW_RUNG_5, 1))
    changed.append("AGENTS.md: truth ladder rung 5 now names the vault")

add_routing_row(
    ROOT,
    "| Literature or background | VAULT.md | REFERENCES.md, "
    "report/report_nodes.md | vault notes as measured fact, any undated "
    "vault claim | none |\n",
    "| Literature or background |",
    changed,
)

add_glossary_rows(
    ROOT,
    [
        (
            "vault note",
            "A note in the Obsidian vault; reference material at rung 5.",
            "a notes/ entry, which is also rung 5 but project-scoped and in-repo",
            "",
        ),
        (
            "source note",
            "A vault note recording one external work, carrying a citekey.",
            "the literature review, which is written prose living in report/",
            "citekey",
        ),
        (
            "citekey",
            "The BibTeX key shared by a vault source note and its refs.bib entry.",
            "D-NN, which identifies a decision",
            "citekey",
        ),
    ],
    changed,
    "vault",
)

append_section(
    ROOT / "AGENTS.md",
    "Vault module (ignore unless VAULT.md exists)",
    """The Obsidian vault named in VAULT.md holds this project's reading. You
read it. You never write to it.

Never create, edit, move, or delete any file under the vault path, in any
channel: not with file tools, not through a shell redirect, not as a
one-off, and not when asked directly. Why: the vault is a live workspace
with its own git plugin auto-pulling and merging, so a write from here races
an editor you cannot see, and it is the human's own knowledge base rather
than a project artefact. As with the report, an absent tool-level block is
not permission.

Vault notes are rung 5. They are reference, never fact. Attribute them
("the vault source note on X says"), never assert them. A number found in a
vault note does not enter HARDWARE.md, a Verify clause, or a report node
until a manual or a measurement puts it there.

The literature review is report prose, and the report module's firewall
covers it in full. Never draft, paraphrase, synthesise, or summarise source
material into a paragraph for the Background section or any other part of
the report, in files or in chat. Reading in the vault and writing in the
report are both the human's work; the boundary between them is not a gap
for you to fill. If asked, refuse and cite this section.

Your permitted mechanical actions are exactly two:
1. Transcribing a source note's bibliographic frontmatter into a
   report/refs.bib entry. That is metadata, not prose.
2. Checking that citekeys cited in report/report_nodes.md resolve to an
   entry in report/refs.bib, and reporting the ones that do not.

Literature report nodes use the existing bullet form, with the citekey named
in the evidence field, one line each:
- [D-07] 2026-08-05 | claim the source supports | alt: sources that disagree | evidence: refs.bib craig2005, vault source note | section: Background""",
    changed,
)

report_hint(
    ROOT,
    "# Literature usually needs nodes where a source decided something: a\n"
    "# method taken from a paper, a value adopted from print rather than\n"
    "# measured, and any place two sources disagree. Name the citekey.\n",
    changed,
)

report(
    changed,
    [
        "Fill the two paths and the citekey convention in VAULT.md.",
        "Create the project's folder in the vault, with a MOC listing its sources.",
        "Create report/refs.bib on the day you first cite, and uncomment the "
        "bibliography line in report/report.typ.",
        "Run python scripts/check_docs.py, then commit.",
    ],
)
