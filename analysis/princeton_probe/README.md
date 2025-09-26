# Princeton Probe Analysis

This folder handles **local analysis** of probe-level subsets shared by Prof. Mueller’s group at Princeton.  
It is the parallel path to the JHTDB loaders — but instead of fetching live from SOAP, we start from **subset files** (likely HDF5/CSV).

---

## Workflow

1. **Drop data subset**  
   - Place raw Princeton subset files in `data/princeton/`.  
   - Supported formats (to be confirmed): CSV, HDF5.  
   - Each file should carry time-series for velocity components (`u, v, w`) and scalar fractions (`Z`).

2. **Run pipeline**  
   - Entry point: `run_pipeline.py`.  
   - This script loads the subset, performs analysis (FFT, dominant cycle detection, ratios), and writes results.  

   Output:
   - `results/princeton_probe/*.analysis.json` — numeric results (dominant frequency, ratios, notes).  
   - `results/princeton_probe/*.metrics.json` — harmonized copy for cross-experiment comparison.  
   - `pulse/auto/YYYY-MM-DD_princeton_batchN.yml` — pulse fossilization (summary, tags, references).  

3. **Inspect results**  
   - See metrics in `results/princeton_probe/`.  
   - Pulses will surface automatically in the Tag Map after the **Build Tags & Graph** workflow.

---

## Key Code

- `tools/fd_connectors/princeton/load_subset.py` — loader for HDF5/CSV subsets.  
- `tools/fd_connectors/princeton/analyze_probe.py` — shared analyzer (FFT, harmonics, ratios).  
- `tools/fd_connectors/princeton/make_pulse_from_probe.py` — builds fossilization pulses.  

---

## Status

- [x] JHTDB path established.  
- [ ] Princeton connectors scaffolded.  
- [ ] Awaiting first subset from Princeton to finalize loader.  

---

📌 **Note:**  
The Princeton path reuses the same *analysis logic* as JHTDB; only the loader differs.  
This keeps coherence across datasets and ensures comparability of NT Rhythm evidence.
