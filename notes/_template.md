# Note title

Filename: `YYYY-MM-DD_short_topic.md`, dated the day it was started. Notes are
low authority by design (rung 5 of the truth ladder) and are never corrected
in place: when one is overtaken, set `status: superseded` and say by what.
Nothing here is true because it is written down here.

Copy this file, keep the headings, delete the guidance lines.

---
status: draft | active | superseded
superseded_by: D-NN | P-NN | another note
scope: which files or hardware this touches
---

## Why
What forced this note. One or two lines. If you cannot say what would change
as a result of writing it, stop and do not write it.

## Findings
What is actually true, with the measurement or the code path that shows it.
Separate what you observed from what you concluded.

## Changes
What will be done, concretely enough to act on without rereading the Why.

## Docs to update when implemented
The list of durable artefacts this change must propagate to, written now while
the reasoning is still loaded. This is the block that keeps the logs honest;
everything above it is scratch.
- DECISIONS.md: D-NN for ...
- PLAN.md: item SN.M, and its Verify clause
- GLOSSARY.md: term ... if it caused confusion
- HARDWARE.md: which row, and whether from manual or measurement
- POSTMORTEMS.md: only if something went wrong and a rule follows from it

## Verification
How the change will be shown to work: the command, the instrument, the pass
condition. This is the draft of the Verify clause that goes into PLAN.md, so
write it in terms that could fail.
