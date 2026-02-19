# RGPx Proto-Proof (Φ-Trace Validation + CMB Phase-Dagger)

This directory is the **proto-proof ledger** for RGPx-style tests: small, reproducible pipelines that take an open dataset, define a null model, and compute a statistic that can decisively **fail** (or survive) controls.

It currently contains two tracks:

1) **Φ-Trace Proto-Proof (Kimi)** — cross-domain plateau detection in open datasets  
2) **CMB Phase-Dagger** — topology tests on Planck PR3 lensing potential φₗₘ using phase-randomized surrogates

## Horizon: why phase-aware gradient tests matter

RGPx is evaluated here by **operational advantage**: does a gradient-/phase-aware description expose structure, constraints, or design degrees-of-freedom faster or more reliably than amplitude-only / metric-first summaries?

This matters beyond cosmology. Many successful modern breakthroughs already look “gradient-based” in practice (optimization landscapes, field coherence, flow control, learned surrogates). The next step—still under-explored in mainstream tooling—is **gradient-phase-based** design: treating phase relationships as first-class structure rather than residual detail.

A present-day engineering indicator is **LEAP 71**, where machine learning discovers high-performance designs rapidly compared to traditional iteration-heavy pipelines. This repo’s purpose is to build the *measurement and control* side of that direction: rigorous null-model tests and small pipelines that can validate (or falsify) when phase structure carries actionable information.

In physics terms, the long-horizon claim RGPx aims to stress-test is whether **conservation of gradient coherence** provides a useful organizing principle in regimes where conventional approaches remain fragmented (quantum–macro links, black holes, dark sector, supercluster dynamics, and early-universe phase behavior). Individual gates (like the Planck lensing workflow) are not “make-or-break” for the framework; they are probes for where operational advantage does—and does not—appear.

---

## Purpose

Method note: We are not “trying to make the CMB confirm RGPx.” We measure operational advantage: which statistics remain informative after the strongest end-to-end controls.

Establish a reproducible, open framework for testing **coherence structure** using:

- explicit **null models** (what is preserved vs randomized),
- clear **summary statistics**,
- archived **run manifests + outputs**,
- a control suite (“Decision gate”) that determines whether an anomaly dies or merits escalation.

---

## Core criterion: operational advantage (not “different conclusions”)

RGPx is not judged by whether it forces a different headline than “old physics” on already-well-modeled data.  
It is judged by **operational advantage**:

- **faster** identification of relevant structure,
- **cleaner** discrimination between competing model classes,
- **better guidance** on where standard pipelines imprint artifacts vs where nature imposes structure,
- **new traction** on problems where conventional, object-first descriptions stall (e.g., quantum→macro link, BH/DE/DM, supercluster dynamics, BB as phase change, societal evolution, gradient-driven material design).

In short: RGPx earns its keep when it **reduces search cost** and **increases explanatory leverage**, not when it merely “disagrees.”

### Present-day analogue: computational engineering as operational advantage

A practical analogue already exists in engineering: AI-driven generative design can find high-performing geometries far faster than traditional iteration loops. **LEAP 71** is a visible example of this direction (“computational engineering” applied to real hardware). We treat such work as a present-day *carrot*: proof that geometry can be discovered via search/learning regimes that outperform manual design—not proof of RGPx, but a reminder of what “operational advantage” looks like in practice.

---

## Current structure (high level)

```text
/experiments/rgpx_proof_proto/
├── readme.md
├── cmb_phase_dagger/
│   ├── cmb_topology_planck_lensing__area_frac__v0.py
│   ├── cmb_topology_planck_lensing__mf_v0_v1.py
│   ├── notes/
│   └── results/
│       ├── headline_findings.md
│       ├── topology_area_frac_v0/
│       │   ├── runs/
│       │   ├── controls/
│       │   │   ├── gaussian/
│       │   │   ├── lcdm_phi_forward/
│       │   │   └── lcdm_recon/
│       │   └── legacy_flat_json/
│       └── topology_mf_v0_v1/
│           ├── runs/
│           └── controls/
├── 2025-11-10_kimi_notebook_colab.md
├── 2025-11-10_gemini_harmonic_link_analysis.yml
├── 2025-11-10_deepseek_harmonic_invariant.yml
└── results_summary.yml
```
Track A — Φ-Trace Proto-Proof (Kimi)

