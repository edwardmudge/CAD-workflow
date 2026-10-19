---
status: active
verified: 2026-10-19
---
# Setup

Day one, about an hour:
1. Copy the template ("Use this template" on GitHub, or copy the folder
   without .git and `git init`). Delete the template banner in README.md.
2. Rename the env in environment.yml (`name:`), then run
   `python scripts/setup_env.py`: it creates the env and enables the hooks.
3. `python code/check.py` passes on the empty template. If it does not, stop
   and fix the environment first.
4. Optional, recommended once: the dry run in WORKFLOW.md, on a separate
   throwaway copy with `python scripts/load_cad_example.py`.
5. Delete `report/` if nothing is assessed.
6. Fill the top of HARDWARE.md (item, revision) and the material grade.
7. Record D-01 in DECISIONS.md: the objective and its constraints. Put the
   first limits in params/requirements.yaml and write S1.1 in PLAN.md, its
   Verify clause first.
8. Add the first part: an ownership.yaml entry, a params.yaml section and
   parts/<id>.py. examples/sensor_mount/ is the pattern to copy.
9. Commit, push, watch the checks pass. Then break something on a branch
   (raise a dimension past a requirement) and watch them fail. A check you
   have never seen fail is not known to work.

## Agent Notes

### Modules
| Module | State in this template | Gives you |
|---|---|---|
| Report | present; delete `report/` to turn it off | Typst report, report_nodes.md, the report firewall, a CI compile job |
| Code | present: `code/check.sh`, exit 0 for pass | code/check.py, the CI code job, the pre-commit hook |
| Hardware core and mechanical | present: HARDWARE.md | identity, units, provenance, pre-flight, parity, CAD register, materials, tolerances, fabrication, inspection |
| CAD | present: params/, parts/, cad/ | build123d parts, SolidWorks bridge, STEP tests, renders, step_diff |
| Robotics | `python scripts/add_robotics.py --dof 6` | frames, rotation convention, DH, joint limits, singularities, stop behaviour |
| Vault | `python scripts/add_vault.py` | VAULT.md: the read-only contract with an Obsidian vault holding the project's reading |

The hardware core and mechanical sections are baked into HARDWARE.md rather
than installed by pack scripts: every CAD project makes physical parts, so
they always apply. The robotics pack still extends HARDWARE.md and is
idempotent. The vault module needs no hardware; see the upstream
engineering-workflow template for its rationale.

### Writing a new domain pack
A pack is one script in `scripts/` that:
1. imports the helpers in `scripts/modules/_common.py`,
2. calls `require_hardware_core()`,
3. appends its sections to HARDWARE.md through `append_section()`, which is a
   no-op if the section is already there,
4. seeds GLOSSARY.md only with pairs that cause real bugs in that domain,
5. adds at most one routing row to AGENTS.md,
6. seeds no postmortems. A rule with no event behind it does not get followed.

### Add only when the project needs it
- `report/refs.bib` and the bibliography line: the day you first cite.
- A second vendor pointer file (GEMINI.md, .cursorrules): copy CLAUDE.md
  verbatim, then add the filename to POINTER_FILES in scripts/check_docs.py.
  Codex reads AGENTS.md directly and needs none.
- `report/sections/`: only past roughly 1500 lines of report.
- A `vendor` part: put the supplier's STEP in cad/vendor/ and list it in
  ownership.yaml with `owner: vendor` and `source` equal to `step`.

### When a second person joins
Do none of this while solo; each item costs time on every commit.
- **File locking.** SolidWorks files cannot be merged, so two people editing
  one SLDPRT lose work. Add `lockable` to the SolidWorks lines in
  .gitattributes and `git lfs lock` a file before editing it, or move native
  files to SolidWorks PDM and keep only STEPs here.
- **CI on every push.** The code job in .github/workflows/checks.yml already
  installs code/requirements.txt and runs code/check.sh. Add a job that
  attaches the exports to a GitHub release on `v*` tags.
- **Branch protection and pull requests**, one required review, with the D
  entry reviewed alongside the parameter change it records.
- **A `responsible` field** (person) in parts/ownership.yaml, and a test that
  every active part has one.
- **Team wiki.** Move notes/ to the team wiki, connect it to the agent, and
  link wiki pages back to D numbers and release tags.
- **Shared agent conventions.** Agree changes to AGENTS.md as a team and
  record each one as a D entry.

### Tools
Git with Git LFS, VS Code with the Python and OCP CAD Viewer extensions,
Miniconda, SolidWorks (MMGS units), Typst if the report module is kept, any
coding agent. scripts/ uses the standard library only; code/ needs the conda
env. On Windows conda may not be on PATH outside the Anaconda Prompt: call
`~/miniconda3/Scripts/conda.exe` by full path. The `python` on PATH may be
another install without build123d, which is why the hook reads
`git config hooks.python`.
