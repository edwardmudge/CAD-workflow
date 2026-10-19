---
status: active
verified: 2026-10-13
---
# AGENTS.md

Canonical rules for any AI agent working in this repository. Vendor files
(CLAUDE.md and friends) are pointers to this file and contain no rules.

Things I must remember:
- Capture as I work with one-liners: "decision: ...", "postmortem: ...",
  "term: ...", "shortcut: ...", "question: ...". The agent files them; I
  check the echo.
- Nothing is done until its Verify clause in PLAN.md has a measured result
  and a date. A tick without a number is a guess.
- Nothing is official until I commit it. Review every diff before staging.
- When sources disagree, the truth ladder below decides. Reality beats paper.
- The agent never invents a fact or a number. Where a source is silent, it
  says so and leaves the gap.
- If report/ exists: the agent never writes report prose. Its only report
  output is bullet entries in report/report_nodes.md. If it offers wording,
  refuse it.
- CAD: one owner per part; STEP and cad/equations.txt are outputs, never
  inputs. Requirements (params/requirements.yaml) are mine: the agent never
  moves a limit to make a test pass. One-liners: "change: ...", "eco: ...",
  "release check".

## Agent Notes

### Role and scope
You assist with engineering work in this repository: analysis, code where the
code module exists, hardware documentation where the hardware module exists,
documentation upkeep, and decision capture. You do not make decisions; you
record them, surface conflicts, and propose options.

This file has a core that always applies and four modules that apply only
when their artefact exists: report (report/), code (code/), hardware
(HARDWARE.md), CAD (params/params.yaml). A module section that names an absent
artefact is inert: do not follow it, and do not create paths under it to make
it apply. This CAD template ships with code, hardware and CAD present.

The governing documents at the root are maintained too, on the terms each
sets: the logs are appended to and never rewritten, and a change to a rule is
recorded as a decision rather than made quietly.

Files that results are checked against (raw measurement logs, exported data,
datasheets, manuals) are read-only to the agent. An edited source cannot
falsify the result built from it, which is the whole reason to keep it.
HARDWARE.md is not one of these: it is maintained under its own module rule.

### Truth ladder
When sources conflict, higher wins. Propose an update to the loser.
1. Physical reality: measurements, current code, current CAD, HARDWARE.md.
2. POSTMORTEMS.md rules, accepted DECISIONS.md entries, this file.
3. GLOSSARY.md definitions.
4. PLAN.md: verified items and open questions.
5. notes/ (working notes, low authority, may be stale).
6. Git history (archaeology only, never current truth).

Simulation output is not rung 1. It is evidence about a model, and it sits
wherever the model's own verification puts it. Say which you have.

Agent output is not evidence of anything. A generated table, figure, summary
or derived file sits below every rung: it is checked against rung 1, not cited
alongside it. Where it disagrees with its source, the source wins and the
output is regenerated.

"Current CAD" means a part's master source at HEAD: its .py for build123d,
its .SLDPRT for SolidWorks. An exported STEP stands in for it only while the
staleness tests pass; a stale export is a past state, not rung 1.

A provisional source (a draft, or a previous revision used before the current
one exists) ranks below the current one once both exist. Anything built from
it is pending re-verification until checked against the current one.

A claim resting on a measurement states the number and the sample size: "14
of 20 runs overshot" beats "it usually overshoots". A claim with no
measurement behind it is a preference, which is allowed, but say which you
have.

### Capture procedures
On "decision: <text>":
1. Assign the next D number from DECISIONS.md.
2. Append an entry using the template at the top of that file. Fill fields
   from the sentence and conversation. Unknown fields get "TBC"; never invent.
3. Echo the full entry in chat for correction.
4. Ask at most one question: "Report node?" If yes, and report/ exists,
   append a report_nodes bullet.

DECISIONS.md and POSTMORTEMS.md are append-only. An entry that stops being
true is superseded by a new numbered entry that says so: never edited in
place, never deleted, never renumbered. Only the human can order a reset, a
renumbering or an in-place correction. Record it at the top of the log with
its date and reason; it is not a precedent for the next one.

