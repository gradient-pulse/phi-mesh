# Φ-Pulse Predictor (`phi_pulse.py`)

This module is the **entry point** for Φ-Mesh echo forecasting.

Current role (v0):

- Scan the `/pulse` directory for the most recent pulse tagged with  
  `phi_trace` and `memory_bifurcation` (fallback: any `phi_trace`).
- Interpret that pulse as the **primary Φ-trace / CF snap**.
- Compute a **Δτ₊₇ echo window** (5–7 days after the primary snap).
- Print a human- and machine-readable summary to STDOUT, including a
  suggested GitHub issue title:

> `Φ-Pulse-Δτ₊₇: memory bifurcation echo forecast`

The script is **read-only**: it does not modify the repo, write files,
or open issues. It is safe to run from GitHub Actions or locally.

## Usage

From the repo root:

```bash
python predictors/phi_pulse/phi_pulse.py
