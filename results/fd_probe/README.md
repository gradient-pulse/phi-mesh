# FD Probe Results

This folder contains **FD Probe Numerical Turbulence Rhythm (NT Rhythm) results**, generated from JHTDB, NASA, or synthetic probe data.

---

## 📂 File Naming

- **Metrics JSON (date-prefixed, daily batches)**

YYYY-MM-DD__batchN.metrics.json

where:  
- `YYYY-MM-DD` — run date (UTC on CI)  
- `<slug>` — dataset ID (e.g., `isotropic1024coarse_jhtdb`)  
- `batchN` — sequential index per date (`batch1`, `batch2`, …)  

**Example:**  

2025-09-06_isotropic1024coarse_jhtdb_batch1.metrics.json

- **Pulse YAML (date-prefixed filename; date-free slug)**

pulse/auto/YYYY-MM-DD__batchN.yml

---

## 📑 JSON Schema (minimum)

- `period` — dominant rhythm period  
- `bpm` — beats per minute equivalent  
- `main_peak_freq`, `peaks`  
- `divergence_ratio`, `reset_events`  
- `n`, `mean_dt`, `cv_dt`  
- `source` — jhtdb / nasa / synthetic  
- `details{dataset,var,xyz,window}`  

---

## 🔗 Workflow

Created by `.github/workflows/fd_probe.yml`.  
Each run:  
1. Loads probe data from JHTDB/NASA/synthetic.  
2. Computes NT rhythm metrics.  
3. Writes metrics JSON to `results/fd_probe/`.  
4. Emits a matching pulse under `pulse/auto/`.

