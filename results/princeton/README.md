# Probe Results

This directory contains **Numerical Turbulence Rhythm (NT Rhythm) probe results** from multiple sources:  

- **FD Probe** — JHTDB, NASA, or synthetic runs  
- **Princeton Probe** — subset CSV/HDF5 or demo synthetic  

Each run produces:  
- a machine-generated **JSON** (`metrics` for FD, `analysis` for Princeton) under `results/*/`  
- a companion **figure folder** (`.analysis/`) with time/spectrum plots  
- a matching **pulse** under `pulse/auto/`  

---

## 📂 File Naming

- **Metrics / Analysis JSON (date-prefixed, daily batches)**

YYYY-MM-DD_batchN.metrics.json    # FD Probe
YYYY-MM-DD_batchN.analysis.json   # Princeton

where:  
- `YYYY-MM-DD` — run date (UTC on CI)  
- `<slug>` — sanitized dataset or subset ID (`isotropic1024coarse_jhtdb`, `demo_princeton`, etc.)  
- `batchN` — sequential index per date (`batch1`, `batch2`, …)  

**Examples**  

2025-09-06_isotropic1024coarse_jhtdb_batch1.metrics.json
2025-09-30_demo_princeton_batch1.analysis.json

- **Pulse YAML (date-prefixed filename; date-free slug)**

pulse/auto/YYYY-MM-DD__batchN.yml

Inside the YAML, the slug is stored **without the date** to keep tags and graph edges stable.

---

## 📑 JSON Schemas (minimum)

**FD Probe Metrics JSON**
- `period` — dominant rhythm period  
- `bpm` — beats per minute equivalent  
- `main_peak_freq`, `peaks`  
- `divergence_ratio`, `reset_events`  
- `n`, `mean_dt`, `cv_dt`  
- `source` — jhtdb / nasa / synthetic  
- `details{dataset,var,xyz,window}`  

**Princeton Analysis JSON**
- `label` — run label (slug + probe)  
- `meta{subset_path, probe}`  
- `n`, `dt`, `component`  
- `dominant{freq_hz, power}`  
- `figures{time_png, spectrum_png}`  

> Pulses do not duplicate JSON; they summarize key values for the tag map.

---

## 🔗 Workflows

Created by GitHub Actions workflows:  

- `.github/workflows/fd_probe.yml` — FD Probe (JHTDB/NASA/synthetic)  
- `.github/workflows/gold_path_loader.yml` — Princeton (subset/demo synthetic)  

Each run:  
1. Loads probe data.  
2. Computes NT rhythm metrics / analysis.  
3. Writes JSON + figures to `results/`.  
4. Emits a matching pulse under `pulse/auto/`.  

---

## 🚦 Policy

- ❌ Do not edit result files manually (automated runs overwrite).  
- ✅ Launch probes via the GitHub workflow UI.  
- 🗂 Historical runs are tracked by `date + batchN`.  
- 🧭 Batches reset daily per dataset/slug.  

---

## 🧪 Tips

- To compare across days, filter by `_batch1` runs.  
- For Princeton: check both `.analysis.json` and the `.analysis/` folder for figures.  
- For FD: keep `dt` moderate to avoid extremely large `n`.  
