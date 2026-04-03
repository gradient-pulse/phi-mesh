# Prototype Run Observations 07

## Objective

Test the validity and limits of the **Binary Local Viability Law** derived from the Connectivity falsification.

---

## Test target

Binary Local Viability Law

---

## Hypothesis

Activation viability at the local scale is not strictly binary, but can exist in a **sub-threshold, partially active or metastable regime**, where connectivity is insufficient for full activation yet does not immediately extinguish dynamics.

---

## Scope

This file investigates whether **activation truly behaves as a binary phenomenon at the local level**, or whether there exists an intermediate regime between:

- fully active (above connectivity threshold)  
- fully inactive (below threshold)  

Focus:
- behavior of fragments **just below connectivity threshold**  
- existence (or non-existence) of:
  - partial activation  
  - metastable dynamics  
  - decaying but persistent local activity  

All tests must:
- operate within previously established fragmented regimes  
- target **near-threshold fragments** specifically  
- introduce **internal structural perturbations only**  

Avoid:
- immediate full disconnection of all fragments  
- reintroduction of global connectivity  
- previously confirmed collapse pathways  

---

## Starting state (reference)

- fragmented_activation_regime  
- thresholded_fragmented_activation_regime  
- sparse_activation_distribution  
- minimal_connectivity_fragments  
- endogenous_feedback_present  

---

## Test discipline

Each cycle must:

- push fragments:
  - slightly below connectivity threshold  
  - or oscillating around threshold  

- explicitly test for:

  - persistence of:
    - weak propagation  
    - incomplete feedback loops  
    - decaying activation  

  - existence of:
    - metastable or transient regimes  
    - partial coherence without full activation  

- evaluate whether:

  - activation:
    - persists in degraded form  
    - decays gradually  
    - or extinguishes immediately  

---

## What counts as falsification

The Binary Local Viability Law is falsified if:

- fragments below connectivity threshold:
  - retain measurable propagation  
  - sustain feedback loops (even weakly)  
  - exhibit delayed extinction  

---

## What does NOT count

- fully active fragments above threshold  
- immediate collapse below threshold (already confirmed)  
- trivial oscillations caused by re-crossing threshold  
- reactivation due to structural recoupling  

---

## Evaluation focus

Each cycle must explicitly assess:

- existence of sub-threshold dynamics  
- continuity vs discreteness of activation  
- time behavior:
  - immediate vs delayed extinction  
- structural requirements for sustained activity  

---

## Exit conditions for this file

This file is complete when one of the following is established:

1. Binary Local Viability holds strictly  
   (no sub-threshold persistence exists)

2. Binary Local Viability fails  
   (sub-threshold metastable activation exists)

3. Refined law  
   (e.g., time-dependent or probabilistic viability threshold)

---

## Notes

This file directly challenges the conclusion from Observations 06:

> **activation viability is binary at local scale**

The goal is to determine whether this is:
- a strict law  
- or an approximation of a more nuanced regime  

---

## Strategic importance

If falsified:

- activation is not purely discrete  
- introduces:
  - metastability  
  - temporal dynamics  
  - graded behavior near threshold  

If confirmed:

- strengthens:
  - quantized activation model  
  - sharp boundary conditions  
  - discrete regime transitions  

This test determines whether the system behaves like:
- a **binary switch**  
or  
- a **near-threshold dynamical system**

---
---

### Cycle 125 — Near-threshold metastability (sub-threshold transient activation)

**What was tested**
- whether **slightly sub-threshold connectivity**:
  - leads to immediate extinction (binary behavior)  
  - or allows transient, decaying activity  

---

**What happened**

- **TU**
  - registered:
    - `transient_sub-threshold_activity`  
    - `incomplete_feedback_loops`  
    - `gradual_decay_dynamics`  
  - detected:
    - residual propagation below threshold  
    - persistence of weakened, incomplete feedback  
  - explicitly maintained:
    - no immediate local collapse  
    - activity decays over time  

- **TU+**
  - maintained:
    - `sub-threshold_dynamics` (dominant)  
  - confirmed:
    - activity persists transiently below threshold  
    - decay rate depends on depth below threshold  
    - system exhibits metastability  
  - rejected:
    - strict binary switching  
    - immediate extinction  

- **cortexLLM**
  - classified regime as:
    - `metastable_sub-threshold_activity_with_time-dependent_decay`  
  - established:
    - activation below threshold is **transient, not stable**  
    - decay is inevitable without recoupling  
    - viability includes a temporal dimension  
  - confirmed:
    - system is not strictly binary  

---

**Finding**

Cycle 125 demonstrates:

- local connectivity threshold:
  - does not define **instantaneous existence**  
  - defines **stability vs decay**  
- activation below threshold:
  - can persist transiently  
  - decays over time  
- system:
  - exhibits **metastable sub-threshold dynamics**  

This establishes:

> **activation viability is not strictly binary but time-dependent near threshold**

and:

> **sub-threshold activity is transient and decay-bound, not immediately extinguished**

---

**Operational delta**

- state distinction added:
  - `metastable_sub-threshold_activation_regime`  
    - defined as:  
      *a condition in which activation persists transiently below connectivity threshold through incomplete feedback loops and decays over time without recoupling*  

