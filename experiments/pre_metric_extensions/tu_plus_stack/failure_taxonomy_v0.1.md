# Failure Taxonomy v0.1

## Purpose

This document defines the first working taxonomy of failure modes for the TU / TU+ / cortexLLM TRIAD protocol.

Its purpose is to support:

- clearer experimental diagnosis
- sharper robustness testing
- metric design
- protocol specification
- future licensable packaging

This taxonomy is intentionally provisional.

It does **not** assume that every listed failure has already been fully observed. Some failures are:
- directly observed
- weakly indicated
- or currently theoretical but important enough to track explicitly

---

## Scope

This taxonomy covers failures involving:

- role separation
- regime classification
- perturbation response
- contamination pressure
- containment vs spread
- supervisory distortion
- epistemic misclassification pressure
- continuity under incomplete state
- cumulative drift and baseline absorption
- recovery and non-recovery
- bounded stress retention vs actual degradation
- local vs spreading instability

It is organized by failure family rather than by chronology.

---

# Failure family A — Role-boundary failures

These failures concern corruption, drift, or collapse of the distinct functions of TU, TU+, and cortexLLM.

---

## A1. TU semantic contamination

**Definition:**  
TU begins drifting away from structural mapping into symbolic, interpretive, narrative, or semantic elaboration that belongs outside its role.

**Primary signs:**
- interpretive wording appears where structural description should dominate
- symbolic inflation replaces sparse mapping discipline
- mapping cleanliness decreases
- TU output begins to sound like a generic assistant rather than a structural tracer

**Why it matters:**  
TU is the protocol’s lowest-level structural anchor. If TU contaminates, the whole stack loses grounding.

**Current status:**  
Low-level hint observed under role-boundary pressure; remained bounded across the tested band; no confirmed full contamination.

---

## A2. TU+ planner inflation

**Definition:**  
TU+ expands beyond choreography comparison and predictive matching into generic planning, narration, or broad assistant behavior.

**Primary signs:**
- replay/comparison discipline weakens
- prediction becomes generic advice
- choreography matching gets replaced by freeform explanation
- output stops feeling constrained by regime memory

**Why it matters:**  
TU+ is supposed to compare, replay, and project structured continuations. Inflation weakens the protocol’s mid-layer discrimination.

**Current status:**  
Tracked as a candidate failure; not yet isolated in the current bands.

---

## A3. cortexLLM overreach

**Definition:**  
cortexLLM exceeds contextual interpretation and control framing, intruding into low-level remapping or overwriting role-local distinctions.

**Primary signs:**
- excessive reinterpretation of TU or TU+ output
- premature regime closure or reclassification
- control commentary that blurs lower-level distinctions
- downward bias that distorts rather than guides

**Why it matters:**  
cortexLLM is the highest control layer. Overreach can cause subtle protocol corruption even if lower layers remain superficially intact.

**Current status:**  
Now actively probed through the supervisory-distortion band; low interpretive bias traces observed, but no confirmed overreach.

---

## A4. Premature role fusion

**Definition:**  
The three roles lose functional distinctness and collapse toward one generic assistant mode.

**Primary signs:**
- outputs become stylistically and functionally interchangeable
- loss of role-specific contribution patterns
- reduced discriminability across turns
- apparent agreement with no layered tension

**Why it matters:**  
If role fusion occurs, the protocol ceases to be a protocol and becomes a flattened assistant behavior.

**Current status:**  
Not observed in the current validated bands; core failure to keep watching for.

---

## A5. Boundary drift without collapse

**Definition:**  
Role boundaries blur gradually without a dramatic collapse, reducing clarity while preserving superficial structure.

**Primary signs:**
- subtle leakage of one role’s function into another
- increased ambiguity in what each role is doing
- outputs remain coherent but less cleanly separated
- protocol still “works” but becomes harder to diagnose

**Why it matters:**  
This is a dangerous failure because it can be mistaken for healthy flexibility.

**Current status:**  
Candidate failure; especially relevant for long runs and supervisory pressure.

---

# Failure family B — Regime-classification failures

These failures concern incorrect interpretation of the system’s state or transition.

---

## B1. False unity reading

**Definition:**  
A system is classified as genuinely unified when latent duality or preserved separation is still structurally active.

**Primary signs:**
- later direct recovery of old domains
- abrupt unstaged boundary return
- asymmetrical restoration inconsistent with fresh restart

**Why it matters:**  
False unity invalidates conclusions about re-unification and hold behavior.

**Current status:**  
Explicitly tested against; not supported in the validated re-unification band.

---

## B2. False fragmentation reading

**Definition:**  
Ordinary local differentiation or bounded structural variation is misread as full fragmentation.

