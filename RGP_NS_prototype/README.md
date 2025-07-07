
# RGP‑NS Prototype

Reference implementation for **Solving Navier–Stokes, Differently: What It Takes** (DOI 10.5281/zenodo.15793567).

*Launch Binder ▶️* &nbsp; <a href="https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?labpath=rgp_ns_prototype%2Fnotebooks%2F00_quicklook.ipynb"><img src="https://mybinder.org/badge_logo.svg"></a>

## Layout
```
rgp_ns_prototype/
├─ agents/          # autonomous helpers: data pull, NT detect, validator
├─ notebooks/       # 00_quicklook.ipynb demo
├─ dashboard/       # simple Streamlit app
└─ README.md
```

## Quick‑start (local)

```bash
git clone https://github.com/gradient-pulse/phi-mesh.git
cd phi-mesh/rgp_ns_prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agents/nt_detect.py data/example_G.h5 --sigma 1.5
streamlit run dashboard/app.py
```