- classification:
  - first successful falsification of Binary Local Viability Law  

- invariants revised:
  - connectivity threshold defines stability, not instantaneous existence  
  - activation viability includes a temporal dimension  
  - decay replaces immediate extinction near threshold

---

### Cycle 126 — Sustained sub-threshold dynamics (decay without plateau)

**What was tested**
- whether **keeping fragments slightly below connectivity threshold for extended duration**:
  - allows a stable sub-threshold regime to form  
  - or leads only to delayed extinction  

---

**What happened**

- **TU**
  - registered:
    - `irreversible_decay_dynamics`  
    - `no_metastable_plateau`  
    - `asymptotic_extinction`  
  - detected:
    - residual propagation continuing temporarily  
    - continued weakening of incomplete feedback loops  
  - explicitly maintained:
    - no spontaneous recovery  
    - no stabilization of sub-threshold activity  

- **TU+**
  - maintained:
    - `decay_dynamics` (dominant)  
  - confirmed:
    - activity decays monotonically  
    - no time-independent metastable plateau appears  
    - extinction is the limit of the process  
  - rejected:
    - stable sub-threshold activation  
    - recurrent or oscillatory sub-threshold persistence  

- **cortexLLM**
  - classified regime as:
    - `sub-threshold_decay_regime_with_no_stable_metastability`  
  - established:
    - sub-threshold activity is **history-dependent residue**, not a new stable state  
    - incomplete feedback loops cannot self-close  
    - extinction is asymptotic but inevitable without recoupling  
  - confirmed:
    - no stable metastable regime exists below threshold  

---

**Finding**

Cycle 126 demonstrates:

- sub-threshold activity:
  - can persist transiently  
  - cannot stabilize indefinitely  
  - decays monotonically toward extinction  
- the system:
  - does not form a true below-threshold plateau  
  - retains only fading memory of prior activation  

This establishes:

> **sub-threshold activity is transient memory, not a self-sustaining regime**

and:

> **metastability below threshold is time-limited and decay-bound, not indefinitely stable**

---

**Operational delta**

- state distinction added:
  - `decay_only_sub-threshold_regime`  
    - defined as:  
      *a condition in which below-threshold activity persists only as monotonic, history-dependent decay and cannot form a stable or plateaued metastable state without recoupling*  

- classification:
  - closure of the Binary Local Viability falsification thread  

- invariants revised:
  - sub-threshold viability is temporal but not indefinite  
  - stable activity requires closed feedback loops  
  - below-threshold dynamics are residual, not self-sustaining  

---

### Cycle 127 — Local reactivation (minimal viable unit)

**What was tested**
- whether **activation can reappear**:
  - after full extinction  
  - via minimal local recoupling  
and whether this requires:
  - global connectivity  
  - or only local structural closure  

---

**What happened**

- **TU**
  - registered:
    - `local_reactivation`  
    - `minimal_viable_subgraph`  
    - `isolated_activation`  
  - detected:
    - formation of a minimal closed feedback loop  
    - local propagation restored within that loop  
  - explicitly maintained:
    - no global reintegration  
    - no spread beyond local structure  

- **TU+**
  - confirmed transition:
    - `post_activation_state → localized_activation_state`  
  - verified:
    - activation reappears immediately once local threshold is exceeded  
    - reactivation is strictly confined to the recoupled subgraph  
  - rejected:
    - need for global connectivity  
    - spontaneous expansion  

- **cortexLLM**
  - classified regime as:
    - `localized_reactivation_via_minimal_closed_feedback_loop`  
  - established:
    - a **single closed feedback loop is sufficient for activation**  
    - this loop is the **minimal viable unit**  
    - activation does not propagate without additional coupling  
  - confirmed:
    - reactivation is local, bounded, and structural  

---

**Finding**

Cycle 127 demonstrates:

- activation:
  - can be reinitiated locally after full extinction  
  - requires only a **minimal closed feedback loop**  
- system:
  - does not require global structure for reactivation  
  - does not spontaneously scale from minimal units  
- structure:
  - defines a smallest viable unit of activation  

This establishes:

> **a minimal closed feedback loop is the atomic unit of activation**

and:

> **activation is locally constructible and globally composable**

---

**Operational delta**

- state distinction added:
  - `localized_reactivation_regime`  
    - defined as:  
      *a condition in which activation reappears within an isolated subgraph that satisfies minimal connectivity requirements, without requiring global reintegration*  

- classification:
  - first identification of atomic activation unit  

- invariants refined:
  - activation requires closed feedback loops  
  - minimal loop defines viability threshold  
  - global activation is an aggregate of local units  

---

## Guidance

👉 **No additional cycles are needed for this falsification thread.**

You now have a complete closure:

- connectivity:
  - global → not required  
  - local → required above threshold  
- viability:
  - not binary → time-dependent near threshold  
  - but stability → binary  
- extinction:
  - exact at last viable unit  
- reactivation:
  - occurs via minimal closed loop  
  - defines atomic unit  

---

## What this means

You have fully mapped:

```text
activation existence ↔ local closed feedback loops
