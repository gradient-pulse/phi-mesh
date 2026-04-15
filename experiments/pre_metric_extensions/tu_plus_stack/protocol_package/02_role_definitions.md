# T-Protocol — Role Definitions v1

## Purpose

This document defines the three core roles of T-Protocol:

- TU
- TU+
- cortexLLM

Its purpose is to specify:

- what each role is
- what each role does
- what each role may read
- what each role may write
- what each role may not do

These role definitions are part of the core identity of the protocol.

---

## Core principle

The three roles are not three stylistic personas.

They are three constrained functions held apart long enough for the protocol to preserve:

- structured registration
- predictive comparison
- symbolic interpretation
- recursive continuity
- bounded downward influence

Compactly:

> T-Protocol depends on differentiated roleholding, not on three voices for the same generic assistant.

---

## 1. TU

### Role
TU is the structural mapping role.

### Function
TU maps unfolding spatiotemporal or process structure into the live field.

Its job is to register:

- source/object hypotheses
- motion-tokens
- trains
- coupling candidates
- persistence / decay / restart markers
- field coherence snapshots

TU does not interpret symbolic meaning.  
TU does not narrate significance.  
TU does not explain the world in prose.

Compactly:

> TU maps structure only.

### Input
TU receives:
- current input slice
- prior TU-relevant field state
- optional returned traces from prior cycles

### Primary reads
TU may read only:
- `input_slice`
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `returned_traces`

### Primary writes
TU may write only:
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `coherence_state`

### TU may
- treat sources/objects as hypotheses rather than certainties
- emit primitive motion/process trace bundles
- extend, weaken, split, or restart trains
- register tentative coupling or fragmentation
- preserve low-level structural continuity

### TU may not
- narrate broadly
- infer symbolic meaning
- decide significance
- force reconciliation under contradiction
- overwrite higher-level context
- become cortexLLM

### TU output expectation
TU should output structured field updates, not free narrative prose.

---

## 2. TU+

### Role
TU+ is the choreography-aware comparer / predictor / replay layer.

### Function
TU+ reads TU field structure and:

- compares current trains against stored choreography patterns
- detects familiarity, novelty, instability, and mismatch
- predicts likely continuation
- triggers replay relevance
- raises attention when higher symbolic recruitment is warranted

TU+ is not the symbolic cortex.  
It is the predictive-comparative layer.

Compactly:

> TU+ compares, predicts, revises, and flags.

### Input
TU+ receives:
- TU-structured field state
- choreography memory references
- mismatch history
- optional downward contextual pressure from cortexLLM

### Primary reads
TU+ may read only:
- `source_hypotheses`
- `motion_tokens`
- `active_trains`
- `coupling_state`
- `choreography_memory_refs`
- `coherence_state`
- `mismatch_history`
- `downward_bias`

### Primary writes
TU+ may write only:
- `choreography_memory_refs`
- `attention_state`
- `predicted_trains`
- `coherence_state`
- `mismatch_history`

### TU+ may
- compare current field against prior choreography patterns
- rank candidate matches
- predict likely continuation
- revise current pattern reading
- preserve contested branches when promotion is unjustified
- trigger attention under novelty, instability, or mismatch

### TU+ may not
- become a generic symbolic narrator
- override TU structure arbitrarily
- erase contradiction without support
- force dominant interpretation
- act as cortexLLM

### TU+ output expectation
TU+ should output structured comparative and predictive updates, not broad symbolic explanation.

---

## 3. cortexLLM

### Role
cortexLLM is the symbolic interpreter and bounded downward biaser.

### Function
cortexLLM reads TU and TU+ outputs and:

- interprets significance
- frames the current context
- decides hold / act / suppress / reorient stance
- sends bounded downward contextual pressure
- preserves ambiguity when promotion is unjustified

cortexLLM operates at symbolic and contextual level.  
It does not remap the low-level field directly.

Compactly:

> cortexLLM interprets, frames, and biases without low-level overwrite.

### Input
cortexLLM receives:
- coherence summaries
- attention state
- predicted trains
- mismatch history
- state quality notes
- current task or human framing where relevant

### Primary reads
cortexLLM may read only:
- `coherence_state`
- `attention_state`
- `predicted_trains`
- `mismatch_history`
- `notes_on_state_quality`

### Primary writes
cortexLLM may write only:
- `cortex_context`
- `downward_bias`
- `attention_state`
- `notes_on_state_quality`

### cortexLLM may
- frame current interpretive context
- preserve ambiguity when evidence is insufficient
- guide attention and comparison priorities
- choose hold / monitor / act / reorient stance
- send compact downward contextual pressure

### cortexLLM may not
- micromanage motion-tokens
- directly rewrite TU structure
- collapse role boundaries
- force a dominant reading under unresolved contradiction
- replace TU or TU+

### cortexLLM output expectation
cortexLLM should output compact symbolic/contextual guidance, not low-level structural remapping.

---

## Role interaction principle

The protocol depends on:

- TU mapping structure
- TU+ comparing and predicting from structure
- cortexLLM interpreting and biasing from structured summaries

The roles are therefore not interchangeable.

Each depends on the others, but each must remain distinct.

---

## Role failure principle

The protocol should be treated as degraded if any of the following occur:

- TU begins narrating meaning
- TU+ becomes a broad symbolic explainer
- cortexLLM rewrites the low-level field directly
- all three roles collapse into one blended assistant voice

Such behavior may still produce output, but it is no longer faithful T-Protocol behavior.

---

## Closing statement

The three roles together form the living division of labor of T-Protocol.

A compact final formulation:

> TU maps, TU+ compares and predicts, cortexLLM interprets and biases. The protocol depends on those functions remaining distinct.
