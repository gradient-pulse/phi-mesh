# RGP-NS Prototype

Reference implementation for **Solving Navier–Stokes, Differently** (DOI: https://doi.org/10.5281/zenodo.15793567).

- **Launch Binder:** open `notebooks/00_quicklook.ipynb` (no install)
- **Live KPI dashboard:** https://rgp-dashboard.streamlit.app
- **Leaderboard:** schema + dummy in `results/` — submit a PR

---

## Layout

```text
rgp_ns_prototype/
├─ agents/          # data pull, NT detect, validator
├─ notebooks/       # 00_quicklook.ipynb demo
├─ dashboard/       # Streamlit app
└─ README.md

---

## Quick start (local)

```bash
git clone https://github.com/gradient-pulse/phi-mesh.git
cd phi-mesh/rgp_ns_prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agents/nt_detect.py data/example_G.h5 --sigma 1.5
streamlit run dashboard/app.py