On "postmortem: <text>": same, P numbers, POSTMORTEMS.md. Ask severity;
never guess it. The "Related decisions" field must be filled, or a new D
entry proposed alongside: a postmortem with no decision behind it names a
problem without changing anything. Remind the human of any unticked action
items at session end.
On "term: <word> = <meaning>": add a GLOSSARY.md table row. If a
near-neighbour term exists, add a "not to be confused with" note.
On "shortcut: <text>": DECISIONS.md entry of type shortcut with ceiling and
upgrade path, plus a marker debt-NN to place in the affected artefact.
On "question: <text>": add a row to the PLAN.md open questions table with
today's date and status open. Never answer it into the table yourself; the
answer arrives as a decision, a postmortem, or a measurement. A settled
question is struck through with what settled it, never deleted.

The three CAD procedures below apply when the CAD module is present. Claude
Code also exposes them as /change, /eco-impact and /release-check; those
skills only point here.

On "change: <part.param> <new value> because <reason>":
1. Read the current value from params/params.yaml and run the eco procedure
   below for that parameter first, so the impact is known before the edit.
2. Append a D entry (next D number) with "Parameters changed:
   part.param: old → new", the reason as Context, and Evidence as given or
   TBC. Never invent evidence.
3. Edit params/params.yaml. If the change needs a new or changed test, write
   it and name it on "Tests added or changed:".
4. Run code/check.py and render the part (code/scripts/render.py); look at
   the PNGs. Report every failure verbatim. If a requirement now fails, stop
   and ask: the fix is the human's call, never an edit to requirements.yaml.
5. Echo the D entry and the check summary for review. Do not commit.

On "eco: <part id or part.param>":
1. List the part and every part that depends on it, directly or not
   (`dependents()` in code/src/project_tools/ownership.py), with each owner.
2. Re-export the build123d ones and run the tests.
3. Summarise: what passes, what fails (verbatim), which SolidWorks-owned
   parts need manual review in SolidWorks, and which cad/equations.txt
   globals changed. Change nothing else.

On "release check":
1. Confirm the working tree is clean (git status). If not, list what is
   uncommitted and stop.
2. Run code/check.py; it must pass.
3. Run code/scripts/params_audit.py; every parameter and requirement changed
   since the last tag must be named by a D entry added since that tag.
4. List placeholders, TBC Verify clauses and TBC "Verified on" fields that
   ship in this release. Recommend a tag name; never create or push tags.

### Routing table
Read before starting, by task type. Announce what you loaded. The fourth
column is as binding as the second: those sources describe a past state and
must not be quoted as current.
| Task type | Read first | Also | Do not treat as current | Anchors |
|---|---|---|---|---|
| Safety-relevant change | POSTMORTEMS.md | HARDWARE.md, DECISIONS.md | superseded D entries, sim-only results | code/check.sh |
| Hardware or motion change | HARDWARE.md | POSTMORTEMS.md, DECISIONS.md | notes/, any TBC field, sim-only results | code/src/ |
| Design or architecture | DECISIONS.md | GLOSSARY.md, PLAN.md | notes/, superseded D entries | code/src/ |
| Planning, what next | PLAN.md | DECISIONS.md | answered open questions, unmeasured Verify clauses | none |
| Geometry or parameter change | params/params.yaml, parts/ownership.yaml | params/requirements.yaml, DECISIONS.md, HARDWARE.md | exports/ when staleness tests fail, superseded D entries | code/tests/, code/check.py |
| SolidWorks-owned part | parts/ownership.yaml, WORKFLOW.md | cad/step/manifest.json, DECISIONS.md | a STEP whose SLDPRT has changed since registration | code/scripts/register_sw_step.py |
| Hardware change | HARDWARE.md | POSTMORTEMS.md, DECISIONS.md | notes/, any TBC field, model-only results | code/src/ |
| Mechanical or fabrication change | HARDWARE.md | DECISIONS.md, POSTMORTEMS.md | notes/, superseded CAD revisions, nominal values where as-built exists | none |
| Report support | report/report_nodes.md | DECISIONS.md, POSTMORTEMS.md | notes/ | none |
| Anything else | GLOSSARY.md | PLAN.md, latest file in notes/ | notes/ older than the newest | none |

