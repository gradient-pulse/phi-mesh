# c08 v5 generalization hypothesis note

## Quick read
v5’s gains look **partly generalizable**, but mostly on **format/commitment-sensitive diagnostic framing**, not broad reasoning depth. In this 12-case set, scaffold diagnosis improves where baseline under-commits or drifts from benchmark-canonical target (notably c08_004, c08_007, c08_008), while clearly etiologic-ambiguity-heavy labeling (c08_010) still fails. This suggests a plausible transfer path to other benchmarks with similar syndrome-vs-etiology and naming-friction patterns, but weaker transfer to truly novel differential reasoning tasks.

## Task-pattern table (12 cases)

| task type | case_ids | observed scaffold benefit | likely mechanism | confidence |
|---|---|---|---|---|
| Acute syndrome recognition (high-signal triad) | c08_001, c08_004, c08_005, c08_006, c08_009 | Net positive (major lift in c08_004; others mostly stable) | **Diagnosis commitment** (forces syndrome-level commitment when physiology is explicit), with some **transition framing** helping prioritize acute decompensation cues | High |
| Label normalization / canonical naming | c08_007, c08_008, c08_011, c08_012 | Positive mainly on c08_007/c08_008; c08_011 stable; c08_012 already baseline-correct by synonym | **Anti-drift normalization** (reduce paraphrase/specificity mismatch vs scorer labels) | High |
| Ambiguity under competing diagnoses (syndrome vs fixed etiology) | c08_003, c08_010 | Little/no gain; c08_010 remains wrong | Missing/insufficient **uncertainty-preserving commitment**; scaffold still overcommits to a single etiology instead of syndrome-first target | High |
| Progression / transition-sensitive cases | c08_004, c08_006, c08_011 | Mild support; clearest practical help in c08_004 framing severity state | **Transition framing** surfaces instability and keeps acute-state reasoning coherent, but not clearly the primary source of diagnosis gain | Medium |
| Probe-sensitive cases (where next question could disambiguate) | c08_001, c08_002, c08_003, c08_008, c08_010 | Weak observed impact on final diagnosis in this run | **Probe structure** present but low-yield for scored endpoint (diagnosis string), given probe score remains low | Medium |

## Is this likely benchmark-specific?
- **Likely benchmark-coupled component:** the gain magnitude is strongly tied to canonical label alignment and substring scoring behavior.
- **Likely portable component:** diagnosis-first commitment can help in other short clinical vignettes where baseline answers drift to risk factor/etiology labels instead of target syndrome.
- **Main risk to generalization:** when tasks require calibrated ambiguity (e.g., “obstructive jaundice, suspected X”), scaffold may still over-specify and lose.

## Single best next experiment (beyond c08)
Run an **out-of-set cross-benchmark ablation** on a different vignette benchmark (same model, same decoding):
1) baseline,
2) scaffold **without** label normalizer,
3) scaffold **with** label normalizer,
then report per-task-type deltas (especially syndrome-vs-etiology ambiguity cases).  

If gains persist in (2), that supports real reasoning transfer; if gains appear mainly in (3), improvement is mostly benchmark-label alignment.
