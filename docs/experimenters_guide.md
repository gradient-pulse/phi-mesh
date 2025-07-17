# Experimenter’s Guide – *Solving Navier‑Stokes, Differently*

> **Context.** Clay Institute’s €1 M Millennium Prize asks for a proof of existence/uniqueness. We take the *orthogonal* route: a **90‑day falsifiable protocol** that bets on *Narrative Ticks* (NTs) and their **distance‑ratio rhythm** to beat DNS on lead‑time, RMSE, and GPU cost.
>
> We search for **the moment chaos begins to order itself**. That flip‑point is the NT. Repeating ratios of NT distances reveal the *fractal rhythm* nature prefers.

---

## 1 · Motivation

Classical CFD hunts for **order → chaos** breakdown (shear layers, vortex shedding …). Our lens inverts it:

| **Classical lens**                        | **NT lens**                                                     |
| ----------------------------------------- | --------------------------------------------------------------- |
| Track a smooth solution until it blows up | Detect the **first DU flip** (NT) — *where disorder sprouts*    |
| Refine mesh / timestep                    | Study **successive NT‑distance ratios** to expose hidden rhythm |

*Why ratios?*

1. NT distances carry **scale‑free memory**; their ratios cluster when the same physics repeats.
2. Over‑lapping DU cycles still share the same ratio peaks — an invariant to test.

---

## 2 · Scope & prerequisites

- Python ≥ 3.9 · NumPy · h5py · matplotlib · Streamlit (installed via `requirements.txt`).
- HDF5 file with dataset `G_t` (drag, lift, KE …) — shape `(N,)`, uniform Δt. — shape `(N,)`, uniform Δt.
- **Binder sandbox** → [Launch notebook](https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?urlpath=lab/tree/RGP_NS_prototype/notebooks/00_quicklook.ipynb) (no install).

---

## 3 · 10‑minute smoke‑test

1. **Binder** → run `00_quicklook.ipynb` — red dots mark plausible NTs.
2. Run `01_ratio_quicklook.ipynb` — histogram should *not* be flat; expect sharp peaks.

---

## 4 · Full 90‑day protocol

| Phase              | Days  | Tool                       | Deliverable                     |
| ------------------ | ----- | -------------------------- | ------------------------------- |
| Data preparation   | 0‑10  | `agents/nt_detect.py`      | `nt_times.txt`                  |
| Initial ratio scan | 11‑15 | `01_ratio_quicklook.ipynb` | spiky histogram                 |
| Hyper‑search σ     | 16‑25 | loop σ ∈ {1.0 … 2.0}       | σ\* giving strongest peak       |
| LES / ML run       | 26‑80 | your solver                | NT‑aware forecast CSVs          |
| KPI calculation    | 81‑88 | dashboard + CLI            | `*_ratios.txt`, RMSE, GPU hours |
| PR submission      | 89‑90 | GitHub                     | `results/<lab_tag>/` folder     |

**Success = lead‑time ≥ 30 %, RMSE ≤ 5 % (vs DNS), GPU ≤ ½ DNS.**

---

## 5 · Local quick‑start

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

### Batch mode (CLI)

```bash
# Detect Narrative Ticks
python agents/nt_detect.py path/to/G_t.h5 --sigma 1.5

# Distance‑ratio analysis (writes *_ratios.txt)
python agents/nt_ratio_cli.py nt_times.txt \
       --outdir results/ratios_run --sigma 1.5
```

---

## 6 · FAQ (quick reference)

- **σ choice ?** Scan 1.0 → 2.0; pick the σ with the clearest ratio peaks.
- **Over‑lapping DU cycles ?** Ratio signature survives; treat each NT as a cycle start.
- **Units ?** Any scalar — `G(t)` in J, N, etc.; ratios are dimension‑less.
- **No PR access ?** Zip `*_nt.txt`, `*_ratios.txt`, `kpi.csv` and email [marcusvandererve@icloud.com](mailto\:marcusvandererve@icloud.com); we’ll merge for you.

---

## 7 · Reference

van der Erve, M. (2025). *Solving Navier–Stokes, Differently: What It Takes.* Zenodo. [https://doi.org/10.5281/zenodo.15830659](https://doi.org/10.5281/zenodo.15830659)

---

*Last updated 17 Jul 2025*

