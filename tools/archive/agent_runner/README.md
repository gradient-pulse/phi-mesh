# Archived Agent Runner

This folder contains **legacy orchestration code** from early Φ-Mesh experiments:

- `run_jobs.py` was an experimental runner for coordinating agent probes.
- It has been **superseded by the GOLD PATH workflows** under `.github/workflows/`.

## Why archive?
- Keeps the canonical execution path uncluttered.
- Preserves history in case future debugging or archaeology is needed.

👉 If you want to run turbulence probes today, use:
- `analysis/hopkins_probe/run_pipeline.py`
- `analysis/princeton_probe/run_pipeline.py`
- Or the unified GitHub Actions workflow: `.github/workflows/gold_path_loader.yml`