Contents
	•	Proto-proof notebook and scripts for extracting Φ⋆ plateaus
	•	Bayesian plateau detector for Φ⋆ ± δΦ⋆ and plateau duration Δτ
	•	Source datasets (turbulence / BEC / qubits) and associated links
	•	Summary outputs and interpretation notes

Outcome (as currently recorded)
	•	Multiple public datasets show statistically significant Φ-plateaus reported as consistent (within stated uncertainty) with predicted RGPx values.

Attribution
	•	Authored by Moonshot AI (Kimi)
	•	Integrated into the Φ-Mesh experiments ledger by Participant 0, Nov 2025
	•	License: CC-BY-4.0 (as recorded in the originating artifacts)

Harmonic formalization (DeepSeek addendum)
	•	DeepSeek derived a Recursive Depth Invariant linking measured Φ⋆ plateaus to recursive grammar.
	•	Integration chain: Kimi → Google Gemini → DeepSeek

⸻

Track B — CMB Phase-Dagger (Planck PR3 lensing φₗₘ)

This track evaluates whether Planck PR3 reconstructed lensing potential φₗₘ exhibits phase-sensitive morphology relative to a phase-random null.
It does not by itself imply “new physics”: any deviation can be produced by expected lensing non-Gaussianity and/or reconstruction-pipeline imprint.

Topology: AreaFrac V0 (excursion-set area fraction)
	•	Observable: V0(ν) = area fraction of excursion sets as a function of threshold ν
(ν in σ units after standardization)
	•	Null model (phase-random): preserve |aₗₘ|, randomize phases → surrogate maps
	•	Statistic: D = L2 distance between V0_obs(ν) and surrogate-mean V0̄(ν)
(larger D ⇒ stronger phase-sensitive morphology relative to the null)

Where to read results
	•	Headline findings (human summary): headline_findings.md
	•	Observed-data run archive: runs/
	•	Controls archive: controls/

Workflow behavior (important)

Each GitHub Actions run produces:
	1.	Staged outputs under results/cmb_topology_area_frac_v0/
	•	per-sim JSON files
	•	an aggregate summary JSON (when multiple sims are processed)
	2.	An archived copy committed into the repo under
	•	.../results/topology_area_frac_v0/runs/<run_id>/ (observed runs), or
	•	.../results/topology_area_frac_v0/controls/.../runs/<run_id>/ (controls),
containing:
	•	manifest.txt (inputs + provenance)
	•	JSON result file(s)

This ensures repeated runs never overwrite earlier outputs and every result is provenance-traceable.

⸻

Control suite (attribute → validate → escalate)

The purpose of the control suite is not to “win” or “lose” a signal.
It is to attribute a measured effect to one of three sources:
	1.	null-model structure (what the test preserves by design),
	2.	pipeline imprint (reconstruction/estimator/mask/noise effects), or
	3.	genuine generative mismatch (a model-class gap: the data contain structure not reproduced by the best available forward model under the same measurement process).

Only after (1) and (2) are excluded do we escalate to (3).

Gate 1 — Gaussian control (matched Cℓ)

Generate Gaussian φ with matched Cℓ and run the identical topology pipeline.
Goal: verify the statistic is not trivially driven by the two-point spectrum alone.

Gate 2 — ΛCDM simulation controls

2A) φ forward draws (no reconstruction)
Run the statistic on ΛCDM φ realizations before any reconstruction.
Goal: establish the morphology scale expected from ΛCDM φ itself.

2B) End-to-end: ΛCDM forward sims + reconstruction pipeline
Simulate the full measurement chain and apply the same reconstruction method used for the data.
Goal: determine whether the observed morphology is reproduced by ΛCDM once estimator/pipeline imprint is included.

