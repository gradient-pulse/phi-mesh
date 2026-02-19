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

---

## Gate status (MF V0+V1)

### Sanity S1 — distance correctness + self-test behavior: PASS
This is a *mechanical validity* gate: “does the test behave normally and compute what it claims?”
- PASS is supported by:
  - `verify_l2_from_curves` (exact match)
  - self-test runs behaving as null draws (non-significant p-values across ℓmax sweep)

### Gate 1 (MF) — Gaussian Cℓ-matched φ control: PASS
Gaussian synalm control derived from (dat−mf) Cℓ behaves like a null draw under MF V0+V1 across an ℓmax sweep (no extreme tails; p-values non-significant).

### Gate 2B (MF) — ΛCDM end-to-end recon control: NOT RUN YET
This is the MF V0+V1 analogue of the AreaFrac Gate 2B result, and it is the next responsible step.
- Question: does **ΛCDM + reconstruction** reproduce the high D1 (and its ℓmax scaling) seen relative to the phase-only surrogate null?

### Gate 3 (MF) — null adequacy / scientific comparability: OPEN
Observed Planck PR3 lensing φ_lm is highly deviant relative to the phase-only surrogate null under MF V0+V1. This establishes “anomaly relative to this null,” not yet a generative mismatch.

---

## Current findings (MF V0+V1)

### Observed vs phase-only null: strong deviation (OPEN, attribution pending)
Observed Planck PR3 lensing φ_lm deviates strongly from the phase-only surrogate null.

**Reference observed run (lmax=256):**
- run_id: **22174563334** (no selftest)
- observed:
  - D0_L2 = 0.1078087878671455
  - D1_L2 = 198.28031845916624
  - D_mf  = 198.28034776801033
  - Z_mf  = 207.3579443423922
  - legacy (for comparison only):
    - D0_sum_sq_legacy = 0.11622734741383169
    - D1_sum_sq_legacy = 393150.84688268346
- surrogate:
  - D0_mean = 0.0012467536925318814 ± 0.000561297835466085
  - D1_mean = 15.462245091363764 ± 2.19222428513228
  - D_mf_mean = 15.462245151312246 ± 2.192224288650166
- p-values (relative to the phase-only surrogate null):
  - p_two_sided_mf = 0.0009995002498750624
- diagnostics:
  - v1_symmetry_corr = 0.993952448783282
  - skew_x_obs = 0.02927515204060797
  - excess_kurt_x_obs = -0.10344702155894003
  - verify_l2_from_curves: D0_match=true, D1_match=true
- files:
  - `results/topology_mf_v0_v1/runs/22174563334/`

**Interpretation at this stage:**  
The deviation is real relative to the phase-only surrogate null. The next work is attribution:
- does the deviation persist across masks / ℓ-range / splits / estimator variants?
- does it reproduce under **ΛCDM + end-to-end reconstruction** (MF Gate 2B analogue)?
- do alternative nulls (beyond phase-only) narrow or remove the effect?

---

## ℓmax sweep — observed vs phase-only null (same nside/n_sims/seed)
Across an ℓmax sweep, the MF deviation strengthens with increasing ℓmax under the same phase-only surrogate null (all runs show an extreme p_two_sided_mf tail at n_sims=2000).

Common settings: nside=256, n_sims=2000, seed=731, ν grid: n_nu=61, ν∈[-3,3].

- lmax=128: run **22177285559**
  - D0_L2 = 0.09346837140279923
  - D1_L2 = 99.63703649454285
  - D_mf  = 99.63708033534161
  - p_two_sided_mf = 0.0009995002498750624
- lmax=192: run **22177351720**
  - D0_L2 = 0.10370041719920363
  - D1_L2 = 144.14466790672424
  - D_mf  = 144.14470520874622
  - p_two_sided_mf = 0.0009995002498750624
- lmax=256: run **22177371714**
  - D0_L2 = 0.1078087878671455
  - D1_L2 = 198.28031845916624
  - D_mf  = 198.28034776801033
  - p_two_sided_mf = 0.0009995002498750624
- lmax=320: run **22177393266**
  - D0_L2 = 0.10845876900224662
  - D1_L2 = 267.0867968828012
  - D_mf  = 267.08681890430177
  - p_two_sided_mf = 0.0009995002498750624

**Note:** with n_sims=2000, the smallest achievable two-sided p-value is ~1/1000 ≈ 0.001, which is what is observed here. Increasing n_sims will sharpen the tail estimate.

---

## Self-test suite — observed := phase-random surrogate (PASS)
We replace the observed φ field by a single phase-random surrogate (selftest_observed_surrogate_seed) and rerun the full MF V0+V1 pipeline. Across an ℓmax sweep, these runs behave like null draws (non-significant p-values), and the internal `verify_l2_from_curves` block matches reported distances exactly in every run. Therefore, the extreme deviations seen in the real Planck reconstruction relative to the phase-scramble null are not a distance-definition or implementation artifact; they are specific to the observed/reconstructed field under the chosen null.

Common settings: nside=256, n_sims=2000, seed=731.

- lmax=128: run **22182665943**, p_two_sided_mf = 0.08695652173913043
  - D0_L2 = 0.004218095623942724
  - D1_L2 = 5.426374495355203
- lmax=192: run **22182697253**, p_two_sided_mf = 0.5987006496751625
  - D0_L2 = 0.0032177503436146672
  - D1_L2 = 10.054108902406368
- lmax=256: run **22175256542** (selftest_observed_surrogate_seed=123), p_two_sided_mf = 0.7876061969015492
  - D0_L2 = 0.001400331684752949
  - D1_L2 = 15.902350364715872
- lmax=320: run **22182720612**, p_two_sided_mf ≈ 0.670664667666167
  - D0_L2 = 0.0005891780357202247
  - D1_L2 = 19.220602086834322

---

## Gaussian control — MF V0+V1 (PASS)
Gaussian synalm controls (matched to Cℓ of (dat−mf), with mf set to zero) behave as null draws under MF V0+V1 (no extreme tails; p-values non-significant) across an ℓmax sweep.

Common settings: nside=256, n_sims=2000, seed=731, gauss_seed=901.

- lmax=128: run **22181165496**, p_two_sided_mf = 0.8085957021489255
  - D0_L2 = 0.01587829006387474
  - D1_L2 = 20.86379903083497
- lmax=192: run **22182466399**, p_two_sided_mf = 0.6866566716641679
  - D0_L2 = 0.003821828230447542
  - D1_L2 = 18.85066752931705
- lmax=256: run **22181076396**, p_two_sided_mf = 0.11794102948525736
  - D0_L2 = 0.00224199010816852
  - D1_L2 = 13.984100227469769
- lmax=320: run **22182497771**, p_two_sided_mf = 0.656671664167916
  - D0_L2 = 0.001548388386815504
  - D1_L2 = 22.28465625595231

**Interpretation update:**  
A strong anomaly exists relative to the phase-only surrogate null in the observed Planck reconstruction, and it strengthens with ℓmax. Gaussian controls with matched Cℓ do not reproduce this behavior under the same MF pipeline. The next responsible attribution step is the **MF Gate 2B analogue**: ΛCDM simulations passed through the end-to-end reconstruction pipeline, evaluated with MF V0+V1, and compared on the same ℓmax sweep.

---

## Notes and definitions
- **p_high**: fraction of surrogates with D ≥ D_obs (one-sided high-D tail).
- **p_two_sided**: two-sided tail probability relative to the surrogate distribution.
- MF runs report both the **proper L2 distances** and legacy “sum-of-squares” distances retained only for backward comparison.
