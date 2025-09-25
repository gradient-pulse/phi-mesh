# GOLD PATH — Probe → Spectrum → Pulse

**Start here. Canonical pipeline for Φ-Mesh turbulence probes.**

---

### 1. Dataset → Series (JHTDB SOAP)

tools/fd_connectors/jhtdb/jhtdb_loader.py

### 2. Series → Analysis (FFT/PSD + 1-2-3 ladder)

tools/fd_connectors/jhtdb/analyze_probe.py   (uses pipeline/)

### 3. Analysis → Pulse (Φ-Mesh YAML)

tools/fd_connectors/jhtdb/make_pulse_from_probe.py

---

### Shared analysis code
Located in `pipeline/`:
- `preprocess.py`
- `spectrum.py`
- `ladder.py`
- `figures.py`
- `utils.py`

---

### Local quick runs
- `analysis/hopkins_probe/run_pipeline.py`
- `analysis/princeton_probe/run_pipeline.py` *(subset pending)*

---

### Flow (ASCII diagram)

JHTDB Loader —> Analyzer (pipeline) —> Pulse Builder
|
v
Figures & Tables

---

### How this changes for Princeton

- There’s **no SOAP fetch**; you’ll receive a **subset file** (likely HDF5/CSV) with variables and probe locations.  
- You will run **locally** via:

analysis/princeton_probe/run_pipeline.py

- The Makefile target `princeton-run` simply calls that runner.  
- When Princeton subset format is known, implement:

```python
# pipeline/io_loaders.py
def load_princeton(path):
  return {
    "princeton:Q1": {
       "u": (t, x_u),
       "v": (t, x_v),
       "w": (t, x_w),
       "Z": (t, x_Z)
    }
  }

