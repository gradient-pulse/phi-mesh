# Prototype Run Observations 04

## Objective

Characterize the stability, reversibility, and structural robustness of the activation regime.

Reference:
- Baseline contract (Cycles 60–90)
- Activation pathway (Cycles 91–100)

---

## Test Discipline

All cycles must:
- operate within activation_state
- introduce structural perturbations only

Signal-space variations remain irrelevant and are excluded.

---

## Initial test axis

Test family 01: **Activation stability under structural degradation**

Question:
Can activation sustain itself if internal structure is weakened?

---
---

### Cycle 101 — Activation stability under slight feedback degradation

**What was tested**
- whether **slight degradation of endogenous feedback**:
  - from activation layer → readiness layer  
affects:
  - stability of activation  
  - threshold distance  
  - or causes reversion to transition boundary  

---

**What happened**

- **TU**
  - registered:
    - `feedback_partially_attenuated`  
  - preserved:
    - activation state  
  - explicitly maintained:
    - threshold distance remains zero  
    - no reversion to transition boundary  
    - no decay into pre-activation state  

- **TU+**
  - maintained:
    - `activation_state` (dominant)  
  - confirmed:
    - activation remains self-sustaining  
    - critical coupling is weakened but intact  
  - rejected:
    - activation loss under slight degradation  
    - dependence on full feedback integrity  

- **cortexLLM**
  - classified regime as:
    - `stable_activation_state_under_partial_feedback_degradation`  
  - established:
    - activation regime exhibits **resilience margin**  
    - endogenous feedback is not singularly fragile  
    - system tolerates minor structural perturbations  
  - confirmed:
    - no re-entry into transition boundary  

---

**Finding**

Cycle 101 demonstrates:

- activation state is:
  - robust under slight feedback degradation  
  - self-sustaining with reduced feedback strength  
- threshold distance remains zero  
- no reversion or instability occurs  

This establishes:

> **activation regime has structural resilience to minor feedback degradation**

and:

> **endogenous feedback operates with tolerance margin, not exact precision**

---

**Operational delta**

- state distinction added:
  - `resilient_activation_regime`  
    - defined as:  
      *a condition in which activation remains stable under partial degradation of endogenous feedback, without threshold reopening or regime reversion*  

- classification:
  - first robustness test of activation regime  

- invariants refined:
  - activation stability does not require full feedback strength  
  - activation regime exhibits fault tolerance to minor structural perturbation  
  - critical coupling can persist under partial feedback attenuation  

---

### Cycle 102 — Activation under moderate feedback degradation (stressed regime)

**What was tested**
- whether **moderate degradation of endogenous feedback**:
  - distributed attenuation from activation → readiness  
affects:
  - persistence of activation  
  - stability of the regime  
  - or causes reversion to transition boundary  

---

**What happened**

- **TU**
  - registered:
    - `feedback_moderately_degraded`  
    - `stressed_activation_state`  
    - `activation_trace_fluctuating`  
  - preserved:
    - activation state  
  - detected:
    - reduced coupling stability  
    - micro-fluctuations in activation trace  
  - explicitly maintained:
    - no reversion to transition boundary  
    - no decay to pre-activation state  

- **TU+**
  - maintained:
    - `activation_state` (dominant)  
  - confirmed:
    - activation persists under structural stress  
    - threshold distance remains zero but becomes fragile  
    - fluctuations are non-divergent  
  - rejected:
    - immediate activation loss  
    - threshold reopening  
    - transition boundary re-entry  

- **cortexLLM**
  - classified regime as:
    - `stressed_activation_state_under_moderate_feedback_degradation`  
  - established:
    - activation regime has **finite stability margin**  
    - feedback strength controls stability, not existence  
    - system enters a **meta-stable activation condition**  
  - confirmed:
    - activation persists despite internal fluctuations  

---

**Finding**

Cycle 102 demonstrates:

