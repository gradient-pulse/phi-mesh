# Headline findings — Planck PR3 lensing φₗₘ topology (AreaFrac V0)

## Headline summary
We tested whether the observed Planck PR3 lensing potential spherical-harmonic field φₗₘ shows **non-null morphology** beyond what is preserved under **phase randomization** (|aₗₘ| fixed, phases randomized).  
Topology v0 uses the **excursion-set area fraction curve V0(ν)** and the statistic **D = L2 distance** between the observed V0(ν) curve and the **surrogate-mean** curve. Large D indicates morphology not explained by amplitude-only structure.

Result: two independent runs (different seeds, different N) both show a **highly significant deviation** from the phase-random surrogate baseline at lmax=256, nside=256.

## Key results (replicated)
- Run **22076484564** (n_sims=20000, seed=730): D_L2=0.1162417694; p_high=4.99975e-05 (two-sided 9.99950e-05)
- Run **22076520271** (n_sims=10000, seed=731): D_L2=0.1161945390; p_high=9.99900e-05 (two-sided 1.99980e-04)

Notes:
- **p_high** = fraction of surrogates with D ≥ D_obs (one-sided “high-D tail”).

## Interpretation guardrail
This is a strong detection of **non-random phase structure / higher-order morphology** relative to a phase-randomized null.  
Such deviations can arise from **expected lensing non-Gaussianity**, from **estimator/pipeline imprint**, or from other systematics; the follow-ups below are meant to separate these.

It is **not yet** evidence for “new physics” by itself. Next discriminators:
- add topology V1/V2 (boundary length, Euler characteristic) under same surrogate scheme
- run controls (Gaussian φ with same power spectrum, or ΛCDM lensing simulations) to separate “expected lensing non-Gaussianity” from pipeline/systematic effects.

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
