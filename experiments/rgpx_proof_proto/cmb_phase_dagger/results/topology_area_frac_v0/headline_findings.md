# Headline findings — Planck PR3 lensing φₗₘ topology (AreaFrac V0)

## Headline summary
We test whether Planck PR3 lensing φₗₘ contains **morphology beyond amplitude-only structure** by comparing the observed **excursion-set area fraction curve V0(ν)** to **phase-randomized surrogates** (|aₗₘ| fixed, phases randomized). The statistic is **D = L2 distance** between V0_obs(ν) and the surrogate-mean V0̄(ν); large D implies non-random phase structure.

Two independent runs (different seeds, different N) show a **highly significant** deviation from the phase-random baseline at lmax=256, nside=256.

## Interpretation guardrail
This is evidence for **non-random phase structure / higher-order morphology** relative to the phase-random null, but **not** a “new physics” claim: it can arise from expected lensing non-Gaussianity, estimator/pipeline imprint, or other systematics. Next discriminators: add V1/V2 (boundary length, Euler characteristic) and run controls (Gaussian φ with same Cℓ, and/or ΛCDM lensing simulations).

## What is at stake (if controls confirm)
If the effect persists under ΛCDM-forward simulations (including reconstruction pipeline) and under Gaussian controls with matched Cℓ, then the remaining explanation is **a mismatch in the assumed generative model** for φ: either (i) missing physics in the lensing potential statistics, or (ii) a non-standard coherence constraint not captured by the usual amplitude-based description. In that case, this becomes evidence for a **model-class failure** — i.e., the type of opening where “new physics” becomes a legitimate scientific hypothesis rather than rhetoric.

## Decision gate
We will treat “new physics” as admissible only if:
1) Gaussian φ with matched Cℓ fails to reproduce D at comparable rate, and
2) ΛCDM lensing simulations + the same reconstruction pipeline fail to reproduce D, and
3) the signal replicates across alternative estimators / masks / data splits.

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
