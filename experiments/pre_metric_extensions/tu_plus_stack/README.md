# TU+ Stack

## Purpose

This subfolder hosts the emerging **coherence-driven division of LLM labor** within the broader pre-metric extensions branch.

The working claim is that a useful world-model-like awareness-support stack may require three distinct, role-bounded layers:

1. **TU** — a mindless choreography mapper  
2. **TU+** — a specialized choreography-aware predictor / comparer / replay layer  
3. **cortexLLM** — a symbolic interpreter and context-framing layer

These layers are not meant to collapse into one assistant.
They are meant to operate over a **shared structured state** across bounded recursive cycles.

This folder exists to make that stack explicit, modular, and testable.

---

## Why this subfolder exists

The broader `pre_metric_extensions` branch explores pre-metric guidance, temporal units, and choreography-sensitive architectures in general.

This subfolder narrows that work to a more specific engineering path:

- how a temporal unit might map unfolding choreographies
- how an intermediate TU+ layer might compare and predict choreography development
- how a higher symbolic layer might interpret that field without remapping it
- how persistent structured state may allow bounded escape from one-shot prompt prison
- how bounded dry-run cycles can test promotion, stress, and collapse of choreography hypotheses

This is therefore the branch-inside-the-branch for the **TU / TU+ / cortexLLM** architecture.

---

## Current architecture

The current stack is:

- **TU**  
  maps traces, motion-tokens, trains, couplings, persistence, decay, restart, and field structure

- **TU+**  
  compares current unfolding choreographies with stored patterns, predicts likely continuation, tracks mismatch, and emits attention / replay / revision signals

- **cortexLLM**  
  interprets significance, frames context, sends bounded downward bias, and critiques the evolving field without overwriting the lower structural mapping

A compact formulation:

> TU maps unfolding choreography structure. TU+ compares, predicts, and revises candidate unfolding choreographies across sources and time. cortexLLM interprets the resulting field symbolically.

---

## What has changed in this branch

The architecture is no longer only conceptual.

It has now been pushed into a bounded prototype logic environment with:

- role-bounded prompts
- shared-state schema
- structured handoffs
- toy run transcript
- bounded disconfirmation tests across multiple cycles

Those tests showed, in bounded form, that the triad can:

- preserve role separation
- maintain continuity through shared state
- absorb mismatch without collapsing
- represent weak coupling
- dissolve unsupported relational hypotheses
- reopen previously weakened hypotheses
- provisionally confirm joint choreography
- stress and later de-confirm joint choreography into a new stable reading

That makes this folder the main proof environment for the triad.

---

## Current files

### `tu_plus_architecture_note.md`
Core architecture note for the stack.

It defines:
- why TU alone is not enough
- the division of labor between TU, TU+, and cortexLLM
- why TU+ should remain specialized
- why shared structured state matters
- falsifiable prototype directions

### `shared_state_schema.md`
Defines the shared state object used by the prompt-instantiated TU / TU+ / cortexLLM triad.

This is the key runtime object that lets the architecture recurse across cycles without collapsing into free prose.

### `Toy_run_transcript.md`
A bounded toy run showing one full TU → TU+ → cortexLLM loop with explicit shared-state updates.

### `openai_responses_api_prototype_plan.md`
Minimal note on how the triad can be run as a prompt-instantiated prototype in the current OpenAI environment.

### `prototype_run_observations_01.md`
Cycle-by-cycle observations from the bounded dry-run sequence.

This is currently the most important evidence file in the folder.

---

## First practical route

The strongest first test path remains:

- bounded unfolding input
- TU choreography mapping
- TU+ predictive / replay comparison
- cortexLLM interpretation and downward bias
- return traces or next input slice
- mismatch update
- repeated bounded cycles

Video remains the strongest eventual first serious input path because it already supplies:

- time
- simultaneity
- persistence
- interruption
- drift
- recurrence

But the first successful prototype route has been narrower:
- hand-authored frame-sequence summaries
- role-bounded prompts
- shared structured state
- bounded recursive evaluation

---

## Discipline note

This subfolder should remain disciplined.

It should not become:
- generic consciousness speculation
- vague embodiment talk
- another all-purpose agent folder
- loose multi-agent enthusiasm without role boundaries

It is specifically for the architecture in which:

- choreography structure is mapped first
- awareness-support is handled by a narrow intermediate layer
- symbolic meaning remains with the higher layer
- recursion is preserved through shared state
- revision is governed by coherence rather than by free-form narration

---

## Relation to the Zenodo note

This folder now directly underlies the Zenodo note:

**World Model: Toward a Coherence-Driven Division of LLM Labor**  
**Evidence from bounded disconfirmation tests**  
DOI: `10.5281/zenodo.19145919`

The Zenodo note is the bounded public fossil.
This folder is the working prototype environment behind it.

---

## Closing statement

This subfolder records the current best initiation recipe for a coherence-driven division of LLM labor.

It exists to answer one practical question:

> What is the smallest layered architecture in which unfolding choreographies can be mapped, predicted, revised, stressed, and interpreted symbolically without collapsing into one generic assistant?

That is the purpose of the TU+ stack.
