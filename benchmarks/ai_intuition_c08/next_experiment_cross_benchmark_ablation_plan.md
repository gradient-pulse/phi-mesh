# Next experiment plan: cross-benchmark ablation after c08 v5

## Objective
Test whether c08 v5 gains are mostly from (a) general scaffolded diagnostic reasoning behavior or (b) benchmark-specific diagnosis-label normalization/alignment.

## Experimental arms
Use the same model and decoding settings across all arms.

1. **Baseline**
   - Current baseline prompt (no scaffold).
2. **Scaffold without label normalization**
   - v5 scaffold structure (diagnosis-first, anti-drift, brevity), but remove final canonical label normalization step.
3. **Scaffold with label normalization**
   - Full v5 scaffold, including canonical diagnosis label normalization.

## Dataset/task selection criteria (second benchmark)
Choose a **different short clinical vignette benchmark** (not c08) with case-level gold diagnoses.

Required properties:
- **Out-of-set content**: no c08 cases/prompts reused.
- **Same task form**: single primary diagnosis output from short vignette-style inputs.
- **Sufficient size**: enough cases for stable per-slice comparisons (target >=40 cases).
- **Heterogeneous case slices** with explicit tagging or easy manual tagging for:
  - syndrome-first labels,
  - etiology-specific labels,
  - syndrome+qualifier labels (e.g., “X, likely Y”),
  - high synonym/wording variability.
- **Gold labels + accepted synonyms** (or enough metadata to construct a strict and a synonym-tolerant scorer).

What to avoid:
- Benchmarks that are mostly free-response explanations with no clear primary diagnosis target.
- Tasks requiring long multi-step management plans as primary score target.
- Datasets with heavy overlap/leakage from c08 wording.
- Evaluation setups where only exact-string match is possible and no synonym policy can be defined.

## Evaluation logic
### Primary comparisons
- Diagnosis accuracy (strict canonical).
- Diagnosis accuracy (synonym-tolerant).
- Delta vs baseline for each arm.

### Slice comparisons (required)
Report per-slice deltas for:
- syndrome-first,
- etiology-specific,
- syndrome+qualifier,
- high-label-variation cases.

### Attribution test: label-alignment vs scaffold gain
Use this decision logic:
- If **Arm 2 > Baseline** on synonym-tolerant scoring and across multiple slices, that supports **general scaffold gain**.
- If **Arm 3 >> Arm 2** mainly on strict scoring, especially in high-label-variation slices, that supports **label-normalization/alignment gain**.
- If Arm 2 gains disappear on syndrome+qualifier ambiguity slices, scaffold is likely still overcommitting (known c08 failure mode).

## Failure modes to watch
- **Overcommitment to fixed etiology** where syndrome+uncertainty is gold.
- **Qualifier loss** (“likely”, timing words like peripartum/postpartum distinctions).
- **Apparent gain only from string normalization** without synonym-tolerant improvement.
- **Slice imbalance** causing misleading aggregate gains.
- **Prompt-length side effects** (verbosity increasing with no diagnosis benefit).

## Single clearest success criterion
The strongest evidence of genuine transfer is:

> **Arm 2 (scaffold without normalization) shows a meaningful and repeatable improvement over baseline on synonym-tolerant diagnosis accuracy, including syndrome+qualifier ambiguity slices, on the out-of-set benchmark.**

If this is not met and gains are concentrated in Arm 3 strict scoring, treat v5 improvement as primarily label-alignment.
