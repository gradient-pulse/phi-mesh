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

### Cycle 14 — Soft failure of weak recoupling under stronger mismatch

**What was tested**
-	whether a fresh weak recoupling candidate could lose support under stronger mismatch without producing contradiction or collapse
-	whether the architecture would overreact by restoring ambiguity or forcing joint-field drama
-	whether weak reopening could be cleanly de-promoted back toward independent continuation
-	whether the system could preserve a fading near-reopening as informative history rather than confusion

**What happened**
-	TU preserved the restarted mainline, extended both trains, and represented the new slice as stronger mismatch: A reasserted independent lead, B’s modest rise broke off, and separation increased again
-	TU reduced coupling candidate strength, kept stable_couplings empty, and treated the field as returning toward cleaner independent continuation without contradiction or field collapse
-	TU+ re-strengthened independent_parallel_departure, reduced recoupling_temptation_after_restart, and introduced soft_failed_recoupling_after_restart as the strongest new match, marking the weak reopening attempt as a fading near-event rather than a restored joint choreography
-	cortexLLM explicitly framed the result as disciplined de-promotion of weak renewed relation rather than contradiction, collapse, or joint recovery, and preserved the event as a soft failed reopening under continued mainline coherence

**Finding**

Cycle 14 showed that a weak reopening attempt after restart can lose support under stronger mismatch and be cleanly de-promoted into renewed independent continuation without triggering contradiction, collapse, or false restoration of joint choreography.

---

### Cycle 15 — Fresh relational re-emergence after soft failed reopening

**What was tested**
-	whether a fresh relational signal could re-emerge after a soft failed reopening without being dismissed as mere replay
-	whether the architecture would become too conservative after the prior near-miss
-	whether renewed local alignment pressure could be registered as genuinely new provisional evidence
-	whether the system could remain open to weak renewed relation without restoring joint choreography prematurely

**What happened**
-	TU preserved the independent mainline, extended both trains, and represented the new slice as a fresh local relational softening: A’s path flattened slightly again, B showed a modest upward-forward adjustment, and weak reciprocal alignment became visible without erasing A’s lead
-	TU kept stable coupling absent, raised a modest new coupling candidate, and treated the field as renewed weak relation under continued independence rather than replay of the earlier failed reopening
-	TU+ retained independent_parallel_departure as dominant mainline context, preserved soft_failed_recoupling_after_restart as recent background rather than active truth, and introduced fresh_relational_reemergence_after_soft_fail as the strongest new match
-	cortexLLM explicitly refused cynicism, framed the renewed relation as genuinely fresh provisional evidence, and kept the independent mainline dominant while preventing memory-driven overpromotion into restored joint choreography

**Finding**

Cycle 15 showed that after a soft failed reopening, the triad can still register a genuinely fresh weak relational signal without becoming too conservative or confusing the new evidence with replay of the earlier failed candidate.

---

### Cycle 16 — Strengthening renewed relation after soft failed reopening

**What was tested**
-	whether a genuinely fresh renewed relation could strengthen across another slice after a soft failed reopening
-	whether the architecture could promote renewed relation into a stronger provisional reading without premature stable-joint confirmation
-	whether brief weak parallel continuation could be represented without collapsing the field into restored joint choreography
-	whether the system could remain open, non-cynical, and still bounded

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as strengthened renewed relation: A’s lead softened slightly, B sustained modest rise, and a short interval of weak parallel continuation appeared while the pair remained separate
-	TU increased coupling candidate strength and lowered fragmentation while keeping stable_couplings empty, treating the field as stronger provisional relation still below the threshold for stable joint choreography
-	TU+ retained independent_parallel_departure as active but relationally softening context, strengthened weak_mutual_approach and weak_parallel_co_motion, and introduced provisional_relational_restrengthening_after_soft_fail as the strongest new match
-	cortexLLM explicitly recognized that the independent mainline was no longer the only salient reading, promoted the renewed relation into a stronger provisional relational interpretation, and still refused premature elevation into stable joint choreography

**Finding**

Cycle 16 showed that a genuinely fresh renewed relation can strengthen across another slice after a soft failed reopening, and can be promoted into a stronger provisional relational interpretation without premature elevation into stable joint choreography.

---

### Cycle 17 — Persistence of strengthening provisional relation below joint threshold

