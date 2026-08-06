---
status: active
verified: 2026-08-04
---
# Setup

Day one, about an hour:
1. Click "Use this template" on GitHub, name the repo, clone it.
2. Delete the TEMPLATE BANNER block in README.md and write the project paragraph.
3. Decide which modules this project has. Delete `report/` if nothing is
   assessed. `code/` and `HARDWARE.md` do not exist until you add them.
4. Seed GLOSSARY.md with three terms you already argue about.
5. Record D-01 in DECISIONS.md: the objective and its constraints.
6. Write S1.1 in PLAN.md, its Verify clause first, before doing the work.
7. Commit, push, watch the checks pass. Then break something on a branch
   (edit CLAUDE.md, or tick a PLAN.md item that has no measured result) and
   watch them fail. A check you have never seen fail is not known to work.

## Agent Notes

### Modules
Nothing here is on by default. Each module is a folder or a file; the rules in
AGENTS.md and the checks in CI key on its existence and are inert without it.

| Module | Turn it on by | Gives you |
|---|---|---|
| Report | shipped present; delete `report/` to turn it off | Typst report, report_nodes.md, the report firewall, a CI compile job |
| Code | `code/check.sh`, executable, exit 0 for pass | the CI code job runs it, whatever the language |
| Hardware core | `python scripts/add_hardware.py` | HARDWARE.md: identity, units, provenance rule, pre-flight, parity table |
| Robotics | `python scripts/add_robotics.py --dof 6` | frames, rotation convention, DH, joint limits, singularities, stop behaviour |
| Mechanical | `python scripts/add_mechanical.py` | CAD revision register, materials, tolerances and datums, process parameters, inspection |
| Vault | `python scripts/add_vault.py` | VAULT.md: the read-only contract with an Obsidian vault holding the project's reading |

Run `add_hardware.py` before any domain pack; the packs extend HARDWARE.md and
refuse to run without it. Packs compose: robotics and mechanical on the same
machine is the normal case, not a conflict. All are idempotent, so a second run
changes nothing. To see a filled-in example, run `add_robotics.py` then
`python scripts/load_fr5_example.py`, which loads a real Fairino FR5 with its
measurements, one genuine postmortem, and its provenance. Those numbers are
another machine's. Verify against yours before any powered run.

The vault module is not a domain pack and needs no hardware. It records where
this project's reading lives, that the agent reads that vault and never writes
to it, and that the written literature review is report prose like any other.
Nothing is copied by machine in either direction: an exporter would need the
vault path committed here and can silently pollute a vault that a git plugin is
already auto-pulling. Do not install it in this template repository — leaving
VAULT.md absent keeps the module inert, which is what lets an agent working
here maintain the design document that lives in the vault.

### Writing a new domain pack
Electronics and instrumentation are not written; the contract is stable enough
that they slot in. A pack is one script in `scripts/` that:
1. imports the helpers in `scripts/modules/_common.py`,
2. calls `require_hardware_core()`, so it cannot run standalone,
3. appends its sections to HARDWARE.md through `append_section()`, which is a
   no-op if the section is already there,
4. seeds GLOSSARY.md only with pairs that cause real bugs in that domain,
5. adds at most one routing row to AGENTS.md,
6. seeds no postmortems. A rule with no event behind it does not get followed.

Electronics would carry schematic and netlist revision, BOM and part numbers,
power budget, register map, bring-up order. Instrumentation would carry DAQ
configuration, calibration certificates and their expiry, measurement
uncertainty, and raw-data provenance for figures.

### Add only when the project needs it
- `code/src/` and `code/tests/`: the day the first script exists. Point
  `code/check.sh` at them; CI needs nothing else.
- `report/refs.bib` and the bibliography line: the day you first cite. Its
  keys are the citekeys named in VAULT.md, so one string ties the vault note,
  the bibliography and the report together.
- A second vendor pointer file (GEMINI.md, .cursorrules): copy CLAUDE.md
  verbatim, then add the filename to POINTER_FILES in scripts/check_docs.py.
- `report/sections/`: only past roughly 1500 lines of report.
- Branch protection with one required review: the day a collaborator joins.

### Tools
Git, VS Code, Typst, Obsidian, any coding agent. Python 3 for the checks; no
third-party packages, standard library only. On Windows the `python` on PATH
may be the Microsoft Store stub, which cannot run the checks: use a real
interpreter (a conda base environment works) and call it by full path.
