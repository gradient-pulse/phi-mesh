# DDXPlus pilot repo state recovery note

## What was found in git history
The expected DDXPlus pilot artifacts are all present in committed history:

- `pilot_manifest_draft.json` — introduced in `3268f82` and later updated in `a766574`.
- `ingestion_stage_counts.json` — introduced in `3268f82`.
- `ingestion_pass_note.md` — introduced in `3268f82`.
- `pilot_content_review_note.md` — introduced in `3268f82`.
- `pilot_adjudication_sample_note.md` — introduced in `cceaf8e`.
- `pilot_semantic_qa_note.md` — introduced in `7a8cc0e`.

## Current presence vs absence (this checkout)
All six expected artifacts are currently **present** in `benchmarks/ai_intuition_c08/second_benchmark_pilot/`.

## Branch/PR/merge status assessment
- Current branch: `work` (HEAD at `a766574`).
- The artifact commits appear in the current branch history and are not deletion-reverted.
- Commit subjects reference PR numbers (`#418`, `#419`, `#422`, `#423`), indicating this work was committed via PR flow and is now in the checked-out branch lineage.

## Most likely reason for the earlier “missing artifacts” observation
Most likely: the earlier environment was on a different/older checkout (or stale working tree) that did not include commits `3268f82` through `a766574`.

## Recommended recovery action
Sync the target working environment to commit `a766574` (or at minimum replay/cherry-pick `3268f82`, `cceaf8e`, `7a8cc0e`, `a766574`) before starting ablation work.
