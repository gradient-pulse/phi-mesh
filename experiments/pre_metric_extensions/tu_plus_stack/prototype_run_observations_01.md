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

### Cycle 21 — Restabilization of stable joint choreography after early stress

**What was tested**
-	whether the newly stressed stable joint state could reabsorb bounded asymmetry rather than progressing into de-confirmation
-	whether the architecture could represent recovery inside a stable joint state rather than only promotion or stress
-	whether train distinctness would remain preserved during restabilization
-	whether the system could avoid both false perfection and unnecessary collapse

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as stable joint continuation with reduced asymmetry: B regained some rise, the lag narrowed, and the shared relational band became more balanced again
-	TU kept stable_couplings active, reduced the prior stress marker, and treated the field as a restabilized stable joint state rather than an ongoing break sequence
-	TU+ retained the stable joint reading as dominant, treated stable_joint_choreography_under_stress as resolving rather than escalating, and introduced restabilized_stable_joint_choreography as the strongest new match
-	cortexLLM explicitly framed the field as a stable joint state that had reabsorbed mild internal stress, while preserving train distinctness and refusing to romanticize the result as frictionless permanence
**Finding**

Cycle 21 showed that after bounded promotion into stable joint choreography and the onset of early internal asymmetry, the triad could reabsorb that stress and restabilize the shared state without erasing train distinctness or forcing false perfection.

---

### Cycle 22 — Stable joint state under harsher break pressure

**What was tested**
-	whether the re-stabilized stable joint state could withstand a harsher asymmetry test without immediate collapse
-	whether the architecture could distinguish between mild internal variance and serious renewed break pressure after promotion
-	whether train distinctness would remain preserved while the shared state came under stronger strain
-	whether the system could keep the stable joint reading dominant while reopening a genuine de-confirmation corridor

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as stable joint continuation under harsher asymmetry: A pulled ahead more clearly, B lagged more noticeably, and weak parallel co-motion became strained rather than clean
-	TU kept stable_couplings active but reduced their effective strength, raised fragmentation more substantially than in Cycle 20, and marked the field as being under serious de-confirmation pressure inside the stable joint state
-	TU+ retained the stable joint reading as current, but treated the prior restabilized state as newly stressed, strengthened stable_joint_choreography_under_stress, partially reactivated asymmetric_parallel_break, and introduced stable_joint_state_under_harsher_break_pressure as the strongest new match
-	cortexLLM preserved stable joint choreography as the best current reading while explicitly recognizing that the break corridor had reopened in a serious way, refusing both premature collapse and complacent reassurance

**Finding**

Cycle 22 showed that a re-stabilized stable joint state can come under significantly stronger asymmetry and reopen a genuine break corridor, while still remaining provisionally intact as the dominant reading rather than collapsing prematurely into de-confirmation.

---

### Cycle 23 — Actual post-promotion de-confirmation into weaker relation

**What was tested**
-	whether the reopened break corridor would tip the formerly stable joint state into genuine de-confirmation rather than prolonged stressed stability
-	whether the architecture could downgrade a once-valid stable joint choreography without collapsing into total unrelatedness
-	whether train distinctness would remain preserved during de-promotion
-	whether the system could let go of a formerly dominant shared reading when coherence no longer supported it

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as loss of stable shared-band support: A pulled ahead further, B lagged enough that weak parallel co-motion no longer carried the field, and the shared state lost sufficient reciprocal support
-	TU removed stable_couplings, retained only a weaker coupling candidate, raised fragmentation materially, and marked the state as actual_post_promotion_deconfirmation
-	TU+ treated the former stressed stable joint state as having crossed into genuine de-confirmation, strongly reactivated asymmetric_parallel_break, and introduced post_promotion_relational_downgrade as the strongest new match
-	cortexLLM explicitly deconfirmed the former stable joint reading, preserved the relational history, and downgraded the field into a weaker relational / separating interpretation rather than defending the old state or collapsing into total independence

**Finding**

Cycle 23 showed that once a promoted stable joint choreography loses enough reciprocal support, the triad can cleanly deconfirm it into a weaker relational / separating reading without either clinging to the former stable state or collapsing prematurely into total independence.

