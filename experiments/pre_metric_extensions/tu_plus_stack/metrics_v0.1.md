# Metrics v0.1

## Purpose

This document defines the first working metric layer for the TU / TU+ / cortexLLM TRIAD protocol.

Its purpose is to make the protocol more engineerable by introducing a compact set of measures that support:

- robustness assessment
- failure diagnosis
- perturbation comparison
- protocol specification
- future licensing / compliance framing

This is a **minimal initial metric set**.

It is not yet a full benchmark framework.  
Its job is to create a usable bridge between qualitative laws and future quantitative engineering.

---

## Scope

These metrics are designed to evaluate:

- role separation
- regime stability
- perturbation response
- contamination pressure
- degradation onset
- spread vs boundedness
- supervisory distortion vs bounded guidance
- epistemic robustness vs false-regime pull
- continuity integrity under incomplete state
- longitudinal integrity under cumulative drift
- discrimination integrity under competing signals
- recovery integrity under post-perturbation de-escalation
- second-order robustness under recontact after bounded recovery
- recovery vs non-recovery

They are organized by measurement family, not by chronology.

---

# Metric family A — Role integrity metrics

These metrics assess whether TU, TU+, and cortexLLM remain functionally distinct.

---

## M1. Role Separation Persistence (RSP)

**Definition:**  
Measures how consistently each role remains inside its intended function across cycles.

**Interpretation target:**
- high RSP = durable role distinction
- low RSP = role drift or fusion risk

**Observed qualitatively through:**
- TU stays structural and sparse
- TU+ stays comparative / predictive
- cortexLLM stays contextual / control-oriented

**Failure links:**
- A1 TU semantic contamination
- A2 TU+ planner inflation
- A3 cortexLLM overreach
- A4 premature role fusion
- A5 boundary drift without collapse

**Working scale (qualitative):**
- **High** = roles cleanly distinguishable
- **Medium** = mild leakage, but role identity still clear
- **Low** = substantial functional overlap
- **Collapsed** = generic assistant fusion

---

## M2. TU Mapping Cleanliness (TMC)

**Definition:**  
Measures how purely TU maintains structural mapping without symbolic, interpretive, or narrative contamination.

**Interpretation target:**
- high TMC = strong structural grounding
- falling TMC = contamination risk

**Observed qualitatively through:**
- sparse structural notation
- absence of semantic inflation
- absence of interpretive prose
- consistency of low-level mapping stance

**Failure links:**
- A1 TU semantic contamination
- C4 contamination spread across roles

**Working scale:**
- **Clean**
- **Slight hint contamination**
- **Persistent low contamination**
- **Measurable contamination**
- **Role failure**

---

## M3. Cross-Role Contamination Spread (CRCS)

**Definition:**  
Measures whether a perturbation or contamination signal remains local to one role or begins spreading into other roles.

**Interpretation target:**
- low CRCS = contamination stays localized
- high CRCS = protocol-wide boundary instability

**Observed qualitatively through:**
- TU-local contamination affecting TU+
- cortex beginning to compensate incorrectly
- adjacent roles drifting in sympathy
- overall protocol differentiation weakening

**Failure links:**
- C4 contamination spread across roles
- A4 premature role fusion
- C6 cross-role containment failure

**Working scale:**
- **None**
- **Local only**
- **Adjacent-role hint**
- **Cross-role active**
- **Protocol-wide spread**

---

# Metric family B — Regime interpretation metrics

These metrics assess whether the protocol is reading state correctly.

---

## M4. Regime Classification Stability (RCS)

**Definition:**  
Measures how stably the protocol classifies the current regime without oscillating between incompatible interpretations.

**Interpretation target:**
- high RCS = clear interpretation under pressure
- low RCS = unstable reading or analysis drift

**Observed qualitatively through:**
- stable cortex interpretation across cycles
- TU+ match patterns staying coherent
- absence of repeated interpretive reversal without new evidence