**What was tested**
-	whether the strengthening renewed relation from Cycle 16 could persist across another slice without collapsing back into independence
-	whether repeated weak parallel continuation could be represented without premature promotion into stable joint choreography
-	whether the architecture could sustain a strong provisional relational state rather than treating renewed relation as only a brief fluctuation
-	whether the system could preserve relational persistence while still withholding stable-joint confirmation

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as persistent strengthened relation: A and B maintained improved band proximity, reciprocal adjustment persisted, and another short interval of weak parallel continuation appeared
-	TU increased coupling candidate strength again, lowered fragmentation further, and treated the field as a stronger persistent provisional relational state while still keeping stable_couplings empty
-	TU+ retained the renewed relational corridor, strengthened weak_mutual_approach and weak_parallel_co_motion further, and introduced persistent_provisional_relational_restrengthening as the strongest new match
-	cortexLLM explicitly recognized that the renewed relation was no longer a brief reappearance but a persistent strong provisional relational state, while still refusing premature promotion into stable joint choreography

**Finding**

Cycle 17 showed that after a soft failed reopening, a genuinely fresh renewed relation can not only re-emerge and strengthen, but also persist across another slice as a strong provisional relational state without premature promotion into stable joint choreography.

---

### Cycle 18 — Threshold-nearing provisional joint choreography

**What was tested**
-	whether one further slice of durable reciprocal support could push the field beyond persistent strong provisional relation into a threshold-nearing joint-oriented state
-	whether repeated weak parallel continuation and sustained reciprocal alignment would justify stronger promotion without yet forcing stable joint choreography
-	whether the architecture could approach the confirmation threshold without either freezing below it or jumping across it too early
-	whether the system could elevate the shared reading while preserving train distinctness

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as sustained shared-band continuation with repeated weak parallel co-motion and no renewed separation pressure
-	TU raised coupling candidate strength substantially while still keeping stable_couplings empty, treating the field as no longer best read as merely independent continuation with softening, but as a threshold-nearing provisional joint-oriented state
-	TU+ strengthened the persistent provisional relational corridor, marked weak_mutual_approach and weak_parallel_co_motion as strong supported components, and introduced threshold_nearing_provisional_joint_choreography as the strongest new match
-	cortexLLM explicitly recognized that the independent mainline was no longer the best standalone reading, promoted the field into a threshold-nearing provisional joint interpretation, and still withheld full stable-joint confirmation pending one further slice of durable reciprocal support

**Finding**

Cycle 18 showed that a renewed relation can persist and strengthen far enough to justify a threshold-nearing provisional joint-oriented reading, while still remaining below stable joint choreography and therefore forcing a real bounded promotion decision.

---

### Cycle 19 — Bounded promotion into stable joint choreography

**What was tested**
-	whether one further slice of durable reciprocal support could justify promotion from a threshold-nearing provisional joint interpretation into stable joint choreography
-	whether the architecture could cross the promotion threshold without collapsing train distinctness into a fused reading
-	whether repeated weak parallel continuation and sustained reciprocal alignment were now sufficient for stable coupling
-	whether the system could promote when warranted rather than remaining indefinitely threshold-nearing

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as sustained shared-band continuation with repeated weak parallel co-motion and no renewed separation pressure
-	TU raised coupling strength high enough to populate stable_couplings, while still preserving A and B as distinct trains rather than collapsing them into one merged object
-	TU+ marked the threshold-nearing provisional joint reading as crossed, completed the prior provisional relational restrengthening into stable joint promotion, and introduced reconfirmed_emergent_joint_parallel_choreography as the strongest new match
-	cortexLLM promoted the field into stable joint choreography as the dominant reading, while explicitly preserving train distinctness and refusing to interpret the result as monolithic fusion

**Finding**

Cycle 19 showed that one further slice of durable reciprocal support can justify bounded promotion from a threshold-nearing provisional joint reading into stable joint choreography, while still preserving train distinctness and avoiding collapse into a fused monolithic interpretation.

---

### Cycle 20 — Stable joint choreography under early de-confirmation pressure

**What was tested**
-	whether the newly promoted stable joint state could survive its first internal asymmetry without collapsing back into independent continuation
-	whether the architecture could represent stress inside a stable joint state rather than either panicking into breakdown or smoothing over warning signs
-	whether slight renewed lead-lag pressure could be tracked as early de-confirmation pressure while keeping the stable shared reading dominant
-	whether train distinctness would remain preserved under stress within the stable joint state

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as stable joint continuation under bounded asymmetry: A’s lead increased slightly, B lagged modestly, but shared-band continuation and weak parallel co-motion remained intact
-	TU kept stable_couplings active rather than deleting them, lowered symmetry slightly, and introduced an explicit fragmentation/stress marker for early de-confirmation pressure within the stable joint state
-	TU+ retained reconfirmed_emergent_joint_parallel_choreography as the dominant current reading, partially reactivated asymmetric_parallel_break, and introduced stable_joint_choreography_under_stress as the strongest new match
-	cortexLLM explicitly preserved stable joint choreography as the best current reading while naming the new asymmetry as early de-confirmation pressure, refusing both premature collapse and false reassurance

