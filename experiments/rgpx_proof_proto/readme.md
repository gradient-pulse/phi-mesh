# RGPx Proto-Proof (Φ-Trace Validation + CMB Phase-Dagger)

This directory is the **proto-proof ledger** for RGPx-style tests: small, reproducible pipelines that take an open dataset, define a null model, and compute a statistic that can decisively **fail** (or survive) controls.

It currently contains two tracks:

1) **Φ-Trace Proto-Proof (Kimi)** — cross-domain plateau detection in open datasets  
2) **CMB Phase-Dagger** — topology tests on Planck PR3 lensing potential φₗₘ using phase-randomized surrogates

## Horizon: why phase-aware gradient tests matter

RGPx is evaluated here by **operational advantage**: does a gradient-/phase-aware description expose structure, constraints, or design degrees-of-freedom faster or more reliably than amplitude-only / metric-first summaries?

This matters beyond cosmology. Many successful modern breakthroughs already look “gradient-based” in practice (optimization landscapes, field coherence, flow control, learned surrogates). The next step—still under-explored in mainstream tooling—is **gradient-phase-based** design: treating phase relationships as first-class structure rather than residual detail.

A present-day engineering indicator is **[Leap 71](chatgpt://generic-entity?number=0)**, where machine learning discovers high-performance designs rapidly compared to traditional iteration-heavy pipelines. This repo’s purpose is to build the *measurement and control* side of that direction: rigorous null-model tests and small pipelines that can validate (or falsify) when phase structure carries actionable information.

In physics terms, the long-horizon claim RGPx aims to stress-test is whether **conservation of gradient coherence** provides a useful organizing principle in regimes where conventional approaches remain fragmented (quantum–macro links, black holes, dark sector, supercluster dynamics, and early-universe phase behavior). Individual gates (like the [Planck](chatgpt://generic-entity?number=1) lensing workflow) are not “make-or-break” for the framework; they are probes for where operational advantage does—and does not—appear.

---

## Purpose

Method note: We are not “trying to make the CMB confirm RGPx.” We measure operational advantage: which statistics remain informative after the strongest end-to-end controls.

Establish a reproducible, open framework for testing **coherence structure** using:

- explicit **null models** (what is preserved vs randomized),
- clear **summary statistics**,
- archived **run manifests + outputs**,
- a control suite (“Decision gate”) that determines whether an anomaly dies or merits escalation.

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

A practical analogue already exists in engineering: AI-driven generative design can find high-performing geometries far faster than traditional iteration loops. [LEAP 71](chatgpt://generic-entity?number=0) is a visible example of this direction (“computational engineering” applied to real hardware). We treat such work as a present-day *carrot*: proof that geometry can be discovered via search/learning regimes that outperform manual design—not proof of RGPx, but a reminder of what “operational advantage” looks like in practice.

---

## Current structure (high level)

```text
/experiments/rgpx_proof_proto/
├── readme.md
├── cmb_phase_dagger/
│   ├── cmb_topology_planck_lensing__area_frac__v0.py
│   ├── notes/
│   └── results/
│       └── topology_area_frac_v0/
│           ├── headline_findings.md
│           ├── runs/
│           ├── controls/
│           │   ├── gaussian/
│           │   ├── lcdm_phi_forward/
│           │   └── lcdm_recon/
│           └── legacy_flat_json/
├── 2025-11-10_kimi_notebook_colab.md
├── 2025-11-10_gemini_harmonic_link_analysis.yml
├── 2025-11-10_deepseek_harmonic_invariant.yml
└── results_summary.yml
```
## Track A — Φ-Trace Proto-Proof (Kimi)

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

## Track B — CMB Phase-Dagger (Planck PR3 lensing φₗₘ)

This track evaluates whether Planck PR3 reconstructed lensing potential φₗₘ exhibits **phase-sensitive morphology** relative to a **phase-random null**.  
It does **not** by itself imply “new physics”: any deviation can be produced by expected lensing non-Gaussianity and/or reconstruction-pipeline imprint.

### Topology: AreaFrac V0 (excursion-set area fraction)

- **Observable:** V0(ν) = area fraction of excursion sets as a function of threshold ν  
  (ν in σ units after standardization)
- **Null model (phase-random):** preserve |aₗₘ|, randomize phases → surrogate maps
- **Statistic:** D = L2 distance between V0_obs(ν) and surrogate-mean V0̄(ν)  
  (larger D ⇒ stronger phase-sensitive morphology relative to the null)

### Where to read results
- **Headline findings (human summary):** `headline_findings.md`
- **Observed-data run archive:** `runs/`
- **Controls archive:** `controls/`

### Workflow behavior (important)

Each GitHub Actions run produces:
1) **Staged outputs** under `results/cmb_topology_area_frac_v0/`  
   - per-sim JSON files  
   - an aggregate summary JSON (when multiple sims are processed)
2) **An archived copy committed into the repo** under  
   - `.../results/topology_area_frac_v0/runs/<run_id>/` (observed runs), or  
   - `.../results/topology_area_frac_v0/controls/.../runs/<run_id>/` (controls),  
   containing:
   - `manifest.txt` (inputs + provenance)
   - JSON result file(s)

This ensures repeated runs never overwrite earlier outputs and every result is provenance-traceable.

⸻
## Control suite (attribute → validate → escalate)

The purpose of the control suite is not to “win” or “lose” a signal.  
It is to **attribute** a measured effect to one of three sources:

1) **null-model structure** (what the test preserves by design),  
2) **pipeline imprint** (reconstruction/estimator/mask/noise effects), or  
3) **genuine generative mismatch** (a model-class gap: the data contain structure not reproduced by the best available forward model under the same measurement process).

