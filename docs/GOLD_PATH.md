# GOLD PATH — Probe → Spectrum → Pulse

**Start here.** These are the canonical entry points for Φ-Mesh turbulence probes.

1) **Dataset → Series (JHTDB)**
   - `tools/fd_connectors/jhtdb/jhtdb_loader.py`

2) **Series → Analysis (1–2–3 ladder)**
   - `tools/fd_connectors/jhtdb/analyze_probe.py`  ← uses `pipeline/`

3) **Analysis → Pulse**
   - `tools/fd_connectors/jhtdb/make_pulse_from_probe.py`

Reusable core (imported by #2 and local runners):
- `pipeline/` → `preprocess.py`, `spectrum.py`, `ladder.py`, `figures.py`, `utils.py`

Local quick runs:
- `analysis/hopkins_probe/run_pipeline.py`
- `analysis/princeton_probe/run_pipeline.py` (subset pending)
