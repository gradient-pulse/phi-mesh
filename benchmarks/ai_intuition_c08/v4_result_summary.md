# c08 benchmark v4 result summary

## What changed conceptually in v4
The scaffold prompt was tightened around a diagnosis-first strategy with explicit anti-drift constraints and hard brevity caps. In practice, this means prioritizing a single benchmark-style diagnosis label, reducing etiologic/mechanistic expansion unless explicitly required by the case label, and constraining scaffold fields to shorter, more selective outputs.

## Compact score summary (gpt-4o-mini)
- Baseline diagnosis: **0.583**
- Scaffold diagnosis: **0.667**
- Scaffold unstable-transition: **0.222**
- Scaffold probe: **0.042**
- Scaffold length ratio: **11.947**

## Current status
v4 is currently the best scaffold prompt version in this c08 run series based on diagnosis and unstable-transition performance while materially reducing length ratio versus prior scaffold runs.

## Scope caveat
These are benchmark-internal, run-specific results for the **gpt-4o-mini** configuration and should not be treated as broad, model-independent performance claims.