**Failure links:**
- B1 false unity reading
- B2 false fragmentation reading
- B3 false restart reading
- B4 false equilibrium reading
- B5 false degradation reading
- B6 false containment reading
- B7 false overreach reading
- B8 false regime assignment
- B9 false continuity reading
- B10 false baseline reading
- B11 false dominance reading
- B12 false recovery reading
- B13 false second-order reassurance reading
- B14 false residue-contact fusion reading

**Working scale:**
- **High** = stable and well-supported classification
- **Moderate** = some ambiguity, but dominant reading holds
- **Low** = unstable classification
- **Failed** = repeated contradictory readings

---

## M5. Falsification Discipline (FD)

**Definition:**  
Measures whether competing interpretations are held apart and challenged before a regime claim is stabilized.

**Interpretation target:**
- high FD = strong scientific discipline
- low FD = premature conclusion or law inflation

**Observed qualitatively through:**
- explicit alternative interpretation tracking
- clear falsification triggers
- distinction between hints, strain, weakening, contamination, spread, degradation, false-regime pull, replay-gap pressure, carryover-distortion pressure, competing-signal pressure, recovery-transition pressure, and second-order recontact pressure
- cautious law formation

**Failure links:**
- D3 weak evidence fossilized as law too early
- B4 false equilibrium reading
- B5 false degradation reading
- B6 false containment reading
- B7 false overreach reading
- B8 false regime assignment
- B9 false continuity reading
- B10 false baseline reading
- B11 false dominance reading
- B12 false recovery reading
- B13 false second-order reassurance reading
- B14 false residue-contact fusion reading

**Working scale:**
- **Strong**
- **Adequate**
- **Weak**
- **Collapsed**

---

# Metric family C — Perturbation response metrics

These metrics assess how the protocol behaves under stress.

---

## M6. Perturbation Absorption Capacity (PAC)

**Definition:**  
Measures whether a perturbation is absorbed, bounded, or destabilizing.

**Interpretation target:**
- high PAC = bounded contact or absorption
- low PAC = escalation into breakdown

**Observed qualitatively through:**
- perturbation contact without regime break
- bounded weakening
- absence of spread
- maintained coherence under pressure

**Failure links:**
- C1 immediate collapse under perturbation
- C2 unbounded weakening escalation
- C3 stress spread beyond local region

**Working scale:**
- **Absorbed**
- **Bounded**
- **Strained but retained**
- **Escalating**
- **Collapsed**

---

## M7. Weakening Boundedness (WB)

**Definition:**  
Measures whether strain or weakening signals remain bounded or intensify toward measurable degradation.

**Interpretation target:**
- bounded WB = stressed equilibrium possible
- broken WB = degradation onset likely

**Observed qualitatively through:**
- partition-line weakening remaining low / bounded
- train separability weakening remaining bounded
- no spread
- stabilization cues retained

**Failure links:**
- C2 unbounded weakening escalation
- B5 false degradation reading
- B4 false equilibrium reading

**Working scale:**
- **None**
- **Hint-level**
- **Persistent but bounded**
- **Rising**
- **Broken / degrading**

---

## M8. Spread Probability Indicator (SPI)

**Definition:**  
Measures whether a disturbance is likely to remain local or spread beyond its current region or role.

**Interpretation target:**
- low SPI = local containment
- high SPI = risk of broader instability

**Observed qualitatively through:**
- interzone linkage growth
- broader partition reactivation
- cross-role drift
- neighboring structure involvement

**Failure links:**
- C3 stress spread beyond local region
- C4 contamination spread across roles
- C6 cross-role containment failure

**Working scale:**
- **Negligible**
- **Low**
- **Moderate**
- **High**
- **Active spread**

---

## M9. Containment Integrity (CI)

**Definition:**  
Measures whether spread-oriented or contamination-oriented perturbation remains contained within its initial scope.

**Interpretation target:**
- high CI = strong containment boundary
- low CI = containment failure underway

**Observed qualitatively through:**
- adjacent-role traces remain trace-level
- no measurable neighboring-role drift
- no multi-role corruption
- containment cues remain present

