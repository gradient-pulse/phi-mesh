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

### Cycle 9 — Full de-confirmation into independent trajectories

**What was tested**

- decisive continuation of asymmetry
- loss of shared band and reciprocal adjustment
- collapse of the stressed joint field
- stabilization of a new independent-source reading

**What happened**

- TU preserved both sources as individually coherent trains, removed stable coupling, and represented the prior joint field as collapsed into two independent trajectories with only weak residual coupling
- TU+ marked `asymmetric_parallel_break` as completed, collapsed `emergent_joint_parallel_choreography`, restored strong separation-oriented readings, and issued separate future predictions for A and B
- cortexLLM accepted that the joint field was no longer dominant, reframed the scene as two independent coherent trajectories, and retained the old joint pattern only as memory rather than current truth

**Finding**

Cycle 9 showed that a provisionally confirmed joint choreography can fully de-confirm into two independent coherent trajectories without collapse of the field or loss of role separation.

---

### Cycle 10 — Explicit ambiguity preservation under contradiction

**What was tested**

- mutually exclusive continuation reports at the same slice
- contradiction between reconvergence and continued independent separation
- pressure on whether the architecture would falsely reconcile incompatible branches
- demand for explicit ambiguity handling rather than coherence smoothing

**What happened**

- TU preserved the stable prior field up to frame 18, then introduced alpha and beta continuation branches as explicit contradictory branches rather than forcing one merged update
- TU registered source-level mutual exclusion, cross-report incompatibility, lowered motion-observation agreement, and raised fragmentation without corrupting the prior trains
- TU+ retained the prior independent baseline as plausible, allowed the reconvergence branch and independent branch to coexist as contested continuations, and promoted `irreducible_branch_conflict` as the strongest current match
- cortexLLM explicitly refused narrative reconciliation, escalated contradiction, and preserved both branches as unresolved ambiguity requiring future evidence or source arbitration

**Finding**

Cycle 10 showed that the triad can preserve mutually exclusive continuation branches as explicit ambiguity, escalate contradiction without false reconciliation, and prevent symbolic interpretation from smoothing away unresolved structural conflict.

---

### Cycle 11 — Resolution of ambiguity into a renewed stable mainline

**What was tested**

- restart pressure after contradiction
- whether a preserved ambiguity could later resolve cleanly
- whether one branch could strengthen while the other decayed
- whether contradiction history could be retained without corrupting current interpretation

**What happened**

- TU reactivated the independent mainline, extended the supported beta branch with new evidence, and marked the unsupported alpha reconvergence branch as decaying rather than deleting it
- TU restored motion-observation agreement, lowered fragmentation, and represented the field as resolved in favor of independent continuation without erasing the conflict history
- TU+ strengthened `independent_parallel_departure`, demoted `irreducible_branch_conflict` from dominant to resolving, promoted `restart_after_ambiguity` as the strongest new reading, and treated the failed reconvergence branch as decaying rather than still contested
- cortexLLM reframed the field as a clean restart of the independent mainline, preserved the failed reconvergence branch only as historical conflict memory, and shifted attention from ambiguity preservation to restart stabilization

**Finding**

Cycle 11 showed that the triad can resolve previously preserved ambiguity into a renewed stable mainline, strengthen the supported branch, let the unsupported branch decay without corruption, and restore coherent continuation without erasing contradiction history.

---

### Cycle 12 — Fresh weak recoupling temptation after restart

**What was tested**

- whether a cleanly restarted independent mainline could remain open to fresh weak relational evidence
- whether renewed proximity would be treated as a new weak coupling candidate rather than automatic revival of the old joint field
- whether memory of prior joint choreography would overdetermine current interpretation
- whether the system could hold the mainline while registering a weak new relational temptation

**What happened**

- TU preserved the resolved independent mainline, extended both trains, and registered reduced separation plus renewed horizontal alignment as a fresh weak coupling candidate without restoring stable joint choreography
- TU raised coupling candidate strength modestly while keeping stable_couplings empty, preserved low fragmentation, and treated the current field as independent continuation with minor relational softening
- TU+ retained `restart_after_ambiguity` and `independent_parallel_departure` as dominant context, partially reactivated `weak_mutual_approach` and `weak_parallel_co_motion`, and introduced `recoupling_temptation_after_restart` as the strongest new match
- cortexLLM explicitly framed the renewed relation as a fresh weak recoupling temptation after restart, not as restoration of the earlier collapsed joint choreography, and kept the independent mainline as the best current reading while monitoring the new weak coupling candidate

