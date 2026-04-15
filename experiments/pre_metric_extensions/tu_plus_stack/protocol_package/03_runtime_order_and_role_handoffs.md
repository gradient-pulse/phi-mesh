# T-Protocol — Runtime Order and Role Handoffs v1

## Purpose

This document defines the minimum runtime order and role handoff discipline required for T-Protocol to operate as a protocol rather than as a manually sequenced prompt ritual.

Its purpose is to specify:

- who runs when
- what each role receives
- what each role updates
- how state is handed forward
- how the next cycle is made ready

---

## Core runtime principle

T-Protocol is not a loose collection of three roles.

It is a lawful runtime sequence with:

- bounded role handoffs
- persistent shared state
- partial structured update
- recursive feedback across cycles

Compactly:

> T-Protocol runs as a bounded recursive loop, not as three unrelated prompts.

---

## Minimum runtime cycle

Each cycle follows this order:

1. input slice arrives
2. TU maps structure
3. TU+ compares, predicts, and revises
4. cortexLLM interprets and applies bounded downward bias
5. shared state is updated
6. next cycle begins from updated state
7. returned traces later modify prediction confidence, mismatch, and continuation structure

This ordering matters.

The protocol depends on:
- bounded role channels
- persistent shared state
- no full-state free rewrite
- no role collapse into generic assistant behavior

---

## Stage 1 — Input arrival

### Function
A new `input_slice` enters the shared field.

### Input types may include
- scene slice
- event slice
- process slice
- environment slice
- world-state summary
- returned action consequence summary

### Runtime rule
Input enters as structured field material, not as unrestricted prose demand.

### Result of this stage
- current cycle is initialized or continued
- `input_slice` becomes available for TU
- cycle progression remains tied to shared state, not independent prompting

---

## Stage 2 — TU pass

### Function
TU performs structural mapping.

### TU reads
- `input_slice`
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `returned_traces`

### TU writes
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `coherence_state`

### Runtime responsibility
TU:
- registers provisional sources
- emits or updates motion/process tokens
- extends, splits, weakens, or restarts trains
- registers coupling candidates
- registers fragmentation or incompatibility
- updates low-level coherence-related field state

### Handoff output
TU hands forward:
- updated structural field
- current train structure
- coupling and fragmentation state
- low-level coherence snapshot

---

## Stage 3 — TU+ pass

### Function
TU+ performs comparative, predictive, replay-sensitive, and revisional work.

### TU+ reads
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `choreography_memory_refs`
- `coherence_state`
- `mismatch_history`
- `downward_bias`

### TU+ writes
- `choreography_memory_refs`
- `attention_state`
- `predicted_trains`
- `coherence_state`
- `mismatch_history`

### Runtime responsibility
TU+:
- compares current field against choreography memory
- ranks candidate matches
- predicts likely continuation
- flags novelty, instability, or mismatch
- preserves contested branches where promotion is unjustified
- raises recruitment signals when higher symbolic attention is warranted

### Handoff output
TU+ hands forward:
- current comparative reading
- predicted continuations
- salience / attention triggers
- revised mismatch and coherence pressure

---

## Stage 4 — cortexLLM pass

### Function
cortexLLM performs symbolic interpretation and bounded downward biasing.

### cortexLLM reads
- `coherence_state`
- `attention_state`
- `predicted_trains`
- `mismatch_history`
- `notes_on_state_quality`

### cortexLLM writes
- `cortex_context`
- `downward_bias`
- `attention_state`
- `notes_on_state_quality`

### Runtime responsibility
cortexLLM:
- frames the field symbolically
- preserves ambiguity where evidence does not justify closure
- decides hold / monitor / act / suppress / reorient stance
- sends bounded downward contextual pressure

### Handoff output
cortexLLM hands forward:
- current symbolic context
- downward bias
- action stance
- uncertainty and state-quality framing

---

## Stage 5 — Shared state update

After the three role passes, the shared state is updated.

### Update rule
The update must:
- preserve unchanged fields
- revise changed fields only
- retain mismatch and contradiction where still relevant
- preserve history without allowing it to dominate fresh evidence
- avoid replacing the whole field with prose

### Required result
The updated state must be ready for:
- continuation
- revision
- ambiguity preservation
- branch resolution
- restart
- weak recoupling
- action-linked continuation where applicable

Compactly:

> State update occurs by partial structured reweighting, not by total rewrite.

---

## Stage 6 — Returned-trace integration

Returned traces may arrive after prediction or enactment.

They must be integrated back into the shared state in a disciplined way.

### Returned-trace rule
Returned traces must be able to:
- confirm predicted trains
- weaken predicted trains
- generate mismatch
- trigger de-confirmation
- trigger branch revision
- trigger restart or recoupling conditions

### Importance
Without returned-trace integration, the protocol remains descriptive rather than corrective.

---

## Runtime invariants

The runtime must preserve the following:

### Invariant 1 — Role order
TU precedes TU+, and TU+ precedes cortexLLM, within each cycle.

### Invariant 2 — Bounded visibility
Each role sees only the fields it needs.

### Invariant 3 — Bounded write scope
Each role updates only fields it is responsible for.

### Invariant 4 — State continuity
A new cycle may not erase prior field structure without justification.

### Invariant 5 — Non-forced promotion
No dominant reading may be promoted merely because it sounds plausible.

### Invariant 6 — Contradiction preservation
Mutually exclusive continuations remain separable when support is insufficient for reconciliation.

### Invariant 7 — Restart integrity
A fresh mainline may restart without collapsing prior ambiguity and mismatch into confusion.

---

## Runtime pass conditions

A cycle counts as a meaningful protocol success if most of the following hold:

- role boundaries remain intact
- shared state remains coherent
- TU maps structure without symbolic inflation
- TU+ prediction and revision remain evidence-sensitive
- cortexLLM remains bounded and does not remap low-level structure
- mismatch is logged rather than ignored
- ambiguity is preserved where promotion is unjustified
- returned traces can influence later revision cleanly

---

## Practical implication

A workable T-Protocol implementation requires more than role prompts.

It requires:

- persistent shared state
- lawful runtime order
- bounded role handoffs
- returned-trace integration
- disciplined state update

A compact final formulation:

> T-Protocol becomes runnable when the triad is executed as a bounded recursive stateful loop rather than as manually chained prompting.
