# Source ingestion readiness checklist (second benchmark pilot)

## What is already ready
- Pilot scope is fixed to **USMLE-style clinical vignette MCQ, diagnosis-only**.
- Inclusion/exclusion and diagnosis-only filtering gates are defined.
- Item schema and manifest-level constraints are defined.
- Pilot size and slice coverage targets are defined (target 48, minimum 40; 4 required primary slice families).
- Empty pilot manifest scaffold exists with ingestion status flags set to not approved/not completed.

## What is still blocked
- External source ingestion approval is not yet granted.
- No source rows are imported yet, so item population cannot begin.
- Canonical synonym dictionary freeze cannot be finalized before seeing real source label surface forms.
- Inter-reviewer tagging adjudication log cannot be produced before real items are tagged.
- Dedup/near-dedup report cannot be produced before source rows are available.

## Source characteristics to confirm before ingestion
Confirm all of the following on the selected source export **before** import:
1. License/terms permit this benchmark construction workflow.
2. Data includes vignette-style clinical stems and MCQ options with a single keyed correct answer.
3. A sufficient diagnosis-only subset is available after filtering (enough to achieve 48 target items, with 40 minimum fallback).
4. Question intent can be reliably filtered to diagnosis asks ("most likely diagnosis/condition" equivalents).
5. Correct option can be mapped to one canonical diagnosis label per retained item.
6. Items are text-sufficient (no required image-only evidence or missing context).
7. Source has stable identifiers needed for traceability (`source_dataset`, `source_split`, `source_item_id`).

## Minimum metadata that must accompany the source
At ingestion time, require at least:
- `source_dataset` name/version identifier.
- `source_split` (or explicit equivalent partition field).
- `source_item_id` stable per-item identifier.
- `question_stem` text.
- `options` map (A/B/C/D/E or source-native keys).
- `correct_option` key.
- A reproducible export stamp (date/time and export method note) recorded in ingestion notes.

## What the first ingestion pass should produce
The first pass should produce a **populated pilot manifest draft** that includes:
- Retained diagnosis-only candidate items with required schema fields filled.
- Canonical label mapping per option (`option_to_label`) and `gold_canonical_label`.
- Initial strict-accepted label set (`allowed_canonical_labels_strict`).
- Primary slice tag per item plus secondary tags where applicable.
- Required tagging rationale for `syndrome_qualifier` / `high_label_variation` tagged items.
- Initial dedup/near-dedup decisions and concise `ingestion_notes` per item.

## Validation checks to run immediately after ingestion
Run these checks immediately on the first populated manifest draft:
1. **Schema validation**: all required fields present and correctly typed.
2. **Key consistency**: `correct_option` exists in `options`; `option_to_label` keys match `options` keys exactly.
3. **Gold consistency**: `gold_canonical_label == option_to_label[correct_option]`.
4. **Strict label validity**: `allowed_canonical_labels_strict` is non-empty and contains the gold label.
5. **Primary slice validity**: exactly one valid primary tag per item.
6. **Rationale requirement**: non-empty `tagging_rationale` whenever `syndrome_qualifier` or `high_label_variation` appears in primary/secondary tags.
7. **Uniqueness/dedup**: no duplicate `item_id`; no exact duplicate `question_stem + gold_canonical_label`; near-duplicates reviewed.
8. **Coverage check**: count items overall (target 48, minimum 40) and verify required slice coverage thresholds are on track.
9. **Traceability check**: every item has non-empty source provenance metadata (`source_dataset`, `source_split`, `source_item_id`).

## Go / No-Go checklist for ingestion approval
Mark **Go** only if every item below is true:
- [ ] External ingestion approval is explicitly granted.
- [ ] Source license/terms are confirmed compatible.
- [ ] Source export includes required provenance + MCQ fields.
- [ ] Diagnosis-only filtering feasibility is confirmed on sample rows.
- [ ] Single-primary canonical label mapping is feasible for retained items.
- [ ] Text sufficiency is acceptable (no required image/context gaps).
- [ ] Expected retained volume is sufficient for pilot target (48; minimum 40).
- [ ] Post-ingestion validation procedure is prepared and ready to run immediately.

If any box remains unchecked, decision is **No-Go**.