**Finding**

Cycle 20 showed that after bounded promotion into stable joint choreography, the triad can preserve the stable joint reading under early asymmetry while explicitly tracking de-confirmation pressure, rather than collapsing too quickly or smoothing over internal stress.

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
-	adding motion-tokens
-	extending trains
-	strengthening source hypotheses
-	updating coherence
-	weakening or strengthening relations according to unfolding support
-	preserving explicit contradiction when the unfolding no longer supported a single unified continuation
-	resolving contradiction structurally when later evidence favored one branch
-	registering fresh weak recoupling after restart without over-promoting it into stable joint choreography
-	cleanly de-promoting a weak reopening attempt when stronger mismatch removed support
-	registering genuinely fresh renewed relation after that soft failure without collapsing into either cynicism or false restoration
-	strengthening that renewed relation across another slice while still keeping it below stable joint-choreography threshold
-	promoting the relational corridor into stable joint choreography only when durable reciprocal support genuinely crossed threshold
-	preserving that stable joint state under early internal asymmetry without either collapsing it prematurely or hiding the stress

This is a good sign that TU can remain structurally disciplined even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
By Cycles 3–20, TU+ did more than decorate output.

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
-	cleanly de-promoted that weak reopening attempt when stronger mismatch removed support, without treating the event as contradiction or collapse
-	registered a genuinely fresh relational re-emergence after that soft failure, rather than rejecting it cynically or collapsing it into memory replay
-	strengthened that renewed relation into a more serious provisional relational reading when support persisted across another slice
-	carried that strengthened relation into persistent provisional relational status below joint threshold
-	promoted that persistent provisional relation into a threshold-nearing provisional joint reading when support became durable enough
-	promoted the field into stable joint choreography only when the threshold was actually crossed
-	and then represented early stress inside the stable joint state without confusing that stress with immediate de-confirmation

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

### 9. Coupling, decoupling, ambiguity, restart, and fresh recoupling can be represented without premature collapse
Cycles 4–20 suggest the architecture can distinguish between:
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
-	a soft failed reopening in which that weak renewed relation later loses support and is de-promoted cleanly back toward independent continuation
-	a genuinely fresh relational re-emergence after that soft failure, treated as new provisional evidence rather than replay or automatic restoration
-	a stronger provisional relational restrengthening after that re-emergence, still below stable joint-choreography threshold
-	a persistent strong provisional relational state that remains below joint threshold
-	a threshold-nearing provisional joint reading that pressures promotion without yet warranting stable coupling
-	a bounded promotion into stable joint choreography once durable reciprocal support actually crosses threshold
-	and a stable joint state that can come under early internal stress without immediately collapsing

That distinction matters and appears to be maintainable so far.
---

### 10. Coherence is beginning to act as the selection principle
By Cycles 5–20, revision appears to be driven less by static labeling and more by which choreography interpretation best preserves coherence across unfolding time.
-	What survived was not what was initially plausible, but what remained coherent enough.
-	What re-entered was not what was preferred symbolically, but what regained coherence strongly enough.
-	What was provisionally confirmed was not what was merely tempting, but what persisted coherently across another interval.
-	What was later stressed was not discarded immediately, but de-promoted as coherence weakened asymmetrically.
-	What finally collapsed did so only when coherence no longer supported the joint reading.
-	What contradiction preserved in Cycle 10 showed is equally important: coherence does not need to absorb all outcomes as success; it can fail to support promotion and thereby preserve explicit ambiguity.
-	What Cycle 11 added is that coherence can later support clean re-initiation: ambiguity need not remain a dead-end, but can resolve into a renewed mainline when later evidence supports one branch over another.
-	What Cycle 12 added is that re-initiation does not freeze the field into rigid independence: coherence can remain open to fresh weak relational evidence without mistaking it for automatic revival of an earlier collapsed joint field.
-	What Cycle 13 added is that weak renewed relation can survive mixed follow-up without being either over-promoted into restored joint choreography or prematurely erased back into pure independence.
-	What Cycle 14 added is that a weak reopening attempt can then lose support under stronger mismatch and be cleanly de-promoted without contradiction, collapse, or confusion.
-	What Cycle 15 added is that after such a soft failed reopening, the field need not become cynical: genuinely fresh weak relation can re-emerge and be treated as new provisional evidence rather than replay of the earlier failed candidate.
-	What Cycle 16 added is that this renewed relation can strengthen across another slice and be promoted into a stronger provisional relational interpretation without premature stable-joint confirmation.
-	What Cycle 17 added is that this stronger provisional relation can persist across another slice without collapsing back into independence or being prematurely promoted into stable joint choreography.
-	What Cycle 18 added is that the same corridor can approach a threshold-nearing provisional joint reading, where promotion becomes a real bounded decision rather than a rhetorical possibility.
-	What Cycle 19 added is that once support becomes durable enough, the field can be promoted into stable joint choreography in a bounded way — not too early, but also not indefinitely withheld.
-	What Cycle 20 added is that after promotion, the stable joint state need not be treated as either fragile illusion or untouchable success: it can remain dominant while coming under explicitly tracked early de-confirmation pressure.