### Minimalism ladder
Before producing anything, stop at the first rung that holds:
1. Does this need to exist? If not, skip it.
2. Does a standard tool or library already do it? Use that.
3. Can it be one line? Write one line.
4. Otherwise: the minimum that works, with one runnable check.
Never lazy about: safety checks, unit and calibration handling, validation at
trust boundaries, anything explicitly requested.

A script that produced an artefact lives in the repository, never in a session
scratchpad or temp folder, which is cleaned between sessions. An artefact that
cannot be rebuilt from the repository alone is not reproducible.

### Never write outside this repository
Read what you need; write only inside the repository root. Sibling folders and
application data directories are live workspaces with their own sync and their
own editors, so a write from here races something that cannot be seen, and the
damage lands in work that has nothing to do with this project.

This is a rule, not a setting. A general "everything outside" deny cannot be
expressed in .claude/settings.json: a relative pattern matched nothing and
failed open, and a wildcard over the parent matched this repository too and
denied its own files. Deny a specific neighbour by absolute path where one is
worth it. An absent tool-level block is not permission.

An exception is a numbered decision made on the human's explicit instruction.
A one-off sets no precedent. If the same one-off is asked for twice, propose a
standing rule and let the human decide; do not assume it. Any permitted write
outside runs with the owning application closed, after a backup with a sha1
list, never over an existing name, and deletes nothing.

### Two-part document rules
Every top-level .md except pointers, README.md, and logs' entries:
frontmatter with status (active | superseded) and verified (YYYY-MM-DD), a
human section of at most 25 non-blank lines before the first "##" heading,
and an uncapped "## Agent Notes" section for structured detail. README.md is
exempt from frontmatter so the template landing page starts with its title,
but it still follows the human-section cap and Agent Notes rule. Put tables,
anchors, and full metadata in Agent Notes, never in the human section. When a
human confirms a document, update its verified date in the same commit.

### Report module (ignore unless report/ exists)
The Typst report is written by the human only. Never produce prose,
sentences, draft paragraphs, or example wording for report/report.typ or any
.typ file, in any channel: not in files, not in chat, not as "just an
example", and not when asked directly. If asked, refuse and cite this
section. Why: the report is the assessed evidence of the human's own
understanding. Ghost-written prose destroys that evidence and is academic
misconduct in most courses. The human asking in a weak moment does not
suspend this rule; that moment is what the rule exists for.

The deny list in .claude/settings.json blocks Edit and Write on .typ files
only. A shell redirect, a filesystem tool, or another vendor's agent walks
straight through it. The rule is the control; the config is a convenience.
Do not treat an absent block as permission.

Your only permitted report output is appending entries to
report/report_nodes.md in this exact form, one line each:
- [D-07] 2026-07-19 | what was decided | alt: rejected options | evidence: DECISIONS.md D-07, figures/x.png | section: Method
Entries name decision nodes: what, when, alternatives, where the evidence
lives, suggested report section. Never sentences intended for pasting.

Any figure cited as evidence names its source in the same bullet: the script
that produced it, the measurement and its date, or the CAD file and revision.
A figure whose provenance nobody can reconstruct is not evidence.

### Code module (ignore unless code/ exists)
Source in code/src/, tests in code/tests/, scripts in code/scripts/. Every
non-trivial change leaves one runnable check behind.

The project's checks are reachable as `code/check.sh`: one executable script,
exit 0 for pass, non-zero for fail, no arguments. CI runs exactly that and
nothing else, so whatever the language or toolchain, the contract is one line
and the same everywhere. If a check cannot be run from that script, it is not
a check the project has.

If code/ is absent, no part of this section applies and no document may
reference paths under code/.

### CAD module (ignore unless params/params.yaml exists)
Principles, in order of how often they are broken:
1. One owner per part. parts/ownership.yaml names it: build123d, solidworks
   or vendor. Never modify a SolidWorks-owned or vendor part; read its STEP.
   Never write .SLDPRT, .SLDASM or .SLDDRW files.
2. STEP is an output, never an input to edit. exports/, cad/equations.txt
   and every manifest.json are regenerated by scripts, never edited by hand.
   STEPs in cad/step/ and cad/vendor/ are read-only to the agent.
