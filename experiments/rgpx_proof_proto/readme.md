# RGPx Proto-Proof (Φ-Trace Validation + CMB Phase-Dagger)

This directory is the **proto-proof ledger** for RGPx-style tests: small, reproducible pipelines that take an open dataset, define a null model, and compute a statistic that can decisively **fail** (or survive) controls.

It currently contains two tracks:

1) **Φ-Trace Proto-Proof (Kimi)** — cross-domain plateau detection in open datasets  
2) **CMB Phase-Dagger** — topology tests on Planck PR3 lensing potential φₗₘ using phase-randomized surrogates

---

## Purpose
Establish a reproducible, open framework for testing **coherence conservation / coherence structure** using:
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
│           ├── runs/               # per-run folders with manifest.txt + JSON
│           └── legacy_flat_json/   # optional (older flat archived JSONs)
├── (phi_trace_proto_proof assets…)
├── 2025-11-10_kimi_notebook_colab.md
├── 2025-11-10_gemini_harmonic_link_analysis.yml
├── 2025-11-10_deepseek_harmonic_invariant.yml
└── results_summary.yml
```
## Track A — Φ-Trace Proto-Proof (Kimi)

Contents
	•	Proto-proof notebook and scripts for extracting Φ⋆ plateaus:
	•	Bayesian plateau detector for Φ⋆ ± δΦ⋆ and plateau duration Δτ
	•	Source datasets (e.g., turbulence / BEC / qubits) and associated links
	•	Summary outputs and interpretation notes

Outcome (as currently recorded)

Multiple public datasets show statistically significant Φ-plateaus reported as consistent (within stated uncertainty) with predicted RGPx values, forming an initial cross-domain replication claim.

Attribution

Authored by Kimi (Moonshot AI).
Integrated into the Φ-Mesh experiments ledger by Participant 0, November 2025.
License: CC-BY-4.0

⸻

Harmonic Formalization — DeepSeek Addendum

DeepSeek derived a Recursive Depth Invariant linking measured Φ⋆ plateaus to recursive grammar:

$$
\mathcal{R}\Phi = -\ln(1 - \Phi\star/\mathcal{K}) / \mathcal{D}
$$

with 𝒦 = 1.618 (Golden Ratio).
Integration chain: Kimi (Φ-Trace Proto-Proof) → Gemini (Harmonic Framework) → DeepSeek (Harmonic Invariant)

⸻

## Track B — CMB Phase-Dagger (Planck PR3 lensing φₗₘ)

This track tests whether the observed morphology of Planck PR3 lensing potential φₗₘ contains structure beyond what survives under phase randomization.

Topology AreaFrac V0 (excursion-set area fraction)
	•	Observable: V0(ν) = area fraction of excursion sets as a function of threshold ν (in σ units after standardization)
	•	Null model: preserve |aₗₘ|, randomize phases → generate surrogate maps
	•	Statistic: D = L2 distance between observed V0(ν) and surrogate-mean V0(ν)

Where to read the current result
	•	Headline findings:
cmb_phase_dagger/results/topology_area_frac_v0/headline_findings.md
	•	Per-run archive (JSON + manifest):
cmb_phase_dagger/results/topology_area_frac_v0/runs/<run_id>/

Workflow behavior (important)

GitHub Actions runs write:
	•	a result JSON (run-specific filename), and
	•	a per-run folder under runs/<run_id>/ containing:
	•	manifest.txt (inputs + provenance)
	•	the run JSON result

This ensures repeats never overwrite earlier results.

⸻

Decision gate (kill it or let it fly)

Any anomaly in this folder must pass a control suite before escalation. For CMB Phase-Dagger, the immediate gate is:
	1.	Gaussian control: generate a Gaussian φ map with the same power spectrum → run identical topology pipeline
	2.	ΛCDM lensing sims: replace Planck φₗₘ with standard simulation products → compare p-value behavior
	3.	Pipeline/systematics checks: masking, apodization, l-range variations, map-space artifacts, mean-field handling

If the anomaly survives 1–3, treat it as a genuine model-class mismatch candidate and proceed to richer topology (V1 boundary length, V2 Euler characteristic) and cross-statistic consistency checks.

⸻

Related Dialogues

Unedited reactions from participating AIs are archived under:
/main/dialogues/rgpx_reactions/

---

### Two small notes (based on what you showed)

1) Your `headline_findings.md` living under  
`.../cmb_phase_dagger/results/topology_area_frac_v0/`  
is exactly right. Keep it there.

2) Moving the older flat JSONs into `legacy_flat_json/` is fine — **as long as** the `runs/<run_id>/` structure remains the canonical record going forward.

When you’re ready to continue the Decision gate tests, tell me which control you want first (Gaussian control vs ΛCDM lensing sims), and I’ll give you the exact next workflow/run parameters + what to record.
