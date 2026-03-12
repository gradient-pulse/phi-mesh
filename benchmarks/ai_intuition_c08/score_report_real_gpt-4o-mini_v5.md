# c08 AI-intuition scoring report

**Run timestamp:** 2026-03-12T08:34:09.837291+00:00

> ⚠️ This run uses mock outputs (`sample_outputs_baseline.jsonl`, `sample_outputs_scaffold.jsonl`).
> Scores below are **pipeline-validation scores only** and are **not benchmark performance claims**.

## Compact summary

| System | Diagnosis correctness | Unstable-transition detection | Probe informativeness | Length ratio vs baseline |
|---|---:|---:|---:|---:|
| Baseline | 0.583 | 0.000 | 0.000 | 1.000 |
| Scaffold | 0.833 | 0.194 | 0.028 | 11.974 |
| Δ (Scaffold - Baseline) | 0.250 | 0.194 | 0.028 | 10.974 |

## Temporary simplifications used in this scoring layer

- Diagnosis correctness: substring match against `primary_diagnosis` and accepted synonyms.
- Unstable-transition detection: lexical overlap between predicted transition flags and `gold_transitions`.
- Probe informativeness: lexical overlap between probe content and accepted probe targets/examples.
- Length ratio: token-count ratio as a placeholder for compute/cost overhead.

These choices are deterministic and inspectable, but intentionally lightweight until real model outputs are available.

## Per-case notes (preview)

- `c08_001`: diag=1.000, unstable=0.000, probe=0.000, tokens=40
- `c08_002`: diag=1.000, unstable=0.000, probe=0.167, tokens=34
- `c08_003`: diag=1.000, unstable=0.000, probe=0.000, tokens=33
- `c08_004`: diag=1.000, unstable=0.667, probe=0.000, tokens=42
- `c08_005`: diag=1.000, unstable=0.333, probe=0.000, tokens=39
