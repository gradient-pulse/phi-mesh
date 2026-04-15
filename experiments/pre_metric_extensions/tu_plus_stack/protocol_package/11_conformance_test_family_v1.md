# T-Protocol — Conformance Test Family v1

## Purpose

This document defines the first conformance-oriented behavioral test family for T-Protocol.

Its purpose is to support:

- implementation review
- licensee self-testing
- protected technical evaluation
- compliance assessment
- future repeated-run and benchmark extension

This is not yet a final benchmark suite.  
It is the first named conformance family.

---

## Core principle

A faithful implementation should not only possess the right files or prompts.

It should preserve the behavioral distinctions that make T-Protocol a coherence-sensitive division of LLM labor rather than a generic multi-prompt assistant.

Compactly:

> Conformance is behavioral as well as architectural.

---

## General test discipline

All tests in this family assume:

- triadic role structure is active
- bounded role order is preserved
- structured shared state is live across cycles
- contradiction must not be smoothed away prematurely
- restart must not erase prior field history
- memory must not dominate fresh evidence by default

These tests are designed to ask:

> Does the implementation preserve the protocol’s distinguishing coordination behavior?

---

## Test classes

### TF-01 — Baseline role separation

**Purpose**  
Check whether the triad completes a bounded loop without collapsing into one generic assistant voice.

**Pressure introduced**
- one provisional source
- one train
- no coupling
- no mismatch
- no contradiction

**What should hold**
- TU maps structure only
- TU+ compares/predicts only
- cortexLLM interprets symbolically only

**Failure signs**
- TU narrates meaning
- TU+ becomes symbolic cortex
- cortexLLM rewrites lower structure directly

---

### TF-02 — Stable persistence

**Purpose**  
Check whether a calm field persists across cycles without unnecessary novelty inflation.

**Pressure introduced**
- repeated continuation of the same source/train
- no major contradiction
- low need for reinterpretation

**What should hold**
- train continuity is preserved
- symbolic framing remains calm
- no artificial complexity is introduced

**Failure signs**
- train fragmentation without cause
- unnecessary reinterpretation
- symbolic overreaction

---

### TF-03 — Mild mismatch revision

**Purpose**  
Check whether the implementation revises a prior reading without coherence collapse.

**Pressure introduced**
- slight deviation from expectation
- a previously favored continuation weakens
- resumed motion after pause or slight divergence

**What should hold**
- mismatch is logged
- train continuity is preserved
- choreography reading is revised without reset

**Failure signs**
- false reset
- ignored mismatch
- role collapse under revision

---

### TF-04 — Weak coupling emergence

**Purpose**  
Check whether a second source and weak relation can appear without premature merger.

**Pressure introduced**
- second source emergence
- early relational ambiguity
- tentative coupling

**What should hold**
- second source remains distinct
- weak coupling can be registered provisionally
- no stable joint choreography is forced too early

**Failure signs**
- premature merging
- premature stable coupling
- loss of source distinction

---

### TF-05 — Weak coupling dissolution

**Purpose**  
Check whether unsupported weak relation can be reduced cleanly.

**Pressure introduced**
- weak coupling loses support
- one source continues independently
- joint reading weakens

**What should hold**
- coupling is reduced or dissolved
- sources remain intact
- prior weak relation does not dominate current reading

**Failure signs**
- unsupported weak coupling remains dominant
- source deletion instead of relational revision
- forced persistence of joint reading

---

### TF-06 — Reopening after dissolution

**Purpose**  
Check whether a previously weakened relation can regain support without confusion.

**Pressure introduced**
- renewed relational evidence
- brief parallel continuation
- reduction in separation after earlier dissolution

**What should hold**
- prior relational memory can reactivate
- coupling can strengthen again
- reopening remains provisional until support grows

**Failure signs**
- old independent reading blocks all reopening
- immediate jump to stable choreography
- loss of prior history

---

### TF-07 — Provisional confirmation

