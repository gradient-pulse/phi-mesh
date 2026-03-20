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

### Cycle 6 — Reopening and provisional strengthening of coupling

**What was tested**

- renewed reciprocal reduction of separation
- re-emergence of relational interpretation after prior dissolution
- brief parallel co-motion
- possible early-stage confirmation of joint choreography

**What happened**

- TU preserved A as dominant, strengthened B, and mapped renewed reconvergence plus brief parallel continuation
- TU raised coupling strength substantially without yet declaring stable joint choreography
- TU+ demoted `passing_then_separation`, recovered `weak_mutual_approach`, introduced `weak_parallel_co_motion`, and logged mismatch against the earlier independent-source expectation
- cortexLLM reopened the relational reading, promoted emerging joint interpretation, but kept it explicitly provisional

**Finding**

Cycle 6 showed that the triad can reopen a previously weakened relational hypothesis when coherence rises again, and can promote an emerging joint choreography without prematurely treating it as fully stable.

---

### Cycle 7 — Provisional confirmation of joint choreography

**What was tested**

- sustained reciprocal evidence across another cycle
- continued parallel co-motion
- absence of renewed separation
- possible promotion from provisional coupling to provisional stable joint choreography

**What happened**

- TU preserved both sources, extended both trains symmetrically, and upgraded the coupling into stable_couplings while keeping fragmentation low
- TU+ stabilized `weak_parallel_co_motion`, introduced `emergent_joint_parallel_choreography` as a strong new match, and faded out earlier non-dominant alternatives
- cortexLLM promoted the joint-parallel reading to the dominant interpretation while keeping it explicitly revisable rather than final

**Finding**

Cycle 7 showed that sustained aligned co-motion can raise a weak relational hypothesis into a provisionally confirmed joint choreography without forcing premature finality.

---

### Cycle 8 — Early de-confirmation pressure on joint choreography

**What was tested**

- asymmetry within the provisionally confirmed joint field
- lead-lag divergence
- weakening of alignment without full collapse
- pressure on whether joint confirmation should be reduced or maintained

**What happened**

- TU preserved both sources as individually coherent but weakened coupling, lowered joint stability, and introduced fragmentation flags marking early break pressure
- TU+ weakened `emergent_joint_parallel_choreography`, introduced `asymmetric_parallel_break` as the strongest current match, and logged mismatch against the earlier joint-continuation expectation
- cortexLLM reframed the field as a stressed joint choreography under de-confirmation pressure, but did not prematurely collapse it into fully independent trajectories

**Finding**

Cycle 8 showed that a provisionally confirmed joint choreography can come under early de-confirmation pressure without forcing premature collapse into independent-source interpretation.

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
- weakening or strengthening relations according to unfolding support

This is a good sign that TU can remain structurally disciplined even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
By Cycles 3–8, TU+ did more than decorate output.

It:
- revised choreography readings
- raised salience when warranted
- logged mismatch
- introduced new relational partial matches
- dissolved weak relational matches when coherence failed to support them
- reopened and strengthened relational matches when coherence rose again
- provisionally confirmed a joint choreography when sustained co-motion supported it
- weakened that same joint choreography when asymmetric break pressure emerged
- issued revised predicted trains

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

### 9. Weak coupling and joint choreography can be represented without premature collapse
Cycles 4–8 suggest the architecture can distinguish between:
- a new provisional source
- a weak coupling candidate
- a stable joint choreography
- a dissolved relational hypothesis
- a reopened but still provisional joint interpretation
- a provisionally confirmed joint choreography
- a stressed joint choreography under de-confirmation pressure

That distinction matters and appears to be maintainable so far.

---

### 10. Coherence is beginning to act as the selection principle
By Cycles 5–8, revision appears to be driven less by static labeling and more by which choreography interpretation best preserves coherence across unfolding time.

What survived was not what was initially plausible, but what remained coherent enough.
What re-entered was not what was preferred symbolically, but what regained coherence strongly enough.
What was provisionally confirmed was not what was merely tempting, but what persisted coherently across another interval.
What was later stressed was not discarded immediately, but de-promoted as coherence weakened asymmetrically.

This suggests that coherence is not merely a measured field property in the schema.
It is beginning to function as the effective driver of revision, selection, promotion, and de-promotion.

That is highly relevant to the RGPx framing of the prototype.

---

### 11. The architecture can reject, re-admit, confirm, and begin to de-confirm relational hypotheses
Cycles 5–8 together are especially important.

- Cycle 5 showed disciplined rejection of an unsupported weak coupling
- Cycle 6 showed disciplined re-opening when reciprocal alignment and co-motion raised coherence again
- Cycle 7 showed provisional confirmation when that co-motion persisted across an additional interval
- Cycle 8 showed early de-confirmation pressure when asymmetry and lag weakened the prior joint field

This suggests the architecture is not simply drifting toward complexity or falling back to independence.
It can move in multiple directions depending on which interpretation coherence supports.

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
- provisional reopening of a previously weakened relational hypothesis
- early-stage confirmation pressure for coupling under reciprocal evidence
- provisional stable coupling confirmation across an additional cycle
- early de-confirmation pressure on a provisionally confirmed joint choreography

---

## What has not yet been tested

The following remain untested:

- full breakdown of a provisionally confirmed joint choreography
- restart pressure
- fragmentation beyond early flags
- stronger mismatch
- high-salience recruitment under real ambiguity
- richer action-confirmation dynamics
- competition between multiple possible couplings

So the current result is more than a baseline success, but still not a full field stress test.

---

## Current verdict

The first eight cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, absorb mild mismatch, represent weak multi-source coupling, dissolve unsupported relational hypotheses, reopen emerging joint interpretations when coherence rises again, provisionally confirm joint choreography when sustained co-motion supports it, and begin to de-confirm that choreography when coherence weakens asymmetrically — all without collapsing role boundaries.

This does not yet prove the full architecture, but it now supports the stronger hunch that a true world model may require an RGPx-driven division of LLM labor organized around coherence-sensitive role specialization.

---

## Recommended next test

The next best test is to introduce one new structural pressure:

- full break pressure on the stressed joint choreography

This will let the triad be tested on:
- whether provisional confirmation can be fully revised without collapse of the overall field
- whether durable confirmation can be distinguished from short-lived stabilization
- whether coherence can drive not only rejection, reopening, confirmation, and early de-confirmation, but disciplined collapse into a new stable reading
