# Expanded-Pool Decision Note

## Current status
The expanded-pool artifacts (`pilot_manifest_expanded_pool.json` and `expanded_pool_note.md`) are not recoverable from reachable refs, reflog commits, or unreachable local git objects, so there is no commit to cherry-pick and no byte-identity path to verify against prior claims; in parallel, the pilot folder remains spec-complete but source-ingestion dependent, meaning expanded-pool work cannot progress without either rerunning the original generation workflow or explicitly closing the path as unrecoverable and moving forward with the preserved pilot baseline.

## Option A: Recreate expanded pool
Re-run the original expanded-pool generation workflow and regenerate both missing artifacts at their expected paths, then continue downstream review/ablation planning from that rebuilt state.

### Risks (Option A)
- Reproducibility risk: if original source inputs/config versions are unavailable, regenerated outputs may not match prior internal assumptions.
- Time risk: regeneration and validation add delay before benchmark planning can proceed.
- Scope-creep risk: rebuilding may pull the team back into data/ingestion work that is currently blocked elsewhere.
- Provenance ambiguity risk: even with regenerated files, historical continuity with the missing prior artifacts remains inferential, not exact.

## Option B: Abandon expanded pool
Formally close the expanded-pool track as unrecoverable in local git provenance and continue only with currently preserved pilot artifacts and existing second-benchmark plan.

### Risks (Option B)
- Coverage risk: potential diversity/volume benefits expected from the expanded pool will not materialize.
- Stakeholder expectation risk: prior assumptions about expanded-pool availability may need re-alignment.
- Future restart cost: if expanded-pool value is reconsidered later, recreation work is only deferred, not eliminated.

## Recommended path
Recommend **Option B (abandon expanded pool)** for now. The provenance result is definitive for current local git state, and the project already has a preserved, reviewable pilot baseline; treating expanded pool as a closed branch reduces uncertainty and prevents additional schedule drag from a low-confidence reconstruction effort.

## Exact next action for tomorrow
Open a planning update and record this decision as: **“Expanded pool abandoned due to unrecoverable git provenance; proceed with second_benchmark_pilot baseline artifacts only.”** Then update the active task board to remove expanded-pool dependencies from near-term benchmark planning.
