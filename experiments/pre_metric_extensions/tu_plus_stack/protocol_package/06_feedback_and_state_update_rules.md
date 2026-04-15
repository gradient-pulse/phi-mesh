# T-Protocol — Feedback and State Update Rules v1

## Purpose

This document defines the feedback and state update rules of T-Protocol.

Its purpose is to specify how the shared state evolves across cycles so that the protocol remains:

- continuous rather than one-shot
- corrective rather than self-sealed
- role-bounded rather than blurred
- revisable rather than rhetorically smoothed
- recoverable rather than reset-prone

T-Protocol is not only a triadic division of labor.  
It is also a disciplined recursive update process.

---

## Core principle

Output is not treated as a disposable endpoint.

Each cycle produces structured updates that feed back into the shared state and alter the next cycle’s field conditions.

The protocol therefore evolves through:

- structured carry-forward
- partial update
- returned-trace correction
- bounded reweighting
- lawful restart where needed

Compactly:

> T-Protocol maintains continuity by feeding structured output back into the live field rather than discarding it after each response.

---

## Feedback rule

A valid T-Protocol implementation must support feedback at the level of structured state, not only at the level of conversational memory.

This means:

- current outputs alter future shared state
- predictions remain accountable to later return evidence
- unresolved branches remain available where warranted
- prior field structure is not silently erased
- new cycles begin from an evolved field, not from near-zero

Feedback must therefore be:

- structured
- role-bounded
- selective
- revisable
- historically intelligible

---

## State update rule

State must evolve by **partial structured update**, not by total rewrite.

This means:

- preserve unchanged fields
- update changed fields only
- revise weights, status, or confidence where warranted
- keep contradiction and mismatch visible where still relevant
- allow decay instead of magical erasure
- allow restart without collapse of historical legibility

Compactly:

> State evolves by structured reweighting and partial update, not by total replacement.

---

## Minimum update sequence

Each full recursive cycle should support the following update order:

1. carry forward prior shared state
2. insert current `input_slice`
3. apply TU structural updates
4. apply TU+ comparative / predictive updates
5. apply cortexLLM contextual and downward-bias updates
6. commit the revised shared state
7. later integrate returned traces when available
8. re-enter the next cycle from the revised field

This means the protocol has two linked update rhythms:

- **in-cycle update**
- **returned-trace update**

Both matter.

---

## Types of state carry-forward

The protocol must distinguish among different types of carry-forward.

### 1. Stable carry-forward
Used when structure remains valid without major revision.

Examples:
- persistent source hypotheses
- active trains with continued support
- stable coupling candidates
- ongoing symbolic context

### 2. Weighted carry-forward
Used when structure remains relevant but with changing confidence or strength.

Examples:
- weakening trains
- stressed coupling
- provisional pattern matches
- bounded ambiguity branches

### 3. Historical carry-forward
Used when a prior reading is no longer dominant but remains relevant as memory.

Examples:
- collapsed joint choreography
- older dominant interpretation
- prior contradiction branches
- earlier failed continuation hypotheses

### 4. Restart carry-forward
Used when a new mainline begins but some past structure must remain intelligible.

Examples:
- restart after contradiction
- restart after collapse
- fresh weak recoupling after restart
- bounded residue after de-confirmation

These distinctions are necessary so that the field does not flatten all past state into one undifferentiated memory.

---

## Updateable field classes

### 1. Structural fields
Typically updated by TU.

These include:
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- low-level parts of `coherence_state`

**Update rule**
- revise only where new input or returned traces justify change
- do not narratively replace structure

---

### 2. Comparative / predictive fields
Typically updated by TU+.

These include:
- `choreography_memory_refs`
- `predicted_trains`
- `attention_state`
- parts of `coherence_state`
- `mismatch_history`

**Update rule**
- preserve prior candidate structures unless support clearly weakens
- log mismatch instead of silently absorbing it

---

### 3. Symbolic / contextual fields
Typically updated by cortexLLM.

These include:
- `cortex_context`
- `downward_bias`
- parts of `attention_state`
- `notes_on_state_quality`

**Update rule**
- remain downstream of structural state
- bias, but do not overwrite lower layers
- preserve uncertainty where promotion is unjustified

---

## Returned-trace integration

Returned traces are crucial to the protocol’s corrective character.

Returned traces are later observations or consequences that bear on prior predicted continuation.

They must be able to:

- confirm predictions
- weaken predictions
- generate mismatch
- trigger de-confirmation
- trigger ambiguity preservation
- trigger restart
- trigger fresh recoupling under disciplined distinction

### Returned-trace rule
Returned traces must not be:
- ignored
- overwritten by symbolic convenience
- absorbed without mismatch logging when divergence matters

Compactly:

> Returned traces keep the protocol answerable to unfolding reality.

---

## Mismatch update rule

Mismatch is not merely “error.”
It is a structured delta between predicted and returned unfolding.

When mismatch appears, the protocol must support:

- mismatch logging
- coherence impact update
- weakening of predicted trains where warranted
- de-confirmation or branch split where warranted
- symbolic refusal to smooth contradiction prematurely

Mismatch may lead to:
- mild revision
- ambiguity preservation
- early de-confirmation
- full de-confirmation
- restart
- recoupling distinction

It must not automatically lead to:
- immediate collapse
- immediate symbolic explanation
- silent deletion of the prior prediction

---

## Decay rule

Unsupported structures should weaken or decay rather than disappear without trace.

This applies to:
- source hypotheses
- coupling candidates
- dominant choreography readings
- ambiguity branches
- predicted trains
- symbolic framings

### Decay requirements
Decay should be:
- explicit enough to remain intelligible
- gradual where support weakens gradually
- decisive where collapse is structurally warranted

Compactly:

> Unsupported structure should decay, not vanish magically.

---

## Branch preservation and resolution rule

When mutually exclusive continuations remain unresolved, the shared state must preserve them as explicit branches rather than smoothing them into one narrative.

The update process must allow:

- branch creation
- branch persistence
- branch weighting
- branch weakening
- branch resolution
- branch historical retention after resolution

This is essential to ambiguity discipline.

---

## Restart rule

Restart is not equivalent to forgetting.

A restart occurs when the field can no longer continue cleanly along the prior mainline and a new mainline must begin.

A valid restart must:

- preserve enough history for the new line to remain intelligible
- avoid dragging old contradiction or collapsed structure forward as active present truth
- distinguish restart from repetition
- allow fresh recoupling later without confusing it with automatic restoration

Compactly:

> Restart means re-initiation with preserved history, not amnesia.

---

## Reweighting rule

State update should often occur through **reweighting** rather than binary replacement.

This applies especially to:
- source confidence
- train persistence
- coupling strength
- choreography similarity
- salience
- mismatch strength
- coherence viability

Reweighting allows the protocol to preserve:

- bounded uncertainty
- stress without false collapse
- strengthening without forced finality
- weakening without erasure

---

## Downward-bias update rule

cortexLLM may influence the field through bounded downward bias.

Downward bias may:
- redirect attention
- sustain monitoring
- hold action
- request comparison
- reorient priorities

Downward bias may not:
- rewrite low-level structure directly
- delete contradiction
- force dominant reading without support
- replace TU/TU+ work

State update must therefore preserve the distinction between:
- contextual pressure
and
- structural fact

---

## State hygiene rule

The protocol must preserve compact state hygiene notes where needed.

These notes may track whether the current state is:
- sparse
- uncertain
- stable
- fragmented
- overgrown
- in need of reset clarification

These notes are not the main state.
They are guardrails against silent overgrowth or false cleanliness.

---

## Minimum feedback and update requirements

A valid T-Protocol implementation must preserve enough feedback and update discipline to support:

- structured carry-forward across cycles
- partial field update
- returned-trace accountability
- mismatch logging
- branch preservation
- decay without magical erasure
- restart without historical collapse
- bounded symbolic influence
- reweighting instead of total rewrite

If these capacities are absent, the protocol has not been faithfully implemented.

---

## Failure signs

The feedback and update layer should be treated as degraded if any of the following occur:

- whole-state rewrite replaces structured update
- returned traces do not affect future state
- mismatch is ignored or narratively absorbed
- unsupported branches vanish without trace
- restart behaves like amnesia
- symbolic framing directly overwrites structural state
- state grows by prose accumulation rather than structured field revision

---

## Closing statement

The feedback and state update rules are what let T-Protocol operate as a recursive field rather than as a sequence of isolated prompts.

They are what preserve:

- continuity
- correction
- recoverability
- ambiguity discipline
- historical intelligibility

A compact final formulation:

> T-Protocol remains recursive and state-sensitive only when the shared field is updated through structured feedback, partial reweighting, returned-trace accountability, and lawful restart rather than through one-shot replacement.