This suggests that coherence is not merely a measured field property in the schema.
It is beginning to function as the effective driver of revision, selection, promotion, de-promotion, collapse, non-promotion under contradiction, re-initiation after ambiguity, disciplined weak reopening after restart, provisional weak continuation under mixed support, soft failed reopening under stronger mismatch, renewed provisional relation after a near-miss, bounded restrengthening of renewed relation when support persists, threshold-nearing joint promotion, bounded stable-joint promotion when threshold is genuinely crossed, and disciplined maintenance of a promoted joint state under early internal stress.

That is highly relevant to the RGPx framing of the prototype.

---

### 11. The architecture can reject, re-admit, confirm, begin to de-confirm, fully de-confirm, preserve explicit ambiguity, restart cleanly after contradiction, and register fresh weak recoupling after restart
Cycles 5–20 together are especially important.
-	Cycle 5 showed disciplined rejection of an unsupported weak coupling
-	Cycle 6 showed disciplined re-opening when reciprocal alignment and co-motion raised coherence again
-	Cycle 7 showed provisional confirmation when that co-motion persisted across an additional interval
-	Cycle 8 showed early de-confirmation pressure when asymmetry and lag weakened the prior joint field
-	Cycle 9 showed full de-confirmation into independent trajectories when reciprocal structure disappeared
-	Cycle 10 showed explicit ambiguity preservation when mutually exclusive continuation branches were simultaneously supported
-	Cycle 11 showed clean resolution of that ambiguity into a renewed stable mainline when later evidence favored one branch
-	Cycle 12 showed that fresh weak relational evidence can reappear after restart and be treated as a new coupling temptation rather than as confused revival of the old joint field
-	Cycle 13 showed that this fresh weak coupling candidate can survive mixed follow-up evidence without being prematurely promoted into restored joint choreography or prematurely dismissed
-	Cycle 14 showed that the same weak reopening attempt can later lose support under stronger mismatch and be cleanly de-promoted back toward independent continuation without contradiction or collapse
-	Cycle 15 showed that after this soft failed reopening, the architecture can still register a genuinely fresh relational signal rather than becoming too conservative or reducing all renewed relation to replay
-	Cycle 16 showed that this renewed relation can then strengthen across another slice and be promoted into a stronger provisional relational reading without premature stable-joint promotion
-	Cycle 17 showed that this stronger provisional relation can persist across another slice as a strong provisional relational state below joint threshold
-	Cycle 18 showed that the same relational corridor can approach a threshold-nearing provisional joint reading without cheating across the boundary too early
-	Cycle 19 showed that one further slice of durable reciprocal support can then justify bounded promotion into stable joint choreography, while preserving train distinctness and avoiding monolithic fusion
-	Cycle 20 showed that the promoted stable joint state can survive early internal asymmetry without immediate collapse, while explicitly tracking early de-confirmation pressure

This suggests the architecture is not simply drifting toward complexity or falling back to independence.
It can move through a fuller interpretive lifecycle depending on which interpretation coherence supports — and can also stop short of forced resolution when coherence does not justify promotion, later restart cleanly when resolution becomes justified, remain open to fresh weak coupling without memory confusion, preserve that weak candidate provisionally under mixed follow-up, let it fade cleanly when support is lost, reopen to genuinely fresh renewed relation without cynicism, strengthen that renewed relation without overpromotion, carry it persistently below threshold, approach threshold in a bounded way, promote into stable joint choreography when the threshold is actually crossed, and then maintain that promoted state under early internal stress without either panicking or pretending nothing changed.