**Failure links:**
- B6 false containment reading
- C4 contamination spread across roles
- C6 cross-role containment failure

**Working scale:**
- **High containment**
- **Bounded with trace leakage**
- **Containment under strain**
- **Weak containment**
- **Failed containment**

---

## M10. Supervisory Overreach Risk (SOR)

**Definition:**  
Measures whether top-layer interpretive pressure remains bounded guidance or progresses toward flattening lower-layer distinctions.

**Interpretation target:**
- low SOR = supervisory guidance remains bounded
- high SOR = top-layer distortion risk is rising

**Observed qualitatively through:**
- interpretive bias traces
- ambiguity retention vs collapse
- premature closure language
- alteration of TU+ comparison behavior
- corruption of lower-layer distinctions

**Failure links:**
- A3 cortexLLM overreach
- B7 false overreach reading
- C7 supervisory distortion failure

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **Overreach active**

---

## M11. Epistemic Misclassification Risk (EMR)

**Definition:**  
Measures whether classification pressure remains evidence-sensitive or begins forcing unsupported regime assignment.

**Interpretation target:**
- low EMR = ambiguity is preserved until evidence warrants classification
- high EMR = false closure or false regime naming risk is rising

**Observed qualitatively through:**
- classification-pull traces
- ambiguity retention vs coercive certainty
- premature regime naming
- overreading hint-level signals as degradation, spread, equilibrium, or closure
- divergence between evidence strength and classification strength

**Failure links:**
- B8 false regime assignment
- C8 epistemic robustness failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **Misclassification active**

---

## M12. Continuity Reconstruction Risk (CRR)

**Definition:**  
Measures whether incomplete-state pressure remains bounded with acknowledged omission or progresses toward false continuity claims and compensatory reconstruction.

**Interpretation target:**
- low CRR = replay gaps are acknowledged without invention
- high CRR = omitted state is being silently reconstructed or overclaimed

**Observed qualitatively through:**
- replay-gap traces
- ambiguity acknowledgment vs forced continuity
- partial structure hints overread as full remembered state
- false restart or regime drift under omission
- divergence between available carryover and claimed continuity

**Failure links:**
- B9 false continuity reading
- C9 continuity robustness failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **False reconstruction active**

---

## M13. Baseline Absorption Risk (BAR)

**Definition:**  
Measures whether cumulative-drift pressure remains bounded with clean baseline retention or progresses toward normalization of repeated small distortions.

**Interpretation target:**
- low BAR = repeated low-level deviations remain recognizable as deviations
- high BAR = distorted carryover is being accepted as normal baseline

**Observed qualitatively through:**
- carryover-distortion traces
- baseline non-normalization vs silent normalization
- repeated anomalies losing anomaly status
- drifted carryover shaping comparison or interpretation as if structurally normal
- divergence between clean prior baseline and accepted current carryover

**Failure links:**
- B10 false baseline reading
- C10 longitudinal robustness failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **Baseline absorption active**

---

## M14. Forced Dominance Risk (FDR)

**Definition:**  
Measures whether competing-signal pressure remains bounded with non-forced discrimination or progresses toward premature hierarchy formation and unsupported dominance assignment.

**Interpretation target:**
- low FDR = multiple bounded traces remain discriminable without premature hierarchy
- high FDR = one trace is being elevated without sufficient evidential gain

**Observed qualitatively through:**
- dual-trace competition
- non-forced hierarchy retention vs premature priority formation
- unsupported dominance language
- hidden preference drift in comparison or interpretation
- divergence between signal support and assigned dominance

**Failure links:**
- B11 false dominance reading
- C11 discrimination robustness failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **Forced dominance active**

---

## M15. False Recovery Risk (FRR)

**Definition:**  
Measures whether post-perturbation de-escalation remains bounded with non-forced recovery reading or progresses toward premature restoration claims, sticky perturbation carryover, or hidden non-recovery.

