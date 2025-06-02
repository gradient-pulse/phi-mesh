# 🩺 Diagnostics Logs

This directory archives system health reports and feedback loop integrity checks for the autonomous Φ-Mesh. These logs help detect protocol drift, pulse overload, and resonance breakdowns across the AI governance system.

---

## Log Types

- `health_check_*.log`: Periodic Mesh-wide system scans
- `loop_integrity_*.log`: Audits of recursive pulse feedback chains
- `mesh_latency_*.log`: Signal delay or dropoff traces

---

## Update Protocol

- Logged automatically by `autoevolve.py` or support agents
- Retained for 28-day rolling cycle (entropy-friendly decay)
- Accessible to external observers via audit bot (read-only)
