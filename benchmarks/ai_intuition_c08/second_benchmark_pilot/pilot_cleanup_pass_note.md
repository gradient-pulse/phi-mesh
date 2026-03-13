# DDXPlus Pilot Cleanup Pass Note

## What was changed
- Filled previously blank `tagging_rationale` fields for 10 high-priority items.
- Reworded stems for the same 10 items plus 2 additional targeted items to make the prompt structure clearer (explicitly framing them as coded-evidence vignettes while preserving all original evidence codes and diagnosis intent).
- Replaced clearly implausible distractors in 2 items:
  - `pilot_ddxplus_0037`: removed distractors like food-poisoning/allergy-style outliers and swapped in more plausible cardiothoracic alternatives.
  - `pilot_ddxplus_0047`: replaced `Atrial fibrillation` with `Viral pharyngitis` for a pediatric respiratory item.

## How many items were touched
- **12 items total** in `pilot_manifest_draft.json`.

## What was intentionally left unchanged
- No benchmark code or execution logic was modified.
- No item IDs, correct options, canonical label constraints, slice tags, or ingestion notes were changed.
- Most items were intentionally left untouched to keep this pass narrow and avoid a rebuild.
- No cache/raw artifact folders were added or staged.

## Readiness for first ablation run
- **Yes — ready with caution.** The highest-value manifest-level issues from the pilot adjudication (blank rationales, a small number of implausible distractors, and weak stem phrasing in targeted items) were addressed without broad restructuring.