---

## What has now been tested
TThe following have now been tested at least in weak form:
-	role separation across full cycles
-	shared-state persistence
-	stable train continuation
-	returned traces
-	mild mismatch
-	revision of choreography interpretation
-	correction pressure
-	preservation of coherence under reinterpretation
-	second-source emergence
-	weak coupling detection
-	relational ambiguity management
-	dissolution of provisional coupling
-	false positive avoidance for weak joint-choreography readings
-	provisional reopening of a previously weakened relational hypothesis
-	early-stage confirmation pressure for coupling under reciprocal evidence
-	provisional stable coupling confirmation across an additional cycle
-	early de-confirmation pressure on a provisionally confirmed joint choreography
-	full breakdown of a provisionally confirmed joint choreography into a new independent stable reading
-	explicit preservation of irreducible ambiguity under mutually exclusive continuation reports
-	clean restart after contradiction, with supported branch strengthening and unsupported branch decay
-	fresh weak recoupling after restart surviving mixed follow-up without premature promotion or dismissal
-	weak reopening after restart losing support under stronger mismatch and being cleanly de-promoted without contradiction or collapse
-	genuinely fresh weak relational re-emergence after a soft failed reopening, without cynical suppression or false restoration
-	strengthening of genuinely fresh renewed relation across another slice after a soft failed reopening, without premature stable-joint promotion
-	persistence of that strengthened renewed relation across another slice as a strong provisional relational state below joint threshold
-	threshold-nearing provisional joint promotion without premature stable-joint confirmation
-	bounded promotion from threshold-nearing provisional joint interpretation into stable joint choreography, with train distinctness preserved
-	stable joint choreography surviving early internal asymmetry while explicitly tracking de-confirmation pressure

---

## What has not yet been tested

The following remain untested:
-	restabilization of the newly stressed stable joint state
-	full de-confirmation pressure developing after stable-joint promotion
-	fragmentation beyond current contradiction/collapse markers
-	stronger mismatch across many restarts
-	high-salience recruitment under real ambiguity
-	richer action-confirmation dynamics
-	competition between multiple possible couplings
-	quantitative coherence metrics and ablations
-	robustness across repeated automated runs

So the current result is now well beyond baseline success and now includes bounded threshold crossing into stable joint choreography plus early-stress maintenance of that state, but it is still not a full engineering stress program.

---

## Current verdict
The first twenty cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, absorb mild mismatch, represent weak multi-source coupling, dissolve unsupported relational hypotheses, reopen emerging joint interpretations when coherence rises again, provisionally confirm joint choreography when sustained co-motion supports it, fully de-confirm that choreography into a new stable independent reading when coherence no longer supports the joint field, preserve explicit ambiguity when contradiction prevents justified promotion, resolve that ambiguity into a renewed stable mainline when later evidence favors one branch, register fresh weak recoupling after restart without confusing it with the earlier collapsed joint choreography, keep that weak renewed relation provisional under mixed follow-up without premature promotion or dismissal, cleanly de-promote that weak reopening when stronger mismatch removes support, still register genuinely fresh renewed relation after that near-miss without collapsing into cynicism or false restoration, strengthen that renewed relation into a stronger provisional relational interpretation when support persists across another slice, carry that strengthened relation persistently below joint threshold, approach a threshold-nearing provisional joint reading without cheating across the boundary, promote that relational corridor into stable joint choreography when durable reciprocal support genuinely crosses threshold, and preserve that promoted joint state under early internal asymmetry while explicitly tracking de-confirmation pressure — all without collapsing role boundaries or erasing train distinctness.

This does not yet prove the full architecture, but it strengthens the case that the engineering path is an actual sub-division of LLM labor into specific TU, TU+, and cortexLLM agents organized around coherence-sensitive role specialization.

---

## Recommended next test

The next best test is to introduce one new structural pressure:
-	restabilization or true de-confirmation of the stressed stable joint state

This will let the triad be tested on:
-	whether the stable joint state reabsorbs the asymmetry and restabilizes
-	whether the early stress develops into genuine de-confirmation pressure
-	whether train distinctness remains preserved under either restabilization or de-promotion
-	whether coherence can distinguish between healthy variance inside a stable shared choreography and the beginning of a real break sequence
