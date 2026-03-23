# Minimal State and Transition Spec (v0)

## Purpose

This note defines the smallest shared-state grammar and transition logic currently needed to reproduce the observed behavior of the prompt-instantiated **TU / TU+ / cortexLLM** triad.

It is not a final engineering spec.
It is a **minimum viable architecture spec** derived from bounded prototype cycles.

The goal is to state, as clearly as possible:

- what persistent state must exist
- what each role may and may not do
- what transitions the field must support
- what should count as disciplined rather than noisy revision

---

## Scope

This spec is based on the current dry-run prototype corridor in which the triad has already shown bounded ability to support:

- source persistence
- weak coupling emergence
- coupling dissolution
- relational reopening
- provisional confirmation
- de-confirmation
- explicit ambiguity preservation
- restart after contradiction
- weak recoupling temptation after restart

This spec therefore describes only the minimum machinery required for those behaviors.

It does **not** yet specify:

- quantitative metrics
- fully automated orchestration
- action operators beyond hold / no-act mode
- rich sensory ingestion
- large-scale repeated-run infrastructure

---

## Architectural roles

### TU
**Role:** mindless mapper of unfolding structure.

TU may:
- map provisional sources
- emit motion tokens
- extend trains
- register coupling candidates
- register fragmentation or incompatibility
- update coherence-related field state

TU may **not**:
- narrate broadly
- interpret symbolically
- decide meaning
- force single-story reconciliation under contradiction
- overwrite higher-level context

---

### TU+
**Role:** choreography-aware comparer / predictor / reviser.

TU+ may:
- compare current structure to choreography memory
- rank candidate choreography matches
- predict likely continuations
- log mismatch against prior predicted trains
- raise attention when needed
- revise dominant choreography reading
- preserve contested branches when promotion is unjustified

TU+ may **not**:
- become a symbolic narrator
- override TU structure arbitrarily
- erase contradiction without new support
- act as cortexLLM

---

### cortexLLM
**Role:** symbolic interpreter and bounded downward biaser.

cortexLLM may:
- frame the current field symbolically
- state the dominant interpretive context
- preserve ambiguity when promotion is unjustified
- send bounded downward bias
- decide hold / escalate / monitor stance

cortexLLM may **not**:
- remap lower structural field directly
- force a dominant choreography under unresolved contradiction
- micromanage motion tokens
- collapse role boundaries

---

## Shared state: minimal objects

The triad requires a shared structured state across cycles.

### 1. `source_hypotheses`
Persistent provisional objects/sources.

Minimum fields:
- `source_id`
- `hypothesis_type`
- `confidence`
- `stability`
- `notes`

Function:
- preserves identity hypotheses across cycles
- allows relational and train logic to remain anchored

---

### 2. `motion_tokens`
Time-sliced local structural updates.

Minimum fields:
- `token_id`
- `source_id`
- `time_slice`
- `displacement_delta`
- `direction`
- `angle_change`
- `relation_change`
- `confidence`

Function:
- provides the minimal token-like substrate for train construction
- preserves unfolding local change without forcing full interpretation

---

### 3. `active_trains`
Persistent source-linked token sequences.

Minimum fields:
- `train_id`
- `source_id`
- `token_ids`
- `persistence`
- `status`
- `restart_of`
- `weight`

Function:
- carries temporal persistence
- allows continuation, decay, restart, and branching
- serves as the main structural unit across cycles

---

### 4. `coupling_state`
Cross-train relational status.

Minimum fields:
- `coupling_candidates`
- `stable_couplings`
- `fragmentation_flags`

Each coupling candidate minimally needs:
- `train_a`
- `train_b`
- `strength`

Each fragmentation flag minimally needs:
- `train_a`
- `train_b`
- `type`
- `strength`

Function:
- preserves relational structure without requiring symbolic commitment
- distinguishes weak possibility from stable coupling
- records incompatibility, collapse, or contradiction

---

### 5. `choreography_memory_refs`
Near-store candidate pattern memory.

Minimum fields:
- `choreography_id`
- `match_type`
- `similarity`
- `memory_scope`