**Finding**

Cycle 12 showed that after a clean restart into independent continuation, the triad can register fresh weak relational evidence as a new coupling temptation without confusing it with the earlier collapsed joint choreography, thereby preserving both memory discipline and openness to renewed coordination.

---

### Cycle 13 — Mixed follow-up under weak recoupling after restart

**What was tested**
-	whether a fresh weak recoupling candidate could survive mixed follow-up evidence after restart
-	whether momentary nearer-band alignment would be over-read as renewed joint choreography
-	whether continued independent motion would prematurely erase the weak relational candidate
-	whether the architecture could keep renewed relation provisional under mixed support

**What happened**
-	TU preserved the restarted independent mainline, extended both trains, and represented the new slice as mixed: momentary nearer-band alignment and modest rise supported weak renewed relation, but retained lead and weakening rise prevented joint confirmation
-	TU raised coupling candidate strength modestly, kept stable_couplings empty, and marked the field as provisional weak recoupling under continued independence rather than restored joint choreography
-	TU+ kept recoupling_temptation_after_restart active, preserved independent_parallel_departure as dominant baseline, and treated the mixed follow-up as enough to keep the weak candidate alive but not enough to justify promotion into stable joint choreography
-	cortexLLM explicitly framed the field as provisional weak recoupling under continued independence, refused both false reopening and premature dismissal, and held the weak relational candidate open for the next slice

**Finding**

Cycle 13 showed that a fresh weak recoupling candidate can survive mixed follow-up evidence after restart without being prematurely promoted into stable joint choreography or prematurely dismissed back into pure independence.

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
- preserving explicit contradiction when the unfolding no longer supported a single unified continuation
- resolving contradiction structurally when later evidence favored one branch
- registering fresh weak recoupling after restart without over-promoting it into stable joint choreography

This is a good sign that TU can remain structurally disciplined even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
By Cycles 3–13, TU+ did more than decorate output.

It:
-	revised choreography readings
-	raised salience when warranted
-	logged mismatch
-	introduced new relational partial matches
-	dissolved weak relational matches when coherence failed to support them
-	reopened and strengthened relational matches when coherence rose again
-	provisionally confirmed a joint choreography when sustained co-motion supported it
-	weakened that same joint choreography when asymmetric break pressure emerged
-	fully de-confirmed it when coherence fell below relational viability
-	preserved contested branches under contradiction instead of forcing false promotion
-	resolved preserved ambiguity into a renewed mainline when later evidence supported one branch
-	registered fresh weak recoupling temptation after restart without confusing it with restoration of the old joint field
-	kept that weak recoupling candidate alive under mixed follow-up without prematurely promoting or dismissing it
-	issued revised predicted trains

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

### 9. Coupling, decoupling, ambiguity, restart, and fresh recoupling can be represented without premature collapse
Cycles 4–13 suggest the architecture can distinguish between:
-	a new provisional source
-	a weak coupling candidate
-	a stable joint choreography
-	a dissolved relational hypothesis
-	a reopened but still provisional joint interpretation
-	a provisionally confirmed joint choreography
-	a stressed joint choreography under de-confirmation pressure
-	a fully decoupled field of independent trajectories
-	an explicitly contradictory field with no dominant choreography
-	a resolved restart in which one branch becomes mainline and the other decays
-	a fresh weak recoupling temptation arising after restart
-	a mixed follow-up in which weak renewed relation remains provisional without stable coupling promotion

That distinction matters and appears to be maintainable so far.

---

### 10. Coherence is beginning to act as the selection principle
By Cycles 5–13, revision appears to be driven less by static labeling and more by which choreography interpretation best preserves coherence across unfolding time.

- What survived was not what was initially plausible, but what remained coherent enough.
- What re-entered was not what was preferred symbolically, but what regained coherence strongly enough.
- What was provisionally confirmed was not what was merely tempting, but what persisted coherently across another interval.
- What was later stressed was not discarded immediately, but de-promoted as coherence weakened asymmetrically.
- What finally collapsed did so only when coherence no longer supported the joint reading.
- What contradiction preserved in Cycle 10 showed is equally important: coherence does not need to absorb all outcomes as success; it can fail to support promotion and thereby preserve explicit ambiguity.
- What Cycle 11 added is that coherence can later support clean re-initiation: ambiguity need not remain a dead-end, but can resolve into a renewed mainline when later evidence supports one branch over another.
- What Cycle 12 added is that re-initiation does not freeze the field into rigid independence: coherence can remain open to fresh weak relational evidence without mistaking it for automatic revival of an earlier collapsed joint field.
- What Cycle 13 added is that weak renewed relation can survive mixed follow-up without being either over-promoted into restored joint choreography or prematurely erased back into pure independence.

