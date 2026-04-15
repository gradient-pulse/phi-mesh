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
```

This is not yet the final machine schema.  
It is the minimum shared basin for the current protocol object.

---

## Field definitions

### 1. `cycle_id`

The current recursive cycle number.

**Purpose**
- distinguishes initialization, continuation, correction, stabilization, and restart conditions

---

### 2. `input_slice`

The current externally supplied unfolding input.

**Purpose**
- represents the current slice of the world or task field

**Examples may include**
- frame-sequence summary
- scene summary
- event summary
- agent-output slice
- later richer sensory or process slices

---

### 3. `source_hypotheses`

Persistent provisional source/object identities.

**Purpose**
- preserves identity hypotheses across cycles
- anchors continuity without forcing certainty too early

---

### 4. `motion_tokens`

Primitive spatiotemporal trace bundles.

**Purpose**
- supplies the minimum local process substrate over which TU and TU+ operate

---

### 5. `active_trains`

Persistent source-linked token sequences.

**Purpose**
- carries temporal continuity
- allows extension, decay, restart, and branching
- serves as the main local structural unit

---

### 6. `coupling_state`

Current relational status among trains.

**Structure may include**
- coupling candidates
- stable couplings
- fragmentation flags

**Purpose**
- preserves horizontal structure without forcing symbolic commitment
- distinguishes weak possibility from stable relation

---

### 7. `choreography_memory_refs`

References to stored choreography patterns.

**Purpose**
- lets TU+ compare current trains against prior pattern forms
- supports promotion, de-promotion, reopening, and decay

---

### 8. `coherence_state`

Whole-field viability summary.

**Purpose**
- summarizes whether the current field supports persistence, contradiction, collapse, promotion, restart, or stable bounded continuation

---

### 9. `mismatch_history`

Ledger of deltas between predicted and returned unfolding.

**Purpose**
- prevents silent forgetting
- supports disciplined revision and de-confirmation

---

### 10. `attention_state`

Current recruitment and salience state.

**Purpose**
- marks when the field should remain background, be monitored, or recruit higher interpretive attention

---

### 11. `cortex_context`

Current symbolic framing.

**Purpose**
- holds the current high-level interpretive context
- remains downstream of structural state rather than replacing it

---

### 12. `downward_bias`

Bounded contextual pressure from cortexLLM.

**Purpose**
- lets cortexLLM influence comparison and attention priorities without low-level overwrite

---

### 13. `predicted_trains`

Candidate continuation structures proposed by TU+.

**Purpose**
- makes the architecture predictive rather than purely descriptive
- provides the basis for mismatch and revision

---

### 14. `action_state`

Current action stance.

**Purpose**
- records whether the protocol is in hold, compare, escalate, or action-linked mode
- bridges prediction and possible enactment

---

### 15. `returned_traces`

Observed return evidence after continuation or enactment.

**Purpose**
- ties prediction back to observed unfolding
- enables correction, de-confirmation, and restart

---

### 16. `notes_on_state_quality`

State hygiene and uncertainty guardrail.

**Purpose**
- preserves compact notes on sparsity, uncertainty, fragmentation, overgrowth, and reset recommendation

---

## Role-bounded visibility

The whole state exists, but each role should focus only on what it needs.

### TU reads primarily
- `input_slice`
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `returned_traces`

### TU writes primarily
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `coherence_state`

### TU+ reads primarily
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `choreography_memory_refs`
- `coherence_state`
- `mismatch_history`
- `downward_bias`

### TU+ writes primarily
- `choreography_memory_refs`
- `attention_state`
- `predicted_trains`
- `coherence_state`
- `mismatch_history`

### cortexLLM reads primarily
- `coherence_state`
- `attention_state`
- `predicted_trains`
- `mismatch_history`
- `notes_on_state_quality`

### cortexLLM writes primarily
- `cortex_context`
- `downward_bias`
- `attention_state`
- `notes_on_state_quality`

This role-bounded access is essential.  
Without it, the triad collapses into one blurred assistant.

---

## State evolution rule

Each cycle should:

1. preserve prior structured state
2. update only changed fields
3. avoid replacing the entire state with prose
4. let returned traces reshape trains and coherence
5. allow splitting, restart, or revision when persistent mismatch appears

Compactly:

> The state evolves by structured reweighting and partial update, not by total rewrite.

---

## Minimal state requirement

A valid T-Protocol implementation must preserve enough structured shared state to support:

- train persistence across cycles
- coupling strengthening and weakening
- mismatch logging
- branch formation under contradiction
- decay without silent erasure
- restart without historical collapse
- bounded symbolic context
- feedback from returned traces

If these capacities are absent, the protocol has not been faithfully implemented.

---

## Closing statement

The shared state schema is the first practical bridge from architecture notes to a runnable triad.

It allows TU, TU+, and cortexLLM to:

- share a live field
- remain role-bounded
- recurse across cycles
- escape one-shot prompt prison without dissolving into noise

A compact final formulation:

> The shared state is the live structured memory of the choreography field, preserved across cycles and read differently by TU, TU+, and cortexLLM.