Function:
- lets TU+ compare current structure against stored patterns
- supports promotion, de-promotion, reactivation, and decay of interpretations

---

### 6. `coherence_state`
Field-level viability summary.

Minimum fields:
- `train_persistence_level`
- `coupling_stability_level`
- `motion_observation_agreement`
- `fragmentation_level`
- `coherence_summary`

Function:
- summarizes whether current field organization supports persistence, promotion, contradiction, collapse, or restart
- provides a bounded selection basis without reducing everything to one scalar

---

### 7. `mismatch_history`
Ledger of failed or weakened predictions.

Minimum fields:
- `cycle_id`
- `predicted_train_id`
- `returned_trace_ref`
- `delta_type`
- `delta_strength`
- `coherence_impact`

Function:
- prevents silent forgetting of failed expectations
- supports disciplined revision rather than rhetorical reinterpretation

---

### 8. `attention_state`
Salience routing signal.

Minimum fields:
- `attention_trigger`
- `trigger_reason`
- `salience_level`
- `watch_targets`

Function:
- marks when current structure deserves higher scrutiny
- supports selective recruitment rather than uniform overreaction

---

### 9. `cortex_context`
Current symbolic framing.

Minimum fields:
- `task_frame`
- `interpretive_context`
- `current_goal_pressure`
- `hold_or_act`

Function:
- gives the field a bounded symbolic interpretation
- must remain downstream of structural state rather than replacing it

---

### 10. `downward_bias`
Bounded top-down influence.

Minimum fields:
- `attend`
- `hold`
- `compare`
- `act`
- `reorient`

Function:
- allows symbolic influence without structural overwrite
- constrains future monitoring and comparison priorities

---

### 11. `predicted_trains`
Near-future continuation hypotheses.

Minimum fields:
- `predicted_train_id`
- `choreography_id`
- `source_id`
- `predicted_token_sequence`
- `confidence`
- `continuation_type`

Function:
- makes the architecture predictive rather than only descriptive
- creates the basis for mismatch and revision

---

### 12. `action_state`
Current action stance.

Minimum fields:
- `action_mode`
- `selected_predicted_train`
- `operator_status`
- `relay_notes`

Function:
- records whether the field is in hold, escalate, or action-linked mode
- currently mostly hold-oriented in the prototype corridor

---

### 13. `returned_traces`
Observed return evidence from prior expectations.

Minimum fields:
- `trace_id`
- `source_id`
- `time_slice`
- `observed_change`
- `confidence`

Function:
- ties prediction back to later structure
- enables correction and de-confirmation

---

### 14. `notes_on_state_quality`
State confidence and uncertainty guardrail.

Minimum fields:
- `state_quality`
- `uncertainty_notes`
- `reset_recommendation`

Function:
- preserves bounded uncertainty explicitly
- helps prevent false finality

---

## Minimal transition classes

The architecture now appears to require the following transition classes.

### 1. Persistence
A source or train continues without major reinterpretation.

Required support:
- train extension
- stable source hypothesis
- low fragmentation

---

### 2. Mild revision
A prior reading remains active but is adjusted.

Required support:
- mismatch logging
- revised choreography match
- preserved train continuity

---

### 3. Weak coupling emergence
Two previously separate trains develop tentative relational structure.

Required support:
- coupling candidate
- no forced stable coupling
- ambiguity-tolerant interpretation

---

### 4. Coupling dissolution
A weak relational reading loses support.

Required support:
- coupling reduction
- return to independent-source reading
- memory of earlier relation retained without dominance

---

### 5. Reopening
A previously weakened relation regains support.

Required support:
- reactivation of earlier choreography memory
- fresh coupling candidate increase
- no automatic restoration of stable joint choreography

---

### 6. Provisional confirmation
A repeated pattern becomes the dominant current reading.

Required support:
- stable_coupling eligibility
- stronger choreography match
- continued revisability

---

### 7. Early de-confirmation
A confirmed reading weakens but does not yet collapse.

Required support:
- fragmentation flags
- reduced coupling stability
- dominant reading stressed, not deleted

