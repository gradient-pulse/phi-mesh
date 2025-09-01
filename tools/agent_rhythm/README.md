# Agent Rhythm Tools

Goal: detect **NT rhythm signatures** from arbitrary event logs and surface them as Φ-Mesh pulses.  
Where `/agents/rgp_ns/` is an *application* (Navier–Stokes), `/tools/agent_rhythm/` is *infrastructure* — a generic rhythm analysis pipeline.

---

## Quickstart (Phi-Mesh maintainers)

1. Drop a CSV with a time column into `inbox/nt_events/`.

   Example:
   ```csv
   t
   0.0
   1.1
   2.4
   4.0
