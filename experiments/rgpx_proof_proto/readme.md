# RGPx Proto-Proof (Φ-Trace Validation + CMB Phase-Dagger)

This directory is the **proto-proof ledger** for RGPx-style tests: small, reproducible pipelines that take an open dataset, define a null model, and compute a statistic that can decisively **fail** (or survive) controls.

It currently contains two tracks:

1) **Φ-Trace Proto-Proof (Kimi)** — cross-domain plateau detection in open datasets  
2) **CMB Phase-Dagger** — topology tests on Planck PR3 lensing potential φₗₘ using phase-aware nulls and simulation controls

---

## Horizon: why phase-aware gradient tests matter

RGPx is evaluated here by **operational advantage**: does a gradient-/phase-aware description expose structure, constraints, or design degrees-of-freedom faster or more reliably than amplitude-only / metric-first summaries?

This matters beyond cosmology. Many modern breakthroughs already look “gradient-based” in practice (optimization landscapes, field coherence, flow control, learned surrogates). The under-explored step in mainstream tooling is **gradient-phase-based** design: treating phase relationships as first-class structure rather than residual detail.

A present-day engineering indicator is **LEAP 71**, where machine learning discovers high-performance designs rapidly compared to traditional iteration-heavy pipelines. This repo’s purpose is to build the *measurement and control* side of that direction: rigorous null-model tests and small pipelines that can validate (or falsify) when phase structure carries actionable information.

In physics terms, the long-horizon claim RGPx aims to stress-test is whether **conservation of gradient coherence** provides a useful organizing principle in regimes where conventional approaches remain fragmented (quantum–macro links, black holes, dark sector, supercluster dynamics, and early-universe phase behavior). Individual gates (like the Planck lensing workflow) are not “make-or-break” for the framework; they are probes for where operational advantage does—and does not—appear.

---

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

## Collaboration Protocol (how we work)

This repo is the traceable premise. Chat is used to draft hypotheses, interpret deltas, and propose the *next minimal falsification step* — but conclusions only “count” once they are written into versioned artifacts here.

Operating rules:
1) **Run Cards only:** each new run is summarized as a compact Run Card in `cmb_phase_dagger/notes/` (run_id, settings, gate, outputs, paths).
2) **One-change steps:** each iteration changes *one* control knob (mask / ℓ-range / estimator / sim list / null) so attribution stays clean.
3) **Curves → GC features:** we prioritize curve-shape descriptors (ν_peak, width, bump count, ℓmax drift) over single scalar distances when deciding Gate 3.
4) **Manifest-driven sims:** end-to-end ΛCDM recon controls are driven by explicit manifests (`data/.../manifest.txt`) committed to the repo.
5) **Memo stays current:** `notes/ops_advantage_memo.md` is updated when a gate changes state (PASS/FAIL/OPEN).
	
---

## Purpose

Method note: We are not “trying to make the CMB confirm RGPx.” We measure operational advantage: which statistics remain informative after the strongest end-to-end controls.

Establish a reproducible, open framework for testing **coherence structure** using:

- explicit **null models** (what is preserved vs randomized),
- clear **summary statistics**,
- archived **run manifests + outputs**,
- a control suite (“Decision gates”) that determines whether an anomaly dies or merits escalation.

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

⸻

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

This track evaluates whether Planck PR3 reconstructed lensing potential φₗₘ exhibits phase-sensitive morphology relative to nulls and end-to-end simulation controls.

### Published output (CMB track)
- **CMB Evidence for Pre-Metric Physics: Operational Advantage from Extending Metric Physics**  
  DOI: https://doi.org/10.5281/zenodo.18759993

This paper reports the current CMB-track result in a method-first format: morphology-sensitive diagnostics provide **operational advantage** for cohort discrimination in the Planck PR3 lensing workflow, while keeping interpretation conservative (no claim of a new cosmological model or unique mechanism).

Where to read results
	•	Headline findings (human summary): cmb_phase_dagger/results/headline_findings.md
	•	Observed-data run archive: cmb_phase_dagger/results/topology_*/runs/
	•	Controls archive: cmb_phase_dagger/results/topology_*/controls/

⸻

Workflow behavior (important)

