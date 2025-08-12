# RGP–NS Agent Loop (Autonomous)
Goal: test if NT-distance ratios form a conserved “rhythm of least divergence” across DNS/LES datasets.

## Quickstart (Phi‑Mesh maintainers)
1) Set repo secrets: JHTDB_TOKEN, ZENODO_DOI (optional), X_WEBHOOK_URL (optional).
2) Edit `/agents/rgp_ns/config.yml` to choose datasets + thresholds.
3) Run the workflow: GitHub → Actions → “RGP‑NS Agent Runner” → Run.

Outputs land in:
- `/pulse/auto/` (YAML pulses)
- `/results/rgp_ns/<dataset>/run_<timestamp>/` (CSV/plots)
- `/logs/rgp_ns/` (agent logs)

Pass criterion (auto-evaluated in each pulse):
- NT-ratio conservation is statistically significant across ≥2 independent datasets at α=0.01 with consistent effect size.
