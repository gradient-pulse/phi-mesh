# Headline findings — Planck PR3 lensing φₗₘ topology (AreaFrac V0)

## Headline summary
We evaluate whether the Planck PR3 reconstructed lensing potential φₗₘ exhibits **phase-sensitive morphology** beyond what is captured by amplitude-only structure. We compare the observed **excursion-set area fraction curve V0(ν)** to **phase-randomized surrogates** (|aₗₘ| fixed, phases randomized). We use

- **D = L2 distance** between V0_obs(ν) and the surrogate-mean V0̄(ν)

Large D indicates **non-random phase structure relative to the phase-random null**.

Two independent observed-data runs at **lmax=256, nside=256** yield **highly significant** deviation from the phase-random baseline with **D ≈ 0.116**.

## What this test is (and is not)
- **What it is:** a **phase-sensitive morphology sensor** for reconstructed φₗₘ. It is designed to detect “structure carried in phases” that disappears under phase scrambling.
- **What it is not:** a standalone “new physics” discriminator. Any high-D signal can arise from:
  - expected lensing non-Gaussianity,
  - reconstruction / quadratic-estimator mode coupling,
  - masking, filtering, noise, or other pipeline effects.

Accordingly, V0(D) is treated as a **morphology diagnostic** whose attribution (sky vs pipeline) is decided by **simulation-based controls**.

## Decision gate logic (controls determine attribution)
A “generative mismatch” (and only then, a “new physics” hypothesis) becomes admissible only if **all** of the following hold:
1) **Gaussian φ with matched Cℓ** fails to reproduce D at comparable rate, and  
2) **ΛCDM simulations passed through the same reconstruction pipeline** fail to reproduce D, and  
3) the signal replicates across alternative estimators / masks / data splits.

(Controls 1–3 separate “expected non-Gaussianity / pipeline imprint” from a genuine model-class mismatch.)

## Decision gate status (controls)

### Gate 1 — Gaussian Cℓ-matched φ control (PASS)
Gaussian synalm control (matched to dat−mf Cℓ) does **not** show an extreme high-D tail.
- Run 22093008970: D_L2=4.7930e-05; p_high=0.7286; p_two_sided=0.5437  
- Files: [controls/gaussian/runs/22093008970/](./controls/gaussian/runs/22093008970/)

### Gate 2A — ΛCDM φ forward sims (PASS; preliminary)
ΛCDM φ forward draws (no reconstruction pipeline) yield D in the ~1e−5 range:
- Run 22094597786: n_lcdm_sims=20; D_mean=8.9426e-06; D_std=1.0949e-05
- Files: [controls/lcdm_phi_forward/runs/22094597786/](./controls/lcdm_phi_forward/runs/22094597786/)

### Gate 2B — ΛCDM φ sims + reconstruction pipeline (RESOLVES anomaly)
ΛCDM reconstructed products yield **D ~ 0.10–0.12**, overlapping the observed-data D≈0.116.
- Run 22104227390: n_lcdm_sims=3; D_mean=0.10638; D_std=0.00780; D_max=0.11621
- Files: [controls/lcdm_recon/runs/22104227390/](./controls/lcdm_recon/runs/22104227390/)

**Interpretation update (what Gate 2B implies):**  
Phase-random surrogates show a highly significant deviation in V0(ν) (D ≈ 0.116), but the same high-D behavior is reproduced by ΛCDM simulations when the reconstruction pipeline is included (D_mean ≈ 0.106 ± 0.008). Therefore this V0(D) signal is **not unique to the observed sky**; it is consistent with **quadratic-estimator / pipeline imprint** (and expected morphology carried through the pipeline) rather than a generative mismatch in φₗₘ.

At **lmax=256, nside=256**, **AreaFrac V0(D)** should be treated as a **reconstruction-/pipeline-sensitive morphology diagnostic**, not a “new physics” discriminator.

**Next discriminators:** extend to **V1/V2** (boundary length, Euler characteristic) and rerun **Gate 2B** with larger **n_lcdm_sims** to tighten the overlap.

## Key results (replicated)
- Run **22076484564** (n_sims=20000, seed=730): D_L2=0.1162417694; p_high=4.99975e-05 (two-sided 9.99950e-05)
- Run **22076520271** (n_sims=10000, seed=731): D_L2=0.1161945390; p_high=9.99900e-05 (two-sided 1.99980e-04)

Notes:
- **p_high** = fraction of surrogates with D ≥ D_obs (one-sided “high-D tail”).

---

## Run registry (exact numbers)

### Run 22076484564 (seed=730, n_sims=20000)
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
  - results/topology_area_frac_v0/runs/22076484564/

### Run 22076520271 (seed=731, n_sims=10000)
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
  - results/topology_area_frac_v0/runs/22076520271/
