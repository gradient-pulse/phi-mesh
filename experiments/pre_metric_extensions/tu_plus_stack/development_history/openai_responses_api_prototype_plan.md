# OpenAI Responses API Prototype Plan

## Purpose

This note defines the first bounded OpenAI-native prototype path for the prompt-instantiated TU / TU+ / cortexLLM triad.

The aim is not full robotics or full video ingestion yet.
The aim is to test whether the triad can run with:

- persistent shared state
- strict role boundaries
- structured outputs
- bounded recursive cycles

---

## Core idea

Use the OpenAI Responses API to run:

- TU as a mindless choreography mapper
- TU+ as a choreography-aware predictor / comparer
- cortexLLM as a symbolic interpreter

All three operate over a shared structured state.

---

## Prototype assumptions

The first prototype will use:

- hand-authored frame-sequence summaries rather than full video
- strict markdown / JSON-like schemas
- a small number of recursive cycles
- human supervision over each loop

This keeps the first test narrow and legible.

---

## Minimal loop

1. initialize shared state
2. pass allowed input fields to TU
3. TU writes allowed output fields
4. update shared state
5. pass allowed input fields to TU+
6. TU+ writes allowed output fields
7. update shared state
8. pass allowed input fields to cortexLLM
9. cortexLLM writes allowed output fields
10. update shared state
11. repeat if needed

---

## Success condition

The prototype succeeds if:

- TU, TU+, and cortexLLM remain role-distinct
- the shared state persists across cycles
- outputs remain schema-bounded
- the triad behaves differently from a single vague assistant

---

## Failure condition

The prototype fails if:

- the roles collapse into generic prose
- state is not meaningfully preserved
- TU or TU+ drift into symbolic narration
- cortexLLM starts micromanaging low-level motion structure

---

## First practical input

The first practical input should be:

- one hand-authored frame-sequence summary
- one shared state object
- one bounded toy loop
- one human-reviewed cycle update

Only after this works should the prototype move toward richer image or video-derived input.

---

## Why this is enough for now

This prototype does not need to prove the final architecture.
It only needs to prove that:

- bounded recursion is possible
- role separation is maintainable
- shared-state persistence improves continuity
- TU / TU+ / cortexLLM can function as a triad rather than collapsing into one assistant

---

## Closing statement

The Responses API prototype is the first practical test of whether the TU / TU+ / cortexLLM architecture can run as a bounded prompt-instantiated machine inside the OpenAI ecosystem.
