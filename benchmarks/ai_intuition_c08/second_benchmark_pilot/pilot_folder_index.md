# Pilot folder index

## Purpose of this folder
This folder is the working pilot artifact set for the second benchmark pass on the DDXPlus 48-item diagnosis-only subset. It preserves the pilot’s spec, run outputs, and prompt-policy decisions in one place so prompt and evaluation changes stay auditable. The current operational direction is to keep a minimal answer-only scaffold plus explicit anti-overcall wording, with guardrail checks available before reruns.

## Operationally active files
- `pilot_prompt_policy_note.md` — locked prompt-policy decision note defining the current default contract and wording to keep/avoid.
- `pilot_status_checkpoint.md` — status checkpoint file for the active pilot workflow (treat as active tracking input when present in the working set).
- `pilot_rerun_safety_note.md` — quick reference for what is safe to rerun versus artifacts that must not be hand-edited.
- `prompt_policy.py` — operational prompt-construction module used by policy checks/runners (referenced by smoke-check notes).
- `check_prompt_policy.py` — fast local guardrail script that validates the operational prompt contract and anti-overcall toggle behavior.
- `prompt_policy_smoke_test_note.md` — smoke-check intent and boundary note (what is validated and what was intentionally not rerun).
- `run_minimal_scaffold_followup.py` — follow-up runner for minimal answer-only scaffold behavior on the pilot manifest.
- `run_anti_overcall_stability.py` — paired-run stability runner for with/without anti-overcall behavior.
- `run_anti_overcall_ablation.py` — anti-overcall ablation runner used for policy comparison tracking in the active workflow.

## Historical comparison artifacts
These files are historical comparison artifacts used to justify the current direction; they are **not** the locked operational default by themselves.
In particular, `run_first_ablation.py` is a historical comparison runner and must not be treated as the locked operational default prompt policy; operational reruns should follow `pilot_prompt_policy_note.md` and use the operational runners listed above.

- `run_first_ablation.py` — first ablation runner that established baseline vs scaffold comparison on the recovered pilot state.
- `first_ablation_metrics.json` — quantitative results from the first ablation comparison arms.
- `first_ablation_report.md` — narrative summary of first-ablation outcomes and interpretation.
- `ablation_error_pattern_note.md` — error-pattern decomposition note that motivated the minimal-scaffold + anti-overcall follow-up.

## Deferred / closed paths
Expanded-pool work is currently a deferred/closed path. Committed provenance and decision notes record that expanded-pool artifacts were not recoverable from local git refs/reflog/unreachable objects, and the recommended path is to proceed with the preserved second_benchmark_pilot baseline only. Treat expanded-pool reconstruction as optional future work, not an active dependency for current pilot prompt-policy and guardrail execution.

## Suggested reading order
1. `pilot_prompt_policy_note.md` (current locked operational policy)
2. `prompt_policy_smoke_test_note.md` + `check_prompt_policy.py` (guardrail behavior)
3. `run_minimal_scaffold_followup.py` and `run_anti_overcall_stability.py` (active runner logic)
4. `first_ablation_report.md` + `ablation_error_pattern_note.md` (historical rationale)
5. `expanded_pool_provenance_note.md` + `expanded_pool_decision_note.md` (closed/deferred branch context)

## Merge/use guidance
Use `pilot_prompt_policy_note.md`, `prompt_policy.py`, and runner scripts as policy/runner inputs; treat `*_metrics.json` and `*_report.md` as generated outputs; and treat `*_note.md` decision/provenance documents as governance context for why the current default is locked.