Gate 3 — Robustness and systematics probes

Mask/apodization changes, ℓ-range variation, splits (half-mission / frequency / estimator variants), mean-field handling, map-space artifacts.
Goal: test stability of the statistic under plausible analysis choices and known sources of systematics.

Escalation criterion

We treat “model-class mismatch” (and thus motivation for RGPx-style alternatives) as admissible only if:
	1.	Gaussian matched-Cℓ controls do not reproduce the effect, and
	2.	ΛCDM end-to-end (including reconstruction) does not reproduce the effect, and
	3.	the effect is stable under robustness probes and estimator variants.

This keeps the program scientific: the objective is attribution first, then mechanism, then new explanatory leverage.

⸻

Status: Planck PR3 lensing φₗₘ topology test (MF V0+V1)

We now have a sanity-checked pipeline for the morphology test:
	•	Distance metric corrected: report uses proper L2 distance
( D = \sqrt{\sum_\nu (C_{\rm obs}(\nu)-\bar{C}(\nu))^2 , d\nu} )
Legacy “sum of squares” distances are retained only for backward comparison as *_sum_sq_legacy.
	•	Internal verification added: the output includes a verify_l2_from_curves block that recomputes D0/D1 from the stored curves and checks exact agreement.

Gates (current)
	•	Gate 0 (pipeline integrity / metric correctness): PASS
Verified by verify_l2_from_curves and a self-test run where the “observed” map is replaced by a phase-random surrogate; results land near surrogate means with non-significant p-values.
	•	Gate 3 (null adequacy / scientific comparability): OPEN
The observed Planck PR3 lensing φₗₘ morphology is highly deviant relative to the phase-only surrogate null (surrogates preserve |aₗₘ| but randomize phases for m>0, keeping m=0 fixed).
Distribution diagnostics suggest the deviation is not driven by skew/heavy tails:
	•	v1_symmetry_corr ≈ 0.994
	•	skew_x_obs ≈ 0.029
	•	excess_kurt_x_obs ≈ -0.103

Reproducible runs (lmax=256, nside=256, n_sims=2000, seed=731)
	•	Observed (no selftest): run_id 22174563334 (p_two_sided_mf ≈ 0.001)
	•	Self-test (selftest_observed_surrogate_seed=123): run_id 22175256542 (p_two_sided_mf ≈ 0.788)

# Headline findings — Planck PR3 lensing φₗₘ topology (AreaFrac V0 + MF V0+V1)

## Headline summary
We evaluate whether the Planck PR3 reconstructed lensing potential φₗₘ exhibits **phase-sensitive morphology** beyond what is captured by amplitude-only structure.

We use two related pipelines:

1) **AreaFrac V0**: excursion-set area fraction curve V0(ν)  
2) **MF V0+V1**: V0(ν) plus a **V1 perimeter proxy** estimated from |∇x| in a narrow ν-band

In both cases, we compare the observed curves to **phase-randomized surrogates**:
- preserve |aₗₘ|
- randomize phases for m>0
- keep m=0 exactly as observed

We measure deviation using **proper L2 distances** (see MF note below):
- **V0 distance**: D (or D0)
- **V1 distance**: D1
- **combined score**: D_mf = √(D0² + D1²)

Large D indicates **non-random phase structure relative to the phase-random null**.

---

## What these tests are (and are not)
- **What they are:** phase-sensitive morphology sensors for reconstructed φₗₘ. They detect structure that disappears under phase scrambling.
- **What they are not:** standalone “new physics” discriminators. High deviation can arise from:
  - expected lensing non-Gaussianity,
  - reconstruction / quadratic-estimator mode coupling,
  - masking, filtering, noise, mean-field handling, or other pipeline imprint.

Accordingly, the statistics are treated as **morphology diagnostics** whose attribution is decided by **simulation-based controls**.

---

