# c08 benchmark v5 result summary

## What changed conceptually in v5
The scaffold retained the v4 diagnosis-first strategy, anti-drift constraints, and brevity caps, and added a minimal post-generation normalization step for scaffold `answer` labels to reduce benchmark-label drift while preserving schema and scorer behavior.

## Compact score summary (gpt-4o-mini)
- Baseline diagnosis: **0.583**
- Scaffold diagnosis: **0.833**
- Scaffold unstable-transition: **0.194**
- Scaffold probe: **0.028**
- Scaffold length ratio: **11.974**

## Current status
v5 is currently the best scaffold prompt/version checkpoint in this c08 run series based on diagnosis correctness.

## Scope caveat
These are benchmark-internal, run-specific results for the **gpt-4o-mini** configuration and should not be treated as broad, model-independent performance claims.
