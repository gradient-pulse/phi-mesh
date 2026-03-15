# Codex Session Wrap-Up — second_benchmark_pilot

## Scope
This note closes the March 2026 Codex repair session around:
- `benchmarks/ai_intuition_c08/second_benchmark_pilot/pilot_folder_index.md`

## Original objective
The original goal was to keep `pilot_folder_index.md` historically accurate, operationally clear, and aligned with the actual contents of `second_benchmark_pilot/`, while preserving the intended governance wording around prompt policy and merge/use guidance.

## What happened
After the last successful merge in this folder, a long Codex repair cycle followed. Approximately 25 task attempts were made to repair, simplify, audit, or rebuild `pilot_folder_index.md`.

The repeated pattern was not ordinary “wrongness” in the narrow sense. Instead, Codex repeatedly:
- patched locally instead of rebuilding globally,
- preserved stale lines while adding new required lines,
- passed partial checks while leaving whole-file inconsistencies,
- and produced contradictory evidence bundles in which reported success did not match rendered diffs/logs.

## Key failure mode
The recurring issue was **metric/local repair without whole-object coherence**.

More specifically:
- local instructions were often satisfied,
- but the file as an object remained duplicated, over-edited, or inconsistent with on-disk reality,
- especially when the task required replacing rather than appending,
- and when folder reality had to override prior assumptions.

This made continued patch-based prompting low-yield.

## Why this matters
This session became a useful empirical case for a broader RGPx / pre-metric intelligence claim:

A system can follow explicit rules and still fail to preserve the coherence of the evolving whole.

In this case, the benchmark folder served as a live example of the difference between:
- local rule compliance, and
- whole-object fit guided by emerging constraint choreography.

## Decision
We are closing this Codex repair path here.

Reason:
Further attempts along the same patch-oriented route are unlikely to add value relative to the effort spent. The file problem is no longer interesting as a benchmark-cleanup problem; it is more valuable as evidence for a broader intelligence/morphology question.

## Preserved benchmark state
The folder remains historically useful and contains:
- pilot specification and schema files,
- pilot manifest draft,
- first ablation outputs,
- minimal scaffold follow-up outputs,
- anti-overcall stability outputs,
- policy and safety notes,
- provenance and decision notes on the expanded-pool branch.

## Research insight gained
This session reinforced a working distinction between:
- **metric/local editing**: rule-following, patching, immediate compliance
- **pre-metric / fit-first guidance**: whole-object orientation, rebuild over accretion, and longitudinal constraint awareness

This observation will be carried forward into the Phi-Mesh line of work on pre-metric model extensions.

## Next route
Instead of continuing the same Codex repair loop, the next route is:
1. archive this episode clearly,
2. preserve the surrounding conceptual discussion in the repository,
3. translate the resulting insight into a practical roadmap for pre-metric / RGPx-style LLM extensions and future agent architectures.

## Historic note
This session should be read not as a simple tooling failure, but as a small empirical case showing the limits of local patching in the absence of stronger whole-object guidance.