- activation state:
  - persists under moderate feedback degradation  
  - becomes dynamically unstable internally  
  - remains globally stable  
- threshold distance remains zero  
- fluctuations:
  - are contained  
  - do not propagate into collapse  

This establishes:

> **activation has a finite stability margin and can enter a stressed but persistent regime**

and:

> **feedback strength modulates stability, not the existence of activation**

---

**Operational delta**

- state distinction added:
  - `stressed_activation_regime`  
    - defined as:  
      *a condition in which activation persists under moderate feedback degradation, exhibiting internal fluctuations but no global collapse or threshold reopening*  

- classification:
  - first meta-stable activation regime  

- invariants refined:
  - activation stability is not binary but graded  
  - threshold-zero state can exhibit internal dynamics without collapse  
  - activation persistence does not require full structural integrity

---

### Cycle 103 — Activation collapse under strong feedback degradation (reversion)

**What was tested**
- whether **strong degradation of endogenous feedback**:
  - activation → readiness  
can:
  - destabilize activation  
  - reopen threshold  
  - cause reversion to transition boundary  

---

**What happened**

- **TU**
  - registered:
    - `feedback_strongly_degraded`  
    - `activation_instability`  
    - `threshold_reopening`  
    - `reversion_pressure_present`  
  - detected:
    - loss of self-sustaining regime  
    - breakdown of critical coupling  
    - emergence of global instability  
  - identified:
    - activation becoming unsustainable  

- **TU+**
  - reclassified regime:
    - `activation_state → transition_boundary_state`  
  - confirmed:
    - threshold distance reopens from zero  
    - global activation coherence is lost  
    - system exits activation regime  
  - rejected:
    - irreversibility of activation  
    - persistence of zero-threshold condition  

- **cortexLLM**
  - classified regime as:
    - `transition_boundary_reentry_under_strong_feedback_degradation`  
  - established:
    - activation collapses due to loss of endogenous feedback  
    - activation layer decouples from propagation  
    - reversion is structurally driven  
  - confirmed:
    - activation state is **conditionally stable, not absolute**  

---

**Finding**

Cycle 103 demonstrates:

- strong feedback degradation:
  - breaks self-sustaining activation  
  - destabilizes critical coupling  
  - causes threshold reopening  
  - drives system back to transition boundary  
- activation is:
  - reversible under sufficient structural degradation  

This establishes:

> **activation requires continuous structural support via endogenous feedback**

and:

> **activation state is conditionally stable and can collapse under strong structural degradation**

---

**Operational delta**

- state distinction added:
  - `activation_collapse_regime`  
    - defined as:  
      *a condition in which strong degradation of endogenous feedback leads to loss of activation coherence, threshold reopening, and re-entry into transition boundary state*  

- classification:
  - first activation collapse and reversion event  

- invariants revised:
  - activation is not irreversible  
  - endogenous feedback is required for maintenance  
  - threshold-zero state can revert to positive under structural degradation  
  - activation stability depends on sustained structural integrity  

---

### Cycle 104 — Partial feedback restoration (failed reactivation)

**What was tested**
- whether **moderate restoration of endogenous feedback**:
  - activation → readiness  
after collapse (Cycle 103) can:
  - re-establish activation  
  - or initiate reactivation pathway  

---

**What happened**

- **TU**
  - registered:
    - `partial_feedback_recovery`  
    - `localized_precursor_reemergence`  
  - detected:
    - partial recoupling of activation layer  
    - local precursor pressure reappearing  
  - explicitly maintained:
    - no propagation  
    - no threshold crossing  
    - no activation re-entry  

- **TU+**
  - maintained:
    - `transition_boundary_state` (dominant)  
  - confirmed:
    - feedback restoration is subcritical  
    - precursor remains localized  
    - threshold distance reduces but stays positive  
  - rejected:
    - activation re-entry under partial restoration  