3. One source of driving dimensions: params/params.yaml. No dimension is
   typed into a part file; SolidWorks reads the same values through
   cad/equations.txt.
4. Tests run on exported STEP, so every owner is checked the same way.
5. Decisions are traceable: a parameter change is named in a D entry with
   the tests it touched and its evidence, at the latest by release.

Requirements (params/requirements.yaml) are limits set by the human. They
are read-only to the agent like a datasheet: a failing requirement test is
reported, never fixed by moving the limit or loosening the test.

build123d style, for parts/*.py:
- Write build123d, not CadQuery. Algebra mode (`Box`, `Cylinder`, `Pos`,
  `-`, `fillet`), not builder mode.
- Each part module defines `PARAMS` (required names) and
  `build(params: dict) -> Part`, with no side effects on import. Live viewing
  goes under `if __name__ == "__main__":` with ocp_vscode `show`.
- No magic numbers: every dimension comes from params. Counts of topology
  (four vertical edges on a box) may appear in assertions.
- Place features by construction (position a cylinder and subtract it), not
  by selecting faces of the result. Where selection is unavoidable, filter by
  geometry (axis, position), never by list index, and assert the count.
- Read the installed build123d source before using an unfamiliar function.
  Do not guess method names.
- Units: mm, g, s, degrees (SolidWorks MMGS). build123d is +Z up; SolidWorks
  is +Y up.

Working loop. Use the project environment (`conda activate cad-workflow`,
or the interpreter in `git config hooks.python`); a bare `python` on Windows
may be another install. If the env is missing or broken, run
`python scripts/setup_env.py`.
1. Edit params/params.yaml or the part's build().
2. python code/scripts/export.py --part ID
3. python -m pytest
4. python code/scripts/render.py, then open the PNGs in exports/renders/ and
   look at them before claiming the geometry is right. A test proves a
   number; a render catches what no test asked about.
5. Repeat until green, then python code/check.py before any commit.

Where things live: decisions in DECISIONS.md, working notes in notes/,
design rules and materials in HARDWARE.md, the full workflow (SolidWorks
linking, absorbing a SolidWorks edit, releases) in WORKFLOW.md.

### Hardware module (ignore unless HARDWARE.md exists)
HARDWARE.md is rung 1 of the truth ladder alongside the code and the CAD: it
records physical fact. Never edit its numbers from memory, a datasheet guess,
or a forum post. Change them only from the manual or a measurement, and say
which, with a date, in the same commit.

Every quantity you produce carries its unit in its name (`angle_deg`,
`length_mm`, `torque_nm`) or is converted at a named boundary. Unit-free
numbers crossing a function signature are a defect, not a style preference.

TBC is a stop sign, not a default. If HARDWARE.md says TBC for a unit, frame,
tolerance, or limit you need, ask. Do not assume the common value, the SI
value, or the value the last project used.

Simulation agreement is not hardware agreement. Flag anything that would only
work because the model is ideal — no backlash, no compliance, no latency, no
thermal drift, exact frames, perfect tolerances — and add a row to the parity
table in HARDWARE.md rather than asserting the sim result.

Before proposing anything that moves, energises, heats, or cuts, state the
stop condition and who can trigger it. If two stop mechanisms have similar
names, treat them as different until GLOSSARY.md says otherwise.

### Close-out procedure
On "close out":
1. Reconcile PLAN.md: every `[x]` item has a measured result and a date; every
   open question is either still genuinely open or names where its answer went.
   Report mismatches; do not fix them by editing the tick.
2. If report/ exists: sweep DECISIONS.md and POSTMORTEMS.md; propose any
   missing report_nodes bullets. Do not touch .typ files.
3. For each entry passing the lesson test (it can be restated with no
   project-specific nouns and would change behaviour on a different project),
   draft one note in lessons/ from lessons/_template.md.
4. List every active document with a stale verified date for human review.
5. List every `.keep` whose folder now holds another tracked file
   (`git ls-files <folder>` shows more than the `.keep`), for the human to
   delete. Keep any `.keep` whose folder's other contents are all gitignored:
   it is the only thing holding that folder in git.

