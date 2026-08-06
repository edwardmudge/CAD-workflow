---
status: active
verified: 2026-08-06
---
# Engineering Workflow Template

A single-repo workflow for running an engineering project, hardware or
software, alongside an AI coding agent. Decisions, mistakes, and terminology
get captured as dated, numbered entries as you work, not left in chat
history; nothing counts as done without a measured Verify. The agent works
from one fixed rule file and a ranked truth ladder, and never marks its own
work complete.

Click "Use this template" above to start a project from this. Day-one setup,
about an hour: SETUP.md. Method and citations behind every convention:
REFERENCES.md.

What a project built on this gives you: PLAN.md tracks work with Verify
gates; DECISIONS.md and POSTMORTEMS.md are append-only logs; GLOSSARY.md
keeps terms consistent. Rules the agent follows: AGENTS.md.

## Agent Notes

### Core files
Always present: AGENTS.md (canonical agent rules; vendor files are pointers
to it), PLAN.md (work items with Verify gates, and the open questions
register), DECISIONS.md and POSTMORTEMS.md (append-only logs, D and P
numbers), GLOSSARY.md (terms), notes/ (dated scratch, low authority,
template in notes/_template.md), lessons/ (close-out staging for Obsidian
export), scripts/check_docs.py and .github/workflows/checks.yml (CI).

### Optional modules
Inert until its artefact exists: report/ (human-written Typst plus
report_nodes.md, the agent's only report channel), code/ (source and tests,
with code/check.sh as the one command CI runs), HARDWARE.md (physical fact,
installed by scripts/add_hardware.py and extended by the domain packs
scripts/add_robotics.py and scripts/add_mechanical.py), VAULT.md (the
read-only contract with an Obsidian vault holding the project's reading,
installed by scripts/add_vault.py).

### Setup and provenance
Setup and how to turn modules on: SETUP.md. Provenance of the method:
REFERENCES.md.
