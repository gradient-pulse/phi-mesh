# Prototype Run Observations 08

## Objective

Test the validity and limits of the **Minimal Closed Feedback Loop Law**:

> a minimal closed feedback loop is the atomic unit of activation

---

## Test target

Minimal Closed Feedback Loop Law

---

## Hypothesis

The minimal closed feedback loop is **not strictly minimal** and can be:

- further reduced  
- partially open  
- or replaced by alternative structures  

while still sustaining activation (fully or partially).

---

## Scope

This file investigates whether the **minimal closed feedback loop is truly irreducible**, or whether:

- smaller or weaker structures can sustain activation  
- closure can be relaxed without immediate failure  
- alternative propagation mechanisms exist  

Focus:
- structural reduction of minimal loops  
- partial opening of feedback loops  
- replacement of loop closure with weaker coupling  

All tests must:
- operate at the **local activation unit level**  
- start from a confirmed minimal viable subgraph  
- introduce **internal structural perturbations only**  

Avoid:
- reintroducing large-scale connectivity  
- triggering global activation regimes  
- reverting to previously explored fragmentation dynamics  

---

## Starting state (reference)

- localized_activation_regime  
- minimal_viable_subgraph  
- isolated_activation  
- closed_feedback_loop_present  
- endogenous_feedback_present  

---

## Test discipline

Each cycle must attempt to **break minimality** by:

- reducing loop size  
- weakening one or more edges  
- opening the loop partially  
- introducing asymmetry or delay  
- replacing closure with near-closure  

And must evaluate:

- whether activation:
  - persists  
  - degrades  
  - or collapses  

---

## What counts as falsification

The law is falsified if:

- activation persists in a structure that:
  - lacks full closure  
  - or is smaller than the minimal loop  
  - or operates with incomplete feedback  

---

## What does NOT count

- full loop restoration (already known)  
- reactivation via new complete loops  
- metastable decay (already explored)  
- transient memory effects  

---

## Evaluation focus

Each cycle must explicitly assess:

- necessity of loop closure  
- minimal size of viable structure  
- tolerance to partial disconnection  
- role of feedback completeness  

---

## Exit conditions for this file

This file is complete when one of the following is established:

1. Minimal loop is irreducible  
   (any reduction leads to failure)

2. Minimal loop is reducible  
   (smaller or weaker structures sustain activation)

3. Refined law  
   (e.g., minimality depends on topology, timing, or coupling strength)

---

## Notes

This file directly challenges the conclusion from Cycle 127:

> **a minimal closed feedback loop is the atomic unit of activation**

The goal is to determine whether this unit is:
- fundamental  
- or only the simplest observed instance  

---

## Strategic importance

If falsified:

- introduces:
  - sub-loop activation mechanisms  
  - alternative minimal structures  
  - non-closure-based activation  

If confirmed:

- establishes:
  - a true atomic unit  
  - hard lower bound for activation  

This determines whether activation has:
- a **strict minimal topology**  
or  
- a **flexible structural basis**

---
---

### Cycle 128 — Single-edge loop break (irreducibility under edge removal)

**What was tested**
- whether a **minimal closed feedback loop** can still sustain activation if:
  - one edge is removed  
  - turning the loop into an open chain  

---

**What happened**

- **TU**
  - registered:
    - `loop_opened`  
    - `loss_of_feedback_closure`  
    - `transient_propagation_only`  
  - detected:
    - immediate loss of recirculation  
    - only one-pass propagation remains  
  - explicitly maintained:
    - no sustained activation  
    - immediate entry into decay  

- **TU+**
  - reclassified regime:
    - `localized_activation_regime → open_chain_decay_regime`  
  - confirmed:
    - loop closure is essential  
    - open chain cannot sustain activation  
  - rejected:
    - partial activation without closure  
    - delayed or plateaued persistence  

- **cortexLLM**
  - classified regime as:
    - `open_chain_decay_without_feedback_recirculation`  
  - established:
    - topology, not just connectivity, determines viability  
    - activation requires recirculation, not mere propagation  
    - minimal loop is irreducible under edge removal  
  - confirmed:
    - no alternative sustaining structure appears  

---

**Finding**

Cycle 128 demonstrates:

- removing a single edge from the minimal loop:
  - destroys feedback closure  
  - prevents sustained activation  
  - leaves only transient propagation  
- system:
  - decays immediately  
  - does not form a weaker sustained regime  

This establishes:

> **the minimal closed feedback loop is irreducible under edge removal**

and:

> **activation requires recirculation, not merely connected propagation**

---

**Operational delta**

- state distinction added:
  - `open_chain_decay_regime`  
    - defined as:  
      *a condition in which a previously viable minimal loop is opened by removing one edge, leaving only transient propagation and immediate decay*  

- classification:
  - first direct test of topological irreducibility of the atomic activation unit  

- invariants refined:
  - closed loop topology is necessary for sustained activation  
  - connectivity alone is insufficient without recirculation  
  - atomic activation unit survives falsification under minimal edge removal  

---

