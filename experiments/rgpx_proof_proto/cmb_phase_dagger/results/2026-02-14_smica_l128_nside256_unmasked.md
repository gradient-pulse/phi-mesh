# CMB Phase Dagger — SMICA (Planck PR3) — Run 2026-02-14

## Data
- Product: Planck PR3 SMICA full-sky temperature FITS
- URL: (paste the `fits_url` you used)
- Field: 0 (temperature)
- Mask: disabled (mask_field=false)
- lmax: 128
- nside: 256

## Null / test
- Surrogates: phase randomization (amplitude preserved)
- n_sims: 10000
- Metric: variance of Rao-U bin means over 8 l-bins

## Result
- observed_metric: 0.01604148
- null_mean: 0.00659674
- null_p95: 0.01781757
- p_value_one_sided_high: 0.06719
- z_score: 1.745

## Interpretation
Not significant (p > 0.01). Under this dagger, “primordial phase-structure / coherence” is **not supported**.

## Provenance
- Workflow run: (paste Actions run link)
- Artifact: cmb_phase_dagger_report.zip

```
{
  "inputs": {
    "fits": "smica.fits",
    "field": 0,
    "mask_field": null,
    "mask_thresh": 0.9,
    "lmax": 128,
    "nside": 256,
    "n_sims": 10000,
    "seed": 1,
    "n_bins": 8
  },
  "observed_metric": 0.016041481470014378,
  "null_summary": {
    "null_mean": 0.006596737754938097,
    "null_std": 0.005412181578802761,
    "null_p95": 0.01781756797889518,
    "null_p99": 0.02532607017110608,
    "n_sims": 10000
  },
  "p_value_one_sided_high": 0.06719328067193281,
  "z_score": 1.745089956343551,
  "observed_extras": {
    "mean_RaoU_overall": 2.2589830035246443,
    "var_RaoU_overall": 0.07340682928648076,
    "bin_means": [
      1.9653292868104812,
      2.22462486212245,
      2.3105137444693535,
      2.388493284950748,
      2.280798155908137,
      2.250173538291609,
      2.3120428977035576,
      2.3061281126733344
    ]
  },
  "notes": {
    "interpretation": "If p_value is not small (e.g., >0.01), this particular phase-coherence dagger does NOT support a primordial phase-structure claim.",
    "mask_note": "If mask field is missing, run proceeds unmasked. For robustness, later add a dedicated Planck common mask FITS and pass it explicitly."
  }
```