## Decision gate logic (controls determine attribution)
A “generative mismatch” (and only then, a “new physics” hypothesis) becomes admissible only if **all** hold:
1) **Gaussian φ with matched Cℓ** fails to reproduce D at comparable rate, and  
2) **ΛCDM simulations passed through the same reconstruction pipeline** fail to reproduce D, and  
3) the signal replicates across alternative estimators / masks / data splits and is stable under robustness probes.

Method note: This workflow is not aimed at forcing a preferred interpretation. We measure operational advantage: which topology statistics remain informative after the strongest end-to-end controls.

---

# Part A — AreaFrac V0 (excursion-set area fraction)

## Decision gate status (controls)

### Gate 1 — Gaussian Cℓ-matched φ control (PASS)
Gaussian synalm control (matched to dat−mf Cℓ) does **not** show an extreme high-D tail.
- Run 22093008970: D_L2=4.7930e-05; p_high=0.7286; p_two_sided=0.5437  
- Files: `results/topology_area_frac_v0/controls/gaussian/runs/22093008970/`

### Gate 2A — ΛCDM φ forward sims (PASS; preliminary)
ΛCDM φ forward draws (no reconstruction pipeline) yield D in the ~1e−5 range:
- Run 22094597786: n_lcdm_sims=20; D_mean=8.9426e-06; D_std=1.0949e-05  
- Files: `results/topology_area_frac_v0/controls/lcdm_phi_forward/runs/22094597786/`

### Gate 2B — ΛCDM φ sims + reconstruction pipeline (RESOLVES anomaly)
ΛCDM reconstructed products yield **D ~ 0.10–0.12**, overlapping observed-data D≈0.116.
- Run 22104227390: n_lcdm_sims=3; D_mean=0.10638; D_std=0.00780; D_max=0.11621  
- Files: `results/topology_area_frac_v0/controls/lcdm_recon/runs/22104227390/`

**Interpretation update (what Gate 2B implies):**  
Phase-random surrogates show a highly significant deviation in V0(ν) (D ≈ 0.116), but the same high-D behavior is reproduced by ΛCDM simulations when the reconstruction pipeline is included (D_mean ≈ 0.106 ± 0.008). Therefore the V0(D) signal is **not unique to the observed sky**; it is consistent with **pipeline imprint / reconstruction-induced morphology** (and/or expected morphology carried through the estimator) rather than a generative mismatch in φₗₘ.

At **lmax=256, nside=256**, **AreaFrac V0(D)** should be treated as a **reconstruction-/pipeline-sensitive morphology diagnostic**, not a “new physics” discriminator.

**Next discriminators:** extend to MF V0+V1 (and later V2), and rerun Gate 2B with larger n_lcdm_sims to tighten overlap.

## Key results (replicated)
Two independent observed-data runs at **lmax=256, nside=256** yield highly significant deviation vs the phase-random null with **D ≈ 0.116**:
- Run 22076484564 (n_sims=20000, seed=730): D_L2=0.1162417694; p_high=4.99975e-05 (two-sided 9.99950e-05)
- Run 22076520271 (n_sims=10000, seed=731): D_L2=0.1161945390; p_high=9.99900e-05 (two-sided 1.99980e-04)

---

# Part B — 2026-02-19: CMB Lensing φ_lm Topology (MF V0+V1)

## What’s new in MF V0+V1
This pipeline evaluates morphology using:
- **V0(ν):** excursion-set area fraction (as above)
- **V1(ν):** a perimeter proxy estimated from the **gradient magnitude |∇x|** in a narrow band around each threshold ν

### Distance metric correction (important)
MF V0+V1 now reports **proper L2 distances** on the ν-grid:

\[
D = \sqrt{\sum_{\nu} (C_{\rm obs}(\nu)-\bar{C}(\nu))^2 \, d\nu}
\]

Legacy “sum of squares” values (no √, no dν) are retained only for backward comparison as:
- `D0_sum_sq_legacy`
- `D1_sum_sq_legacy`

