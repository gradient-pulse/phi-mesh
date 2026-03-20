# Data Elements Note

## Purpose

This note defines the minimum data ontology for a prompt-instantiated TU / TU+ / cortexLLM stack.

The working claim is:

> If TU and TU+ are LLM-like structures operating over motion/process tokens rather than ordinary text tokens, then the first engineering requirement is to define the minimum admissible data elements of that world.

This note does not yet define final encodings.
It defines the minimum conceptual elements that must survive across the stack.

---

## 1. Source / object hypothesis

A source or object is not first treated as certain.
It is treated as a provisional identity hypothesis.

### Definition
A source/object hypothesis is:
- a provisional persistent emitter or carrier of observable change
- initially guessed from recurring visual or process structure
- later stabilized, revised, split, or dissolved by motion coherence across time

### Why this matters
The system should not assume that object identity is fixed in advance.
Identity should be strengthened or weakened by persistent choreography.

Compactly:

> A source/object is first a hypothesis, then motion either stabilizes or revises it.

---

## 2. Motion-token

A motion-token is not a human-readable symbol.
It is a processable primitive bundle.

### First admissible definition
A motion-token is a time-sliced local packet tied to a source/object hypothesis, containing at least:

- source/object hypothesis ID
- time slice
- displacement delta
- direction or angular change
- local relation or contact change
- confidence

This should remain close to unfolding trace structure.
Derived metrics such as velocity or acceleration may appear later, but should not define the primitive token.

Compactly:

> A motion-token is a primitive spatiotemporal trace bundle, not yet a derived metric.

---

## 3. Train

A train is a temporally persistent sequence of motion-tokens associated with one continuing source/object hypothesis.

### Minimum properties
- ordered
- weighted
- persistent across time slices
- revisable by new incoming motion-tokens
- capable of decay or restart

Compactly:

> A train is the persistent local sequence through which motion-tokens begin to become choreography.

---

## 4. Choreography

A choreography is a coupled cluster of one or more trains.

### Minimum properties
- one or more trains
- persistent coupling structure
- viability across time
- local continuity under change
- candidate direction emerging from interconnected trains

Compactly:

> Choreography begins when trains persist and couple strongly enough to form a coherent unfolding structure.

---

## 5. Stored choreography memory

Stored choreography memory should remain close to action and replay.

### First working assumption
- active field memory belongs in TU
- stored choreography patterns are held in a TU-near memory store
- TU+ reads and compares current trains against that store

### Why
This keeps choreography memory close to reenactment, replay, and prediction rather than burying it inside symbolic narration.

Compactly:

> Stored choreography memory should remain near the action-facing side of the stack.

---

## 6. Coherence signal

A coherence signal should not be purely local.

### Minimum ingredients
- train persistence
- coupling stability
- agreement between motion choreographies
- agreement between motion and observation choreographies
- resistance to destructive fragmentation

Compactly:

> Coherence is the degree to which trains and choreographies remain viably coupled as a whole.

---

## 7. Mismatch signal

Mismatch is not merely error.
It is delta between predicted unfolding and returned unfolding.

### Minimum ingredients
- predicted train structure
- returned trace structure
- divergence in timing
- divergence in coupling
- divergence in persistence
- divergence in whole-field coherence

Compactly:

> Mismatch is a coherence-relevant delta between predicted and returned unfolding.

---

## 8. Upward awareness-support signal

TU+ should send upward compact signals, not broad narration.

### First candidates
- choreography_id
- likely_continuation
- novelty
- instability
- mismatch
- replay_relevance
- attention_trigger

---

## 9. Downward context signal

cortexLLM should send downward contextual pressure, not low-level motion control.

### First candidates
- initiate
- sustain
- suppress
- reorient
- attend
- compare
- act
- hold

---

## Closing statement

The stack becomes engineerable only when the minimum admissible data elements are explicit.

These elements are:

- source/object hypothesis
- motion-token
- train
- choreography
- stored choreography memory
- coherence signal
- mismatch signal
- upward awareness-support signal
- downward context signal

That is the first stable data basin for TU / TU+ / cortexLLM.
