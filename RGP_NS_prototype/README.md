
# RGP‑NS Prototype

Reference implementation for **Solving Navier–Stokes, Differently: What It Takes** (DOI 10.5281/zenodo.15793567).

*Launch Binder ▶️* &nbsp; <a href="https://mybinder.org/v2/gh/gradient-pulse/phi-mesh/HEAD?labpath=rgp_ns_prototype%2Fnotebooks%2F00_quicklook.ipynb"><img src="https://mybinder.org/badge_logo.svg"></a>

• Try it live → open `00_quicklook.ipynb` in Binder (no install).

• Live KPI dashboard → <https://rgp-dashboard.streamlit.app>

• KPI schema & dummy file in `results/` – submit a PR to appear on the leaderboard.

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
---
### Batch mode (CLI)

```bash
# 1. Detect Narrative Ticks
python agents/nt_detect.py path/to/G_t.h5 --sigma 1.5

# 2. Compute successive-distance ratios (writes *_ratios.txt)
python agents/nt_ratio_cli.py nt_times.txt --outdir results --sigma 1.5

python agents/nt_ratio_cli.py nt_times_run1.txt nt_times_run2.txt \
       --outdir results/ratios_run --sigma 1.5
```
➡️  For a 1-page walkthrough see the [Experimenter’s Guide](../docs/experimenters_guide.md).
