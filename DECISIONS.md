---
status: active
verified: 2026-10-13
---
# Decision log

Append-only. Newest at the bottom. Entry template:

## D-NN Title (accepted | superseded by D-MM) [decision | shortcut]
- Context: what forced a choice, in one or two lines.
- Decision: We will ...
- Alternatives: what was rejected and in one clause why.
- Consequences: + what gets easier. - what gets harder or is given up.
- Parameters changed: part.param: old → new, one per change, or "none". Requirement changes name their R id.
- Tests added or changed: test names, or "none".
- Evidence: calculations, FEA output, supplier data, renders, measurements. TBC until there is some.
- Supersedes: D-MM, or "none".
- Verified on: YYYY-MM-DD, and how it was checked against reality. TBC until it has been.
- Non-revertible unless: the condition that reopens this. Until it holds, do not re-litigate.
- (shortcut only) Ceiling: known limit. Upgrade path: how to lift it. Marker: debt-NN.

A decision with "Verified on: TBC" is a plan, not a finding. Say which you have
when you cite it. "Non-revertible unless" is what stops the same argument
being had every session: name the condition, then let the entry stand.
Every field line must be present (scripts/check_docs.py checks); "none" and
"TBC" are valid answers. At release, code/scripts/params_audit.py fails if a
parameter changed since the last tag is not named on a "Parameters changed"
line.