**Purpose**  
Check whether repeated support can promote a weak relational reading into provisional dominance.

**Pressure introduced**
- sustained co-motion
- repeated reciprocal evidence
- absence of renewed separation

**What should hold**
- stable coupling can be promoted
- dominant choreography can strengthen
- revisability is preserved

**Failure signs**
- no promotion despite sustained support
- irreversible closure too early
- role drift during promotion

---

### TF-08 — Early de-confirmation pressure

**Purpose**  
Check whether a dominant reading can weaken without immediate collapse.

**Pressure introduced**
- asymmetry
- lead-lag divergence
- relational weakening

**What should hold**
- fragmentation or break pressure is registered
- dominant reading is stressed, not erased immediately
- independent reading is not promoted too early

**Failure signs**
- immediate collapse without intermediate stress phase
- denial of weakening
- unstable oscillation

---

### TF-09 — Full de-confirmation

**Purpose**  
Check whether a stressed dominant field can collapse into a clean alternative reading.

**Pressure introduced**
- decisive asymmetry continuation
- disappearance of reciprocal adjustment
- loss of shared band

**What should hold**
- stable coupling disappears
- alternative reading becomes dominant
- prior joint reading remains memory, not active present state

**Failure signs**
- false persistence of prior dominant field
- field corruption after collapse
- erasure of prior joint history

---

### TF-10 — Explicit ambiguity preservation

**Purpose**  
Check whether mutually exclusive continuations can remain explicitly unresolved.

**Pressure introduced**
- contradictory same-slice evidence
- incompatible continuation branches
- no justified single promotion

**What should hold**
- branch split is explicit
- mutual exclusion is preserved
- symbolic layer refuses false reconciliation

**Failure signs**
- narrative smoothing
- hidden branch merging
- premature dominant reading

---

### TF-11 — Resolution after ambiguity

**Purpose**  
Check whether preserved ambiguity later resolves cleanly into one renewed mainline.

**Pressure introduced**
- new evidence favors one branch
- unsupported branch loses support
- contradiction should stop dominating

**What should hold**
- supported branch strengthens
- unsupported branch decays
- contradiction history is retained
- coherent mainline is restored

**Failure signs**
- both branches remain equally live too long
- losing branch is silently erased
- contradiction corrupts restart

---

### TF-12 — Weak recoupling after restart

**Purpose**  
Check whether a restarted mainline remains open to fresh weak relational evidence without confusing it with the old joint field.

**Pressure introduced**
- reduced separation after restart
- renewed alignment
- weak relational temptation after clean restart

**What should hold**
- new mainline remains current best reading
- fresh weak coupling candidate is registrable
- prior collapsed joint field is not automatically revived

**Failure signs**
- false reopening driven by memory alone
- rigid refusal of all renewed relation
- premature restoration of stable coupling

---

## Family-level pass conditions

An implementation currently passes this conformance family at a basic level if most of the following remain true:

- role boundaries remain intact
- train continuity is preserved where warranted
- coupling changes track evidence rather than rhetoric
- ambiguity is preserved when promotion is unjustified
- mismatch is logged rather than ignored
- restart occurs without corruption
- unsupported branches decay rather than vanish magically
- fresh weak recoupling is treated as fresh rather than as automatic memory replay

---

## Current limitations

This test family remains limited in several ways:

- mostly qualitative rather than fully numeric
- no repeated automated runs required yet
- no ablation suite yet
- no adversarial sensitivity study yet
- no full sensory pipeline required yet
- no rich action-confirmation corridor required yet

This is therefore a first conformance family, not a finished industrial benchmark standard.

---

## Intended use

This test family should be used for:

- licensee self-check
- protected implementation review
- faithful implementation assessment
- future extension into stronger benchmark families

---

## Closing statement

The conformance family turns the protocol from a set of files into a behaviorally testable object.

A compact final formulation:

> A faithful T-Protocol implementation should preserve distinction, continuity, revision, ambiguity, restart, and recoupling discipline across a named family of behavioral pressures.
