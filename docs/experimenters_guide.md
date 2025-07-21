# Experimenter’s Guide – *Solving Navier‑Stokes, Differently*

> **Context.** Clay Institute’s €1 M Millennium Prize asks for a proof of existence / uniqueness. We take the *orthogonal* route: a **90‑day, falsifiable protocol** that bets on **Narrative Ticks (NTs)** and their **distance‑ratio rhythm** to beat DNS on lead‑time, RMSE, and GPU cost.
>
> We look for **the instant disorder begins to order itself**. That flip‑point is the NT. Repeating ratios of NT distances reveal the *fractal rhythm* nature prefers.

---

## 1 · Motivation

Classical CFD hunts for **order → chaos** breakdown (shear layers, vortex shedding …). Our lens inverts it:

| Classical lens                            | NT lens                                                            |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Track a smooth solution until it blows up | Detect the **first DU flip** (NT) — *where disorder sprouts order* |
| Refine mesh / timestep                    | Study **successive NT‑distance ratios** to expose hidden rhythm    |

**Why ratios?**

1. NT distances carry **scale‑free memory**; their ratios cluster when the same physics repeats.
2. Over‑lapping DU cycles still share the same ratio peaks — an invariant to test.

---

## 2 · Scope & Prerequisites

- Python ≥ 3.9 • NumPy • h5py • matplotlib • Streamlit (see `requirements.txt`).
- HDF5 file with dataset `G_t` (drag, lift, KE …) — shape `(N,)`, uniform Δt — the same scalar used in the NT detection. `(N,)`, uniform Δt.
- **Binder sandbox** → [Launch notebook](https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?urlpath=lab/tree/RGP_NS_prototype/notebooks/00_quicklook.ipynb) (no install).

---

## 3 · 10‑Minute Smoke‑Test

1. **Binder** → run \`\` — red dots mark candidate NTs.
2. Run \`\` — histogram should *not* be flat; look for sharp peaks.

---

## 4 · Full 90‑Day Benchmark

| Phase              | Days  | Tool                       | Deliverable                 |
| ------------------ | ----- | -------------------------- | --------------------------- |
| Data preparation   | 0‑10  | `agents/nt_detect.py`      | `nt_times.txt`              |
| Initial ratio scan | 11‑15 | `01_ratio_quicklook.ipynb` | Spiky histogram             |
| Hyper‑search σ     | 16‑25 | loop σ ∈ 1.0 – 2.0         | σ\* with strongest peaks    |
| LES / ML run       | 26‑80 | Your solver                | NT‑aware forecast CSVs      |
| KPI calculation    | 81‑88 | dashboard + CLI            | `*_ratios.txt`, RMSE, GPU h |
| PR submission      | 89‑90 | GitHub                     | `results/<lab_tag>/…`       |

**Target KPI**   lead‑time ≥ 30 %   •   RMSE ≤ 5 %   •   GPU ≤ ½ DNS

---

## 5 · Local Quick‑Start

```bash
# clone & env
git clone https://github.com/gradient-pulse/phi-mesh.git
cd phi-mesh/RGP_NS_prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1 Detect NTs
python agents/nt_detect.py data/example_G.h5 --sigma 1.5

# 2 Ratio histogram quick‑look
jupyter lab notebooks/01_ratio_quicklook.ipynb   # or use Binder
```

### Batch Mode (CLI)

```bash
# Detect Narrative Ticks
python agents/nt_detect.py path/to/G_t.h5 --sigma 1.5

# Distance‑ratio analysis (writes *_ratios.txt)
python agents/nt_ratio_cli.py nt_times.txt \
       --outdir results/ratios_run --sigma 1.5
```

---

## ❖ PoLA × NT Convergence — why the ratios matter

The **Principle of Least Action (PoLA)** is normally phrased as *"nature minimises action along a path."* In **RGP** that law appears as a **minimal‑divergence rhythm**:

> **Narrative Ticks (NTs)** mark the instant a flow chooses the *least disruptive* pivot to stay coherent. Over many flips, the **ratios between successive NT distances** expose the rhythm that minimises unnecessary gradient drift.

| **Classical PoLA**           | **RGP / NT lens**                        |
| ---------------------------- | ---------------------------------------- |
| Minimise ∫ L dt along a path | Minimise *recursive tension* between NTs |
| “Path of least action”       | “Rhythm of least divergence”             |

**Implication for experimenters →** If your NT‑distance histogram stabilises around the same ratio peaks across runs, you’re watching PoLA express itself inside turbulence.

---

## 6 · FAQ (Quick Reference)

| Question                    | Answer                                                                                                                                       |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **σ choice?**               | Scan 1.0 – 2.0; pick the σ giving the clearest ratio peaks.                                                                                  |
| **Over‑lapping DU cycles?** | Ratio signature survives; treat each NT as a cycle start.                                                                                    |
| **Units?**                  | Any scalar (`G(t)` in J, N …); ratios are dimension‑less.                                                                                    |
| **No PR access?**           | Zip `*_nt.txt`, `*_ratios.txt`, `kpi.csv` and email [marcusvandererve@icloud.com](mailto\:marcusvandererve@icloud.com); we’ll merge for you. |

---

## 7 · Reference

van der Erve, M. (2025). *Solving Navier-Stokes, Differently: What It Takes* (V1.2). Zenodo. [https://doi.org/10.5281/zenodo.15830659](https://doi.org/10.5281/zenodo.15830659)



*Last updated 21 Jul 2025*

