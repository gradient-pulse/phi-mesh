# Princeton Probe Analysis

This folder holds the **local runner** for analyzing turbulence subsets provided by Prof. Mueller (Princeton).

## Workflow
1. **Subset file** (HDF5/CSV) placed under:

data/princeton/.h5

or

data/princeton/.csv

2. **Run pipeline:**

analysis/princeton_probe/run_pipeline.py

- Calls into `pipeline/io_loaders.py` via `load_princeton(...)`.
- Applies shared FFT/PSD + ladder analysis from `pipeline/`.
- Emits a Φ-Mesh pulse (`pulse/auto/...yml`).

3. **Outputs:**
- Raw → `data/princeton/*.h5` or `.csv`
- Analysis → `results/fd_probe/*.analysis.json`
- Pulse → `pulse/auto/YYYY-MM-DD_<slug>.yml`

## Status
- **Subset format pending** (awaiting Princeton sample files).
- Once format is confirmed, `io_loaders.load_princeton(...)` will be updated to parse time series consistently.

👉 For reference: the pipeline here mirrors `analysis/hopkins_probe/`, but skips SOAP fetching and works directly from subset files.