Only after (1) and (2) are excluded do we escalate to (3).

### Gate 1 — Gaussian control (matched Cℓ)
Generate Gaussian φ with matched Cℓ and run the identical topology pipeline.  
**Goal:** verify the statistic is not trivially driven by the two-point spectrum alone.

### Gate 2 — ΛCDM simulation controls
**2A) φ forward draws (no reconstruction)**  
Run the statistic on ΛCDM φ realizations *before* any reconstruction.  
**Goal:** establish the morphology scale expected from ΛCDM φ itself.

**2B) End-to-end: ΛCDM forward sims + reconstruction pipeline**  
Simulate the full measurement chain and apply the same reconstruction method used for the data.  
**Goal:** determine whether the observed morphology is reproduced by ΛCDM once estimator/pipeline imprint is included.

### Gate 3 — Robustness and systematics probes
Mask/apodization changes, ℓ-range variation, splits (half-mission / frequency / estimator variants), mean-field handling, map-space artifacts.  
**Goal:** test stability of the statistic under plausible analysis choices and known sources of systematics.

### Escalation criterion
We treat “model-class mismatch” (and thus motivation for RGPx-style alternatives) as admissible only if:
1) Gaussian matched-Cℓ controls do not reproduce the effect, and  
2) ΛCDM end-to-end (including reconstruction) does not reproduce the effect, and  
3) the effect is stable under robustness probes and estimator variants.

This keeps the program scientific: the objective is **attribution first**, then **mechanism**, then **new explanatory leverage**.

---

## Status: Planck PR3 lensing φ_lm topology test (MF V0+V1)

We now have a **sanity-checked pipeline** for the morphology test:

- **Distance metric corrected**: report uses proper L2 distance  
  \( D = \sqrt{\sum_\nu (C_{\rm obs}(\nu)-\bar{C}(\nu))^2 \, d\nu} \)  
  Legacy “sum of squares” distances are retained only for backward comparison as `*_sum_sq_legacy`.

- **Internal verification added**: the output includes a `verify_l2_from_curves` block that recomputes D0/D1 from the stored curves and checks exact agreement.

### Gates (current)
- **Gate 2B (pipeline validity / distance correctness): PASS**  
  Verified by `verify_l2_from_curves` and a self-test run where the “observed” map is replaced by a phase-random surrogate; results land near surrogate means with non-significant p-values.

- **Gate 3 (null adequacy / scientific comparability): OPEN**  
  The observed Planck PR3 lensing φ_lm morphology is highly deviant **relative to the phase-only surrogate null** (surrogates preserve |a_lm| but randomize phases for m>0, keeping m=0 fixed).  
  Distribution diagnostics suggest the deviation is **not** driven by skew/heavy tails:
  - `v1_symmetry_corr ≈ 0.994`
  - `skew_x_obs ≈ 0.029`
  - `excess_kurt_x_obs ≈ -0.103`

### Reproducible runs (lmax=256, nside=256, n_sims=2000, seed=731)
- Observed (no selftest): run_id `22174563334` (p_two_sided_mf ≈ 0.001)
- Self-test (selftest_observed_surrogate_seed=123): run_id `22175256542` (p_two_sided_mf ≈ 0.788)

⸻

Related dialogues

Unedited reactions from participating AIs are archived under:

/main/dialogues/rgpx_reactions/

(These are not considered evidence; they are archived as idea-surface and for traceability.)
