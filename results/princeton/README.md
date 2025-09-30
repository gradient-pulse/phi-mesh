# Probe Results

This directory contains **Numerical Turbulence Rhythm (NT Rhythm) probe results**, from multiple sources:  

- **FD Probe (JHTDB / NASA / synthetic)**  
- **Princeton probe (subset CSV or demo synthetic)**  

Each run produces:  

- a machine-generated **metrics or analysis JSON** under `results/*/`  
- a companion **figure folder** (`.analysis/`) with time/spectrum plots  
- a matching **pulse** under `pulse/auto/`  

---

## 📂 File Naming

- **Metrics/Analysis JSON (date-prefixed, daily batches)**

YYYY-MM-DD_batchN.metrics.json    # FD Probe
YYYY-MM-DD_batchN.analysis.json   # Princeton

where:  
- `YYYY-MM-DD` — run date (UTC on CI)  
- `<slug>` — sanitized dataset or subset identifier (`isotropic1024coarse_jhtdb`, `demo_princeton`, etc.)  
- `batchN` — sequential index per date (`batch1`, `batch2`, …)  

**Examples**  

2025-09-06_isotropic1024coarse_jhtdb_batch1.metrics.json
2025-09-30_demo_princeton_batch1.analysis.json

Batches **restart at 1 every new date**.

- **Pulse YAML (date-prefixed filename; date-free slug)**  

Pulses are written to `pulse/auto/` as:  

YYYY-MM-DD__batchN.yml

Inside, the slug is stored without the date to keep tags and edges stable.  

---

## 📑 JSON Schemas (minimum)

- **FD Probe Metrics JSON**  
- `period`, `bpm`, `main_peak_freq`, `peaks`  
- `divergence_ratio`, `reset_events`  
- `n`, `mean_dt`, `cv_dt`  
- `source`, `details{dataset,var,xyz,window}`  

- **Princeton Analysis JSON**  
- `label`, `meta{subset_path,probe}`  
- `n`, `dt`, `component`  
- `dominant{freq_hz,power}`  
- `figures{time_png,spectrum_png}`  

> Pulses **do not duplicate metrics**; they summarize key values pulled from JSON.

---

## 🔗 Workflows

Created by GitHub Actions workflows:  

- `.github/workflows/fd_probe.yml` — FD Probe (JHTDB/NASA/synthetic)  
- `.github/workflows/gold_path.yml` — Princeton (subset/demo synthetic)  

Each run:  
1. Loads probe data.  
2. Computes NT rhythm metrics or Princeton analysis.  
3. Writes JSON + figures to `results/`.  
4. Emits a matching pulse under `pulse/auto/`.  

---

## 🚦 Policy

- ❌ **Do not edit result files manually** — automated runs overwrite.  
- ✅ **Launch probes via the GitHub workflow UI**.  
- 🗂 Historical runs are tracked by **date + batchN**.  
- 🧭 Batches reset daily per dataset/slug.  

---

## 🧪 Tips

- To compare across days, filter by `_batch1` runs.  
- For Princeton: check both `analysis.json` and the `.analysis/` folder for figures.  
- For FD: keep `dt` in check to avoid very large `n`.  