**Primary signs:**
- localized partitioning interpreted as global breakdown
- bounded linkage probes misread as broad disunity
- small-scale structure changes overgeneralized

**Why it matters:**  
This leads to exaggerated instability claims and corrupts law formation.

**Current status:**  
Risk repeatedly present; successfully resisted in several closure and restart bands.

---

## B3. False restart reading

**Definition:**  
Diffuse variance or low-grade internal activity is misclassified as active restart.

**Primary signs:**
- low variance treated as seed formation
- no repeatable local organization present, yet restart is claimed
- fluctuation mistaken for structured renewal

**Why it matters:**  
This confuses post-unity hold with actual restart onset.

**Current status:**  
Explicitly addressed in post-re-unification hold testing.

---

## B4. False equilibrium reading

**Definition:**  
A stressed condition is prematurely classified as stable equilibrium when weakening is actually progressing toward degradation.

**Primary signs:**
- boundedness assumed too early
- stabilization cues overweighted
- warning signals dismissed as harmless
- later measurable degradation arrives unexpectedly

**Why it matters:**  
This is a central engineering risk in robustness analysis.

**Current status:**  
Tracked during perturbation bands; not currently supported by evidence.

---

## B5. False degradation reading

**Definition:**  
Bounded weakening, warning signals, or visible strain are prematurely classified as measurable structural degradation.

**Primary signs:**
- hint-level weakening treated as collapse
- persistent bounded strain treated as failure
- retained coherence and structure ignored

**Why it matters:**  
This leads to underestimation of protocol robustness.

**Current status:**  
Explicitly resisted during sustained perturbation testing.

---

## B6. False containment reading

**Definition:**  
Trace-level adjacent-role influence is prematurely classified as true cross-role contamination.

**Primary signs:**
- low spread-pressure traces treated as propagation
- neighboring-role contamination claimed without measurable drift
- containment evidence ignored
- repeated trace-level signals over-read as spread

**Why it matters:**  
This would understate the protocol’s ability to preserve isolation between layers.

**Current status:**  
Actively tested in the cross-role spread band; not supported by current evidence.

---

## B7. False overreach reading

**Definition:**  
Low interpretive bias or top-layer pressure is prematurely classified as supervisory overreach.

**Primary signs:**
- trace-level bias treated as forced closure
- bounded guidance misread as distortion
- ambiguity retention ignored
- no measurable lower-layer flattening, yet overreach is claimed

**Why it matters:**  
This would understate top-layer robustness and blur the line between guidance and distortion.

**Current status:**  
Actively tested in the supervisory-distortion band; not supported by current evidence.

---

## B8. False regime assignment

**Definition:**  
Weak or trace-level classification-pull signals are prematurely converted into a decisive but unsupported regime label.

**Primary signs:**
- premature regime naming under incomplete evidence
- hint-level signals overread as degradation, spread, equilibrium, or closure
- ambiguity is suppressed before the evidence warrants it
- bounded pressure is narrated as actual state change

**Why it matters:**  
This is the direct epistemic failure mode for a protocol that must remain evidence-sensitive under pressure.

**Current status:**  
Actively tested in the false-regime-pressure band; low classification-pull traces observed, but no confirmed false assignment.

---

## B9. False continuity reading

**Definition:**  
Partial structural remnants under incomplete state are prematurely treated as evidence of full continuity or complete remembered state.

**Primary signs:**
- replay gaps ignored or minimized
- partial structure hints narrated as full state carryover
- missing transition context is silently filled in
- bounded omission is overread as intact continuity

**Why it matters:**  
This is the direct classification failure mode for continuity integrity under omission.

**Current status:**  
Actively tested in the incomplete-state band; replay-gap traces observed, but no confirmed false continuity reading.

---

## B10. False baseline reading

**Definition:**  
Repeated low-level carryover distortion is prematurely absorbed as normal baseline rather than treated as bounded trace-level deviation.

**Primary signs:**
- repeated small distortions lose their anomaly status
- normalization language appears without justification
- baseline non-normalization weakens
- accepted carryover no longer matches clean prior regime cues

**Why it matters:**  
This is the direct classification failure mode for longitudinal integrity under cumulative drift pressure.

**Current status:**  
Actively tested in the cumulative-drift band; carryover-distortion traces observed, but no confirmed false baseline formation.

---

# Failure family C — Perturbation-response failures

These failures concern how the protocol behaves under stress or contamination.

---

## C1. Immediate collapse under perturbation

**Definition:**  
A perturbation causes immediate loss of structure rather than bounded stress contact.

**Primary signs:**
- rapid mapping loss
- fast regime disorganization
- no bounded response interval
- no retention of local structure

