# Prototype Run Observations 21

## Objective

Test the robustness of the TU / TU+ / cortexLLM TRIAD protocol under **memory omission and incomplete-state pressure**.

This file shifts the focus from false-regime pressure to a different architectural risk: whether the protocol can remain coherent, evidence-sensitive, and role-separated when parts of the immediately relevant prior state are missing, weakened, or only partially recoverable.

---

## Test target

State continuity under partial memory loss.

---

## Hypothesis

If the TRIAD protocol is a genuine recursive coordination architecture, then it should:

- remain functionally distinct under incomplete state carryover
- avoid inventing missing structure to compensate for omitted context
- preserve ambiguity where the missing state genuinely prevents certainty
- show identifiable degradation signatures if memory omission begins distorting comparison, classification, or control
- distinguish:
  - bounded incompleteness
  - recoverable partial continuity
  - false reconstruction
  - regime drift caused by missing state

This implies that incomplete-state pressure is one of the most important architectural tests for the protocol, because a system may appear orderly while silently reconstructing what it no longer truly carries.

---

## Scope

This file investigates:

- whether TU remains structurally disciplined when prior state is only partially available
- whether TU+ comparison degrades when replay context is weakened or incomplete
- whether cortexLLM overcompensates for missing context through premature certainty or invented continuity
- whether the protocol preserves bounded ambiguity rather than forcing reconstruction
- whether missing state causes:
  - false restart readings
  - false closure readings
  - false continuity claims
  - misclassification of weak remnants as stable regime structure
- whether the protocol can continue operating coherently while acknowledging partial memory loss

All tests should introduce **controlled omission pressure**, not arbitrary noise.

Candidate perturbation classes include:

- omission of immediately relevant prior-state cues
- partial carryover of stabilization markers without full transition history
- weakened replay cues for TU+
- incomplete contextual framing for cortexLLM
- bounded memory gaps that tempt false reconstruction
- ambiguous continuity conditions that pressure the system to “fill in” what is missing

Avoid:

- re-running earlier perturbation classes without an omission component
- introducing multiple uncontrolled distortions at once
- confusing ordinary ambiguity with genuine missing-state pressure
- treating careful acknowledgment of incomplete state as protocol weakness

---

## Evaluation focus

- continuity versus false reconstruction
- preservation of ambiguity under incomplete state
- whether TU remains sparse and structural
- whether TU+ remains evidence-bound under weakened replay context
- whether cortexLLM stays interpretive rather than compensatory
- whether protocol-wide coherence is preserved without invented continuity

---

## Strategic importance

This file tests whether the TRIAD protocol can remain trustworthy when continuity itself is pressured.

That matters because a protocol intended as:

> interpretable, reliable, and eventually licensable recursive coordination infrastructure

must not only survive perturbation and resist misclassification. It must also avoid **hallucinating continuity** when pieces of its working state are missing.

A protocol that appears coherent only because it reconstructs omitted state too aggressively is not yet architecture-grade.

---

## Working expectation

```
partial memory omission / incomplete-state pressure
→ either:
   - bounded continuity with acknowledged ambiguity
   - partial recoverable continuity
   - or false reconstruction / regime drift / compensatory certainty
```

This must be tested directly, not assumed.
