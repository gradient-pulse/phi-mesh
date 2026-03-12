# Replacement source candidates (post-MedQA terms block)

## Candidate 1 (recommended): DDXPlus English release (figshare; synthetic diagnostic cases)

- **Likely terms/licensing clarity:**
  - Stronger than MedQA based on publicly stated terms in the project README: dataset released under **CC-BY** and distributed via a named public host (figshare).
  - Still requires one final check at ingestion time: confirm the exact figshare record license text matches the README claim.
- **Fit to diagnosis-only vignette subset construction:**
  - High for diagnosis labels (`PATHOLOGY`) and differential diagnosis fields.
  - Not native MCQ; would require generating MCQ-style option sets from differential/pathology fields (allowed only after approval).
- **Likely ease of strict + synonym-tolerant scoring:**
  - High for strict scoring due structured pathology labels/codes.
  - Medium-high for synonym-tolerant scoring using condition metadata (English names/aliases).
- **Likely risks:**
  - Synthetic language/distribution shift vs real exam prose.
  - Additional design decisions needed to map to pilot MCQ schema and slice tags.

## Candidate 2 (backup): HumanDx educational case exports (only with explicit written usage permission)

- **Likely terms/licensing clarity:**
  - Potentially acceptable only if export access and usage rights are explicitly granted in writing for this workflow.
  - Without that written grant, terms clarity remains weak.
- **Fit to diagnosis-only vignette subset construction:**
  - Medium-high; real vignette cases with final diagnosis labels can fit diagnosis-only intent.
  - Format variability likely requires heavier normalization.
- **Likely ease of strict + synonym-tolerant scoring:**
  - Medium; diagnosis labels are available but granularity/wording heterogeneity increases canonicalization effort.
- **Likely risks:**
  - Access and licensing may be institution/account dependent.
  - Higher curation burden and less standardized provenance fields.

## Selection
- **Recommended replacement:** **DDXPlus English release (figshare)**.
- **Backup replacement:** **HumanDx educational case exports with explicit written usage permission**.

DDXPlus is safer than MedQA for this workflow because its documentation explicitly states a dataset release license (CC-BY) and a public distribution route, while MedQA dataset-content permissions remained ambiguous.