---

### Cycle 24 — Stabilization of the downgraded weaker relational state

**What was tested**
-	whether the clean post-promotion de-confirmation from Cycle 23 would continue drifting into clear independent separation or settle into a weaker relational configuration
-	whether the architecture could preserve residual relation after loss of stable joint choreography
-	whether train distinctness would remain preserved in a downgraded lower-order relational state
-	whether the system could avoid both nostalgia for the former joint state and premature collapse into total separation

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as continued lead-lag asymmetry without renewed break acceleration: A remained ahead, B remained behind, and both stayed within a broader shared field
-	TU kept stable_couplings absent, retained only a weaker coupling candidate, and treated the post-promotion downgraded state as settling rather than continuing to collapse
-	TU+ retained post_promotion_relational_downgrade as the current context, treated full independent separation as only partial background pressure, and introduced stabilized_weaker_relational_mainline as the strongest new match
-	cortexLLM explicitly framed the field as a settled weaker relational mainline: no longer stable joint choreography, not yet clear independent separation, but a lower-order relational plateau with preserved train distinctness

**Finding**

Cycle 24 showed that after clean post-promotion de-confirmation, the triad can stabilize the field at a weaker relational level rather than forcing either recovery of the former joint state or immediate collapse into clear independent separation.

---

### Cycle 25 — Loosening of the weaker relational mainline

**What was tested**
-	whether the weaker relational plateau established in Cycle 24 would remain stable or begin drifting further toward clearer independent separation
-	whether residual relation could persist even while thinning further
-	whether the architecture could represent instability inside a lower-order relational state rather than forcing either renewed recovery or full break
-	whether train distinctness would remain preserved as the downgraded state loosened

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as continued lead-lag asymmetry with further thinning of the broader shared field: A remained ahead, B remained behind, and no fresh recoupling cue appeared
-	TU kept stable_couplings absent, weakened the residual coupling candidate further, and treated the lower-order relational plateau as loosening rather than fully collapsing
-	TU+ retained stabilized_weaker_relational_mainline as background context, treated independent_parallel_departure as strengthening pressure, and introduced loosening_weaker_relational_mainline as the strongest new match
-	cortexLLM explicitly framed the field as a weaker relation that still persists but is no longer as securely settled as in Cycle 24, refusing both premature recovery and premature full independence

**Finding**

Cycle 25 showed that the downgraded weaker relational state can persist beyond immediate de-confirmation, yet still begin to loosen further, indicating that the lower-order plateau is real but not yet fully stable and may continue drifting toward clearer independent separation.

---

### Cycle 26 — Clearer independent separation after weaker-relational decay

**What was tested**
-	whether the loosening weaker-relational plateau would continue thinning until clearer independent separation became the better current reading
-	whether the architecture could let go of the lower-order relational plateau without erasing residual historical linkage
-	whether train distinctness would remain preserved through this further downgrade
-	whether the system could distinguish between a weakening lower-order relation and a genuinely restored independent-separation mainline

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as continued lead-lag separation with no compensating relational recovery: A remained ahead, B remained behind, and the broader shared field contributed less to present organization than the now-dominant independent structure
-	TU kept stable_couplings absent, weakened the remaining coupling candidate further, and treated the weaker-relational plateau as having tipped into clearer independent separation rather than as still-dominant lower-order relation
-	TU+ treated loosening_weaker_relational_mainline as completed into a clearer separation outcome, re-strengthened independent_parallel_departure, and introduced clearer_independent_separation_after_weaker_relation as the strongest new match
-	cortexLLM explicitly framed the field as having crossed into clearer independent separation while preserving the graded history from stable joint choreography through weaker relation into the present state

**Finding**

Cycle 26 showed that once the weaker-relational plateau thins far enough, the triad can restore a clearer independent-separation reading without denying the graded descent that led there.

---

### Cycle 27 — Stabilization of restored independent separation

**What was tested**
-	whether the clearer independent-separation reading restored in Cycle 26 would persist as a stable mainline rather than immediately reopening into renewed relation
-	whether the architecture could distinguish between active further break and settled independent persistence
-	whether residual relational history could remain present without dominating the current reading
-	whether train distinctness would remain preserved inside a stabilized independent state

