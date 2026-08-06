---
status: active
verified: 2026-08-04
---
# Plan

What is being built, in what order, and how each step proves itself.

Current stage: not started.
Next verify gate: none yet.

An item is not done because it looks done. It is done when its Verify clause
carries a measured result and the date it was measured. Anything else is a
guess wearing a tick.

Open questions live at the bottom. A question is closed by pointing at where
the answer went (a D number, a P number, a HARDWARE.md row), never by
deleting it.

## Agent Notes

### Conventions

Item states: `[ ]` not started, `[~]` in progress, `[x]` verified.

Number items `SN.M`: stage N, item M. Stages are milestones you would tell
someone about; items are a session or two of work. Never renumber a shipped
item; supersede it with a new one and say so.

Item shape:

```
#### S1.1 Item title [x]
Goal: one line, what this buys.
1. step — done
2. step — done
**Verify:** the pass condition, stated so it could fail.
Measured: what actually came back, 2026-08-04.
Record: D-03, P-01.
```

`**Verify:**` states the condition *before* the work, in terms that admit
failure ("FK of the home pose puts the tip within 0.5 mm of 196.9 mm"), not
after it in terms that cannot ("FK works"). `Measured:` is filled in only once
the number exists. CI rejects any `[x]` item whose Verify has no measured
result and no date, so the tick cannot run ahead of the evidence.

For software the measurement is usually a test name and its result; for
hardware it is usually an instrument reading, a date, and the thing it was
read off. Both are numbers. Neither is "seems fine".

`Record:` names the DECISIONS.md or POSTMORTEMS.md entries this item produced,
so the plan and the logs stay reachable from each other. CI rejects references
to D or P numbers that do not exist.

### Work items

**S1 — Stage name**

#### S1.1 First item [ ]
Goal: TBC.
1. TBC
**Verify:** TBC — state the condition so that it could fail.

### Open questions

Raise a question the moment it blocks a decision, not once it is answered.
"Status: open" with a stale date is a finding, not an embarrassment.

| # | Question | Raised | Status | Answer / where it went |
|---|---|---|---|---|
| Q-01 | Delete this row when the first real question arrives. | 2026-08-04 | open | |
