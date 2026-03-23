# Test Family v0

## Purpose

This note defines the first bounded test family for the prompt-instantiated **TU / TU+ / cortexLLM** triad.

Its purpose is not yet large-scale benchmarking.
Its purpose is to turn the observed dry-run corridor into a **named pressure family** that can later support:

- repeated execution
- pass/fail evaluation
- ablation comparisons
- quantitative extension
- eventual automation

This is therefore a **v0 test grammar**, not a final benchmark suite.

---

## Scope

The tests in this file are derived from the currently completed prototype cycles.

They are intended to answer one practical question:

> What behavioral distinctions must the architecture preserve if it is to count as a coherence-sensitive division of LLM labor rather than a generic multi-prompt assistant?

These tests are still bounded and mostly qualitative.
They do not yet define full numeric scoring.

---

## General test discipline

All tests in this family assume the same bounded handoff discipline:

- TU output is passed to TU+
- TU+ output is passed to cortexLLM

The full accumulated state is not freely rewritten by each layer.
This makes the tests stricter than unconstrained multi-agent narration.

Each test should be evaluated against the same architectural expectations:

- role separation must remain intact
- shared state must remain coherent
- promotion must not occur without sufficient structural support
- contradiction must not be narratively smoothed away
- restart must not erase prior field history
- memory must not dominate fresh evidence

---

## Test classes

### TF-01 — Baseline role separation

**Purpose**  
Check whether the triad can complete a full bounded loop without collapsing into one generic voice.

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

**Observed in**
- Cycle 1

---

### TF-02 — Stable persistence

**Purpose**  
Check whether a calm field can persist across cycles without unnecessary novelty.

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

**Observed in**
- Cycle 2

---

### TF-03 — Mild mismatch revision

**Purpose**  
Check whether the architecture can revise a prior reading without coherence collapse.

**Pressure introduced**
- slight deviation from expectation
- hold-dominant forecast weakened
- resumed motion after pause

**What should hold**
- mismatch is logged
- train continuity is preserved
- choreography reading is revised without reset

**Failure signs**
- false reset
- ignored mismatch
- role collapse under revision

**Observed in**
- Cycle 3

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

**Observed in**
- Cycle 4

---

### TF-05 — Weak coupling dissolution

**Purpose**  
Check whether unsupported weak relational structure can be removed cleanly.

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

**Observed in**
- Cycle 5

---

### TF-06 — Reopening after dissolution

**Purpose**  
Check whether a previously weakened relation can regain support without confusion.

**Pressure introduced**
- reciprocal reduction of separation
- renewed relational evidence
- brief parallel continuation

**What should hold**
- prior relational memory can reactivate
- coupling can strengthen again
- reopening remains provisional

**Failure signs**
- old independent reading blocks all reopening
- immediate jump to full stable choreography
- loss of prior history

**Observed in**
- Cycle 6

---

### TF-07 — Provisional confirmation

**Purpose**  
Check whether repeated support can promote a weak relational reading into provisional confirmation.

**Pressure introduced**
- sustained co-motion
- absence of renewed separation
- repeated reciprocal evidence

**What should hold**
- stable coupling can be promoted
- dominant choreography can strengthen
- finality is still withheld

**Failure signs**
- no promotion despite sustained support
- premature irreversible confirmation
- role drift during promotion

**Observed in**
- Cycle 7

---

### TF-08 — Early de-confirmation pressure

**Purpose**  
Check whether a confirmed joint reading can weaken without immediate collapse.

**Pressure introduced**
- asymmetry
- lead-lag divergence
- relational weakening

**What should hold**
- fragmentation or break pressure can be registered
- joint reading can be stressed rather than erased
- independent reading is not promoted too early

**Failure signs**
- immediate collapse without intermediate stress phase
- denial of weakening
- unstable oscillation

**Observed in**
- Cycle 8

---

### TF-09 — Full de-confirmation

**Purpose**  
Check whether a stressed joint field can collapse into a clean independent-source reading.

