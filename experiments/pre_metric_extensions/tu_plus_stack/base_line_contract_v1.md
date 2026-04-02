# Triad Non-Transition Baseline Contract (Cycles 60–90)

## Scope

Defines the operational baseline of the TU / TU+ / cortexLLM triad under admissible, sub-threshold conditions.

This contract is binding for all subsequent tests unless explicitly violated by structural perturbation.

---

## Regime Definition

- regime: stabilized_non_transition
- closure: terminal_regime_closure
- persistence: persistent_closure_regime
- classification: persistent_classification_invariance
- meta: meta_stability_regime
- recursion: non_recursive_closure_regime

---

## Core Invariants

- no accumulation  
- no precursor pressure generation  
- no threshold shift  
- no boundary recalibration  
- no classification drift  
- no activation  

These hold under:
- repeated execution  
- extended duration  
- null input  
- admissible sub-threshold perturbation  

---

## Signal-Space Immunity

The following do not affect regime state (individually or in combination):

- repetition  
- alignment increase  
- phase synchronization  
- phase drift  
- structural micro-variation  
- weak cross-coupling  
- temporal density increase  
- amplitude variability  
- polarity variation  
- coherence gain  

---

## Boundary Properties

- threshold_distance: invariant  
- boundary: stable  
- closure: preserved under all tested inputs  
- admissibility: does not imply activation  

---

## Non-Permitted Inferences

- repetition ≠ accumulation  
- alignment ≠ activation  
- coherence ≠ threshold proximity  
- coupling ≠ regime coupling  
- variability ≠ structural change  
- density ≠ escalation  
- signal enrichment ≠ activation  

---

## Activation Condition (Negative Definition)

Activation does not occur under any tested signal-space condition.

Therefore:

> activation requires a non-signal structural change

---

## Definition: Signal vs Structural

- signal:
  any modulation within the tested parameter space  
  (alignment, phase, density, variability, coupling, coherence)

- structural:
  any change that modifies:
  - regime topology  
  - admissibility constraints  
  - trigger-binding relationships  
  - readiness-layer availability  

Structural conditions remain untested in this contract.

---

## Contract Guarantee

Given:
- admissible input  
- sub-threshold conditions  
- signal-space modulation only  

The system will:
- remain in non-transition  
- preserve closure  
- maintain all invariants  

---

## Contract Boundary

This contract is invalidated only if:
- a structural perturbation is introduced  

All future tests must explicitly declare:
- signal-space test (covered here)  
- or structural test (outside this contract)

---