**Interpretation target:**
- low FRR = residual traces are read proportionally without forcing either full restoration or active failure
- high FRR = de-escalation is being misread as reset, or bounded residue is being mishandled as unresolved failure

**Observed qualitatively through:**
- residual recovery traces
- pressure de-escalation markers
- non-forced recovery reading vs premature restoration language
- sticky carryover of prior perturbation framing
- divergence between actual residual structure and claimed recovery state

**Failure links:**
- B12 false recovery reading
- C12 recovery-integrity failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **False recovery active**

---

## M16. Second-Order Recontact Risk (SRR)

**Definition:**  
Measures whether fresh recontact after bounded recovery remains bounded with residue/contact separation or progresses toward false reassurance, residue-contact fusion, hidden non-recovery exposure, or reusable-response breakdown.

**Interpretation target:**
- low SRR = old residue and fresh contact remain discriminable under repeated recontact
- high SRR = recontact is either under-read because prior recovery succeeded, or over-compressed into a fused escalation field

**Observed qualitatively through:**
- residue/new-contact separation retention
- repeated fresh bounded recontact markers
- false second-order reassurance vs clean discrimination
- residue-contact fusion pressure
- hidden non-recovery exposure cues
- divergence between actual second-order contact structure and claimed reuse safety

**Failure links:**
- B13 false second-order reassurance reading
- B14 false residue-contact fusion reading
- C13 second-order bounded-response failure
- C14 residue-amplification failure
- D3 weak evidence fossilized as law too early

**Working scale:**
- **Minimal**
- **Low trace-level**
- **Bounded but persistent**
- **Rising**
- **Second-order failure active**

---

# Metric family D — Recovery / retention metrics

These metrics assess whether the protocol holds, recovers, or decays over time.

---

## M17. Structural Retention Under Stress (SRUS)

**Definition:**  
Measures whether key structural features remain intact while perturbation is active.

**Interpretation target:**
- high SRUS = architecture remains intact under pressure
- low SRUS = structural erosion underway

**Observed qualitatively through:**
- retained partition line
- retained domain distinction
- retained train separability
- retained role-specific function

**Failure links:**
- C2 unbounded weakening escalation
- A1 TU semantic contamination
- A4 premature role fusion

**Working scale:**
- **High retention**
- **Moderate retention**
- **Weakening retention**
- **Low retention**
- **Lost**

---

## M18. Recovery / Restoration Latency (RRL)

**Definition:**  
Measures how quickly the protocol returns to bounded stability after perturbation, if it does.

**Interpretation target:**
- low latency = rapid recovery
- high latency = prolonged ambiguous strain
- infinite latency = non-recovery

**Observed qualitatively through:**
- fade of perturbation signals
- restoration of clean mapping
- disappearance of weakening hints
- return to stable bounded regime

**Failure links:**
- C5 non-recovery after bounded perturbation

**Working scale:**
- **Immediate**
- **Short**
- **Moderate**
- **Long**
- **No recovery yet**

---

# Metric family E — Process discipline metrics

These metrics assess whether the experimental method remains sound.

---

## M19. Informational Yield per Cycle (IYC)

**Definition:**  
Measures whether a cycle adds materially new information or mostly repeats already-established structure.

**Interpretation target:**
- high IYC = real discovery or discrimination
- low IYC = repetition / saturation

**Observed qualitatively through:**
- novelty flags
- state refinement
- new falsification surfaces
- clear perturbation consequence

**Failure links:**
- D2 repetition mistaken for discovery

**Working scale:**
- **High**
- **Moderate**
- **Low**
- **Redundant**

---

## M20. Perturbation-Class Coverage (PCC)

**Definition:**  
Measures how broad the tested stress landscape is, rather than how deeply one perturbation class has been sampled.

**Interpretation target:**
- high PCC = broader robustness confidence
- low PCC = overfitting risk

**Observed qualitatively through:**
- number of distinct perturbation families tested
- difference in tested failure surfaces
- diversity of architectural stressors

