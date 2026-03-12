# Second benchmark ingestion & filtering spec (USMLE-style clinical vignette MCQ, diagnosis-only)

## Scope
Define a reproducible pipeline for constructing an out-of-set USMLE-style vignette subset for cross-benchmark ablation with the c08 setup.

## 1) Eligible source item types
Include only items that satisfy all conditions:
- Clinical vignette question stem with enough patient context to infer a diagnosis.
- Single-best-answer MCQ format with one keyed correct option.
- Target label is a **diagnosis** (disease, syndrome, pathologic condition, or named clinical entity).
- English-language item text with readable stem and options.
- No duplicated stem/answer pair within this benchmark subset.

## 2) Excluded item types
Exclude any item with one or more of the following:
- Primary task is treatment/management, next step, diagnostic test selection, prognosis, epidemiology, or mechanism (rather than diagnosis).
- Multi-select questions, assertion-reason formats, or items with multiple simultaneously correct answers.
- Image-dependent items (radiology/pathology/ECG/photo) unless the image content is fully restated in text.
- Items where diagnosis depends on unavailable external context.
- Items with ambiguous or contested answer key after review.
- Near-duplicate items (same core case pattern and same diagnosis wording).

## 3) Diagnosis-only filtering rules
Apply this sequence:
1. **Question intent gate**: keep only stems whose explicit ask is the most likely diagnosis / most likely condition / best diagnosis equivalent.
2. **Answer-key gate**: keyed answer must be diagnostic label, not a test or intervention.
3. **Single-primary-label gate**: map to one canonical diagnosis label (see scoring section); if multiple primary diagnoses are required, exclude.
4. **Text sufficiency gate**: confirm the stem alone (plus options for MCQ condition) provides enough information for diagnosis.

## 4) MCQ options vs free-form model outputs
For cross-benchmark comparability, support both views:
- **MCQ-constrained view (auxiliary)**: model chooses A/B/C/D/E option.
- **Diagnosis-text view (primary)**: model outputs a diagnosis string only.

Normalization policy:
- For each item, store `option_to_label` mapping from each option to canonical diagnosis label.
- If model output is an option token/letter, convert via `option_to_label`.
- If model output is diagnosis text, normalize text to canonical label via the scoring dictionaries.
- If output includes explanation text, parse first explicit diagnosis span; if no diagnosis span is detectable, mark invalid.

## 5) Strict canonical scoring
Define per-item fields:
- `gold_canonical_label`
- `allowed_canonical_labels_strict` (normally one label; optional small set only for pre-specified equivalent canonical forms)

Scoring rule:
- Prediction is correct iff normalized predicted canonical label exactly matches one member of `allowed_canonical_labels_strict`.
- No partial credit.
- Invalid/empty/unmapped outputs score incorrect.

## 6) Synonym-tolerant scoring
Define global dictionary:
- `canonical_label -> accepted_surface_forms[]` (abbreviations, spelling variants, common synonymous names).

Scoring rule:
- Map prediction text to canonical label by dictionary lookup (case-insensitive, punctuation-insensitive, whitespace-normalized).
- If mapped canonical label equals `gold_canonical_label`, score correct.
- If multiple canonical labels match same prediction string, resolve by pre-registered priority; unresolved collisions are scored incorrect and logged.

Governance:
- Freeze synonym dictionary before arm comparison runs.
- Record all unmatched frequent predictions for post-hoc audit only (no mid-run dictionary edits).

## 7) Required slice tags
Tag each retained item with one primary slice (and optional secondary tags):

- `syndrome_first`: gold is syndrome-level label without fixed etiology requirement (e.g., nephritic syndrome).
- `etiology_specific`: gold requires causal/pathogen/entity-level specificity (e.g., diagnosis with specific organism/genetic etiology).
- `syndrome_qualifier`: gold requires syndrome + qualifier/temporal/probabilistic modifier to be considered fully correct.
- `high_label_variation`: diagnosis has known high wording diversity (multiple common aliases/abbreviations), independent of clinical difficulty.

Tagging process:
- Two-pass manual tagging with adjudication for disagreements.
- Maintain a short written rationale per item for `syndrome_qualifier` and `high_label_variation` tags to improve reproducibility.

## 8) Dataset size targets for first ablation
Minimum target constraints:
- Total retained items: **>= 40**.
- Per required slice: target **>= 8** items each (overlap allowed, but ensure each slice has adequate standalone representation).

Recommended endpoint values:
- **Recommended minimal pilot size: 48 items.**
- **Recommended full first-pass size: 96 items.**
