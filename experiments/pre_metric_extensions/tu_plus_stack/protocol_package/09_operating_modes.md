# T-Protocol — Operating Modes v1

## Purpose

This document defines the operating modes of T-Protocol.

The protocol is not a single fixed-intensity runtime pattern.  
Its discipline and depth must vary depending on application requirements.

Operating modes exist to let the same core protocol be deployed under different practical constraints without losing its identity.

---

## Core principle

The core triadic protocol remains the same across modes.

What changes by mode is the **intensity profile** of the protocol, including:

- feedback depth
- ambiguity retention
- revision tolerance
- action discipline
- evaluation strictness
- latency tolerance
- risk posture

Compactly:

> Operating modes change the constraint profile of the same protocol, not the identity of the protocol itself.

---

## Mode structure

T-Protocol currently defines three modes:

- Light
- Standard
- High-Integrity

These are not three different architectures.  
They are three different operating profiles of the same triadic runtime.

---

## 1. Light mode

### Definition
Light mode is the lowest-intensity valid form of T-Protocol.

It is intended for situations where:
- speed matters
- protocol overhead must remain low
- continuity is still helpful
- ambiguity handling adds value, but only in bounded form

### Typical use cases
- conversational systems
- workflow support
- rapid decision assistance
- lower-risk iterative support tools

### Characteristics
- shallow feedback depth
- lighter state carry-forward
- bounded but reduced ambiguity retention
- lower evaluation strictness
- low-to-moderate latency tolerance
- emphasis on responsiveness with preserved basic triadic discipline

### What must still hold
Even in Light mode, the following remain mandatory:
- role distinction
- bounded handoff order
- structured shared state
- non-forced promotion
- basic returned-trace accountability where applicable

### What Light mode is not
It is not:
- a collapse into ordinary prompt chaining
- permission to discard state discipline
- permission to merge roles informally

Compactly:

> Light mode is the minimum disciplined runtime form of T-Protocol.

---

## 2. Standard mode

### Definition
Standard mode is the default fuller form of T-Protocol.

It is intended for situations where:
- repeated interaction matters
- continuity matters strongly
- prediction and revision matter
- ambiguity must be preserved more carefully
- bounded recovery and restart behavior matter

### Typical use cases
- planning systems
- enterprise coordination
- long-horizon state management
- multi-step interpretation
- recursive advisory systems

### Characteristics
- fuller feedback depth
- stronger state continuity
- stronger ambiguity retention
- stronger mismatch accountability
- stronger revision discipline
- moderate latency tolerance
- balanced emphasis on interpretability and usability

### What must still hold
Standard mode must preserve all core invariants and should support:
- branch preservation where needed
- restart integrity
- bounded symbolic guidance
- clear distinction between weakening and collapse

Compactly:

> Standard mode is the main working form of T-Protocol for serious state-sensitive coordination.

---

## 3. High-Integrity mode

### Definition
High-Integrity mode is the strongest-discipline form of T-Protocol.

It is intended for situations where:
- novelty is high
- ambiguity is consequential
- recovery must be carefully handled
- edge-case misclassification is costly
- interpretive discipline matters more than speed

### Typical use cases
- supervisory autonomy
- robotics oversight
- anomaly-aware supervisory systems
- edge-case interpretation layers
- safety-relevant coordination settings

### Characteristics
- deepest feedback discipline
- strongest continuity preservation
- strongest ambiguity retention before closure
- strongest mismatch and contradiction discipline
- strongest restart and returned-trace accountability
- highest evaluation strictness
- highest acceptable overhead and latency tolerance

### What High-Integrity mode is for
It is for cases where the protocol should:
- stay oriented under change
- resist premature closure
- preserve unresolved alternatives when warranted
- handle recovery and renewed contact carefully
- reduce brittle drift under unfamiliar conditions

### What High-Integrity mode is not
It is not:
- raw reflex control
- hard real-time motor control
- a substitute for low-level deterministic safety loops

Compactly:

> High-Integrity mode is the strongest supervisory and interpretive discipline form of T-Protocol.

---

## Mode comparison dimensions

### 1. Feedback depth
- **Light** — shallow
- **Standard** — moderate
- **High-Integrity** — deep and explicit

### 2. State carry-forward
- **Light** — basic continuity
- **Standard** — strong continuity
- **High-Integrity** — strongest continuity and recovery relevance

### 3. Ambiguity retention
- **Light** — bounded
- **Standard** — important
- **High-Integrity** — critical

### 4. Mismatch accountability
- **Light** — basic
- **Standard** — strong
- **High-Integrity** — strict

### 5. Restart / recovery discipline
- **Light** — minimal but valid
- **Standard** — present and important
- **High-Integrity** — explicit and central

### 6. Evaluation strictness
- **Light** — basic internal checks
- **Standard** — stronger internal checks
- **High-Integrity** — highest internal discipline and review

### 7. Latency tolerance
- **Light** — low latency required
- **Standard** — moderate latency acceptable
- **High-Integrity** — higher latency acceptable if interpretive quality improves

---

## Mode selection rule

The correct rule is:

> Select the lowest mode that still preserves the continuity, ambiguity handling, recovery discipline, and interpretive quality required by the application.

This avoids:
- under-deploying the protocol where stronger discipline is needed
- over-deploying the protocol where a lighter form is sufficient

---

## Mode invariance

Across all three modes, the following remain invariant:

- triadic role structure
- bounded role handoff order
- structured shared state
- feedback-mediated recursion
- non-forced promotion
- contradiction sensitivity
- faithful use discipline

If these are materially abandoned, the system has not simply changed mode.  
It has ceased to be a faithful T-Protocol implementation.

---

## Practical deployment guidance

### Use Light mode when
- responsiveness matters most
- risk is lower
- continuity helps but need not be maximally deep
- the system supports low-friction repeated interaction

### Use Standard mode when
- the system must keep its bearings over time
- revision and mismatch matter
- state continuity is operationally important
- the use case is serious but not maximally safety-sensitive

### Use High-Integrity mode when
- novelty and ambiguity are high
- false closure is costly
- recovery quality matters strongly
- supervisory interpretation under uncertainty is central

---

## Closing statement

Operating modes let T-Protocol adapt to application demands without losing its identity.

They should be understood as:
- different intensity profiles
- of one protocol
- under one set of invariants

A compact final formulation:

> T-Protocol modes are different constraint apertures of the same triadic recursive protocol, not different protocols.
