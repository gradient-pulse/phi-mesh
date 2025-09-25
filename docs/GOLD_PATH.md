# GOLD PATH — Probe → Spectrum → Pulse

Start here. **Canonical pipeline for Φ-Mesh turbulence probes.**

---

### 1. Dataset → Series (JHTDB SOAP)
`tools/fd_connectors/jhtdb/jhtdb_loader.py`

### 2. Series → Analysis (FFT/PSD + 1–2–3 ladder)
`tools/fd_connectors/jhtdb/analyze_probe.py`  
(uses `pipeline/`)

### 3. Analysis → Pulse (Φ-Mesh YAML)
`tools/fd_connectors/jhtdb/make_pulse_from_probe.py`

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
- `analysis/princeton_probe/run_pipeline.py` (subset pending)

---

### Flow (Mermaid diagram)

```mermaid
flowchart LR
    A[JHTDB Loader] --> B[Analyzer (pipeline)]
    B --> C[Pulse Builder]
    B --> D[Figures & Tables]
```