- **cortexLLM**
  - classified regime as:
    - `transition_boundary_with_subcritical_reactivation_attempt`  
  - established:
    - reactivation attempt occurs but fails  
    - propagation is not restored  
    - activation layer remains insufficiently coupled  
  - confirmed:
    - system remains in transition boundary  

---

**Finding**

Cycle 104 demonstrates:

- partial feedback restoration:
  - reintroduces local precursor pressure  
  - reduces threshold distance  
  - does not restore activation  
- system:
  - attempts reactivation  
  - fails due to lack of propagation and critical coupling  

This establishes:

> **reactivation requires full structural reconstitution, not partial recovery**

and:

> **localized precursor reemergence without propagation is insufficient for activation re-entry**

---

**Operational delta**

- state distinction added:
  - `failed_reactivation_regime`  
    - defined as:  
      *a condition in which partial restoration of feedback produces localized precursor pressure but fails to re-establish propagation, critical coupling, or activation*  

- classification:
  - first failed reactivation attempt  

- invariants refined:
  - activation re-entry requires restoration of propagation and critical coupling  
  - partial feedback recovery cannot reconstitute activation  
  - transition boundary can host subcritical reactivation attempts without resolution  

---

### Cycle 105 — Strong feedback restoration with partial propagation (near-critical reactivation)

**What was tested**
- whether **strong restoration of endogenous feedback**:
  - with partial re-enablement of propagation pathways  
after failed reactivation (Cycle 104) can:
  - re-enter activation  
  - or reach a stable near-critical state  

---

**What happened**

- **TU**
  - registered:
    - `strong_feedback_recovery`  
    - `partial_propagation_reestablished`  
    - `extended_precursor_pressure`  
    - `near_critical_reactivation_state`  
  - detected:
    - precursor pressure extending beyond local scope  
    - propagation partially restored  
  - explicitly maintained:
    - no threshold crossing  
    - no activation re-entry  

- **TU+**
  - maintained:
    - `transition_boundary_state` (dominant)  
  - confirmed:
    - strong feedback restoration is insufficient alone  
    - propagation remains incomplete  
    - threshold distance is minimal but positive  
  - rejected:
    - automatic activation re-entry under strong restoration  

- **cortexLLM**
  - classified regime as:
    - `transition_boundary_with_near_critical_reactivation_under_partial_propagation`  
  - established:
    - system reaches **near-critical reactivation state**  
    - precursor pressure extends but does not fully globalize  
    - propagation remains non-coherent  
  - confirmed:
    - activation re-entry is blocked by incomplete structural reconstitution  

---

**Finding**

Cycle 105 demonstrates:

- strong feedback restoration:
  - re-establishes coupling  
  - extends precursor pressure  
  - partially restores propagation  
- system:
  - approaches activation threshold  
  - does not cross it  
- activation re-entry fails due to:
  - incomplete propagation coherence  

This establishes:

> **reactivation requires full propagation coherence, not partial propagation**

and:

> **even strong structural restoration can produce stable near-critical reactivation without activation**

---

**Operational delta**

- state distinction added:
  - `near_critical_reactivation_regime`  
    - defined as:  
      *a condition in which strong feedback restoration and partial propagation produce extended precursor pressure and near-threshold dynamics without threshold crossing or activation re-entry*  

- classification:
  - first high-energy, near-critical reactivation regime  

- invariants refined:
  - activation re-entry requires full propagation coherence  
  - strong feedback restoration alone is insufficient  
  - transition boundary can sustain near-critical reactivation states without resolution

---

### Cycle 106 — Activation re-entry via propagation coherence restoration

**What was tested**
- whether **full restoration of propagation coherence**:
  - after near-critical reactivation (Cycle 105)  
can:
  - enable threshold crossing  
  - and re-enter activation  

---

**What happened**

