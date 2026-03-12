# Pilot subset specification (first pilot build)

## Benchmark type
USMLE-style clinical vignette MCQ, filtered to **diagnosis-only** items (recommended candidate in shortlist).

## Target pilot size
- **Primary target:** 48 retained items.
- **Hard minimum for pilot readiness:** 40 retained items.
- **Slice coverage target:** at least 8 items per required slice tag (`syndrome_first`, `etiology_specific`, `syndrome_qualifier`, `high_label_variation`), allowing overlap across tags.

## Inclusion rules
Keep only items that satisfy all of the following:
1. English clinical vignette stem with enough patient context for diagnosis.
2. Single-best-answer MCQ with one keyed correct option.
3. Prompt intent is diagnosis ("most likely diagnosis/condition" or equivalent).
4. Keyed answer is a diagnosis label (not test, treatment, management, prognosis, epidemiology, mechanism).
5. Item can be mapped to one canonical diagnosis label for strict scoring.
6. Stem+options provide sufficient textual evidence (no required missing context).

## Exclusion rules
Exclude items if any of these are true:
- Non-diagnosis task focus (management, next test, mechanism, etc.).
- Multi-select / multiple-correct / assertion-reason format.
- Image-dependent with non-textual critical evidence.
- Ambiguous or contested answer key after review.
- Duplicate or near-duplicate case pattern with same diagnosis wording.
- Requires multiple simultaneous primary diagnoses.

## Required fields per item
Each pilot item must include:
- `item_id`
- `source_dataset`
- `source_split`
- `source_item_id`
- `question_stem`
- `options` (A/B/C/D/E style map)
- `correct_option`
- `option_to_label` (option -> canonical diagnosis label)
- `gold_canonical_label`
- `allowed_canonical_labels_strict`
- `slice_tags_primary` (exactly one required primary tag)
- `slice_tags_secondary` (optional list)
- `tagging_rationale` (required when primary or secondary includes `syndrome_qualifier` or `high_label_variation`)
- `ingestion_notes`

Reference structure is specified in `schema_for_items.md`.

## Slice-tagging rules
1. Assign exactly one **primary** slice from:
   - `syndrome_first`
   - `etiology_specific`
   - `syndrome_qualifier`
   - `high_label_variation`
2. Additional slice properties may be added in `slice_tags_secondary`.
3. Perform two-pass tagging with adjudication log for disagreements.
4. For `syndrome_qualifier` and `high_label_variation`, include concise rationale text per item.

## Scoring requirements
### Strict canonical scoring (required)
- Normalize prediction to a canonical diagnosis label.
- Score correct iff normalized label is in `allowed_canonical_labels_strict`.
- No partial credit.
- Invalid/empty/unmapped predictions are incorrect.

### Synonym-tolerant scoring (required)
- Use a frozen global dictionary: `canonical_label -> accepted_surface_forms[]`.
- Case/punctuation/whitespace-insensitive normalization.
- If multiple canonical labels match one prediction surface form, use pre-registered priority; unresolved collision scores incorrect and is logged.
- Do not edit dictionary mid-run; audit unmatched frequent predictions post-run only.

## Build steps for this pilot
1. Acquire approved external USMLE-style source dataset export.
2. Run diagnosis-only filtering gates.
3. Deduplicate and near-deduplicate curation.
4. Canonicalize labels and populate strict field set.
5. Apply slice tagging and rationale annotations.
6. Assemble pilot manifest and validate schema.

## Blocked until source ingestion
The following remain blocked in this first pilot build:
- Actual item population (48 target items) from external USMLE-style dataset.
- Final canonical synonym dictionary freeze based on observed pilot label surface forms.
- Inter-reviewer adjudication log from real item tagging.
- Empirical dedup report against imported source rows.

These require user-approved external data access/ingestion before completion.
