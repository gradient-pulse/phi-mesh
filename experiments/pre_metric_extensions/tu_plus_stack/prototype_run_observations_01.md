# Prototype Run Observations 01

## Scope

This note records observations from the first three bounded dry-run cycles of the prompt-instantiated TU / TU+ / cortexLLM triad.

The purpose is to preserve the baseline before introducing stronger pressures such as:
- second-source interaction
- coupling
- restart pressure
- fragmentation
- stronger mismatch
- more explicit action-confirmation dynamics

---

## What was tested

### Cycle 1
A first full dry-run cycle using:
- one provisional source
- one train
- no coupling
- no returned traces
- no mismatch

### Cycle 2
A second dry-run cycle using the full post-cycle-1 shared state, testing:
- persistence across cycles
- stabilization of the same source/train
- continued role separation
- slight refinement of choreography match and hold-state interpretation

### Cycle 3
A third dry-run cycle introducing a mild returned-trace mismatch:
- a prior hold-dominant expectation
- brief confirmation of hold
- followed by slight resumed rightward motion
- revision of the active choreography interpretation
- mismatch logging without collapse of coherence

---

## Important test discipline used

During the dry runs, only the output of the immediately prior role was passed forward:

- TU output was passed to TU+
- TU+ output was passed to cortexLLM

This made the test stricter than a full-state pass-through, because each role had to operate from bounded upstream structure rather than from the full accumulated state.

This strengthens the finding that role separation is viable.

---

## Main findings so far

### 1. Role separation is viable
The triad did not collapse into one generic assistant voice.

- **TU** remained a mapper of structure
- **TU+** remained a predictor / comparer
- **cortexLLM** remained a symbolic interpreter and biaser

This is already a meaningful threshold crossed.

---

### 2. Shared state is not ornamental
The shared state proved useful rather than decorative.

It allowed:
- continuity across cycles
- stabilization of the active train
- strengthening of source confidence
- preservation and revision of the predictive match
- symbolic context that did not overwrite lower-level structure

---

### 3. Stable persistence can be carried across cycles
Cycle 2 showed that the architecture can preserve a calm, coherent field without inventing unnecessary novelty or collapse.

This is important because it suggests the triad can:
- hold a stable interpretation
- lightly refine it
- avoid overreacting
- maintain narrow role discipline

---

### 4. TU+ can remain narrow
TU+ did not become a second cortexLLM.
It stayed in its lane by:
- matching choreography memory
- refining likely continuation
- preserving or raising attention appropriately
- logging mismatch when needed
- revising the best-fit choreography without drifting into broad narration

This supports the idea that prompt-instantiated specialization is feasible.

---

### 5. cortexLLM can bias without micromanaging
cortexLLM framed the scene symbolically and sent compact downward bias without rewriting motion structure.

This is important because it suggests the stack can support top-down influence without collapsing into symbolic domination of all layers.

---

### 6. Mild mismatch can be absorbed without coherence collapse
Cycle 3 is the first genuinely important pressure test.

The prior expectation was roughly:
- hold state
- maybe resume later

The returned trace showed:
- brief hold
- then slight resumed rightward motion

The architecture absorbed this by:
- **TU** extending the train rather than fragmenting it
- **TU+** revising the choreography match from a hold-dominant reading toward a pause-to-resume reading
- **cortexLLM** updating the symbolic framing without overreacting

This shows that the triad can revise interpretation under mild mismatch while preserving coherence and role boundaries.

---

### 7. TU can remain disciplined under revision
In Cycle 3, TU did not narrate or speculate.
It simply:
- added the new motion-tokens
- extended the train
- strengthened the source hypothesis
- updated coherence

This is a good sign that TU can remain mapper-first even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
In Cycle 3, TU+ did more than simply decorate the output.

It:
- weakened the old `approach_then_pause` reading
- introduced a stronger `approach_pause_resume` reading
- raised attention salience
- logged mismatch
- issued a revised predicted train

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

## What has now been tested

The following have now been tested at least in weak form:

- returned traces
- mild mismatch
- revision of choreography interpretation
- correction pressure
- preservation of coherence under reinterpretation

---

## What has not yet been tested

The following remain untested:

- second source/object
- coupling between trains
- restart pressure
- fragmentation
- stronger mismatch
- high-salience recruitment under real ambiguity
- richer action-confirmation dynamics

So the current result is now more than a baseline success, but still not a full field stress test.

---

## Current verdict

The first three cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and refine stable choreography across cycles, and absorb mild mismatch without losing coherence or collapsing role boundaries.

This does not yet prove the full architecture, but it does justify moving to the next pressure test.

---

## Recommended next test

The next best test is to introduce one new structural pressure:

- a second source/object with weak coupling

This will let the triad be tested on:
- multi-source persistence
- coupling detection
- cross-train coherence
- ambiguity between independent and linked choreographies

That is now the next meaningful step.
