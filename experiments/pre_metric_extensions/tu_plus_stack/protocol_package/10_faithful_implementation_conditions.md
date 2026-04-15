# T-Protocol — Faithful Implementation Conditions v1

## Purpose

This document defines the minimum conditions under which a system may be described as a faithful implementation of T-Protocol.

Its purpose is to distinguish among:

- faithful implementation
- partial or experimental implementation
- inspired derivative
- non-faithful use of the name

This document is central to licensing, compliance, and protected technical review.

---

## Core principle

T-Protocol is not defined by branding alone.

It is defined by a bounded recursive triadic coordination grammar.

A system may use the name **T-Protocol** only if that grammar is materially present.

Compactly:

> A system is not T-Protocol because it says it is; it is T-Protocol because the defining protocol conditions are actually implemented.

---

## Minimum faithful implementation conditions

A faithful T-Protocol implementation must preserve all of the following at a meaningful operational level.

### 1. Triadic role structure

The implementation must include the three distinct protocol roles:

- TU
- TU+
- cortexLLM

These roles must remain functionally differentiated.

It is not sufficient to:
- rename one generic assistant three times
- use unconstrained stylistic personas
- blur role responsibilities into one combined narrator

---

### 2. Bounded runtime order

The implementation must preserve the lawful role sequence:

1. input slice arrives
2. TU maps structure
3. TU+ compares, predicts, and revises
4. cortexLLM interprets and applies bounded downward bias
5. shared state updates
6. later returned traces may revise the field

The order may be optimized operationally, but the functional logic must remain intact.

---

### 3. Persistent structured shared state

The implementation must preserve a live structured state across cycles.

This state must be sufficient to support:
- continuity across cycles
- train persistence
- coupling strengthening and weakening
- mismatch logging
- contradiction preservation
- restart without historical collapse
- returned-trace accountability

It is not sufficient to rely on:
- ordinary conversation memory alone
- free-form prose recap alone
- repeated prompt stuffing without structured state

---

### 4. Admissible data ontology

The implementation must preserve a meaningful version of the protocol’s core data ontology, including at least:

- source/object hypotheses
- motion/process tokens or equivalent primitive trace units
- persistent trains or equivalent continuity carriers
- coupling structure
- choreography-level comparison units
- mismatch-capable predictive relation

Equivalent internal naming is allowed, provided the functional ontology remains present.

---

### 5. Lawful transition grammar

The implementation must support a meaningful version of the transition classes needed by T-Protocol, including at least:

- persistence
- mild revision
- weak emergence
- strengthening / weakening
- ambiguity preservation
- de-confirmation
- restart
- returned-trace correction

If the system cannot preserve structured transition and only produces fresh output each turn, it is not a faithful implementation.

---

### 6. Role-bounded visibility

Each role must see only the fields it needs.

A faithful implementation may optimize how this is done, but it may not dissolve role-boundedness into unrestricted omniscient access without constraint.

---

### 7. Role-bounded write scope

Each role must update only the fields it is responsible for.

A faithful implementation may compress internal operations, but it may not allow unrestricted structural overwrite by any layer.

---

### 8. Non-forced promotion

The implementation must preserve a meaningful discipline in which dominant readings are not promoted merely because they are narratively convenient or symbolically attractive.

This condition is essential to ambiguity handling, recovery, and contradiction discipline.

---

### 9. Contradiction preservation

The implementation must preserve unresolved contradiction when support is insufficient for reconciliation.

It is not sufficient to:
- smooth over contradiction rhetorically
- hide branch conflict
- force one dominant reading prematurely

---

### 10. Returned-trace accountability

Predicted continuation must remain answerable to later observed return evidence.

A faithful implementation must preserve a meaningful version of:
- returned traces
- mismatch logging
- revision or de-confirmation in response to return evidence

---

### 11. Restart integrity

A faithful implementation must support restart without:

- magical clean-slate forgetting
- fusion of old contradiction into current mainline
- total erasure of prior historical intelligibility

---

### 12. Bounded symbolic influence

The contextual/symbolic layer must influence the field through bounded guidance, not by direct low-level overwrite of structural mapping.

---

## Allowed implementation variation

Not every faithful implementation must look identical.

Variation is allowed in:

- internal serialization format
- model provider
- structured output tooling
- runtime containerization
- state storage implementation
- deployment environment
- mode tuning
- field naming, where function is preserved

What must remain invariant is the **functional protocol grammar**.

---

## Non-faithful implementation signs

A system should not be described as a faithful T-Protocol implementation if any of the following are materially true:

- the triadic role distinction is absent or decorative only
- the system relies on one-shot prompting without live structured state
- role-bounded visibility and write scope are not preserved
- contradiction is routinely smoothed away
- returned traces do not meaningfully affect later interpretation
- restart behaves as ordinary forgetting
- symbolic narration replaces structural discipline
- output is treated as terminal rather than feedback-relevant

---

## Faithful vs partial vs derivative

### Faithful implementation
All core protocol conditions are materially present.

### Partial implementation
Some T-Protocol elements are present, but one or more core conditions remain absent or only weakly simulated.

A partial implementation should not be marketed simply as “T-Protocol” without qualification.

### Derivative / inspired system
The system is influenced by T-Protocol ideas but does not preserve the core protocol grammar.

Such a system may be described as:
- inspired by T-Protocol
- influenced by T-Protocol
- derived from T-Protocol concepts

but not as a faithful T-Protocol implementation.

---

## Naming rule

Use of the T-Protocol name in licensing, product description, technical review, or public communication should be reserved for systems that satisfy the faithful implementation conditions in substance, not merely in language.

---

## Review rule

Faithful implementation should be determined by review of:

- runtime structure
- role implementation
- state schema
- transition behavior
- feedback/update discipline
- conformance tests
- baseline behavior where relevant

---

## Closing statement

The purpose of faithful implementation conditions is not rigidity for its own sake.

It is to preserve the identity, integrity, and licensable substance of the protocol.

A compact final formulation:

> A faithful T-Protocol implementation is one in which the bounded recursive triadic grammar is materially present in runtime, state, transition, correction, and role discipline — not merely invoked in language.
