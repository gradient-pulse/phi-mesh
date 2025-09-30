# Princeton Probe Results

This folder contains **Princeton probe results**, generated from subset CSV/HDF5 or demo synthetic data.

---

## 📂 File Naming

- **Analysis JSON (date-prefixed, daily batches)**

YYYY-MM-DD__batchN.analysis.json

where:  
- `YYYY-MM-DD` — run date (UTC on CI)  
- `<slug>` — subset identifier (`demo_princeton`, `subsetX`, etc.)  
- `batchN` — sequential index per date (`batch1`, `batch2`, …)  

**Example:**  

2025-09-30_demo_princeton_batch1.analysis.json

- **Figures**  
Each run creates a folder:

results/princeton/YYYY-MM-DD__batchN.analysis/

containing:
- `time.png` — time series plot  
- `spectrum.png` — spectrum plot  

- **Pulse YAML (date-prefixed filename; date-free slug)**

pulse/auto/YYYY-MM-DD__batchN.yml

---

## 📑 JSON Schema (minimum)

- `label` — run label (slug + probe)  
- `meta{subset_path, probe}`  
- `n`, `dt`, `component`  
- `dominant{freq_hz, power}`  
- `figures{time_png, spectrum_png}`  

---

## 🔗 Workflow

Created by `.github/workflows/gold_path_loader.yml`.  
Each run:  
1. Loads probe subset or demo synthetic.  
2. Computes NT rhythm analysis.  
3. Writes analysis JSON + figures to `results/princeton/`.  
4. Emits a matching pulse under `pulse/auto/`.  
