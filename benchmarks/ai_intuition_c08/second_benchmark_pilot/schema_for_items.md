# Schema for pilot items

This schema defines the expected item shape for `second_benchmark_pilot` manifests.

## JSON object shape (per item)

```json
{
  "item_id": "pilot_usmle_0001",
  "source_dataset": "string",
  "source_split": "string",
  "source_item_id": "string",
  "question_stem": "string",
  "options": {
    "A": "string",
    "B": "string",
    "C": "string",
    "D": "string",
    "E": "string"
  },
  "correct_option": "A",
  "option_to_label": {
    "A": "canonical diagnosis label",
    "B": "canonical diagnosis label",
    "C": "canonical diagnosis label",
    "D": "canonical diagnosis label",
    "E": "canonical diagnosis label"
  },
  "gold_canonical_label": "canonical diagnosis label",
  "allowed_canonical_labels_strict": ["canonical diagnosis label"],
  "slice_tags_primary": "syndrome_first",
  "slice_tags_secondary": ["etiology_specific"],
  "tagging_rationale": "required if syndrome_qualifier or high_label_variation present",
  "ingestion_notes": "string"
}
```

## Field constraints
- `item_id`: unique within pilot manifest.
- `options`: should include all present option keys from source item; for USMLE-style items this is typically A-E.
- `correct_option`: must be one key present in `options`.
- `option_to_label`: must include exactly the same keys as `options`.
- `gold_canonical_label`: must equal `option_to_label[correct_option]`.
- `allowed_canonical_labels_strict`: non-empty list; normally one label; small pre-approved equivalent set allowed.
- `slice_tags_primary`: exactly one of:
  - `syndrome_first`
  - `etiology_specific`
  - `syndrome_qualifier`
  - `high_label_variation`
- `slice_tags_secondary`: optional zero-or-more tags from same controlled set.
- `tagging_rationale`: required non-empty string when either primary or any secondary tag is `syndrome_qualifier` or `high_label_variation`.

## Manifest-level constraints
- Manifest contains top-level metadata and an `items` array.
- No duplicate `item_id`.
- No exact duplicate `question_stem` + `gold_canonical_label` pairs.
- Pilot build target: 48 items (minimum 40).
- Coverage target: at least 8 items in each required slice tag (overlap allowed).
