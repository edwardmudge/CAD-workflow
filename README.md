# Engineering Workflow Template

A single-repo workflow for running an engineering project, hardware or
software, alongside an AI coding agent. Decisions and mistakes are logged as
dated, numbered entries as you work, and nothing is marked done without a
measured Verify.

## Getting started

1. Click **Use this template** above and clone your new repository.
2. Work through the day-one checklist in `SETUP.md` (about an hour).
3. Read `AGENTS.md` for the rules your agent works from.

## Repository layout

- `AGENTS.md` - canonical rules for any AI agent working in the repo
- `PLAN.md` - work items with Verify gates, and the open questions register
- `DECISIONS.md`, `POSTMORTEMS.md` - append-only logs, numbered `D-NN` / `P-NN`
- `GLOSSARY.md` - agreed terminology
- `notes/` - dated scratch notes, low authority
- `lessons/` - close-out staging for Obsidian export
- `report/` - report module scaffold, with agent output limited to `report/report_nodes.md`
- `code/`, `HARDWARE.md`, `VAULT.md` - optional modules, inert until their file or folder exists
- `scripts/`, `.github/workflows/checks.yml` - the CI that enforces all of the above

## Method

Provenance and citations behind every convention in this template: `REFERENCES.md`.

## Agent Notes

Read AGENTS.md in full before making changes; nothing above overrides it.
The report module scaffold is present in this template repository. The
`code/`, `HARDWARE.md`, and `VAULT.md` modules are absent until installed, so
their sections in AGENTS.md are inert here even though they're listed above
for projects built from this template.