- **TU**
  - registered:
    - `propagation_coherent_global`  
    - `activation_state_reentered`  
    - `threshold_crossed`  
  - detected:
    - precursor pressure globalizing coherently  
    - activation layer fully recoupling  
    - threshold distance → zero  
  - initiated:
    - reactivation transition  

- **TU+**
  - reclassified regime:
    - `transition_boundary_state → activation_state`  
  - confirmed:
    - threshold crossing re-established  
    - activation re-entry is structurally valid  
  - rejected:
    - persistence of near-critical boundary state  

- **cortexLLM**
  - classified regime as:
    - `activation_reentry_state_under_global_propagation_coherence`  
  - established:
    - propagation coherence is the decisive missing condition  
    - activation is repeatable under full structural reconstitution  
  - confirmed:
    - transition boundary is not terminal  

---

**Finding**

Cycle 106 demonstrates:

- activation re-entry occurs when:
  - propagation becomes fully coherent  
  - activation layer recouples critically  
- threshold crossing:
  - is re-achievable  
  - follows the same structural pathway as initial activation  

This establishes:

> **activation is repeatable given full structural reconstitution**

and:

> **propagation coherence is the decisive condition for both initial activation and reactivation**

---

**Operational delta**

- state distinction added:
  - `reactivated_activation_regime`  
    - defined as:  
      *a condition in which activation is re-entered after collapse through full restoration of propagation coherence and critical coupling*  

- classification:
  - first successful activation re-entry  

- invariants refined:
  - activation is reversible and repeatable  
  - transition boundary is a recoverable intermediate state  
  - propagation coherence is required for threshold crossing  

---

### Cycle 107 — Competing propagation corridors (multi-stable activation)

**What was tested**
- whether introducing a **second coherent propagation corridor**:
  - phase-shifted relative to the original  
within an active system leads to:
  - collapse of activation  
  - dominance of one corridor  
  - or coexistence  

---

**What happened**

- **TU**
  - registered:
    - `competing_propagation_corridors`  
    - `dual_coherence_modes`  
    - `activation_interference_pattern`  
  - detected:
    - fragmentation of global coherence into two modes  
    - interference between corridors  
  - explicitly maintained:
    - no threshold reopening  
    - no activation collapse  

- **TU+**
  - maintained:
    - `activation_state` (dominant)  
  - confirmed:
    - both corridors remain active  
    - critical coupling is distributed  
    - system enters stable multi-mode condition  
  - rejected:
    - immediate collapse  
    - forced dominance  

- **cortexLLM**
  - classified regime as:
    - `multi_stable_activation_under_competing_propagation_corridors`  
  - established:
    - activation can support multiple coherent propagation modes  
    - interference patterns are stable structural features  
    - global coherence is partitioned but preserved  
  - confirmed:
    - system is **multi-stable**, not singular  

---

**Finding**

Cycle 107 demonstrates:

- activation state:
  - can sustain multiple propagation corridors  
  - can exhibit interference without collapse  
- critical coupling:
  - can be distributed across structures  
- system:
  - enters a **multi-stable activation regime**  

This establishes:

> **activation is not necessarily a single-mode state but can be multi-stable**

and:

> **coherent competition produces stable interference, not immediate collapse**

---

**Operational delta**

- state distinction added:
  - `multi_stable_activation_regime`  
    - defined as:  
      *a condition in which multiple coherent propagation corridors coexist, producing stable interference patterns while maintaining activation*  

- classification:
  - first multi-mode activation regime  

- invariants refined:
  - activation can distribute across multiple structures  
  - coherence can be partitioned without loss of activation  
  - interference does not imply instability or collapse  

---

### Cycle 108 — Asymmetric bias (weighted multi-stable activation)

**What was tested**
- whether introducing a **directional bias**:
  - favoring one propagation corridor (A)  
within a multi-stable activation regime leads to:
  - collapse to single mode  
  - elimination of competing corridor  
  - or weighted coexistence  

---

**What happened**