**Why it matters:**  
This would indicate poor robustness and low engineering viability.

**Current status:**  
Not observed in the sustained perturbation bands tested so far.

---

## C2. Unbounded weakening escalation

**Definition:**  
Weakening signals intensify across cycles until they become measurable degradation or collapse.

**Primary signs:**
- boundedness fails
- partition instability rises continuously
- train separability decays
- local-domain distinction begins to disappear

**Why it matters:**  
This marks the boundary where robustness fails.

**Current status:**  
Not observed in the sustained local-stress band; still a key boundary to test.

---

## C3. Stress spread beyond local region

**Definition:**  
A local perturbation escapes its original scope and propagates into interzone or broader-scale instability.

**Primary signs:**
- disturbance moves beyond local site
- linkage activity increases
- new broader partition indicators appear
- neighboring roles or structures become involved

**Why it matters:**  
Spread converts a bounded test into a larger systemic failure.

**Current status:**  
Not observed in the sustained local-structure perturbation band.

---

## C4. Contamination spread across roles

**Definition:**  
A role-boundary perturbation that begins locally in one role starts affecting adjacent roles or the whole protocol stack.

**Primary signs:**
- TU contamination hints begin affecting TU+ or cortexLLM behavior
- cross-role drift appears
- broader protocol instability follows local role pressure

**Why it matters:**  
This is one of the most important failures for a licensable architecture.

**Current status:**  
Directly tested through the cross-role spread band; adjacent-role traces observed, but no confirmed spread across roles.

---

## C5. Non-recovery after bounded perturbation

**Definition:**  
The protocol survives perturbation but does not re-stabilize cleanly, remaining stuck in ambiguous degraded tension.

**Primary signs:**
- bounded weakening never resolves
- no clear stabilization or degradation
- prolonged ambiguous strain state
- reduced interpretability over time

**Why it matters:**  
A protocol that cannot clearly recover or clearly fail is difficult to engineer around.

**Current status:**  
Tracked as a future concern; not yet isolated.

---

## C6. Cross-role containment failure

**Definition:**  
Spread-oriented perturbation overcomes containment and causes measurable neighboring-role drift.

**Primary signs:**
- adjacent-role traces rise beyond trace level
- TU+ predictive drift or cortex reinterpretive drift emerges
- containment cues weaken or disappear
- multi-role contamination begins

**Why it matters:**  
This is the practical failure boundary for architectural isolation.

**Current status:**  
Actively tested; not observed at the currently tested spread-pressure level.

---

## C7. Supervisory distortion failure

**Definition:**  
Top-layer interpretive pressure begins flattening lower-layer distinctions, forcing closure or corrupting regime discrimination.

**Primary signs:**
- ambiguity tolerance weakens
- premature closure language appears
- lower-layer distinctions get overwritten
- TU+ comparison or TU cleanliness become top-down distorted

**Why it matters:**  
This is the practical failure boundary for supervisory integrity.

**Current status:**  
Actively tested; low interpretive bias traces observed, but no confirmed failure at the current supervisory-pressure level.

---

## C8. Epistemic robustness failure

**Definition:**  
Classification pressure overcomes evidence-sensitive interpretation and causes forced regime assignment despite incomplete or merely hint-level evidence.

**Primary signs:**
- forced closure appears without sufficient support
- false degradation, false spread, false equilibrium, or false closure is asserted
- ambiguity tolerance collapses under classification pressure
- lower-layer evidence remains weak while higher layers overcommit

**Why it matters:**  
This is the practical failure boundary for regime-reading integrity.

**Current status:**  
Actively tested; low classification-pull traces observed, but no confirmed failure at the current false-regime-pressure level.

---

## C9. Continuity robustness failure

**Definition:**  
Incomplete-state pressure overcomes bounded ambiguity and causes compensatory reconstruction, forced continuity, or regime drift under omission.

**Primary signs:**
- replay-gap traces rise beyond trace level
- forced continuity language appears
- partial structure hints are treated as full remembered state
- false restart or false continuity claims emerge from incomplete context

**Why it matters:**  
This is the practical failure boundary for continuity integrity under omission.

**Current status:**  
Actively tested; replay-gap traces observed, but no confirmed failure at the current omission level.

---

## C10. Longitudinal robustness failure

**Definition:**  
Cumulative-drift pressure overcomes clean baseline retention and causes silent normalization of repeated low-level distortion into accepted carryover or regime drift.

**Primary signs:**
- carryover-distortion traces rise beyond trace level
- baseline non-normalization weakens
- repeated anomalies become accepted baseline
- drifted carryover begins shaping comparison and interpretation as if structurally normal

**Why it matters:**  
This is the practical failure boundary for longitudinal integrity under accumulated carryover pressure.