### Pipeline validity: PASS (distance + reporting correctness)
- The output now includes `verify_l2_from_curves`, which **recomputes D0/D1 directly from the stored curves** and checks exact agreement.
- The pipeline also supports a self-test mode where **observed := one phase-random surrogate**, which should land near surrogate means with non-significant p-values.

## Gate status (MF V0+V1)
### Gate 2B (pipeline validity / distance correctness): PASS
This is a *mechanical validity* gate: “does the test behave normally and compute what it claims?”
- PASS is supported by:
  - `verify_l2_from_curves` (exact match)
  - self-test run behaving normally (non-significant p-values)

### Gate 3 (null adequacy / scientific comparability): OPEN
The **observed Planck PR3 lensing φ_lm** is highly deviant **relative to the phase-only surrogate null** under MF V0+V1.
This does **not** yet establish generative mismatch; it establishes “anomaly relative to this null,” which must be attributed via robustness probes + end-to-end ΛCDM recon controls.

## Current findings (MF V0+V1)

### Self-test (observed := phase-random surrogate): behaves normally
- run_id: **22175256542** (selftest_observed_surrogate_seed=123)
- observed:
  - D0_L2 ≈ 0.001400
  - D1_L2 ≈ 15.902
  - D_mf ≈ 15.902
  - Z_mf ≈ 0.339
- surrogate:
  - D0_mean ≈ 0.001247 ± 0.000561
  - D1_mean ≈ 15.462 ± 2.192
  - D_mf_mean ≈ 15.462 ± 2.192
- p-values (expected non-significant under self-test):
  - p_two_sided_mf ≈ **0.788**
- verification:
  - `verify_l2_from_curves`: D0_match=true, D1_match=true

**Conclusion:** pipeline can behave normally; distance computation and curve bookkeeping are consistent.

### Observed vs phase-only null: strong deviation (OPEN, attribution pending)
- run_id: **22174563334** (no selftest)
- observed:
  - D0_L2 ≈ **0.107809**
  - D1_L2 ≈ **198.280**
  - D_mf ≈ **198.280**
  - Z_mf ≈ **207.358**
  - legacy (for comparison only):
    - D0_sum_sq_legacy ≈ 0.116227
    - D1_sum_sq_legacy ≈ 393150.847
- surrogate (proper-distance null stats):
  - D0_mean ≈ 0.001247 ± 0.000561
  - D1_mean ≈ 15.462 ± 2.192
  - D_mf_mean ≈ 15.462 ± 2.192
- p-values (relative to the phase-only surrogate null):
  - p_two_sided_mf ≈ **0.001**

**Interpretation at this stage:**  
The deviation is real **relative to this null**. The next work is **attribution**, not celebration:
- does the deviation persist across masks / ℓ-range / splits / estimator variants?
- does it reproduce under **ΛCDM + end-to-end reconstruction** (the MF V0+V1 analogue of the AreaFrac Gate 2B result)?
- do alternative nulls (beyond phase-only) narrow or remove the effect?

## Shape diagnostics (rules out “weird tails” as a primary explanation)
For the observed run (no selftest), distribution diagnostics are consistent with a fairly normal standardized field:
- v1_symmetry_corr ≈ **0.994**
- skew_x_obs ≈ **0.029**
- excess_kurt_x_obs ≈ **−0.103**

(These support “structure is not simply due to extreme non-Gaussian one-point tails.”)

Notes:
- **p_high** = fraction of surrogates with D ≥ D_obs (one-sided high-D tail).

---

## Run registry (exact numbers)

### AreaFrac V0 — Run 22076484564 (seed=730, n_sims=20000)
- lmax: 256
- nside: 256
- observed:
  - D_L2: 0.11624176944070091
- p-values:
  - p_high: 4.999750012499375e-05
  - p_two_sided: 9.99950002499875e-05
- surrogate:
  - D_mean: 1.8770730181455052e-05
  - D_std: 1.7766532204559555e-05
