# c08 AI-intuition scoring report

**Run timestamp:** {{timestamp}}

> ⚠️ This run uses mock outputs (`sample_outputs_baseline.jsonl`, `sample_outputs_scaffold.jsonl`).
> Scores below are **pipeline-validation scores only** and are **not benchmark performance claims**.

## Compact summary

| System | Diagnosis correctness | Unstable-transition detection | Probe informativeness | Length ratio vs baseline |
|---|---:|---:|---:|---:|
| Baseline | {{baseline_diagnosis}} | {{baseline_unstable}} | {{baseline_probe}} | 1.000 |
| Scaffold | {{scaffold_diagnosis}} | {{scaffold_unstable}} | {{scaffold_probe}} | {{scaffold_length_ratio}} |
| Δ (Scaffold - Baseline) | {{delta_diagnosis}} | {{delta_unstable}} | {{delta_probe}} | {{delta_length_ratio}} |

## Temporary simplifications used in this scoring layer

- Diagnosis correctness: substring match against `primary_diagnosis` and accepted synonyms.
- Unstable-transition detection: lexical overlap between predicted transition flags and `gold_transitions`.
- Probe informativeness: lexical overlap between probe content and accepted probe targets/examples.
- Length ratio: token-count ratio as a placeholder for compute/cost overhead.

These choices are deterministic and inspectable, but intentionally lightweight until real model outputs are available.

## Per-case notes (preview)

{{per_case_preview}}
