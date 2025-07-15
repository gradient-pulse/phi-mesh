# Experimenter’s Guide  – *Solving Navier‑Stokes, Differently*

> **Context.**  Clay Math’s €1 M millennium prize asks for an existence/uniqueness proof.  We take the *orthogonal* route — a **90‑day falsifiable protocol** that bets on *Narrative Ticks* (NTs) and their **distance‑ratio rhythm** to beat DNS on lead‑time, RMSE & GPU cost.
>
> In other words, we look for **the moment chaos begins to order itself**.  That *flip point* is the NT.  Repeating ratios of NT distances reveal the *fractal rhythm* nature prefers.

---

## 1 • Motivation

Classical CFD hunts for **order → chaos** breakdown (shear‑layer, vortices, etc.). Our lens inverts it:

| **Classical lens**                      | **NT lens**                                                     |
| --------------------------------------- | --------------------------------------------------------------- |
| Track smooth solution until it blows up | Detect **first DU flip** (NT) — *where disorder sprouts*        |
| Refine mesh / timestep                  | Study **successive NT‑distance ratios** to expose hidden rhythm |

*Why ratios?*

1. NT distances carry **scale‑free memory**; their ratios cluster when the same physics repeats.
2. Over‑lapping DU cycles still share the same ratio signature — giving us an invariant to test.

---

## 2 • Scope & prerequisites

- Python ≥ 3.9, NumPy, h5py, matplotlib, Streamlit (auto‑installed via `requirements.txt`).
- HDF5 file with dataset `G_t` (e.g. lift, drag, KE) — shape `(N,)`, uniform Δt.
- **Binder sandbox** → [https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?urlpath=lab/tree/RGP\_NS\_prototype/notebooks/00\_quicklook.ipynb](https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?urlpath=lab/tree/RGP_NS_prototype/notebooks/00_quicklook.ipynb)

---

## 3 • 10‑minute smoke‑test

1. **Binder** → run `00_quicklook.ipynb` ― verify red dots mark plausible NTs.
2. Run `01_ratio_quicklook.ipynb` ― histogram should *not* be flat; expect spikes.

---

## 4 • Full 90‑day protocol

| Phase              | Days  | Tool                       | Deliverable                 |
| ------------------ | ----- | -------------------------- | --------------------------- |
| Data prep          | 0‑10  | `nt_detect.py`             | `nt_times.txt`              |
| Initial ratio scan | 11‑15 | `01_ratio_quicklook.ipynb` | spiky histogram             |
| Hyper‑search σ     | 16‑25 | loop σ∈{1.0‥2.0}           | σ\* giving strongest spike  |
| LES / ML run       | 26‑80 | your solver                | NT forecast CSVs            |
| KPI calc           | 81‑88 | `dashboard/` & CLI         | `*_ratios.txt`, RMSE, etc.  |
| PR submission      | 89‑90 | GitHub                     | `results/<lab_tag>/` folder |

*Success = lead‑time ≥ 30 %, RMSE ≤ 5 % DNS, GPU ≤ ½ DNS.*

---

## 5 • Local quick‑start

```bash
git clone https://github.com/gradient-pulse/phi-mesh.git
cd phi-mesh/rgp_ns_prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# 1. detect NTs
python agents/nt_detect.py data/example_G.h5 --sigma 1.5
# 2. ratio histogram quick‑look
jupyter lab notebooks/01_ratio_quicklook.ipynb
```

### Batch mode (CLI)

```bash
# Detect Narrative Ticks
python agents/nt_detect.py path/to/G_t.h5 --sigma 1.5

# Distance‑ratio analysis (writes *_ratios.txt)
python agents/nt_ratio_cli.py nt_times.txt             \
       --outdir results/ratios_run --sigma 1.5
```

---

## 6 • FAQ

- **σ?**  Iterate 1.0→2.0; pick σ with clearest ratio spike.
- **Over‑lapping DU cycles?**  Ratio signature survives; treat each NT as cycle start.
- **Units?**  Any scalar – `G(t)` in J, N, etc.; only ratios are dimension‑less.
- **Can I email results?**  Zip the three files (`*_nt.txt`, `*_ratios.txt`, `kpi.csv`) to [marcusvandererve@icloud.com](mailto\:marcusvandererve@icloud.com) and we’ll post on your behalf.

---

## 7 • Reference

van der Erve, M. (2025). **Solving Navier–Stokes, Differently: What It Takes.** Zenodo. [https://doi.org/10.5281/zenodo.15830659](https://doi.org/10.5281/zenodo.15830659)