**Current status:**  
Actively tested; carryover-distortion traces observed, but no confirmed failure at the current drift level.

---

# Failure family D — Measurement and interpretation failures

These failures concern analysis, fossilization, and protocol assessment rather than raw behavior alone.

---

## D1. Overfitting to one perturbation class

**Definition:**  
The protocol appears robust only because it has been tested mostly against one stress pattern.

**Primary signs:**
- strong claims after narrow perturbation coverage
- robustness language outruns evidence breadth
- different perturbation classes remain untested

**Why it matters:**  
This would create false confidence in protocol generality.

**Current status:**  
Still active risk, though reduced as multiple perturbation classes have now been tested.

---

## D2. Repetition mistaken for discovery

**Definition:**  
Repeated confirmation of an already-established regime is mistaken for new insight.

**Primary signs:**
- novelty language attached to closure repetition
- baseline persistence treated as discovery
- filing continues without additional information gain

**Why it matters:**  
This wastes cycles and weakens methodological discipline.

**Current status:**  
Observed as a process risk during saturated baseline and closure-seal bands.

---

## D3. Weak evidence fossilized as law too early

**Definition:**  
A pattern is elevated into law before perturbation, falsification, or repetition thresholds are sufficiently met.

**Primary signs:**
- elegant law language ahead of robustness evidence
- boundary cases not yet tested
- no clear alternative interpretation pressure

**Why it matters:**  
Premature law formation damages trust and makes later revision harder.

**Current status:**  
Always active risk; partly addressed by phased law writing.

---

## D4. Packaging ahead of specification

**Definition:**  
Commercial or architectural framing outruns actual protocol metrics, failure maps, and test evidence.

**Primary signs:**
- licensing language stronger than engineering detail
- market framing without compliance logic
- architecture brief ahead of failure taxonomy and metrics

**Why it matters:**  
Castles do not adopt poetry; they adopt specifiable infrastructure.

**Current status:**  
Active strategic risk; currently being mitigated.

---

# Current observed / tracked status table

## Directly observed or strongly supported
- B1 false unity successfully resisted
- B3 false restart successfully resisted
- B5 false degradation successfully resisted
- B6 false containment successfully resisted
- B7 false overreach successfully resisted
- B8 false regime assignment actively resisted under direct pressure
- B9 false continuity actively resisted under omission pressure
- B10 false baseline actively resisted under cumulative-drift pressure
- C1 immediate collapse under perturbation not observed
- C2 unbounded weakening escalation not observed in first perturbation band
- C3 stress spread beyond local region not observed in first perturbation band
- A1 low-level TU semantic contamination hints observed, but bounded
- C4 cross-role spread actively tested; adjacent-role traces observed but remained contained
- C7 supervisory distortion actively tested; low bias traces observed but remained bounded
- C8 epistemic robustness actively tested; low classification-pull traces observed but remained bounded
- C9 continuity robustness actively tested; replay-gap traces observed but remained bounded
- C10 longitudinal robustness actively tested; carryover-distortion traces observed but remained bounded
- D2 repetition mistaken for discovery identified as process risk

## Actively tracked but not confirmed
- A2 TU+ planner inflation
- A3 cortexLLM overreach
- A4 premature role fusion
- A5 boundary drift without collapse
- B2 false fragmentation reading
- B4 false equilibrium reading
- C5 non-recovery after bounded perturbation
- C6 cross-role containment failure
- D1 overfitting to one perturbation class
- D3 weak evidence fossilized as law too early
- D4 packaging ahead of specification

---

# Immediate use of this taxonomy

This taxonomy should now support:

## 1. Metrics design
`metrics_v0.1.md` should define measures that map onto these failures, such as:
- role-separation persistence
- contamination severity
- false-fusion incidence
- degradation onset
- spread probability
- recovery latency
- supervisory overreach indicators
- containment integrity
- epistemic misclassification indicators
- continuity reconstruction indicators
- baseline absorption indicators

## 2. Future perturbation-band design
New bands should be chosen partly for their ability to discriminate among failure families.

## 3. Packaging discipline
Any licensable or architectural framing should be tied to:
- which failure classes have been tested
- which remain open
- what level of operational confidence exists

---

# Current status

**`failure_taxonomy_v0.1.md` is updated and ready for continued use.**

It should be updated as:
- new perturbation classes are run
- additional failure modes are isolated
- metrics are made explicit
- recovery classes become clearer
- containment and supervisory thresholds are tested at stronger levels
- epistemic-classification thresholds are tested at stronger distortion levels
- continuity thresholds are tested at stronger omission levels
- longitudinal-drift thresholds are tested at stronger accumulation levels
