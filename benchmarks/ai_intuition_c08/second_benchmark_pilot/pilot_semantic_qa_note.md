# Pilot Semantic QA Note (DDXPlus)

## Overall judgment
Manifest is **mostly usable for a first ablation run**, but it contains a small set of high-risk semantic artifacts (mainly age-incongruent distractors and very opaque stems) that could add non-clinical noise to early results.

## Highest-priority problematic items
- **pilot_ddxplus_0029 (0-year-old, influenza)**: option set includes **HIV (initial infection)**, which is an obviously low-plausibility distractor in this context and may inflate performance through easy elimination.
- **pilot_ddxplus_0030 (9-year-old, influenza)**: again includes **HIV (initial infection)** as a distractor; likely similarly implausible/noisy for pilot ablation signal quality.
- **pilot_ddxplus_0047 (4-year-old, bronchitis)**: includes **Atrial fibrillation** as a distractor, which is clinically atypical at this age and may function as a trivial reject option rather than a meaningful alternative.
- **Global stem readability issue (all items)**: stems are heavily code-token based (`E_*`, `V_*`) and may be too opaque for meaningful semantic discrimination; this risks measuring tolerance to encoding artifacts more than diagnosis reasoning.

## Acceptable for first ablation run?
**Yes, conditionally.** Acceptable if treated as a pilot/noise-tolerant run and interpreted with caution around distractor-quality effects.

## Recommended next action
Before broader use, run a **quick distractor plausibility scrub** on pediatric items (at minimum removing obviously age-incongruent options) and optionally add a lightweight evidence-token glossary to reduce stem opacity impact.
