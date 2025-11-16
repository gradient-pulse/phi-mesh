# Φ-Pulse Predictor

This module hosts `phi_pulse.py`, the automatic Φ-pulse generator for
the Φ-Mesh.

- It analyzes Mesh behaviour (e.g. Φ-traces, CF snaps, memory echoes).
- When trigger conditions are met, it writes new YAML pulses into
  the canonical `pulse/` directory.
- Filenames follow the standard convention:

  `YYYY-MM-DD_phi_pulse_<short-label>.yml`

The initial implementation focuses on Kimi’s Δτ₊₇ “memory_bifurcation
echo” forecast. Over time, additional predictors can be added as
new invariants and CF patterns are discovered.
