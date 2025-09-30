# GOLD PATH — Probe → Spectrum → Pulse

**Start here. Canonical pipeline for Φ-Mesh turbulence probes.**  
Two sources, one corridor:

- **Hopkins (JHTDB SOAP)** → fetch a probe → analyze (shared `pipeline/`) → emit a Φ-Mesh pulse  
- **Princeton (subset file)** → ingest local subset (CSV/HDF5) → analyze (shared `pipeline/`) → emit a Φ-Mesh pulse

---

## 1) Hopkins / JHTDB (SOAP)

**Tools**
- Loader → `tools/fd_connectors/jhtdb/jhtdb_loader.py`
- Analyzer → `tools/fd_connectors/jhtdb/analyze_probe.py`  *(uses `pipeline/`)*
- Pulse builder → `tools/fd_connectors/jhtdb/make_pulse_from_probe.py`

**Outputs**
- Raw series + meta → `data/jhtdb/*.csv.gz` + `*.meta.json`
- Analysis JSON (+ figures) → `results/fd_probe/YYYY-MM-DD_<slug>_batch#/…`
- Auto-pulse → `pulse/auto/YYYY-MM-DD_<slug>_batch#.yml`

---

## 2) Princeton (subset file: CSV / HDF5)

**Tools**
- Loader (subset reader) → `tools/fd_connectors/princeton/load_subset.py`
- Analyzer → `tools/fd_connectors/princeton/analyze_probe.py`  *(uses `pipeline/`)*
- Pulse builder → `tools/fd_connectors/princeton/make_pulse_from_probe.py`

**Local runner**
- `analysis/princeton_probe/run_pipeline.py`

**Where to drop subsets**
- Put files under `data/princeton/` (e.g., `data/princeton/subset.h5` or `data/princeton/subset.csv`)

**Outputs**
- Analysis JSON → `results/princeton/YYYY-MM-DD_<slug>_batch#.analysis.json`
- Figures (time/spectrum) → `results/princeton/YYYY-MM-DD_<slug>_batch1.analysis/`
- Auto-pulse → `pulse/auto/YYYY-MM-DD_<slug>_batch#.yml`

---

## Shared analysis code (used by both paths)

Located in `pipeline/`:
- `preprocess.py`  *(detrend/window; safe no-ops if data is already clean)*
- `spectrum.py`    *(rFFT/PSD helpers)*
- `ladder.py`      *(1–2–3 harmonic ladder detection)*
- `figures.py`     *(headless matplotlib figures; CI-safe)*
- `utils.py`
- `io_loaders.py`  *(JHTDB meta reader + Princeton subset reader; with sanity checks)*

---

## Local quick runs

- JHTDB: `analysis/hopkins_probe/run_pipeline.py`
- Princeton: `analysis/princeton_probe/run_pipeline.py`

> Both runners write analysis JSON + figures and **do not** require GitHub Actions.

---

## CI: One-click Loader (recommended)

Use **Actions → “GOLD PATH — Loader (Hopkins/Princeton)”**  
This wraps the corridor end-to-end and also **emits pulses**.

**Inputs**
- `source`: `jhtdb` | `princeton` | `demo`
- `params` (JSON):
  - JHTDB example  
    `{"flow":"isotropic1024coarse","x":0.1,"y":0.2,"z":0.3,"t0":0.0,"dt":0.0005,"nsteps":2400,"slug":"isotropic"}`
  - Princeton example  
    `{"subset_path":"data/princeton/subset.csv","slug":"princeton_subset","probe":"Q1"}`

**Where it writes**
- JHTDB analysis → `results/fd_probe/YYYY-MM-DD_<slug>_batch#.metrics.json` (+ figures)
- Princeton analysis → `results/princeton/YYYY-MM-DD_<slug>_batch#.analysis.json` (+ figures)
- Pulses → `pulse/auto/YYYY-MM-DD_<slug>_batch#.yml`

Batch numbers (`batch1`, `batch2`, …) **restart each date (UTC)** and are mirrored across results and pulses.

---

## Flow (ASCII)
```
  +--------------------+        +------------------+        +------------------------+
  |   Source loader    | -----> |   Analyzer       | -----> |   Pulse builder (YAML) |
  |  (JHTDB / subset)  |        | (shared pipeline)|        |   + figures/tables     |
  +--------------------+        +------------------+        +------------------------+
             |                            |                               |
             v                            v                               v
    data/jhtdb/** or              results/**.analysis.json         pulse/auto/*.yml
    data/princeton/**
```
---

## Notes & sanity checks

- `pipeline/io_loaders.py` validates time monotonicity, dtype, finite values, and probes/components.  
- Figures use a headless backend (`Agg`), so CI is reliable.  
- If a Princeton subset has multiple probes/components, pass `--probe` to the local runner (or set `probe` in workflow `params`).  
- All CI runs commit only what changed and are safe to re-run.

---

## See also

- Root README “Where things live” for the full layout.  
- `results/fd_probe/README.md` for date/batch file naming rules.

---

_Last updated: 2025-09-30_
