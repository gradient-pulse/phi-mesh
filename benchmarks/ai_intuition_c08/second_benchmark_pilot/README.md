# second_benchmark_pilot

Pilot artifact set for the **post-c08-v5 cross-benchmark ablation** using the recommended second benchmark type:
**USMLE-style clinical vignette MCQ (diagnosis-only subset)**.

See codex_session_wrapup_2026-03-15.md for the closure note on the post-merge Codex repair cycle around pilot_folder_index.md.
https://github.com/gradient-pulse/phi-mesh/blob/main/benchmarks/ai_intuition_c08/second_benchmark_pilot/codex_session_wrapup_2026-03-15.md

This folder intentionally contains **spec-first artifacts** (no benchmark code changes, no source data copy) so we can lock scope before full ingestion.

## Contents
- `pilot_subset_spec.md` — pilot construction rules and blocking dependencies.
- `schema_for_items.md` — required item-level schema for future ingested items.
- `empty_manifest.json` — valid placeholder manifest for pilot items.

## Pilot goal
Build the **first pilot subset** with a target of **48 items** (recommended minimal pilot size in the ingestion spec), while preserving required slice coverage and strict diagnosis-only filtering.

## Current status
- Spec and schema are ready.
- Manifest scaffold is ready.
- Item population is blocked until an approved external USMLE-style source dataset is ingested.