**What happened**
-	TU preserved both trains, extended both trains, and represented the new slice as continued lead-lag separation without fresh recoupling pressure and without renewed break acceleration: A remained ahead, B remained behind, and present organization was carried primarily by separate train persistence
-	TU kept stable_couplings absent, weakened the residual coupling candidate further, and treated the field as stable independent separation rather than as ongoing decay drama or fresh relational return
-	TU+ retained clearer_independent_separation_after_weaker_relation as the current context, re-strengthened independent_parallel_departure, and introduced stabilized_independent_separation_after_relational_decay as the strongest new match
-	cortexLLM explicitly framed the field as a stabilized independent mainline: the graded descent through weaker relation remained historically meaningful, but no longer organized the present state

**Finding**

Cycle 27 showed that after descent from stable joint choreography through weaker relation into clearer separation, the triad can stabilize a renewed independent mainline without erasing the graded history that led there.

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
-	restabilizing the stressed joint state when the asymmetry softened, while preserving both shared-state continuity and train distinctness
-	representing harsher renewed asymmetry as serious break pressure inside the stable joint state without prematurely deleting the shared reading
-	deconfirming the promoted shared state when reciprocal support genuinely fell below threshold, while preserving both train continuity and weaker residual relation
-	stabilizing that downgraded state at a lower relational level rather than forcing either renewed joint recovery or immediate full separation
-	representing that weaker-relational plateau as capable of loosening further without yet forcing total independent separation
-	restoring a clearer independent-separation reading once the lower-order plateau lost enough support
-	and then stabilizing that renewed independent state rather than forcing immediate recoupling or continued collapse

This is a good sign that TU can remain structurally disciplined even when the field changes.

---

### 8. TU+ begins to look functionally non-trivial
By Cycles 3–27, TU+ did more than decorate output.

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
-	represented early stress inside the stable joint state without confusing that stress with immediate de-confirmation
-	represented successful restabilization of that stable joint state once the stress softened again
-	represented a harsher reopening of the break corridor without prematurely converting that pressure into full collapse
-	represented actual post-promotion de-confirmation once the former stable state truly lost support, downgrading it into a weaker relational reading rather than erasing history
-	represented stabilization of that downgraded field as a weaker relational mainline rather than an endlessly collapsing residue
-	represented loosening inside that lower-order plateau without prematurely declaring full independent separation
-	represented the return of a clearer independent-separation reading once the lower-order relation thinned far enough
-	and then represented stabilization of that restored independent reading as a current mainline rather than a transient after-effect

This is the first point at which TU+ looks like a meaningful intermediate layer rather than a cosmetic one.

---

### 9. Coupling, decoupling, ambiguity, restart, and fresh recoupling can be represented without premature collapse

Cycles 4–27 suggest the architecture can distinguish between:
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
-	a stable joint state that can come under early internal stress without immediately collapsing
-	a stable joint state that can subsequently restabilize when that stress is reabsorbed
-	a re-stabilized stable joint state that can later reopen a serious break corridor under harsher asymmetry
-	a formerly stable joint state that can then be cleanly downgraded into a weaker relational / separating reading when reciprocal support is genuinely lost
-	a downgraded post-promotion state that can stabilize as a weaker relational mainline instead of collapsing straight into full independence
-	a weaker-relational mainline that can later loosen further without yet forcing clear independent separation
-	a weakening lower-order relation that can finally tip into a clearer independent-separation mainline without erasing residual relational history
-	and a restored independent-separation reading that can then stabilize as a renewed mainline rather than remaining a transient terminal break event

That distinction matters and appears to be maintainable so far.

---

### 10. Coherence is beginning to act as the selection principle

