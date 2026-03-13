# Pilot adjudication sample note (manual pass 1)

Scope: first manual-quality pass on a stratified sample from `pilot_manifest_draft.json` (committed draft only).

Sampling used: deterministic random sample (`seed=42`) with exactly 4 items each from `source_split=train|validate|test` (12 total).

## Per-item adjudication (compact)

| Item | Split | Stem / diagnosis framing | Gold-label correctness | Distractor plausibility | Duplicate / weak option risk | Slice-tag & rationale quality |
|---|---|---|---|---|---|---|
| `pilot_ddxplus_0004` | train | Weak: stem is encoded evidence IDs, clinically opaque. | Uncertain-medium confidence (not enough semantic evidence decoding). | Mixed: respiratory set mostly plausible; `Cluster headache` weaker. | Moderate risk (URTI/Bronchitis/Influenza overlap). | Weak: generic rationale text only. |
| `pilot_ddxplus_0001` | train | Weak/opaque encoded framing. | Medium confidence only. | Good-mixed (mostly same organ system; `Tuberculosis` a harder outlier). | Moderate (URTI/Bronchitis/Pneumonia close). | Weak-generic rationale. |
| `pilot_ddxplus_0012` | train | Weak/opaque encoded framing. | Medium confidence. | Reasonable cardiopulmonary differential set. | Low duplicate risk. | Weak-generic rationale; tag appears formulaic. |
| `pilot_ddxplus_0005` | train | Weak/opaque encoded framing. | Medium confidence. | Mixed; sinusitis pair plausible, `Chagas` implausible distractor. | High local confusion risk (`Acute` vs `Chronic rhinosinusitis`). | Better than most (has secondary tag), but rationale still generic. |
| `pilot_ddxplus_0024` | validate | Weak/opaque encoded framing. | Medium confidence. | Mostly plausible pulmonary options. | Moderate (`Bronchitis` vs `Bronchiectasis` risk). | Weak-generic rationale. |
| `pilot_ddxplus_0020` | validate | Weak/opaque encoded framing. | Low-medium confidence (age 13 + option set seems noisy). | Mixed-poor (`Atrial fibrillation` in this set for pediatric case is weak). | Low duplicate risk, but option quality uneven. | Weak: empty rationale field. |
| `pilot_ddxplus_0019` | validate | Weak/opaque encoded framing. | Medium confidence. | Mixed; URTI/Influenza/Viral pharyngitis plausible, `Chagas` weak. | Moderate (viral URI cluster). | Weak-generic rationale. |
| `pilot_ddxplus_0028` | validate | Weak/opaque encoded framing. | Low-medium confidence (`Panic attack` vs severe cardiopulmonary options feels unstable). | Mixed; several strong alternatives may outrank gold depending on decoded evidence. | Low duplicate risk. | Weak-generic rationale. |
| `pilot_ddxplus_0036` | test | Weak/opaque encoded framing. | Medium confidence. | Mixed; respiratory triad plausible, `HIV (initial infection)` weaker. | Moderate (URTI/Bronchitis/Pneumonia/Influenza cluster). | Weak-generic rationale. |
| `pilot_ddxplus_0043` | test | Weak/opaque encoded framing. | Low-medium confidence. | Mixed-poor; several distractors look far afield (`Chagas`, `Cluster headache`). | Low duplicate risk; quality spread too wide. | Weak: empty rationale field. |
| `pilot_ddxplus_0044` | test | Weak/opaque encoded framing. | Medium confidence. | Good-mixed for pulmonary items; `Cluster headache` weak. | Moderate (URTI/Bronchitis/Pneumonia). | Weak-generic rationale. |
| `pilot_ddxplus_0041` | test | Weak/opaque encoded framing. | Medium confidence. | Mixed; bronchitis vs sinusitis/pneumothorax/cardiac panic spread is broad. | Low duplicate risk. | Weak-generic rationale. |

## Overall quality judgment

**Judgment: usable with caution for a first ablation run, but not yet publication-grade.**

Strengths:
- Split balance and label coverage in this sample look workable.
- Many items preserve at least partial in-domain distractor structure.

Main weaknesses (recurring):
1. **Stem readability is consistently low** (ID-coded evidences prevent true human clinical validation).
2. **Tagging rationale quality is weak** (often boilerplate; some entries blank).
3. **Distractor quality inconsistency** (some options are clearly out-of-distribution vs other choices).
4. **Frequent near-neighbor respiratory clusters** create ambiguity not always explained by rationale.

## First ablation readiness

**Yes — good enough for a first ablation run** if treated as a pilot stress-test and not a final quality claim.

## Recommended next action (single)

Before cross-benchmark scoring, run a **targeted cleanup pass on rationale + distractor outliers** for this pilot manifest (prioritize items with blank rationale and obviously implausible distractors), without changing benchmark code.
