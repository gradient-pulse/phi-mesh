# DDXPlus pilot ingestion pass note

- Source release: `ddxplus-raw-pilot-v1` (published GitHub pre-release assets)
- Ingestion mode: parse of `release_train_patients`, `release_validate_patients`, `release_test_patients`
- Retained items: **48** (target 48)
- Retained by split: train=16, validate=16, test=16
- Primary slice distribution: {'high_label_variation': 31, 'etiology_specific': 4, 'syndrome_qualifier': 7, 'syndrome_first': 6}

## Filtering summary
Rows were retained only when differential diagnosis parsed, >=5 options available, and PATHOLOGY present in top-5 options.
Excluded rows are counted in `ingestion_stage_counts.json`.

## Notes
- This pass materializes a populated draft manifest from real published pre-release assets.
- No raw download cache directory is included in the repository.