This suggests that **coherence** is not merely a measured field property in the schema.
It is beginning to function as the effective driver of revision, selection, promotion, de-promotion, collapse, non-promotion under contradiction, re-initiation after ambiguity, disciplined weak reopening after restart, and provisional weak continuation under mixed support.

That is highly relevant to the RGPx framing of the prototype.

---

### 11. The architecture can reject, re-admit, confirm, begin to de-confirm, fully de-confirm, preserve explicit ambiguity, restart cleanly after contradiction, and register fresh weak recoupling after restart
Cycles 5–13 together are especially important.
-	Cycle 5 showed disciplined rejection of an unsupported weak coupling
-	Cycle 6 showed disciplined re-opening when reciprocal alignment and co-motion raised coherence again
-	Cycle 7 showed provisional confirmation when that co-motion persisted across an additional interval
-	Cycle 8 showed early de-confirmation pressure when asymmetry and lag weakened the prior joint field
-	Cycle 9 showed full de-confirmation into independent trajectories when reciprocal structure disappeared
-	Cycle 10 showed explicit ambiguity preservation when mutually exclusive continuation branches were simultaneously supported
-	Cycle 11 showed clean resolution of that ambiguity into a renewed stable mainline when later evidence favored one branch
-	Cycle 12 showed that fresh weak relational evidence can reappear after restart and be treated as a new coupling temptation rather than as confused revival of the old joint field
-	Cycle 13 showed that this fresh weak coupling candidate can survive mixed follow-up evidence without being prematurely promoted into restored joint choreography or prematurely dismissed

This suggests the architecture is not simply drifting toward complexity or falling back to independence.
It can move through a fuller interpretive lifecycle depending on which interpretation coherence supports — and can also stop short of forced resolution when coherence does not justify promotion, later restart cleanly when resolution becomes justified, remain open to fresh weak coupling without memory confusion, and preserve that weak candidate provisionally under mixed follow-up.

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
- full breakdown of a provisionally confirmed joint choreography into a new independent stable reading
- explicit preservation of irreducible ambiguity under mutually exclusive continuation reports
- clean restart after contradiction, with supported branch strengthening and unsupported branch decay
- fresh weak recoupling temptation after restart without false reopening of the earlier collapsed joint choreography
- fresh weak recoupling after restart surviving mixed follow-up without premature promotion or dismissa

---

## What has not yet been tested

The following remain untested:

- fragmentation beyond current contradiction/collapse markers
- stronger mismatch across many restarts
- high-salience recruitment under real ambiguity
- richer action-confirmation dynamics
- competition between multiple possible couplings
- quantitative coherence metrics and ablations
- robustness across repeated automated runs

So the current result is now well beyond baseline success, but still not a full engineering stress program.

---

## Current verdict

The first thirteen cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, absorb mild mismatch, represent weak multi-source coupling, dissolve unsupported relational hypotheses, reopen emerging joint interpretations when coherence rises again, provisionally confirm joint choreography when sustained co-motion supports it, fully de-confirm that choreography into a new stable independent reading when coherence no longer supports the joint field, preserve explicit ambiguity when contradiction prevents justified promotion, resolve that ambiguity into a renewed stable mainline when later evidence favors one branch, register fresh weak recoupling after restart without confusing it with the earlier collapsed joint choreography, and keep that weak renewed relation provisional under mixed follow-up without premature promotion or dismissal — all without collapsing role boundaries.

This does not yet prove the full architecture, but it strengthens the case that the engineering path is an actual sub-division of LLM labor into specific TU, TU+, and cortexLLM agents organized around coherence-sensitive role specialization.

---

## Recommended next test

The next best test is to introduce one new structural pressure:
-	stronger mismatch under weak recoupling after restart

This will let the triad be tested on:
-	whether a fresh weak coupling candidate after restart can withstand contradictory follow-up without confusion
-	whether memory of prior coupling, contradiction, and restart can remain available without dominating current interpretation
-	whether coherence can distinguish between genuine new recoupling and noisy relational churn
-	whether weak reopening remains disciplined under harsher perturbation
