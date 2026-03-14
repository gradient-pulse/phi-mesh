# Pilot rerun safety note

## Safe to rerun
The following scripts are safe to rerun as process checks or controlled reruns when needed:
- `run_first_ablation.py`
- `run_minimal_scaffold_followup.py`
- `run_anti_overcall_ablation.py`
- `run_anti_overcall_stability.py`
- `check_prompt_policy.py`

## Generated outputs — do not hand-edit
Treat generated metrics and reports as run artifacts. Do not hand-edit generated JSON/Markdown outputs; replace them only by rerunning the corresponding script when a justified rerun is approved.

## Documentation / governance only
Notes, checklists, and governance documents in this folder may be updated manually for clarity, provenance, and decision tracking, as long as they do not claim regenerated results unless a real rerun occurred.

## Practical rule
If a file is a generated metric/report, regenerate it via script or leave it untouched; if a file is documentation, edit it directly with a brief, auditable note.
