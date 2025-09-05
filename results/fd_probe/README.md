# FD Probe Results

This folder contains **Numerical Turbulence Rhythm (NT Rhythm) probe results**.  
Each JSON file here is machine-generated and paired with a pulse YAML entry under `pulse/auto/`.

---

## 📂 File Naming

- **Metrics JSON**

  `<dataset>_<source>_batchN.metrics.json`

  - `dataset`: sanitized dataset slug (e.g. `demo`, `data_nasa_demo_timeseries.csv`)
  - `source`: one of `synthetic`, `nasa`, or `jhtdb`
  - `batchN`: sequential batch index (`batch1`, `batch2`, …)

- **Example**  
  `data_nasa_demo_timeseries.csv_nasa_batch1.metrics.json`

This ensures results remain traceable across multiple runs on the same dataset.

---

## 📑 Contents of Metrics JSON

Each metrics file records the computed NT rhythm metrics:

- `period` — dominant rhythm period  
- `bpm` — beats per minute equivalent  
- `main_peak_freq` — primary peak frequency  
- `peaks` — spectrum peaks  
- `divergence_ratio` — coherence vs divergence indicator  
- `reset_events` — detected resets  
- `source` — data source (`synthetic`, `nasa`, or `jhtdb`)  
- `details` — probe metadata:
  - `dataset`: dataset slug or path  
  - `var`: variable name (e.g. `u`)  
  - `xyz`: spatial probe location  
  - `window`: time window `[t0, t1, dt]`  

---

## 🔗 Workflow Connection

Files here can be created via **two routes**:

1. **Direct probe workflow**:  
   `.github/workflows/fd_probe.yml` (manual dispatch in GitHub Actions UI).

2. **Agent job runner**:  
   `.github/workflows/agent_fd_jobs.yml`  
   - Drop a YAML job into `inbox/fd_jobs/`  
   - Agent picks it up, runs the probe, writes metrics here, and emits a matching pulse.

Each run:
1. Pulls a time series from the selected source.  
2. Computes NT rhythm metrics.  
3. Writes JSON results into this folder.  
4. Emits a matching YAML pulse into `pulse/auto/`.  

---

## 🚦 Usage Rules

- ❌ **Do not edit files here manually** — they will be overwritten.  
- ✅ **Always launch probes via the GitHub workflow interface or the agent jobs inbox.**  
- 🗂 Historical runs are preserved with `batch1`, `batch2`, etc., for traceability.

---

## 📌 Summary

- Canonical home for **FD probe outputs**.  
- Every file links to a **pulse** for semantic tracking.  
- Naming convention = `<dataset>_<source>_batchN`.  
- Backed by **two workflows** (`fd_probe.yml` and `agent_fd_jobs.yml`) to cover both manual and agent-driven runs.
