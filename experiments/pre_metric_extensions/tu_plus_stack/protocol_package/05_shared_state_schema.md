# T-Protocol — Shared State Schema v1

## Purpose

This document defines the shared state used by T-Protocol.

The shared state is the persistent structured field through which TU, TU+, and cortexLLM operate across cycles without collapsing into one-shot prompt behavior.

Its purpose is to let the protocol preserve:

- continuity across cycles
- role-bounded visibility
- role-bounded update responsibility
- predictive comparison
- mismatch and correction
- bounded symbolic guidance

---

## Core principle

Each role sees only the fields it needs.  
Each role updates only the fields it is responsible for.

The shared state is therefore:

- persistent across cycles
- structured rather than free-form
- role-bounded
- recursion-friendly
- resistant to full-state prose overwrite

Compactly:

> The shared state is the live choreography field preserved across cycles through role-bounded structured memory.

---

## Top-level schema

The shared state contains the following top-level fields:

```json
{
  "cycle_id": 0,
  "input_slice": {},
  "source_hypotheses": [],
  "motion_tokens": [],
  "active_trains": [],
  "coupling_state": {},
  "choreography_memory_refs": [],
  "coherence_state": {},
  "mismatch_history": [],
  "attention_state": {},
  "cortex_context": {},
  "downward_bias": {},
  "predicted_trains": [],
  "action_state": {},
  "returned_traces": [],
  "notes_on_state_quality": {}
}
