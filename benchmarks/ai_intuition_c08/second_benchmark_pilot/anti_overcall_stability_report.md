# Anti-overcall stability report (DDXPlus pilot)

## Setup summary
- Manifest: `benchmarks/ai_intuition_c08/second_benchmark_pilot/pilot_manifest_draft.json` (48 items)
- Model: `gpt-4o-mini`
- Repeats per arm: 3
- Arms compared:
  - minimal scaffold without anti-overcall
  - minimal scaffold with anti-overcall

## Per-run accuracies
- Run 1: without=0.2292, with=0.3542, delta=+0.1250
- Run 2: without=0.2500, with=0.3542, delta=+0.1042
- Run 3: without=0.2917, with=0.3958, delta=+0.1042

## Means
- Mean accuracy (without anti-overcall): **0.2569**
- Mean accuracy (with anti-overcall): **0.3681**
- Mean delta (with - without): **+0.1111**

## Stability call
- Stable enough to keep anti-overcall as default pilot instruction? **Yes — anti-overcall shows a consistent positive delta across all repeated runs.**

## Recommended next action
- Run the same 3x/arm protocol on a second disjoint 48-item slice to confirm transfer stability before freezing defaults.
