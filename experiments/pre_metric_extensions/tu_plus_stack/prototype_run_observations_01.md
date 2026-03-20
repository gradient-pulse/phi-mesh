# Prototype Run Observations 01

## Provisional statement

So far, the dry runs suggest that a prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, and absorb mild ambiguity without collapsing into one generic assistant voice.

This statement is provisional and should be updated as new cycles are added.

---

## Scope

This note records observations from bounded dry-run cycles of the prompt-instantiated TU / TU+ / cortexLLM triad.

Its purpose is to preserve findings incrementally while the prototype is exposed to stronger pressures such as:
- stable coupling confirmation
- restart pressure
- fragmentation
- stronger mismatch
- richer action-confirmation dynamics
- competition between multiple possible couplings

---

## Important test discipline used

During the dry runs, only the output of the immediately prior role was passed forward:

- TU output was passed to TU+
- TU+ output was passed to cortexLLM

This made the test stricter than a full-state pass-through, because each role had to operate from bounded upstream structure rather than from the full accumulated state.

This strengthens the finding that role separation is viable.

---

## Cycle-by-cycle findings

### Cycle 1 — Baseline role separation

**What was tested**

- one provisional source
- one train
- no coupling
- no returned traces
- no mismatch

**What happened**

- TU mapped one source and one train without narrating
- TU+ matched and predicted without becoming symbolic cortex
- cortexLLM framed the scene symbolically and sent compact downward bias

**Finding**

Cycle 1 established the baseline:
the triad can complete one full bounded loop without collapsing role boundaries.

---

### Cycle 2 — Stable persistence across cycles

**What was tested**

- persistence across cycles
- stabilization of the same source/train
- continued role separation
- slight refinement of choreography match and hold-state interpretation

**What happened**

- TU preserved and lightly stabilized the active train
- TU+ slightly strengthened the choreography match
- cortexLLM moved toward a calm observe-and-hold framing

**Finding**

Cycle 2 showed that the architecture can preserve a calm, coherent field across cycles without inventing unnecessary novelty or collapse.

---

### Cycle 3 — Mild mismatch and revision

**What was tested**

- prior hold-dominant expectation
- brief confirmation of hold
- slight resumed rightward motion
- mismatch logging
- revision of active choreography interpretation

**What happened**

- TU extended the train rather than fragmenting it
- TU+ revised the choreography match from a hold-dominant reading toward a pause-to-resume reading
- cortexLLM updated the symbolic framing without overreacting

**Finding**

Cycle 3 showed that the triad can absorb mild mismatch, revise the active choreography interpretation, and preserve coherence without losing role separation.

---

### Cycle 4 — Second source and weak coupling ambiguity

**What was tested**

- emergence of a second provisional source
- weak cross-train relation
- coupling detection without overcommitment
- symbolic handling of relational ambiguity

**What happened**

- TU introduced source B while preserving A as the dominant coherent train
- TU registered weak coupling without prematurely merging the two sources
- TU+ introduced a weak relational choreography match without overcommitting to stable joint choreography
- cortexLLM framed the field as relationally ambiguous and kept the system in hold/observe mode

**Finding**

Cycle 4 showed that the triad can introduce a second provisional source and track weak cross-train coupling without prematurely collapsing the field into a confirmed joint choreography.

---

### Cycle 5 — Dissolution of weak coupling

**What was tested**

- persistence of two sources
- weakening of prior weak coupling
- possible dissolution of relational interpretation
- rejection of a weak joint-choreography hypothesis

**What happened**

- TU preserved both sources while allowing A to continue independently and B to stall
- TU reduced effective coupling without deleting B or forcing a merger
- TU+ downgraded `weak_mutual_approach`, promoted `passing_then_separation`, and logged that the earlier weak coupling failed to stabilize
- cortexLLM reframed the field as passing-and-separation rather than emerging joint choreography

**Finding**

Cycle 5 showed that the triad can dissolve a weak coupling hypothesis when coherence fails to stabilize it, and can return to an independent-source reading without losing continuity or role separation.

---

## Cross-cycle findings so far

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
- stabilization of active trains
- strengthening of source confidence
- preservation and revision of predictive matches
- symbolic context that did not overwrite lower-level structure

---

### 3. Stable persistence can be carried across cycles
The architecture can preserve a calm, coherent field without inventing unnecessary novelty or collapse.

This suggests the triad can:
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
- revising best-fit choreography without drifting into broad narration

This supports the idea that prompt-instantiated specialization is feasible.

---

### 5. cortexLLM can bias without micromanaging
cortexLLM framed scenes symbolically and sent compact downward bias without rewriting motion structure.

This suggests the stack can support top-down influence without collapsing into symbolic domination of all layers.

---

### 6. Mild mismatch can be absorbed without coherence collapse
The architecture can revise interpretation under mild mismatch while preserving coherence and role boundaries.

This is one of the first genuinely important non-baseline results.

---

### 7. TU can remain disciplined under revision
Under changed evidence, TU did not narrate or speculate.
It remained mapper-first by:
- adding motion-tokens
- extending trains
- strengthening source hypotheses
- updating coherence
- weakening relations when the unfolding no longer supported them

This is a good sign that TU can remain structurally disciplined even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
By Cycles 3–5, TU+ did more than decorate output.

It:
- revised choreography readings
- raised salience when warranted
- logged mismatch
- introduced new relational partial matches
- dissolved weak relational matches when coherence failed to support them
- issued revised predicted trains

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

### 9. Weak coupling can be represented without premature collapse
Cycles 4–5 suggest the architecture can distinguish between:
- a new provisional source
- a weak coupling candidate
- a stable joint choreography
- and a dissolved relational hypothesis

That distinction matters and appears to be maintainable so far.

---

### 10. Coherence is beginning to act as the selection principle
By Cycle 5, revision appears to be driven less by static labeling and more by which choreography interpretation best preserves coherence across unfolding time.

What survived was not what was initially plausible, but what remained coherent enough.

This suggests that coherence is not merely a measured field property in the schema.
It is beginning to function as the effective driver of revision and selection.

That is highly relevant to the RGPx framing of the prototype.

---

## What has now been tested

The following have now been tested at least in weak form:

- role separation across full cycles
- shared-state persistence
- stable train continuation
- returned traces
- mild mismatch
- revision of choreography interpretation
- correction pressure
- preservation of coherence under reinterpretation
- second-source emergence
- weak coupling detection
- relational ambiguity management
- dissolution of provisional coupling
- false positive avoidance for weak joint-choreography readings

---

## What has not yet been tested

The following remain untested:

- stable coupling confirmation
- restart pressure
- fragmentation
- stronger mismatch
- high-salience recruitment under real ambiguity
- richer action-confirmation dynamics
- competition between multiple possible couplings

So the current result is more than a baseline success, but still not a full field stress test.

---

## Current verdict

The first five cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, absorb mild mismatch, represent weak multi-source coupling, and dissolve unsupported relational hypotheses without collapsing role boundaries.

This does not yet prove the full architecture, but it does justify moving to the next pressure test.

---

## Recommended next test

The next best test is to introduce one new structural pressure:

- stable coupling confirmation under stronger reciprocal evidence

This will let the triad be tested on:
- whether a relational hypothesis can grow rather than dissolve
- whether stable joint choreography can be distinguished from coincidence
- whether coherence can drive not only rejection but also confirmation
