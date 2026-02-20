## Operational Advantage Memo — Planck PR3 φₗₘ Topology via RGPx Grammar (Δ → GC → CF → UD)

**Objective:** Demonstrate operational advantage of RGPx grammar (Δ → GC → CF → UD) on CMB lensing φₗₘ morphology, while keeping attribution falsifiable under end-to-end ΛCDM controls.

### RGPx grammar mapping
- **Δ (gradients):** MF V1 perimeter proxy from |∇x| in ν-bands; Δ strength increases with ℓmax.
- **GC (gradient choreographies):** stable features of V1(ν) and V0(ν) across controlled perturbations (ν_peak, width, inflections, ℓmax drift).
- **CF (contextual filters):** reconstruction pipeline elements that imprint GC features (mask/apod, mean-field, estimator couplings, noise).
- **UD cycles:** bifurcations in GC stability as CF knobs change (mask variant flips ν_peak; ℓ-range toggle breaks shape correlation).

### Current status
- **AreaFrac V0:** anomaly vs phase-only null exists, but **resolved by end-to-end ΛCDM+recon** (Gate 2B overlap). Therefore V0(D) is **CF-sensitive**, not a generative mismatch.
- **MF V0+V1:** strong deviation vs phase-only null; Gaussian Cℓ-matched control passes; preliminary end-to-end ΛCDM+recon (N=3) overlaps → **Gate 3 OPEN**.

### Operational advantage already demonstrated
- The analysis correctly predicts that “φ alone” is not the object; **φ filtered by the measurement chain (CF) is the object**. The pipeline can *locate* CF-driven morphology and set up controlled isolation.

### Next falsification target
- Promote from “D is high” to “GC features are unmodeled after end-to-end controls.”
- Required: **ΛCDM+recon sims N≥20** and **GC-feature envelope** comparison:
  - {ν_peak, peak width, bump count/inflections, ℓmax drift, curve-shape correlation}.

### Next actions (minimal)
1) Download + index more recon sims from GitHub Release.
2) Run MF Gate 2B with N≥20 at ℓmax sweep (128/192/256/320).
3) Compare observed vs sim envelope on GC features, not just D_mf.
