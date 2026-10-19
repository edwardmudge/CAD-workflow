---
status: active
verified: 2026-08-04
---
# References

Where each part of this workflow comes from. Two tiers, kept separate on
purpose: established practice (books, standards, long-settled convention)
and community patterns (recent, unaudited, may not age well).

Read this before defending the method to a supervisor. Cite tier 1 freely.
Cite tier 2 as "current practice in AI-assisted development", not as
settled engineering.

## Agent Notes

### Tier 1: established practice

| Artefact here | Practice | Source |
|---|---|---|
| DECISIONS.md entries | Architecture Decision Records | Michael Nygard, "Documenting Architecture Decisions", 2011. ThoughtWorks Technology Radar lists lightweight ADRs at Adopt. |
| GLOSSARY.md, enforced naming | Ubiquitous Language | Eric Evans, *Domain-Driven Design*, Addison-Wesley, 2003, ch. 2. |
| POSTMORTEMS.md format and blamelessness | Blameless postmortem culture | Beyer et al. (eds), *Site Reliability Engineering*, O'Reilly, 2016, ch. 15. Free at sre.google/books. |
| Routing table, code and test anchors | Requirements traceability matrix | IEC 61508 family; DO-178C in aerospace; ISO 10218 and ISO/TS 15066 for industrial and collaborative robot documentation. |
| PLAN.md Verify clauses; no tick without a measured result | Verification and validation; the V-model | ISO/IEC/IEEE 15288, *Systems and software engineering: system life cycle processes*, 2023. IEC 61508-1 §7 on verification planning. |
| PLAN.md open questions register | Risk and issue log; open-items list | PMI, *PMBOK Guide*, 7th ed., 2021, on issue logs. NASA/SP-2016-6105, *Systems Engineering Handbook*, on open work and TBC/TBD tracking. |
| HARDWARE.md units, frames, and the TBC stop sign | Units discipline and interface control | The Mars Climate Orbiter loss, NASA MCO MIB Phase I report, 1999, remains the canonical unit-mismatch case. Interface Control Document practice, ISO/IEC/IEEE 15288 §6.4.4. |
| Mechanical pack: tolerances, datums, as-designed vs as-built | Geometric dimensioning and tolerancing | ASME Y14.5-2018; ISO 1101:2017 for the ISO GPS equivalent. |
| Hardware pre-flight checklist | Checklist discipline for irreversible operations | Gawande, *The Checklist Manifesto*, 2009. Degani and Wiener, "Cockpit Checklists", NASA Ames, 1990, on why checklists fail. |
| CI doc checks, branch protection | Continuous Integration | Martin Fowler, "Continuous Integration", martinfowler.com, rev. 2006. |
| Human vs agent document split; report/ vs notes/ | Diátaxis documentation framework | diataxis.fr. Used by Django, Canonical, Gatsby. |
| Shortcut entries with ceiling and upgrade path | Technical debt metaphor; YAGNI | Ward Cunningham, OOPSLA 1992 experience report. Kent Beck, *Extreme Programming Explained*, 1999. |
| Minimalism ladder | Simple design, "do the simplest thing that could possibly work" | Beck, as above. Also John Ousterhout, *A Philosophy of Software Design*, 2018, on deep modules. |
| Small deliberate steps, DRY, one source of truth | | Hunt and Thomas, *The Pragmatic Programmer*, 1999 (20th anniversary ed. 2019). |
| Append-only logs, commit as the official act | Version control convention | Universal practice; see Chacon and Straub, *Pro Git*, free at git-scm.com/book. |
| Close-out audit cadence | Retrospectives, definition of done | *The Scrum Guide*, scrumguides.org. |
| STEP as the interchange format; AP214 now, AP242 as the upgrade path | Product data exchange | ISO 10303-214 (automotive design) and ISO 10303-242 (managed model-based 3D engineering). |
| Clearance hole table in code/src/project_tools/standards.py | Metric clearance holes, medium series | ISO 273, *Fasteners: clearance holes for bolts and screws*. |
| requirements.yaml `test` field; test_requirements_trace_to_parts_and_tests | Requirements traceability matrix | As the routing table row above: IEC 61508 family, DO-178C. |
| cad/equations.txt | SolidWorks global variables linked to an external file | SolidWorks help, "Exporting and Linking Equations to External Files", help.solidworks.com. |

### Tier 2: community patterns in AI-assisted development

