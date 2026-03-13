# First ablation report (DDXPlus pilot)

This is the **first real-model ablation from the recovered pilot state** (worktree at/after commit `a766574`) on the cleaned DDXPlus pilot manifest.

## Runtime compatibility fix applied
- Implemented a robust Responses API JSON extractor in `run_first_ablation.py` that accepts either `output_text` or segmented `output[].content[].text` payloads, preventing runtime breakage from response-shape variance.

## Compact metrics (n=48)
- baseline: 15/48 = **0.3125**
- scaffold without label normalization: 9/48 = **0.1875**
- scaffold with label normalization: 9/48 = **0.1875**

## Gain decomposition
- scaffold gain vs baseline: **-0.1250**
- normalization gain vs scaffold-no-norm: **+0.0000**

## Interpretation on DDXPlus pilot
Observed gains are mixed; treat as provisional on this pilot.
