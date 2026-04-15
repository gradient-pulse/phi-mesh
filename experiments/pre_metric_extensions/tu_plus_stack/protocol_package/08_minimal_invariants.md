# T-Protocol — Minimal Invariants v1

## Purpose

This document defines the minimum invariants that must hold for an implementation to count as a faithful instance of T-Protocol.

These invariants are not optional style preferences.  
They are the minimal structural commitments that preserve the identity of the protocol.

If they are violated, the system may still function in some sense, but it should not be represented as a valid T-Protocol implementation.

---

## Core principle

T-Protocol does not derive its identity from names alone.

It derives its identity from a small set of preserved constraints on:

- role distinction
- state continuity
- update discipline
- promotion discipline
- contradiction handling
- memory use
- restart integrity

Compactly:

> The invariants are the non-negotiable conditions under which the protocol remains itself.

---

## Invariant 1 — Role separation

No role may silently absorb the work of another.

This means:
- TU may not become symbolic narrator
- TU+ may not become free symbolic interpreter
- cortexLLM may not remap the low-level field directly

**Why it matters**
Without role separation, the triad collapses into one blurred assistant.

---

## Invariant 2 — Role-bounded visibility

Each role must see only the fields it needs.

This means:
- no unrestricted whole-state access by default
- no flattening of all information into one shared unrestricted narrative space
- no role-independent omniscient prompt behavior

**Why it matters**
Without bounded visibility, the protocol loses its disciplined differentiation.

---

## Invariant 3 — Role-bounded write scope

Each role may update only the fields it is responsible for.

This means:
- TU updates structure-facing fields
- TU+ updates comparison, prediction, and salience-facing fields
- cortexLLM updates symbolic context, downward bias, and state-quality framing

**Why it matters**
Without bounded write scope, the protocol becomes unstable and self-overwriting.

---

## Invariant 4 — State continuity

A new cycle must not implicitly reset prior field structure unless explicitly justified.

This means:
- prior trains remain available where warranted
- prior hypotheses do not vanish without cause
- history is not silently discarded between cycles

**Why it matters**
Without state continuity, the protocol falls back into one-shot prompt presentism.

---

## Invariant 5 — Partial update, not total rewrite

The shared state must evolve by structured reweighting and partial update, not by total prose replacement.

This means:
- unchanged fields persist
- changed fields are revised specifically
- the whole state is not replaced by free narrative summary

**Why it matters**
Without partial update discipline, the live field dissolves into unstable narration.

---

## Invariant 6 — Non-forced promotion

No choreography, coupling, or dominant reading may be promoted merely because it is narratively attractive or symbolically convenient.

Promotion must follow:
- structural support
- repeated support where relevant
- preserved mismatch awareness
- preserved revisability

**Why it matters**
Without non-forced promotion, the protocol overcommits and loses ambiguity discipline.

---

## Invariant 7 — Contradiction preservation

Mutually exclusive continuations must remain separable when evidence does not justify reconciliation.

This means:
- branches may coexist explicitly
- contradiction may remain unresolved
- symbolic smoothing is not permitted as a substitute for support

**Why it matters**
Without contradiction preservation, the protocol becomes rhetorically neat but structurally false.

---

## Invariant 8 — Memory without domination

Past dominant readings may remain available, but they must not automatically overdetermine present interpretation.

This means:
- memory may inform
- memory may bias comparison
- memory may not override fresh evidence by default

**Why it matters**
Without this invariant, the protocol becomes stuck in its own prior conclusions.

---

## Invariant 9 — Decay without magical erasure

Unsupported branches, couplings, or interpretations should weaken or decay, not disappear without trace.

This means:
- decline is represented
- unsupported structure remains historically intelligible
- loss of dominance is not confused with total deletion

**Why it matters**
Without this invariant, the protocol loses its revision history and becomes harder to trust.

---

## Invariant 10 — Returned-trace accountability

Predicted continuations must remain answerable to returned evidence.

This means:
- returned traces must be integrable into state
- mismatch must be loggable
- predictions must be revisable in light of return evidence

**Why it matters**
Without returned-trace accountability, the protocol becomes a self-sealed storyteller.

---

## Invariant 11 — Restart without corruption

A restarted mainline must be able to emerge without collapsing old ambiguity, contradiction, or coupling history into confusion.

This means:
- restart is distinct from simple forgetting
- restart is distinct from magical clean slate
- restart preserves enough historical structure to remain intelligible

**Why it matters**
Without restart integrity, the protocol cannot recover cleanly from contradiction or collapse.

---

## Invariant 12 — Bounded symbolic influence

cortexLLM may guide interpretation and attention, but may not directly overwrite the low-level structural field.

This means:
- downward bias is bounded
- symbolic framing remains downstream of structural state
- contextual guidance is not allowed to become low-level command substitution

**Why it matters**
Without bounded symbolic influence, the protocol becomes top-down narration rather than disciplined recursive coordination.

---

## Invariant 13 — Distinction between stress and collapse

The protocol must preserve the distinction between bounded strain and actual breakdown.

This means:
- weakening need not imply collapse
- low-grade mismatch need not imply de-confirmation
- bounded stress may coexist with continuity

**Why it matters**
Without this invariant, the protocol loses recovery discipline and overreads pressure as failure.

---

## Invariant 14 — Distinction between reopening and revival

Fresh renewed relation must be distinguishable from automatic revival of a previously collapsed relation.

This means:
- new evidence is treated as new
- memory alone may not restore a prior field
- reopening remains evidence-bound

**Why it matters**
Without this invariant, the protocol confuses historical memory with present structure.

---

## Invariant 15 — Faithful triadic identity

The protocol must remain recognizably triadic and recursive.

This means:
- TU, TU+, and cortexLLM remain distinct
- the shared state remains live across cycles
- the runtime sequence remains bounded and ordered
- output is not treated as a disposable endpoint only

**Why it matters**
Without this invariant, the implementation may still be useful, but it is no longer T-Protocol in the strict sense.

---

## Minimum invariant requirement

A valid T-Protocol implementation must preserve, at minimum:

- role separation
- role-bounded visibility
- role-bounded write scope
- state continuity
- partial update discipline
- non-forced promotion
- contradiction preservation
- memory without domination
- decay without magical erasure
- returned-trace accountability
- restart without corruption
- bounded symbolic influence

If these invariants are materially abandoned, faithful use of the T-Protocol name should not be claimed.

---

## Closing statement

The invariants are the protocol’s identity constraints.

They are what prevent T-Protocol from collapsing into:

- generic prompt chaining
- unconstrained agent narration
- symbolic overwrite
- one-shot presentism
- false continuity
- rhetorical smoothing

A compact final formulation:

> T-Protocol remains itself only when its role, state, transition, and correction discipline are preserved as invariants rather than treated as optional stylistic choices.