Each GitHub Actions run produces:
	1.	Staged outputs under:

	•	results/cmb_topology_area_frac_v0/ or results/cmb_topology_mf_v0_v1/
	•	per-run JSON output(s)

	2.	An archived copy committed into the repo under:

	•	.../results/topology_*/*/runs/<run_id>/ (observed runs), or
	•	.../results/topology_*/controls/<control_name>/runs/<run_id>/ (controls),

containing:
	•	manifest.txt (inputs + provenance; includes run_note when provided)
	•	JSON result file(s)

This ensures repeated runs never overwrite earlier outputs and every result is provenance-traceable.

Parallel runs (important)

Many workflows set a concurrency group to prevent parallel runs from colliding (especially when a workflow commits results back into main). If you want to run parameter sweeps in parallel, use either:
	•	a unique concurrency group per sweep, or
	•	an input-driven concurrency key (e.g., include lmax), or
	•	disable repo-committing in the job and archive only as artifacts (then commit later).

(Parallelism is optional; correctness + provenance comes first.)

⸻

Control suite (attribute → validate → escalate)

The purpose of the control suite is not to “win” or “lose” a signal.
It is to attribute a measured effect to one of three sources:
	1.	null-model structure (what the test preserves by design)
	2.	pipeline imprint (reconstruction/estimator/mask/noise effects)
	3.	genuine generative mismatch (model-class gap: the data contain structure not reproduced by the best available forward model under the same measurement process)

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

Topology pipelines (current)

A) AreaFrac V0 (excursion-set area fraction)
	•	Observable: V0(ν) = area fraction of excursion sets as a function of threshold ν
(ν in σ units after standardization)
	•	Null model (phase-random): preserve |aₗₘ|, randomize phases → surrogate maps
	•	Statistic: D = L2 distance between V0_obs(ν) and surrogate-mean V0̄(ν)
(larger D ⇒ stronger phase-sensitive morphology relative to the null)

Status: AreaFrac V0 shows a strong deviation versus the phase-only surrogate null at lmax=256, nside=256, but this anomaly is resolved once ΛCDM simulations are passed through the reconstruction pipeline (Gate 2B). Therefore AreaFrac V0 is currently best treated as pipeline-/reconstruction-sensitive, not a discriminant of generative mismatch.

B) MF V0+V1 (AreaFrac + perimeter proxy)

This pipeline evaluates morphology using:
	•	V0(ν): excursion-set area fraction
	•	V1(ν): a perimeter proxy estimated from gradient magnitude |∇x| in a narrow band around each threshold ν

Distance metric (corrected)
MF V0+V1 reports proper L2 distances on the ν-grid:

[
D = \sqrt{\sum_{\nu} (C_{\rm obs}(\nu)-\bar{C}(\nu))^2 , d\nu}
]

Legacy “sum of squares” values (no √, no dν) are retained only for backward comparison as:
	•	D0_sum_sq_legacy
	•	D1_sum_sq_legacy

Pipeline validity: PASS
	•	The output includes verify_l2_from_curves, which recomputes D0/D1 directly from the stored curves and checks exact agreement.
	•	A self-test mode exists: observed := one phase-random surrogate, expected to yield non-significant p-values.

Current gate status (MF V0+V1)
	•	Gate 0 — Mechanical sanity (L2 correctness + self-test): PASS
	•	Gate 1 — Gaussian Cℓ-matched control: PASS (non-extreme p-values across an ℓmax sweep)
	•	Gate 2B — ΛCDM end-to-end recon control (MF analogue of AreaFrac Gate 2B): PASS (preliminary; N=3)
	•	Gate 3 — Robustness / null adequacy / splits / masks / ℓ-sensitivity: OPEN
	•	Attribution: pipeline-/reconstruction-consistent at lmax=256, nside=256 (N=3); robustness + larger N pending

The exact run registry and interpretation state live in:
	•	cmb_phase_dagger/results/headline_findings.md

⸻

Where run notes go

Run notes belong in manifest files alongside the archived result:
	•	.../runs/<run_id>/manifest.txt

Workflows should accept an optional run_note input and write it into the manifest for provenance and searchability (especially for parameter sweeps like ℓmax).

⸻

Related dialogues

Unedited reactions from participating AIs are archived under:

/main/dialogues/rgpx_reactions/

(These are not considered evidence; they are archived as idea-surface and for traceability.)