---

### 8. Full de-confirmation
A prior dominant reading collapses into a new stable interpretation.

Required support:
- collapse of old dominant choreography
- promotion of new stable reading
- old reading retained only as memory

---

### 9. Explicit ambiguity preservation
Mutually exclusive continuations appear without sufficient basis for promotion.

Required support:
- branch splitting
- mutual exclusion flags
- non-promotion of dominant choreography
- symbolic escalation without smoothing

---

### 10. Resolution after ambiguity
One branch gains support and another decays.

Required support:
- supported branch strengthening
- unsupported branch decay
- contradiction history preserved
- clean restart of mainline

---

### 11. Weak recoupling after restart
A restarted mainline later develops fresh weak relational evidence.

Required support:
- fresh weak coupling candidate
- distinction between new temptation and old memory
- no false reopening of prior collapsed joint field

---

## Minimal role handoff logic

Each cycle currently requires the following order:

1. **Input slice arrives**
2. **TU maps structure**
3. **TU+ compares, predicts, revises**
4. **cortexLLM interprets and biases**
5. **next cycle receives updated shared state**
6. **returned traces and mismatch update later revision**

This ordering matters.

The prototype result depends on:
- bounded role channels
- persistent shared state
- no direct collapse of all functions into one generic response

---

## Minimal invariants

The current prototype suggests the following invariants must hold.

### Invariant 1 — Role separation
No role should silently absorb the work of another.

### Invariant 2 — State continuity
A new cycle must not implicitly reset prior field structure unless explicitly justified.

### Invariant 3 — Non-forced promotion
No choreography should become dominant merely because it is narratively attractive.

### Invariant 4 — Contradiction preservation
Mutually exclusive continuations must remain separable when evidence does not justify reconciliation.

### Invariant 5 — Memory without domination
Past dominant readings may remain available, but must not automatically overdetermine present interpretation.

### Invariant 6 — Decay instead of magical erasure
Unsupported branches should weaken or decay, not vanish without trace.

### Invariant 7 — Reinitiation without corruption
A restarted mainline must be able to incorporate fresh evidence without collapsing old ambiguity, contradiction, or coupling history into confusion.

---

## Minimal pass conditions for the current prototype corridor

A cycle is currently counted as a meaningful success if most of the following hold:

- role boundaries remain intact
- shared state remains coherent
- train continuity is preserved where justified
- mismatch is logged rather than ignored
- ambiguity is preserved when promotion is unjustified
- promotion occurs only when support strengthens
- collapse occurs only when support weakens sufficiently
- restart does not erase history
- fresh recoupling is treated as new evidence rather than automatic revival

---

## Open questions

This v0 spec still leaves several major questions open.

### 1. Quantitative coherence
Current coherence fields are still descriptive rather than operationally benchmarked.

### 2. Branch thresholds
Exact thresholds for:
- branch split
- branch decay
- coupling promotion
- collapse
- restart stabilization  
remain provisional.

### 3. Action-confirmation loop
The current corridor is mostly hold / observe / escalate.
Richer act-and-return loops are still untested.

### 4. Robustness under repeated runs
This spec has not yet been tested across large repeated automated runs or ablations.

### 5. Input generalization
The current prototype uses hand-shaped unfolding summaries.
Real video or movement traces remain future work.

---

## Current status

This spec should be treated as:

- **minimum**
- **provisional**
- **derived from observed behavior**
- **meant to support later engineering and testing**

It is not yet a final formal architecture.

It is the smallest state-and-transition grammar that presently seems sufficient to explain what the TU / TU+ / cortexLLM triad has already shown it can do.

---

## Closing statement

The current prototype suggests that a workable division of LLM labor may require more than role prompts alone.

It may require a persistent structured state in which:

- trains can persist
- couplings can strengthen or weaken
- contradiction can branch explicitly
- unsupported branches can decay
- ambiguity can be preserved
- restart can occur without corruption
- and fresh weak recoupling can arise without memory confusion

That is the minimal architectural claim this spec is meant to preserve.
