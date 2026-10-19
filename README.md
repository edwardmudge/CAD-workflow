# CAD Workflow Template

<!-- TEMPLATE BANNER: delete this block and write the project paragraph. -->
A single-repo workflow for designing parts in build123d alongside SolidWorks,
with an AI coding agent. One parameters file drives both tools, tests run on
the exported STEP whichever tool made it, and every parameter change traces
to a decision, its tests and its evidence. Built on the engineering-workflow
template: decisions and mistakes are logged as numbered entries, and nothing
is marked done without a measured Verify.

## Setup

From the repo root, once per copy (any `python` on PATH will do; the script
finds conda itself):

```
python scripts/setup_env.py
```

It creates the conda env named in `environment.yml`, enables the pre-commit
hook (`core.hooksPath .githooks`) with that env's Python, points VS Code at
the env and runs `code/check.py`. Rerunning it is harmless and quick. VS Code
also runs it on folder open (`.vscode/tasks.json`) once you allow automatic
tasks for the folder. From then on a commit is blocked when any check fails.
Emergency bypass: `git commit --no-verify`, then fix and rerun
`python code/check.py` before pushing.

Manual equivalent, in a shell where conda works: `conda env create -f
environment.yml`, `conda activate cad-workflow`, `python code/check.py
--install-hooks`, `python code/check.py`.

Then work through `SETUP.md` (day one), and try the dry run in `WORKFLOW.md`
on a throwaway copy.

## Repository layout

- `params/params.yaml` - driving dimensions, materials, design rules; `params/requirements.yaml` - limits, each linked to its test
- `parts/` - build123d part sources and `ownership.yaml` (who owns each part)
- `cad/` - SolidWorks files (Git LFS), `step/` exports from SolidWorks, `vendor/` supplier STEPs, generated `equations.txt`
- `exports/` - generated STEP, STL, renders and manifest; never committed or edited
- `code/` - helpers, scripts and tests; `code/check.py` runs everything
- `examples/sensor_mount/` - the made-up example, installed by `scripts/load_cad_example.py`
- `AGENTS.md` - rules for any AI agent (`CLAUDE.md` points to it); `WORKFLOW.md` - how to work
- `PLAN.md`, `DECISIONS.md`, `POSTMORTEMS.md`, `GLOSSARY.md`, `HARDWARE.md` - plan, logs, terms, physical facts
- `SETUP.md` - day one, modules, and what to add when a second person joins
- `report/`, `notes/`, `lessons/` - report scaffold, dated notes, close-out lessons

## Method

Provenance and citations behind every convention: `REFERENCES.md`.

## Agent Notes

Read AGENTS.md in full before making changes; nothing above overrides it.
Present in this template: report, code, hardware (with mechanical) and CAD
modules. Optional: robotics and vault packs (see SETUP.md).
