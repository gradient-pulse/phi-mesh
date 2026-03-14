# DDXPlus first ablation: error-pattern note

## Compact bucket summary (item-level, n=48)

Using `first_ablation_metrics.json` item rows across all three arms (`baseline`, `scaffold_no_norm`, `scaffold_with_norm`):

- **Baseline correct, both scaffold arms wrong:** **7** (14.6%)
- **Scaffold correct, baseline wrong:** **1** (2.1%)
- **All three wrong:** **32** (66.7%)
- **All three correct:** **8** (16.7%)

This decomposition matches top-line accuracy gaps:
- baseline: **15/48 = 0.3125**
- scaffold (no norm): **9/48 = 0.1875**
- scaffold (with norm): **9/48 = 0.1875**

## Representative items (most informative buckets)

| Bucket | Item | Gold | Baseline | Scaffold (both variants) | Why this is informative |
|---|---|---|---|---|---|
| baseline-only | `pilot_ddxplus_0010` | Anaphylaxis | **Anaphylaxis** ✅ | Acute pulmonary edema ❌ | Scaffold seems to drift to severe cardiopulmonary interpretation under coded evidence opacity. |
| baseline-only | `pilot_ddxplus_0023` | Myasthenia gravis | **Myasthenia gravis** ✅ | Guillain-Barré syndrome ❌ | Near-neighbor neuro distractor chosen by scaffold; suggests over-commitment after forced rationale step. |
| baseline-only | `pilot_ddxplus_0024` | Bronchiectasis | **Bronchiectasis** ✅ | Pneumonia ❌ | Scaffold biases toward common/high-salience respiratory label when evidence tokens are opaque. |
| baseline-only | `pilot_ddxplus_0037` | Inguinal hernia | **Inguinal hernia** ✅ | Bronchitis ❌ | Cross-system misfire: scaffold moves to familiar respiratory option despite non-respiratory gold. |
| scaffold-only | `pilot_ddxplus_0045` | URTI | Acute rhinosinusitis ❌ | **URTI** ✅ | Rare scaffold win appears as finer URTI-vs-rhinosinusitis calibration. |
| all-wrong | `pilot_ddxplus_0031` | Boerhaave | Possible NSTEMI / STEMI ❌ | Possible NSTEMI / STEMI ❌ | Shared cardiac-overcall under chest-pain-like distractor structure. |
| all-wrong | `pilot_ddxplus_0033` | GERD | Possible NSTEMI / STEMI ❌ | Possible NSTEMI / STEMI ❌ | Option-set includes multiple cardiac labels; all arms collapse to severity-overcall. |
| all-wrong | `pilot_ddxplus_0015` | Panic attack | Possible NSTEMI / STEMI ❌ | Possible NSTEMI / STEMI ❌ | Strong distractor pull toward acute coronary framing across all prompting styles. |

## Likely causes of baseline > scaffold on this DDXPlus pilot

Most likely explanation is a **stacked interaction** of dataset format + prompt burden:

1. **Coded-vignette opacity dominates signal extraction.**
   Cases are primarily tokenized evidence IDs (`E_...`) rather than natural clinical narratives, limiting the usefulness of extra reasoning scaffolds.
2. **Scaffold overproduction burden hurts answer stability.**
   Requiring `answer + rationale_short + uncertainty` appears to introduce additional generation degrees of freedom and distract from selecting the best option label.
3. **Option-set / label-style mismatch is amplified by scaffolding.**
   Many options are close neighbors (e.g., URTI/rhinosinusitis; neuro/cardiopulmonary confounds). Scaffolded justification likely increases commitment to plausible but wrong neighbor classes.
4. **Distractor structure + severity-overcall pattern persists.**
   Across arms, `Possible NSTEMI / STEMI` is the most frequent predicted label (12/48), indicating a persistent high-severity attractor that scaffolding does not mitigate.
5. **Cardiac-overcall appears systematic, not random.**
   Chest/respiratory/anxiety cases repeatedly collapse into acute cardiac outputs; scaffold prompts do not reduce this tendency and sometimes worsen it by forcing explicit rationale.

## Recommended next experiment (single)

Run **one constrained scaffold variant** on the same manifest (no new dataset):

- Keep scaffold minimal: `{"answer": "<exact option label>"}` only.
- Add explicit anti-overcall instruction: *"Do not favor severe/cardiac options unless uniquely supported by evidence IDs."*
- Add option-pointer constraint: require selecting from the provided option strings verbatim (no free-form diagnosis wording).

This isolates whether baseline advantage is caused primarily by scaffold output burden vs. latent evidence-opacity limitations.
