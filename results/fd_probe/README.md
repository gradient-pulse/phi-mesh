# FD Probe Results

This folder contains **Numerical Turbulence Rhythm (NT Rhythm) probe results**.  
Each file here is a machine-generated **metrics JSON** created by the FD Probe workflow, and each run emits a matching **pulse** under `pulse/auto/`.

---

## 📂 File Naming

- **Metrics JSON (date-prefixed, daily batches)**

YYYY-MM-DD___batchN.metrics.json

where:

- `YYYY-MM-DD` — run date (UTC on CI)
- `<dataset>` — sanitized dataset slug (e.g., `isotropic1024coarse`)
- `<source>` — `synthetic`, `nasa`, or `jhtdb`
- `batchN` — **sequential index per date** (`batch1`, `batch2`, …)

**Examples**

2025-09-06_isotropic1024coarse_jhtdb_batch1.metrics.json
2025-09-06_isotropic1024coarse_jhtdb_batch2.metrics.json

Batches **restart at 1 every new date**.

- **Pulse YAML (date-prefixed filename; date-free slug)**

Pulses are written to `pulse/auto/` as:

YYYY-MM-DD___batchN.yml

The slug `<dataset>_<source>_batchN` is preserved without the date to keep tags and edges stable; the filename itself carries the date.

---

## 📑 Metrics JSON Schema (minimum)

Each metrics file records NT rhythm metrics computed from the time series:

- `period` — dominant rhythm period  
- `bpm` — beats per minute equivalent  
- `main_peak_freq` — primary peak frequency  
- `peaks` — spectrum peaks  
- `divergence_ratio` — coherence vs divergence indicator  
- `reset_events` — detected resets  
- `n` — number of inter-event intervals (when available)  
- `mean_dt` — mean inter-event interval (when available)  
- `cv_dt` — coefficient of variation of inter-event intervals (when available)  
- `source` — data source (`synthetic`, `nasa`, or `jhtdb`)  
- `details` — probe metadata:
- `dataset` — dataset slug or path  
- `var` — variable name (e.g., `u`)  
- `xyz` — spatial probe location  
- `window` — time window `[t0, t1, dt]`

> Pulses **do not duplicate metrics**; they summarize (`n`, `mean_dt`, `cv_dt`) pulled from JSON.

---

## 🔗 Workflow

Created by `.github/workflows/fd_probe.yml`. Each run:

1. Pulls a time series from the selected source.  
2. Computes NT rhythm metrics.  
3. Writes date-prefixed JSON to `results/fd_probe/`.  
4. Emits a matching pulse into `pulse/auto/` with a date-prefixed filename.

---

## 🚦 Policy

- ❌ **Do not edit files here manually** — automated runs will overwrite.  
- ✅ **Launch probes via the GitHub workflow UI**.  
- 🗂 Historical runs are tracked by **date + batchN**.  
- 🧭 Batches **reset per day** for the same dataset/source pair.

---

## 🧪 Tips

- To compare runs across days, filter by `_<dataset>_<source>_batch1.metrics.json`.  
- Large runs: keep `dt` reasonable in `window` to avoid huge `n`.  
- If you need to replay with a different probe point, adjust `xyz` and the date/batch will stay traceable.