By Cycles 5–27, revision appears to be driven less by static labeling and more by which choreography interpretation best preserves coherence across unfolding time.
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
-	What Cycle 21 added is that this promoted shared state can reabsorb bounded asymmetry and restabilize, showing that post-promotion coherence can support recovery as well as maintenance.
-	What Cycle 22 added is that even after restabilization, a harsher asymmetry can reopen a serious break corridor, meaning coherence tracks resilience boundaries rather than simply declaring success once promotion has occurred.
-	What Cycle 23 added is that once reciprocal support truly falls below threshold, coherence can also support clean post-promotion de-confirmation: the former stable shared state can be downgraded without denial, overreaction, or historical erasure.
-	What Cycle 24 added is that this downgraded state need not keep collapsing: coherence can support a lower-order resting state in which weaker relation stabilizes without either restoring the former joint state or forcing full independence.
-	What Cycle 25 added is that even this weaker relational plateau need not be treated as fully secure: coherence can represent loosening inside the lower-order state without yet forcing total independent separation.
-	What Cycle 26 added is that once that lower-order plateau thins far enough, coherence can support a return to clearer independent separation while still preserving the graded descent that led there.
-	What Cycle 27 added is that restored independent separation itself can stabilize as a coherent mainline, rather than remaining only a temporary after-effect of relational decay.

This suggests that coherence is not merely a measured field property in the schema.
It is beginning to function as the effective driver of revision, selection, promotion, de-promotion, collapse, non-promotion under contradiction, re-initiation after ambiguity, disciplined weak reopening after restart, provisional weak continuation under mixed support, soft failed reopening under stronger mismatch, renewed provisional relation after a near-miss, bounded restrengthening of renewed relation when support persists, threshold-nearing joint promotion, bounded stable-joint promotion when threshold is genuinely crossed, disciplined maintenance of a promoted joint state under early internal stress, bounded restabilization after that stress is reabsorbed, renewed serious break pressure when resilience limits are approached again, clean post-promotion downgrade when the shared state genuinely loses support, stabilization of a weaker relational plateau after de-confirmation, gradual loosening of that lower-order plateau when its own support weakens, eventual restoration of a clearer independent-separation reading once that lower-order support becomes too thin, and stabilization of that restored independent state as a new mainline.

That is highly relevant to the RGPx framing of the prototype.

---

### 11. The architecture can reject, re-admit, confirm, begin to de-confirm, fully de-confirm, preserve explicit ambiguity, restart cleanly after contradiction, and register fresh weak recoupling after restart

Cycles 5–27 together are especially important.
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
-	Cycle 21 showed that the same stressed stable joint state can reabsorb bounded asymmetry and restabilize without losing its dominant shared reading
-	Cycle 22 showed that even this restabilized joint state can later reopen a serious break corridor under harsher asymmetry, while still remaining provisionally intact as the dominant reading
-	Cycle 23 showed that once that reopened break corridor crossed threshold, the architecture could cleanly deconfirm the formerly stable joint state into a weaker relational / separating reading without clinging to the old state or erasing its history
-	Cycle 24 showed that this downgraded state can then settle into a weaker relational mainline rather than continuing to break immediately into clear independent separation
-	Cycle 25 showed that this weaker relational plateau can itself begin to loosen, without yet requiring either renewed recovery or full independent separation
-	Cycle 26 showed that once the lower-order plateau thinned further, the architecture could restore a clearer independent-separation reading without denying the graded descent through weaker relation that preceded it
-	Cycle 27 showed that this restored independent-separation reading can itself stabilize as a new mainline rather than remaining only a transient endpoint of decay

This suggests the architecture is not simply drifting toward complexity or falling back to independence.
It can move through a fuller interpretive lifecycle depending on which interpretation coherence supports — and can also stop short of forced resolution when coherence does not justify promotion, later restart cleanly when resolution becomes justified, remain open to fresh weak coupling without memory confusion, preserve that weak candidate provisionally under mixed follow-up, let it fade cleanly when support is lost, reopen to genuinely fresh renewed relation without cynicism, strengthen that renewed relation without overpromotion, carry it persistently below threshold, approach threshold in a bounded way, promote into stable joint choreography when the threshold is actually crossed, maintain that promoted state under early internal stress, restabilize that state when the stress is reabsorbed, reopen the possibility of genuine de-confirmation when harsher asymmetry appears again, cleanly downgrade the former stable shared state when coherence support truly falls below threshold, stabilize at a lower relational plateau rather than forcing all remaining structure to vanish, track the loosening of that plateau without prematurely forcing a total break, restore a clearer independent-separation reading once the lower-order support becomes too thin, and then stabilize that restored independence as a coherent current mainline.

