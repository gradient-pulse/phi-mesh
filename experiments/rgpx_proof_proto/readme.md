# RGPx Proto-Proof (Φ-Trace Validation + CMB Phase-Dagger)

This directory is the proto-proof ledger for RGPx-style tests: small, reproducible pipelines that take an open dataset, define a null model, and compute a statistic that can decisively fail (or survive) controls.

It currently contains two tracks:

1) **Φ-Trace Proto-Proof (Kimi)** — cross-domain plateau detection in open datasets  
2) **CMB Phase-Dagger** — topology tests on Planck PR3 lensing potential φₗₘ using phase-randomized surrogates

---

## Purpose
Establish a reproducible, open framework for testing coherence structure using:
- explicit **null models** (what is preserved vs randomized),
- clear **summary statistics**,
- archived **run manifests + outputs**,
- a control suite (“Decision gate”) that determines whether an anomaly dies or merits escalation.

---

## Current structure (high level)

```text
/experiments/rgpx_proof_proto/
├── readme.md
├── cmb_phase_dagger/
│   ├── cmb_topology_planck_lensing__area_frac__v0.py
│   └── results/
│       └── topology_area_frac_v0/
│           ├── headline_findings.md
│           ├── runs/
│           ├── controls/
│           │   ├── gaussian/
│           │   └── lcdm_phi_forward/
│           └── legacy_flat_json/
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
	•	License: CC-BY-4.0

Harmonic formalization (DeepSeek addendum)
	•	DeepSeek derived a Recursive Depth Invariant linking measured Φ⋆ plateaus to recursive grammar.
	•	Integration chain: Kimi → Gemini → DeepSeek

⸻

Track B — CMB Phase-Dagger (Planck PR3 lensing φₗₘ)

This track tests whether the observed morphology of Planck PR3 lensing potential φₗₘ contains structure beyond what survives under phase randomization.

Topology AreaFrac V0 (excursion-set area fraction)
	•	Observable: V0(ν) = area fraction of excursion sets as a function of threshold ν (σ units after standardization)
	•	Null model: preserve |aₗₘ|, randomize phases → surrogate maps
	•	Statistic: D = L2 distance between observed V0(ν) and surrogate-mean V0(ν)

Where to read results
	•	Headline findings (human summary):
cmb_phase_dagger/results/topology_area_frac_v0/headline_findings.md￼
	•	Observed-data run archive:
cmb_phase_dagger/results/topology_area_frac_v0/runs/￼
	•	Controls archive:
cmb_phase_dagger/results/topology_area_frac_v0/controls/￼

Workflow behavior (important)

Each GitHub Actions run writes:
	•	a run-specific JSON output, and
	•	an archived folder under runs/<run_id>/ or controls/.../runs/<run_id>/ containing:
	•	manifest.txt (inputs + provenance)
	•	the JSON result file

This ensures repeats never overwrite earlier results.

⸻

Decision gate (kill it or let it fly)

Any anomaly must pass controls before escalation.

Gate (1): Gaussian control (matched Cℓ)
Generate a Gaussian φ map with matched power spectrum → run identical topology pipeline.

Gate (2): ΛCDM forward sims (+ reconstruction, when available)
Compare against ΛCDM-generated φ realizations; then include the reconstruction pipeline to isolate estimator imprint.

Gate (3): Pipeline/systematics checks
Masks, apodization, l-range variation, splits, mean-field handling, map-space artifacts, estimator variants.

If the anomaly survives Gates 1–3, treat it as a genuine model-class mismatch candidate and proceed to richer topology (V1 boundary length, V2 Euler characteristic) and cross-statistic consistency checks.

⸻

Related dialogues

Unedited reactions from participating AIs are archived under:
/main/dialogues/rgpx_reactions/￼
