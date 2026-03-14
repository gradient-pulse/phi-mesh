# Minimal scaffold follow-up report (DDXPlus pilot)

This artifact captures the minimal-scaffold follow-up requested after the first three-arm ablation.

## Prompt variant tested
- Output schema constrained to `{'answer': '<exact option label>'}` only.
- No rationale/confidence fields allowed.
- Added anti-overcall instruction against unjustified severe/cardiac choices.

## Results (n=48)
- minimal scaffold follow-up: 16/48 = **0.3333**
- baseline reference: **0.3125**
- gain vs baseline: **+0.0208**

## Notes
- Source manifest: `pilot_manifest_draft.json`.
- This run does not modify benchmark core code; it only emits follow-up artifacts.
