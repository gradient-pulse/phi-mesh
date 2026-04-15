# T-Protocol — Compliance and Review v1

## Purpose

This document defines the compliance and review logic for T-Protocol.

Its purpose is to specify how a candidate implementation is assessed for:

- faithful implementation
- conformance with core protocol requirements
- deployment readiness
- ongoing compliance after modification
- correct use of the T-Protocol name

This is not a legal contract by itself.  
It is the protocol-side review and compliance framework that supports licensing and protected technical evaluation.

---

## Core principle

Compliance is not satisfied by branding, enthusiasm, or partial resemblance.

A system should count as compliant only if the defining operational grammar of T-Protocol is materially present in:

- runtime structure
- role discipline
- state persistence
- transition handling
- feedback/update discipline
- conformance behavior

Compactly:

> Compliance means the protocol is actually being preserved, not merely described.

---

## What compliance review is for

Compliance review exists to answer five practical questions:

1. Is the implementation recognizably T-Protocol?
2. Are the triadic roles materially distinct?
3. Is the shared state truly live across cycles?
4. Does the implementation behave correctly under core conformance pressures?
5. Should the system be allowed to use the T-Protocol name without qualification?

---

## Review stages

### Stage 1 — Document review

The reviewer should first assess the candidate implementation against the package documents, especially:

- `01_protocol_overview.md`
- `02_role_definitions.md`
- `03_runtime_order_and_role_handoffs.md`
- `04_data_ontology.md`
- `05_shared_state_schema.md`
- `06_feedback_and_state_update_rules.md`
- `07_transition_grammar.md`
- `08_minimal_invariants.md`
- `09_operating_modes.md`
- `10_faithful_implementation_conditions.md`

**Purpose**
- confirm that the implementer understands the protocol object
- detect obvious non-faithful simplifications early
- clarify intended deployment mode and use case

---

### Stage 2 — Structural implementation review

The reviewer should then check whether the implementation materially preserves:

- triadic role structure
- bounded runtime order
- role-bounded visibility
- role-bounded write scope
- persistent structured shared state
- returned-trace path where relevant
- lawful feedback and update discipline

**Purpose**
- confirm that the implementation is structurally protocol-like, not just rhetorically similar

---

### Stage 3 — Behavioral conformance review

The reviewer should assess the implementation against the conformance family in:

- `11_conformance_test_family_v1.md`

At minimum, the reviewer should confirm whether the implementation preserves:
- role separation
- stable persistence
- mild revision
- weak coupling emergence/dissolution
- ambiguity preservation
- de-confirmation handling
- restart integrity
- weak recoupling discipline

**Purpose**
- verify that the implementation behaves like T-Protocol under named pressures

---

### Stage 4 — Baseline stability review

The reviewer should assess the implementation against:

- `12_non_transition_baseline_contract.md`

**Purpose**
- ensure that benign signal-space change is not being overread as true structural activation
- verify calm-regime stability
- reduce false positives in later deployment interpretation

---

### Stage 5 — Deployment review

The reviewer should assess whether the chosen deployment matches the protocol and the selected operating mode.

This includes checking:
- deployment class
- mode selection
- latency expectations
- returned-trace availability
- supervisory vs reflex control separation
- state persistence strategy

**Purpose**
- ensure the protocol is being applied where it actually fits

---

## Compliance categories

### 1. Faithful compliant implementation
The implementation materially satisfies the faithful implementation conditions and passes core review.

Allowed description:
- T-Protocol implementation
- compliant T-Protocol deployment

---

### 2. Qualified / partial implementation
The implementation preserves meaningful parts of T-Protocol, but one or more core conditions are missing, weakened, or still under review.

Allowed description:
- partial T-Protocol implementation
- T-Protocol-derived pilot
- T-Protocol-inspired deployment under review

Not allowed without qualification:
- simply “T-Protocol”

---

### 3. Non-compliant / non-faithful implementation
The implementation materially lacks core protocol conditions.

Examples:
- decorative triadic prompts only
- no persistent structured shared state
- role collapse into one generic assistant
- no returned-trace accountability where relevant
- contradiction smoothing as default behavior

Allowed description:
- inspired by T-Protocol concepts

Not allowed:
- representation as a T-Protocol implementation

---

## Minimum review evidence

A candidate implementation should provide enough evidence for review, including as applicable:

- role definitions as instantiated in the system
- runtime sequencing logic
- shared state representation
- state update mechanism
- feedback/returned-trace path
- example cycle traces
- conformance test results
- deployment mode declaration
- known deviations from core package

This evidence need not reveal proprietary model internals unrelated to the protocol, but it must be sufficient to evaluate the protocol layer itself.

---

## Review questions

A reviewer should ask at least the following:

### Structural
- Are TU, TU+, and cortexLLM materially distinct?
- Is the role order preserved?
- Is state persistent and structured across cycles?
- Are visibility and write scope bounded?

### Behavioral
- Does the system preserve ambiguity when warranted?
- Does mismatch affect later state?
- Can restart occur without historical collapse?
- Can weak recoupling be distinguished from automatic revival?
- Does the system avoid forcing dominant readings too early?

### Deployment
- Is the selected mode appropriate?
- Is this being used as supervisory coordination rather than miscast as raw reflex control?
- Is the returned-trace path adequate for the intended use?

---

## Re-review triggers

A compliant implementation should be re-reviewed if any material change occurs in:

- role definitions
- runtime order
- shared state design
- feedback/update logic
- transition handling
- mode calibration
- deployment domain
- returned-trace pathway
- conformance behavior

Compactly:

> Material protocol change requires re-review.

---

## Compliance failure signs

A review should be treated as failed or incomplete if any of the following are true:

- the triadic role distinction is only stylistic
- shared state is absent or decorative
- runtime order is not materially preserved
- contradiction is routinely smoothed away
- returned traces do not influence later field behavior
- restart behaves as clean forgetting
- symbolic framing overwrites structural mapping
- conformance tests are not meaningfully passable

---

## Ongoing compliance principle

Compliance is not a one-time label only.

A faithful deployment should remain reviewable over time, especially when:
- tuned
- optimized
- accelerated
- embedded in larger orchestration stacks
- adapted for new domains

This matters because protocol identity can be diluted gradually.

---

## Closing statement

The purpose of compliance and review is to preserve the identity and seriousness of T-Protocol while still allowing deployment variation.

A compact final formulation:

> A T-Protocol review asks whether the bounded recursive triadic grammar is materially present in structure, behavior, and deployment — and whether the system still deserves the name after implementation choices are made.