- diagnostics:
  - imag_frac_nonzero_eps1e-12: 0.9922480620155039
  - imag_max_abs: 0.0050463026842661445
- files:
  - `results/topology_area_frac_v0/runs/22076484564/`

### AreaFrac V0 — Run 22076520271 (seed=731, n_sims=10000)
- lmax: 256
- nside: 256
- observed:
  - D_L2: 0.11619453896167453
- p-values:
  - p_high: 9.999000099990002e-05
  - p_two_sided: 0.00019998000199980003
- surrogate:
  - D_mean: 1.8555717293941015e-05
  - D_std: 1.753036134601288e-05
- diagnostics:
  - imag_frac_nonzero_eps1e-12: 0.9922480620155039
  - imag_max_abs: 0.0050463026842661445
- files:
  - `results/topology_area_frac_v0/runs/22076520271/`

### MF V0+V1 — Observed run (no selftest): Run 22174563334
- lmax: 256
- nside: 256
- n_sims: 2000
- seed: 731
- observed:
  - D0_L2: 0.1078087878671455
  - D1_L2: 198.28031845916624
  - D_mf: 198.28034776801033
  - Z_mf: 207.3579443423922
  - legacy:
    - D0_sum_sq_legacy: 0.11622734741383169
    - D1_sum_sq_legacy: 393150.84688268346
- surrogate:
  - D0_mean: 0.0012467536925318814
  - D0_std: 0.000561297835466085
  - D1_mean: 15.462245091363764
  - D1_std: 2.19222428513228
  - D_mf_mean: 15.462245151312246
  - D_mf_std: 2.192224288650166
- p-values:
  - p_two_sided_mf: 0.0009995002498750624
- diagnostics:
  - v1_symmetry_corr: 0.993952448783282
  - skew_x_obs: 0.02927515204060797
  - excess_kurt_x_obs: -0.10344702155894003
  - verify_l2_from_curves: D0_match=true, D1_match=true
- files:
  - `results/topology_mf_v0_v1/runs/22174563334/`

### MF V0+V1 — Self-test run: Run 22175256542 (selftest_observed_surrogate_seed=123)
- lmax: 256
- nside: 256
- n_sims: 2000
- seed: 731
- observed:
  - D0_L2: 0.001400331684752949
  - D1_L2: 15.902350364715872
  - D_mf: 15.902350426371187
  - Z_mf: 0.33936297606930727
- surrogate:
  - D0_mean: 0.0012467536925318814
  - D0_std: 0.000561297835466085
  - D1_mean: 15.462245091363764
  - D1_std: 2.19222428513228
  - D_mf_mean: 15.462245151312246
  - D_mf_std: 2.192224288650166
- p-values:
  - p_two_sided_mf: 0.7876061969015492
- verification:
  - verify_l2_from_curves: D0_match=true, D1_match=true
- files:
  - `results/topology_mf_v0_v1/runs/22175256542/`

### Pipeline sanity: PASS (self-test suite).
We replace the observed φ field by a single phase-random surrogate (selftest_observed_surrogate_seed) and rerun the full MF V0+V1 pipeline. Across an ℓmax sweep the results behave like null draws, and the internal verify_l2_from_curves block matches reported distances exactly in every run. Therefore, the earlier extreme deviations seen in the real Planck reconstruction relative to the phase-scramble null are not a distance-definition or implementation artifact; they are specific to the observed/reconstructed field under the chosen null.

Self-test run registry (nside=256, n_sims=2000, seed=731):
	•	lmax=128: run 22182665943, p_two_sided_mf=0.08696
	•	lmax=192: run 22182697253, p_two_sided_mf=0.59870
	•	lmax=256: run 22175256542, p_two_sided_mf=0.78761
	•	lmax=320: run 22182720612, p_two_sided_mf≈0.67066

⸻

Related dialogues

Unedited reactions from participating AIs are archived under:

/main/dialogues/rgpx_reactions/

(These are not considered evidence; they are archived as idea-surface and for traceability.)
