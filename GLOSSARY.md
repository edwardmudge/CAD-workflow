---
status: active
verified: 2026-10-13
---
# Glossary

Terms this project must use consistently, in docs, chat, and identifiers.
If a needed term is missing, propose an entry before using the concept.
The five most confusable pairs live at the top of the table below.

## Agent Notes
| Term | Definition (one sentence) | Not to be confused with | Identifier |
|---|---|---|---|
| parameter | A driving dimension in params/params.yaml that the design may change. | requirement, a limit the design must meet | params.yaml |
| requirement | A limit the design is tested against, set by the human and read-only to the agent. | design rule, a project-wide rule such as minimum wall | requirements.yaml `id` |
| owner | The one tool that authors a part: build123d, solidworks or vendor. | responsible, the person accountable for it once a team forms | ownership.yaml `owner` |
| master | A part's native parametric source: its .py or its .SLDPRT. | export, a STEP or STL derived from it and never edited | ownership.yaml `source` |
| stale export | An export whose recorded source or params hash no longer matches the current files. | failing test, which judges the geometry rather than its freshness | test_build123d_export_is_current |
| placeholder | A part listed in ownership.yaml but not modelled yet; its tests skip. | vendor part, which is complete but owned by a supplier | ownership.yaml `status` |
| nominal dimension | The intended size before tolerance is applied. | basic dimension, which is theoretically exact and toleranced by a geometric frame | |
| tolerance | Permitted deviation of one feature from nominal. | clearance, which is the gap between two features | |
| clearance | The gap between two mating features as assembled. | allowance, the intended minimum clearance at worst case | |
| datum | A referenced feature that measurement is taken from. | origin, which is a coordinate system that need not touch the part | |
| as-designed | The geometry in the master at a stated release tag. | as-built, the geometry actually produced and measured | |
| as-built | The part as it physically exists, including rework. | as-designed; the difference is a finding, not an error to be edited away | |
| worst-case stack | Every tolerance at its least favourable limit. | statistical stack, which allows a stated fraction of assemblies to fail | |
| build orientation | How a part sits on the machine during fabrication. | part orientation in the assembly; the first is a structural decision | |
