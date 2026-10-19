---
status: active
verified: 2026-10-13
---
# Workflow

How a part goes from a number in params/params.yaml to a STEP a supplier
can trust, with SolidWorks and build123d working from the same values.

The daily loop:
1. Change params/params.yaml or a part's build(), or ask the agent to
   ("change: sensor_bracket.thickness 7 because ...").
2. `python code/scripts/export.py --part ID`, then `python -m pytest`.
3. `python code/scripts/render.py` and look; the agent looks at the PNGs.
4. Repeat until green. `python code/check.py`, review the diff, commit.

SolidWorks reads the same numbers through cad/equations.txt and the same
geometry through the exported STEPs. Parts that SolidWorks owns are exported
to STEP by hand and registered, so the same tests cover them.

Decisions go in DECISIONS.md as you make them; at the latest, every
parameter changed since the last release tag needs one before the next tag.
Only exports from a tagged commit go to suppliers.

New here? Run the dry run in Agent Notes on a copy of the template first.

## Agent Notes

### Changing a parameter
1. Edit the value in params/params.yaml. Never type a dimension into a part
   file or into SolidWorks.
2. If a limit is involved, it lives in params/requirements.yaml and is the
   human's to change, with a D entry naming the R id.
3. Record the decision: D entry with `Parameters changed: part.param: old →
   new`, the tests touched and the evidence (calculation, FEA, supplier
   data, measurement). During exploration this can wait; before a release
   tag it cannot (code/scripts/params_audit.py checks).
4. `python code/check.py`. It regenerates cad/equations.txt and fails once if
   the file changed, so the new equations are staged with the params.
5. In SolidWorks, Rebuild any part linked to cad/equations.txt.

### SolidWorks: linking a part to the parameters
1. Run `python code/scripts/gen_sw_equations.py` (check.py does this too).
2. In the SolidWorks part: Tools > Equations, tick "Link to external file"
   and choose cad/equations.txt. Its globals appear, named
   `<part id>_<param>`, for example `"sensor_bracket_hole_spacing"`.
3. Set a dimension to `= "sensor_bracket_hole_spacing"` to drive it.
4. After params change: regenerate, then Rebuild in SolidWorks. Linked
   globals cannot be edited inside SolidWorks; that is the point.

The line syntax (`"name"= 6mm`, `30deg`, unitless numbers) and the comment
lines starting `'` were confirmed on 2026-10-19 by linking a file in this
format in SolidWorks 2025. If a later version rejects it, the format lives in
one function, `equation()` in code/scripts/gen_sw_equations.py. The file is
CRLF (.gitattributes keeps it so).

### SolidWorks: using build123d parts in assemblies and drawings
- Insert the STEP from exports/ (run export first on a fresh clone; the
  folder is not committed). With 3D Interconnect enabled the part stays
  linked to the STEP and can be updated when it is regenerated.
- build123d is +Z up, SolidWorks +Y up: an inserted part lies with its +Z
  towards the viewer in the Front view. Orient it with mates; do not remodel.
- Drawings of a linked STEP can lose dimension references when its faces
  change (a new hole renumbers faces). After a large change, check the
  drawing for dangling dimensions; at release, consider breaking the link so
  the released drawing cannot drift.

### SolidWorks-owned parts
1. Add the part to parts/ownership.yaml: `owner: solidworks`, `source:
   cad/<name>.SLDPRT`, `step: cad/step/<id>.step`. Use `status: placeholder`
   until it is modelled.
2. Model it, driving shared dimensions from cad/equations.txt.
3. File > Save As > STEP AP214 to the `step` path. AP214 matches what
   build123d writes; AP242 is the upgrade path if model-based definition
   (PMI) is ever needed.
4. `python code/scripts/register_sw_step.py <id>`: records hashes, prints
   bounding box, volume and holes. Remove `status: placeholder`.
5. Commit the SLDPRT, the STEP and cad/step/manifest.json together. If the
   SLDPRT is saved again, the staleness test fails until steps 3 and 4 are
   repeated.
SolidWorks files go through Git LFS. Every save is a full copy, so commit
them at meaningful points and watch the LFS quota on the remote.

### Absorbing a SolidWorks edit into code
When a build123d part was tweaked in SolidWorks (say, on an imported copy):
1. Export the edited part from SolidWorks as STEP AP214.
2. `python code/scripts/step_diff.py exports/<id>.step edited.step
   --export exports/diff` shows volume added and removed, where, and the
   mass change; open exports/diff/*.step to see the regions.
3. Re-express the change in params or build(), re-export, and repeat the
   diff until it reports "identical within tolerance".
4. Record the change as a D entry. Discard the SolidWorks copy: the .py is
   the master.

### Releases
1. "release check" (AGENTS.md): clean tree, check.py passes, params_audit
   passes, open TBCs listed.
2. Tag: `git tag -a v0.1 -m "..."` (the human tags; agents never do).
3. Export at the tag, then send the STEPs (and PDF drawings from SolidWorks)
   with the tag name in the filenames or covering note.
4. Add a row to the CAD and revision register in HARDWARE.md.

### Dry run with the example
On a throwaway copy of the template, never in a real project:
1. `python scripts/load_cad_example.py`, `python
   code/scripts/gen_sw_equations.py`, then `python code/check.py`. Expect
   pass, with the cover interface test skipped (placeholder).
2. Thickness 6 → 7 in params.yaml, export: the bounding-box test passes at
   the new size and the manifest hashes change.
3. Thickness 8: the mass test fails naming R-01, the mass and the limit.
   Revert.
4. Edit a param without exporting: the staleness test fails and says to run
   export. Revert.
5. Commit, tag v0.1, change a parameter, run params_audit: it fails until a
   new D entry names the parameter.
6. "eco: sensor_bracket.hole_spacing": the agent lists sensor_cover for
   SolidWorks review.
7. Enable the hook, break a test, try to commit (blocked), fix, commit
   (allowed).

### Working with an agent on CAD
- Test first, then geometry: write the requirement and its test, then let
  the agent iterate build() until the tests pass. Numbers catch what
  pictures miss, and pictures catch what nobody wrote a test for.
- Both of you look: the agent at the PNG renders, you in the OCP CAD Viewer
  (run the part file in VS Code) before accepting.
- Interface tests are the most valuable tests: hole patterns and mating
  faces between parts, especially between a build123d part and a SolidWorks
  part.
- Choose the owner by geometry: build123d for prismatic, parametric,
  repetitive parts; SolidWorks for freeform and complex geometry.
- One decision per commit, with its D number in the message.
- For changes that matter, have a second agent review the first agent's
  geometry: give it the step_diff output and the renders, not the code.