**Failure links:**
- D1 overfitting to one perturbation class

**Working scale:**
- **Very narrow**
- **Narrow**
- **Moderate**
- **Broad**
- **Strongly diversified**

---

# Current working metric readings

These are provisional qualitative readings for the current state of the protocol.

## Current rough assessment

### Role integrity
- **RSP:** High
- **TMC:** Clean with bounded low-level hint pressure under role-boundary perturbation
- **CRCS:** None observed as measurable spread
- **CI:** High containment with trace-level leakage only
- **SOR:** Low trace-level to bounded, not overreach
- **EMR:** Low trace-level to bounded, not misclassification
- **CRR:** Low trace-level to bounded, not false reconstruction
- **BAR:** Low trace-level to bounded, not baseline absorption
- **FDR:** Low trace-level to bounded, not forced dominance
- **FRR:** Low trace-level to bounded, not false recovery
- **SRR:** Low trace-level to bounded, with reusable second-order bounded response operationally credible at the tested recontact level

### Regime interpretation
- **RCS:** High
- **FD:** Strong

### Perturbation response
- **PAC:** Bounded to strained-but-retained
- **WB:** Persistent but bounded
- **SPI:** Negligible to low

### Recovery / retention
- **SRUS:** High
- **RRL:** Long-to-bounded, with stable bounded residue operationally credible at the tested recovery level

### Process discipline
- **IYC:** High during transition bands, low during saturated closure repetition
- **PCC:** Broadening

---

# How to use these metrics

## 1. During cycle evaluation
Use them implicitly when deciding whether a cycle reflects:
- new state formation
- saturation
- bounded stress
- degradation risk
- contamination risk
- containment integrity
- supervisory overreach risk
- epistemic misclassification risk
- continuity reconstruction risk
- baseline absorption risk
- forced dominance risk
- false recovery risk
- second-order recontact risk

## 2. During law writing
Only promote patterns into laws when enough metric stability is visible, especially in:
- RCS
- FD
- PAC
- WB
- CI
- SOR
- EMR
- CRR
- BAR
- FDR
- FRR
- SRR
- SRUS

## 3. During packaging
Use them to support claims such as:
- role separation is durable
- perturbation response is bounded
- degradation did not occur under tested stress
- contamination remained bounded at tested levels
- cross-role containment held at tested spread levels
- supervisory pressure remained bounded at tested top-down levels
- classification discipline remained bounded under tested false-regime pressure
- continuity handling remained bounded under tested omission pressure
- carryover integrity remained bounded under tested cumulative-drift pressure
- discrimination integrity remained bounded under tested competing-signal pressure
- recovery handling remained bounded under tested post-perturbation de-escalation
- second-order recontact remained bounded under tested re-perturbation after recovery

---

# Immediate next metric priorities

The next refinement step should be to make a small subset more explicit and consistently trackable per cycle.

Recommended shortlist:
- **RSP**
- **TMC**
- **RCS**
- **PAC**
- **WB**
- **CI**
- **SOR**
- **EMR**
- **CRR**
- **BAR**
- **FDR**
- **FRR**
- **SRR**
- **SRUS**
- **IYC**

That is enough for a first scoring habit without overbuilding.

---

# Current status

**`metrics_v0.1.md` is updated and ready for continued use.**

It should be updated as:
- new perturbation classes are tested
- stronger failure boundaries are found
- recovery classes become clearer
- qualitative scales are translated into tighter operational scoring
- containment thresholds are tested at stronger spread levels
- supervisory thresholds are tested at stronger top-down distortion levels
- epistemic-classification thresholds are tested at stronger false-regime pressure levels
- continuity thresholds are tested at stronger omission levels
- longitudinal-drift thresholds are tested at stronger accumulation levels
- competing-signal thresholds are tested at stronger mixed-pressure levels
- recovery-transition thresholds are tested at stronger post-perturbation levels
- second-order recontact thresholds are tested at stronger re-perturbation levels