| Artefact here | Pattern | Source |
|---|---|---|
| AGENTS.md as the single canonical instruction file, vendor files as pointers | AGENTS.md convention | agents.md. Adopted across Codex, Cursor, Copilot, Claude Code and others through 2025-2026. |
| Wiki as compounding agent memory; markdown knowledge base maintained alongside an agent; AGENTS.md as the schema layer | LLM Wiki | Andrej Karpathy, `llm-wiki.md` gist, October 2025: gist.github.com/karpathy/442a6bf555914893e9891c11519de94f. Explicitly an "idea file", not a spec. |
| Named procedures the agent invokes; user-invoked orchestration vs model-invoked discipline | Agent skills | mattpocock/skills, github.com/mattpocock/skills. |
| Minimalism ladder wording; marked shortcuts with a named upgrade path | Ponytail ruleset | DietrichGebert/ponytail, github.com/DietrichGebert/ponytail. |
| Two-part documents; capture loops; truth ladder | Prior version of this method | `WIKI_CONSTRUCTION_GUIDE.md`, this author, distilled from the FR5-StreamingSys project. Unpublished; the de-domained copy lives in the `fairino-fr5-sim` repo under `wiki-template/`. Not reproduced here, so treat this row as provenance, not a citation a reader can follow. |
| Routing table's "do not treat as current" column | Negative routing: naming what is stale, not only what is current | Boot Matrix in the same prior method. In practice the most-used column there: it stops an agent quoting a superseded measurement it found by reading around. |
| build123d parts in algebra mode, construction over selection, asserted selector counts | Code-CAD; the topological naming problem | build123d documentation, build123d.readthedocs.io. Selection by index breaks when an upstream change renumbers faces, in any CAD kernel. |
| CAD module as a whole: params file, one owner per part, tests on exported STEP, staleness manifest, PNG renders for the agent | Code-CAD with an AI agent | A brief written by another agent for this author, October 2026, adapted to this template. No published source; treat as current practice, not settled engineering. |
| .claude/skills wrappers | Agent skills | Claude Code skills. Kept as pointers only, like CLAUDE.md, so the rules stay in AGENTS.md and Codex loses nothing by reading AGENTS.md alone. |

### Honest note on the Karpathy LLM Wiki

This workflow is not an LLM Wiki and should not be described as one. The
LLM Wiki pattern has the agent compile a knowledge base from raw source
documents, and the agent owns the wiki layer. Here the human owns every
durable artefact and the agent only files entries into fixed templates.
Where the deliverable is an assessed report, that split is not a preference
but a requirement: the report must evidence the human's own understanding.

What is genuinely shared: plain markdown over a database, AGENTS.md as the
schema layer that tells the agent how knowledge is maintained, an
append-only log, knowledge that compounds across sessions rather than being
re-derived, and periodic linting. The reported failure mode of that pattern
also applies here: it degrades past roughly 200 files, which is why the
base template ships nine root files and grows only on demand, one module at a
time. This CAD template adds two (HARDWARE.md, WORKFLOW.md) because every
CAD project needs them.

### Not adopted, and why

- RAG or vector search over the repo: at this size the agent reads the files
  directly. Adding embeddings would introduce a tool without beating plain
  markdown.
- adr-tools and one file per decision: rejected for capture speed. See the
  design rationale.
- CODEOWNERS and peer review: team practices, no solo equivalent. Replaced by
  the manual commit gate.
- Vendor-specific agent machinery (slash commands, hooks, subagent
  definitions): rejected to keep AGENTS.md the only place rules live. A hook
  could close the shell-redirect hole in the report firewall, but only for one
  vendor, and a rule that holds in one tool and not another is worse than a
  rule that is plainly a rule. Revisit if a single agent becomes permanent.
  Exception: .claude/skills wrappers that only point at an AGENTS.md
  procedure, as CLAUDE.md does. The git pre-commit hook is not vendor
  machinery; it runs for every agent and every human.
- From the CAD brief: one ADR file per decision under docs/decisions/
  (DECISIONS.md gained its fields instead); uv (conda, as in the author's
  other projects); installing the project code as a package (any checkout
  must run its own code); requirement limits inside params.yaml (an agent
  could pass a test by moving the limit).
- One file per plan item, or an issue tracker: rejected for the same reason as
  adr-tools. PLAN.md is read top to bottom in one pass, which is what makes
  the open questions register get looked at.