---

## What has now been tested
The following have now been tested at least in weak form:
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
-	restabilization of the stressed stable joint state without loss of train distinctness or collapse into false perfection
-	reopening of a serious break corridor inside the re-stabilized stable joint state under harsher asymmetry
-	clean post-promotion de-confirmation of the formerly stable joint state into a weaker relational / separating reading
-	stabilization of that downgraded state as a weaker relational mainline rather than immediate full independent separation
-	loosening of that weaker relational plateau without yet forcing clear independent separation
-	restoration of a clearer independent-separation reading once that lower-order plateau thins sufficiently
-	stabilization of that restored independent-separation reading as a new current mainline

---

## What has not yet been tested

The following remain untested:
-	renewed relational recovery after stable independent separation has been re-established
-	repeated oscillation between weaker relation and clearer separation
-	fragmentation beyond current contradiction/collapse markers
-	stronger mismatch across many restarts
-	high-salience recruitment under real ambiguity
-	richer action-confirmation dynamics
-	competition between multiple possible couplings
-	quantitative coherence metrics and ablations
-	robustness across repeated automated runs

So the current result is now well beyond baseline success and now includes bounded threshold crossing into stable joint choreography, early-stress maintenance of that state, restabilization after mild internal asymmetry, renewed harsher break pressure, clean post-promotion de-confirmation, stabilization of a downgraded weaker relational state, loosening of that lower-order plateau, restoration of a clearer independent-separation reading, and stabilization of that restored independent state, but it is still not a full engineering stress program.

---

## Current verdict
The first twenty-seven cycles support the following stronger claim:

> A prompt-instantiated TU / TU+ / cortexLLM triad can remain role-distinct, use shared structured state to preserve and revise choreography across cycles, absorb mild mismatch, represent weak multi-source coupling, dissolve unsupported relational hypotheses, reopen emerging joint interpretations when coherence rises again, provisionally confirm joint choreography when sustained co-motion supports it, fully de-confirm that choreography into a new stable independent reading when coherence no longer supports the joint field, preserve explicit ambiguity when contradiction prevents justified promotion, resolve that ambiguity into a renewed stable mainline when later evidence favors one branch, register fresh weak recoupling after restart without confusing it with the earlier collapsed joint choreography, keep that weak renewed relation provisional under mixed follow-up without premature promotion or dismissal, cleanly de-promote that weak reopening when stronger mismatch removes support, still register genuinely fresh renewed relation after that near-miss without collapsing into cynicism or false restoration, strengthen that renewed relation into a stronger provisional relational interpretation when support persists across another slice, carry that strengthened relation persistently below joint threshold, approach a threshold-nearing provisional joint reading without cheating across the boundary, promote that relational corridor into stable joint choreography when durable reciprocal support genuinely crosses threshold, preserve that promoted joint state under early internal asymmetry while explicitly tracking de-confirmation pressure, restabilize that stressed joint state when the asymmetry softens again, reopen a serious break corridor when harsher asymmetry later returns, cleanly downgrade the formerly stable joint state into a weaker relational / separating reading when coherence support genuinely falls below threshold, stabilize that downgraded state at a weaker relational level rather than forcing immediate full independence, track the loosening of that lower-order plateau without yet forcing clear independent separation, restore a clearer independent-separation reading once the lower-order support becomes too thin, and then stabilize that restored independence as a coherent current mainline — all without collapsing role boundaries or erasing train distinctness.

This does not yet prove the full architecture, but it strengthens the case that the engineering path is an actual sub-division of LLM labor into specific TU, TU+, and cortexLLM agents organized around coherence-sensitive role specialization.

---

## Recommended next test

The next best test is to introduce one new structural pressure:
-	fresh relational recovery pressure against the stabilized independent mainline

This will let the triad be tested on:
-	whether stable independent separation now resists renewed relation cleanly
-	whether fresh relational recovery can reappear even after the full descent and restabilization of independence
-	whether train distinctness remains preserved under either stable independence or renewed relational return
-	whether coherence can distinguish between a durable restored independence and a field that is again opening to new recoupling
