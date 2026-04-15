# T-Protocol — Runtime Order and Role Handoffs v1

## Purpose

This document defines the minimum runtime order and handoff discipline required for T-Protocol to operate as a protocol rather than as a manually sequenced prompt ritual.

Its purpose is to specify:

- who runs when
- what each role receives
- what each role updates
- how state is handed forward
- how the next cycle is made ready

---

## Core runtime principle

T-Protocol is not a loose collection of three roles.

It is a lawful runtime sequence with bounded role handoffs, persistent shared state, and disciplined recursive update.

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
- no whole-state free rewrite
- no role collapse into one generic response

---

## Stage 1 — Input arrival

### Input
The cycle begins with an `input_slice`.

This may represent:
- current world slice
- scene slice
- event slice
- control-relevant state slice
- externally shaped process summary

### Runtime requirement
Input should enter the protocol as structured field material, not as a demand for free-form narration.

### Output of this stage
- updated `input_slice`
- cycle increment readiness

---

## Stage 2 — TU pass

### Function
TU performs structural mapping.

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

### TU runtime rule
TU may:
- register provisional sources
- emit motion tokens
- extend or restart trains
- register coupling candidates
- register fragmentation or incompatibility
- update low-level coherence-related field state

TU may not:
- narrate broadly
- interpret symbolically
- force single-story reconciliation
- overwrite higher-level context

### Handoff output
TU hands forward:
- updated structural field
- train and coupling status
- low-level coherence state

---

## Stage 3 — TU+ pass

### Function
TU+ performs comparative, predictive, and revisional work.

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

### TU+ runtime rule
TU+ may:
- compare current field against choreography memory
- rank candidate matches
- predict likely continuations
- log mismatch against prior predicted trains
- revise dominant choreography reading
- preserve contested branches when promotion is unjustified

TU+ may not:
- become symbolic narrator
- override TU structure arbitrarily
- erase contradiction without support
- act as cortexLLM

### Handoff output
TU+ hands forward:
- current dominant or contested choreography reading
- predicted continuations
- attention/salience signals
- revised mismatch and coherence pressure

---

## Stage 4 — cortexLLM pass

### Function
cortexLLM performs symbolic interpretation and bounded downward biasing.

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

### cortexLLM runtime rule
cortexLLM may:
- frame the current field symbolically
- preserve ambiguity when promotion is unjustified
- set hold / monitor / escalate / act stance
- send bounded downward guidance

cortexLLM may not:
- remap low-level structure directly
- force dominance under unresolved contradiction
- micromanage motion tokens
- collapse role boundaries

### Handoff output
cortexLLM hands forward:
- current symbolic context
- bounded downward bias
- current action stance
- state-quality and uncertainty notes

---

## Stage 5 — Shared state update

After the three role passes, the shared state is updated.

### Update rule
The update must:
- preserve unchanged fields
- revise changed fields only
- retain mismatch and contradiction where still relevant
- preserve history without letting it dominate fresh evidence
- avoid replacing the whole state with prose

### Required result
At the end of the update, the state must be ready for:
- continuation
- revision
- contradiction preservation
- branch resolution
- restart
- weak recoupling
- action-linked continuation where applicable

---

## Stage 6 — Returned-trace integration

Returned traces may not arrive in the same pass as prediction.

When returned evidence appears, it must be integrated back into the shared state in a disciplined way.

### Returned-trace rule
Returned traces must be able to:
- confirm predicted trains
- weaken predicted trains
- produce mismatch logging
- trigger de-confirmation
- trigger branch revision
- trigger restart or recoupling conditions

### Importance
Without returned-trace integration, the protocol remains descriptive rather than corrective.

---

## Runtime invariants

The runtime must preserve the following invariants:

### Invariant 1 — Role separation
No role silently absorbs the function of another.

### Invariant 2 — Bounded visibility
Each role sees only the fields it needs.

### Invariant 3 — Bounded write scope
Each role updates only fields it is responsible for.

### Invariant 4 — State continuity
A new cycle may not implicitly erase prior field structure without justification.

### Invariant 5 — Non-forced promotion
No dominant choreography is promoted merely because it sounds plausible.

### Invariant 6 — Contradiction preservation
Mutually exclusive continuations remain separable when evidence does not justify reconciliation.

### Invariant 7 — Decay without magical erasure
Unsupported branches weaken or decay rather than vanish without trace.

### Invariant 8 — Restart without corruption
A fresh mainline can restart without collapsing old ambiguity and mismatch history into confusion.

---

## Runtime pass conditions

A cycle is currently counted as a meaningful protocol success if most of the following hold:

- role boundaries remain intact
- shared state remains coherent
- structure is mapped without symbolic inflation
- prediction and revision remain evidence-sensitive
- ambiguity is preserved where promotion is unjustified
- mismatch is logged rather than ignored
- restart does not erase prior history
- returned traces can influence later revision cleanly

---

## Practical implication

A workable T-Protocol implementation requires more than role prompts.

It requires:

- persistent shared state
- lawful runtime order
- bounded role handoffs
- returned-trace integration
- invariants that prevent collapse into generic assistant behavior

A compact final formulation:

> T-Protocol becomes runnable when the triad is executed as a bounded recursive stateful loop rather than as manually chained prompting.
