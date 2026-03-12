# Second benchmark candidate shortlist (for post-c08-v5 cross-benchmark ablation)

## Repo-first scan result
I scanned this repo for already-present benchmark/case/eval assets that match the required format (short clinical vignette -> single primary diagnosis with gold labels). Practical finding: only `benchmarks/ai_intuition_c08/*` appears to be a true clinical diagnosis benchmark package; no second in-repo benchmark/task set with comparable artifacts was found.

## External candidate shortlist (3)

### 1) **USMLE-style clinical vignette MCQ datasets (diagnosis-only subset)**
Examples: MedQA-USMLE-style question banks, filtered to items where the keyed option is a diagnosis label.

- **Fit to single-primary-diagnosis vignette format:** **High** after filtering. Most stems are short-to-medium clinical vignettes with one best diagnosis answer.
- **Strict + synonym-tolerant scoring ease:** **High.** Strict can score by keyed canonical answer; synonym-tolerant can use option text normalization + diagnosis synonym map.
- **Syndrome-vs-etiology ambiguity suitability:** **Medium-High.** Many items distinguish syndrome labels vs etiologic specifics; explicit slice tagging is feasible.
- **Risks/drawbacks:** MCQ format may induce option-cueing effects; some items test management/test-next-step rather than diagnosis and must be excluded.

### 2) **DDXPlus-style diagnostic simulation dataset (patient vignette + pathology label)**
A large synthetic differential-diagnosis corpus with structured symptom findings and a primary pathology target.

- **Fit to single-primary-diagnosis vignette format:** **High.** Direct case-to-diagnosis mapping is native.
- **Strict + synonym-tolerant scoring ease:** **High.** Canonical pathology IDs make strict scoring straightforward; synonym layer can be built from ontology terms.
- **Syndrome-vs-etiology ambiguity suitability:** **Medium.** Has both syndrome-level and etiologic labels, but synthetic generation may underrepresent real-world qualifier nuance.
- **Risks/drawbacks:** Synthetic wording/distribution shift may limit transfer claims to real clinical prose; may overestimate gains from scaffold regularity.

### 3) **HumanDx / educational clinicopathologic challenge case collections (final diagnosis labeled)**
Case-vignette sets with final diagnosis, often built for differential diagnosis training.

- **Fit to single-primary-diagnosis vignette format:** **Medium-High.** Usually vignette-first with a final diagnosis, though structure is less standardized.
- **Strict + synonym-tolerant scoring ease:** **Medium.** Final diagnoses exist, but normalization effort can be nontrivial due heterogeneous naming granularity.
- **Syndrome-vs-etiology ambiguity suitability:** **High.** Real-world ambiguity and qualifier-heavy labels are common and useful for c08 failure-mode stress tests.
- **Risks/drawbacks:** Access/licensing and export format can be variable; curation burden is higher than MCQ/synthetic datasets.

## Recommendation
- **Recommended candidate:** **USMLE-style clinical vignette MCQ diagnosis-only subset**.
- **Backup candidate:** **DDXPlus-style diagnostic simulation dataset**.

The top recommendation is the best next move because it gives fast, reproducible scoring with enough real vignette heterogeneity to test scaffold-transfer vs label-normalization effects without a heavy data-engineering detour.
