# CORPUS_LOCK — RGPx Scientist

Lock date: 2026-02-24  
Status: FROZEN (do not edit corpus files in-place)

## What is frozen
This lock freezes the app’s foundational paper corpus and its testable claim-card layer as of 2026-02-24.

Canonical files:
- `phi-mesh/rgpx_scientist/foundational_papers_index.yml`
- `phi-mesh/rgpx_scientist/foundational_papers_manifest.yml`
- `phi-mesh/rgpx_scientist/foundational_claims_index.yml`

The PDFs referenced by `foundational_papers_index.yml` are part of the frozen corpus.
Integrity is enforced by `foundational_papers_manifest.yml` (sha256 + bytes + pages).

## Enforcement rule (hard stop)
On app startup, the corpus verifier MUST:
1) check every listed PDF exists at the indexed repo path
2) verify `bytes` and `sha256` match the manifest
3) (optional) verify `pages` match the manifest

If any check fails, the app must refuse to run in “frozen mode” and report the failing `paper_id` and field mismatch.

## What counts as a change
Any of the following constitutes a NEW CORPUS VERSION and requires a new lock:
- modifying any PDF (even metadata)
- renaming/moving a PDF
- adding/removing a paper from `foundational_papers_index.yml`
- changing `sha256`, `bytes`, or `pages` in the manifest
- editing claim cards in `foundational_claims_index.yml`

## How to make updates (do not break provenance)
Do not mutate the frozen corpus. Instead:
- create a new corpus lock file (e.g. `CORPUS_LOCK_YYYY-MM-DD.md`)
- update index/manifest/claims together in one commit
- optionally move prior PDFs to an archive folder, but keep prior lock files intact

## Notes
- Paper versions (v1.0/v1.1/v1.2 etc.) are treated as distinct artifacts if included. If a version is not in the index+manifest, it is out-of-scope for the app.
- The manifest is the source of truth for verification; Zenodo DOIs are reference/backup, not integrity anchors.
- This lock supersedes prior locks for current app verification, while preserving prior lock files for provenance.

Signed: Marcus (Participant 0) / RGPx Scientist
