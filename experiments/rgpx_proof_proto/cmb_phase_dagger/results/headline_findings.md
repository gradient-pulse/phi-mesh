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
