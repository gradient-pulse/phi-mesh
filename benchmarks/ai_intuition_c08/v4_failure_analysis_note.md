# c08 v4 problematic-case note (failed + regressed only)

Scope: cases where v4 scaffold diagnosis still failed, plus cases where scaffold regressed vs baseline (per committed v4 scoring heuristic).

| case_id | gold label | baseline answer | scaffold answer | failure type | suggested prompt-level remedy |
|---|---|---|---|---|---|
| c08_007 | Hyperthyroidism (likely Graves disease) | Graves' disease | Hyperthyroidism | under-specific answer | Add a rule to retain key qualifier when present in label pattern (`X, likely Y`): include likely etiology when signal is strong (e.g., Graves). |
| c08_008 | Bell palsy | Left-sided facial nerve (CN VII) palsy likely due to viral infection (Bell's palsy) | Left-sided Bell's palsy | label drift | Add a hard canonicalization pass: emit exact benchmark label string when a near-synonym is detected (e.g., normalize `Bell's palsy` -> `Bell palsy`). |
| c08_010 | Obstructive jaundice (suspected pancreatic head malignancy) | Cholangiocarcinoma | Cholangiocarcinoma | etiologic overreach | Add a guardrail: when target label is syndrome-first with uncertainty, forbid jumping to one definitive etiology unless explicitly required. |
| c08_011 | Peripartum cardiomyopathy | Peripartum cardiomyopathy | Postpartum cardiomyopathy | label drift (regression) | Add anti-paraphrase constraint for timing-critical labels: preserve canonical term (`peripartum`) instead of substituting (`postpartum`). |

**Highest-leverage next refinement to test:**
A final "canonical diagnosis label normalizer" step in the scaffold prompt that maps semantically-correct drafts to benchmark-canonical strings, while preserving required qualifiers/timing words (e.g., `likely Graves disease`, `peripartum`, apostrophe-free `Bell palsy`).
