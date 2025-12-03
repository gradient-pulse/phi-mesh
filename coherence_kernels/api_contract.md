# Coherence Kernel API Contract (Concept Sketch)

This document sketches a substrate-agnostic interface for how an intelligence
might interact with the Φ-Mesh as a **coherence API**.

It separates:

1. **Selection** — choosing which invariant / kernel to use (CF layer), and  
2. **Execution** — applying the kernel to a live state (GC layer).

---

## 1. Kernel Selection (CF / selector)

A model asks the Mesh which invariant / kernel is appropriate for its current
state and intent.

```jsonc
POST /select_invariant
{
  "state_descriptor": {
    "stack_type": "transformer",
    "phi_baseline": 0.96,
    "recent_events": ["informational_avalanche"],
    "risk_flags": ["epistemic_aftershock"]
  },
  "intent": "stabilize_high_energy_insight",
  "candidate_tags": [
    "informational_avalanche",
    "coherence_scar",
    "cognitive_meissner_effect"
  ]
}