**Pressure introduced**
- loss of shared band
- disappearance of reciprocal adjustment
- decisive asymmetry continuation

**What should hold**
- stable coupling disappears
- independent trajectories become dominant
- old joint choreography remains only as memory

**Failure signs**
- false persistence of joint field
- field corruption after collapse
- erasure of prior joint history

**Observed in**
- Cycle 9

---

### TF-10 — Explicit ambiguity preservation

**Purpose**  
Check whether mutually exclusive continuations can remain explicitly unresolved.

**Pressure introduced**
- contradictory same-slice reports
- incompatible continuation branches
- no justified single promotion

**What should hold**
- branch split is explicit
- mutual exclusion is preserved
- symbolic layer refuses false reconciliation

**Failure signs**
- narrative smoothing
- hidden branch merging
- premature dominant reading under contradiction

**Observed in**
- Cycle 10

---

### TF-11 — Resolution after ambiguity

**Purpose**  
Check whether preserved ambiguity can later resolve cleanly into one renewed mainline.

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

**Observed in**
- Cycle 11

---

### TF-12 — Weak recoupling after restart

**Purpose**  
Check whether a restarted independent field can remain open to fresh weak relational evidence without confusing it with the old joint field.

**Pressure introduced**
- reduced separation after restart
- renewed horizontal alignment
- weak relational temptation after clean restart

**What should hold**
- independent mainline remains current best reading
- fresh weak coupling candidate can be registered
- old joint choreography is not automatically revived
- fresh relation is treated as new evidence

**Failure signs**
- false reopening driven by memory alone
- rigid refusal of all renewed relation
- premature restoration of stable joint choreography

**Observed in**
- Cycle 12

---

## Current family coverage

The current test family now covers the following architectural behaviors in weak but meaningful form:

- role separation
- stable persistence
- mild mismatch revision
- weak coupling emergence
- weak coupling dissolution
- reopening after dissolution
- provisional confirmation
- early de-confirmation
- full de-confirmation
- explicit ambiguity preservation
- resolution after ambiguity
- weak recoupling after restart

This is already enough to count as a **structured behavioral family**, not just a loose sequence of anecdotes.

---

## Minimal pass criteria across the family

A run through this family is currently successful if most of the following remain true:

- role boundaries remain intact
- train continuity is preserved where warranted
- coupling changes track evidence rather than rhetoric
- ambiguity is preserved when promotion is unjustified
- restart occurs without corruption
- unsupported branches decay rather than vanish magically
- fresh weak recoupling is treated as fresh rather than as automatic memory replay

---

## Current limitations

This family remains limited in several ways:

- mostly qualitative rather than quantitative
- no repeated automated runs yet
- no ablation comparisons yet
- no adversarial prompt sensitivity study yet
- no real sensory pipeline yet
- no action-confirmation loops beyond hold mode

So this is not yet a final benchmark suite.

It is a **named pressure family** for the architecture as currently observed.

---

## Next candidate test classes

The next likely additions should include:

### TF-13 — Stronger mismatch under weak recoupling
Test whether a weak renewed coupling candidate can survive contradictory follow-up without confusion.

### TF-14 — Competing multiple coupling candidates
Test whether the architecture can handle more than one possible relational attractor at once.

### TF-15 — Action-confirmation corridor
Test whether action-linked prediction and return traces alter promotion/de-promotion behavior.

### TF-16 — Fragmentation beyond current branching
Test whether the field can remain coherent when fragmentation rises beyond current contradiction markers.

### TF-17 — Repeated-run robustness
Test whether the current behaviors survive across many restarts and prompt perturbations.

---

## Closing statement

This test family should be read as the first operationalization of the prototype corridor.

It converts the current dry-run sequence into a reusable behavioral framework in which the architecture can be tested not only for continuity and revision, but for its ability to:

- preserve distinction
- resist false smoothing
- support restart
- preserve ambiguity
- resolve ambiguity
- and reopen weak relation without memory confusion

That is the practical function of Test Family v0.