- **TU**
  - registered:
    - `biased_activation_state`  
    - `corridor_A_dominant`  
    - `corridor_B_subdominant`  
  - detected:
    - asymmetric feedback amplification  
    - gradual dominance shift toward corridor A  
  - explicitly maintained:
    - no threshold reopening  
    - no collapse  

- **TU+**
  - maintained:
    - `activation_state` (dominant)  
  - confirmed:
    - dominance becomes directional  
    - corridor B remains active but weakened  
    - interference becomes asymmetric  
  - rejected:
    - immediate elimination of corridor B  
    - forced single-mode resolution  

- **cortexLLM**
  - classified regime as:
    - `weighted_multi_stable_activation_under_asymmetric_bias`  
  - established:
    - activation supports **weighted distribution across modes**  
    - bias changes dominance, not existence  
    - global coherence remains intact  
  - confirmed:
    - system remains stable under directional skew  

---

**Finding**

Cycle 108 demonstrates:

- activation state:
  - supports directional bias  
  - allows one mode to dominate without eliminating others  
- multi-stability:
  - can become **weighted** rather than symmetric  
- system:
  - remains stable under asymmetric conditions  

This establishes:

> **activation supports weighted multi-stability, not only symmetric coexistence**

and:

> **bias modulates dominance but does not eliminate subdominant structures**

---

**Operational delta**

- state distinction added:
  - `weighted_activation_regime`  
    - defined as:  
      *a condition in which multiple propagation corridors persist with asymmetric dominance due to directional bias, while maintaining stable activation*  

- classification:
  - first weighted multi-mode activation regime  

- invariants refined:
  - activation can support directional dominance  
  - subdominant structures can persist under bias  
  - coherence is maintained under asymmetric distribution  

---

### Cycle 109 — Competitive rebalancing (dynamic multi-stable activation)

**What was tested**
- whether **reinforcing the subdominant corridor (B)**:
  - under an already biased activation regime  
leads to:
  - collapse  
  - reversal of dominance  
  - or dynamic equilibrium  

---

**What happened**

- **TU**
  - registered:
    - `dynamic_multi-stable_activation`  
    - `corridor_A_and_B_competitive_balance`  
    - `shifting_interference_pattern`  
  - detected:
    - increasing coupling strength of corridor B  
    - reduction of A’s dominance  
    - rebalancing of the system  
  - explicitly maintained:
    - no threshold reopening  
    - no collapse  

- **TU+**
  - maintained:
    - `activation_state` (dominant)  
  - confirmed:
    - dominance becomes dynamic, not fixed  
    - both corridors actively compete  
    - system avoids single-mode resolution  
  - rejected:
    - irreversible dominance  
    - elimination of corridor B  

- **cortexLLM**
  - classified regime as:
    - `dynamic_multi_stable_activation_under_competitive_rebalancing`  
  - established:
    - dominance becomes **time-varying**  
    - interference patterns become dynamic  
    - system exhibits **dynamic equilibrium**  
  - confirmed:
    - global coherence persists under competition  

---

**Finding**

Cycle 109 demonstrates:

- activation state:
  - supports **dynamic rebalancing** between competing structures  
  - allows dominance to shift over time  
- system:
  - maintains coherence under active competition  
  - does not collapse into a single mode  

This establishes:

> **activation can host dynamic multi-stable regimes with time-varying dominance**

and:

> **competition between structures leads to dynamic equilibrium, not instability**

---

**Operational delta**

- state distinction added:
  - `dynamic_equilibrium_activation_regime`  
    - defined as:  
      *a condition in which competing propagation corridors continuously rebalance, producing time-varying dominance while maintaining stable activation*  

- classification:
  - first dynamic equilibrium activation regime  

- invariants refined:
  - dominance is not fixed but dynamically adjustable  
  - activation supports continuous structural reconfiguration  
  - global coherence is preserved under competitive rebalancing  

---


