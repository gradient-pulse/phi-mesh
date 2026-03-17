# Proto Temporal Unit Build Plan

## Purpose

This note defines the first practical build plan for the proto temporal unit described in:

- `experiments/pre_metric_extensions/proto_temporal_unit.md`

Its purpose is not to hard-code the final temporal-unit architecture.

Its purpose is to define:
- what must stay stable
- what may vary
- what toy environments should be used
- how Codex should build the first scaffold
- how iterative runs should converge toward a better design

The central principle is:

> Codex should not be asked to invent the temporal unit from scratch. It should be asked to build the smallest experimental arena in which candidate temporal-unit rules can vary, run, be scored, and be revised.

---

## Build philosophy

The proto temporal unit should be developed in the same spirit that makes LLMs powerful:
- simple process elements
- repeated local updates
- emergent higher-order behavior

This means the first implementation should avoid:
- premature formal closure
- large monolithic design
- direct coding of high-level intelligence concepts
- hard-coded final equations for Φ, resonance, or choreography

Instead, the first prototype should:
- preserve the stable architectural intuition
- expose uncertain elements as tunable parameters
- run small toy cases
- record what happens
- and let repeated runs reveal better local rules

---

## Stable principles

The following principles should remain fixed unless strong evidence suggests otherwise.

### S-01 — Clocked corridor
Every task arrival and every subsequent event must be clocked into a case corridor.

### S-02 — Minimal event ledger
Events should remain minimally specified historical occurrences.

### S-03 — Unique longitudinal choreography strings
Each choreography string is a unique longitudinal family of events.

### S-04 — Simultaneity families
Cross-choreography coupling occurs through simultaneity or near-simultaneity, not by treating events as belonging to many strings.

### S-05 — Dynamic replay
New events trigger replay of their associated choreography string.

### S-06 — Spread through simultaneity
Replay can activate other strings through simultaneity families.

### S-07 — Dynamic swarm state
Weights, activeness, resonance, and field structure are generated dynamically at the present clock instant rather than stored as fixed event labels.

### S-08 — Coherence-sensitive cutoff
Broad replay should stop when a sufficiently stable coherence basin forms.

### S-09 — LLM as interpreter
The temporal unit maintains the active field; the LLM interprets and articulates it.

These are the design anchors.

---

## Variable parameters

The following should be treated as exploration points, not fixed truths.

### V-01 — Event-to-string attachment rule
How strongly a new event attaches to an existing choreography string versus starting a new one.

### V-02 — Simultaneity window
How close in time two events must be to count as simultaneous.

### V-03 — Decay rate
How quickly event relevance fades without reinforcement.

### V-04 — Reinforcement gain
How much replay or simultaneity boosts event or string significance.

### V-05 — Spread depth
How many simultaneity-linked strings can be activated before replay stops broadening.

### V-06 — Cutoff threshold
What counts as a sufficient coherence plateau for stopping broad replay.

### V-07 — Weight composition
How longitudinal persistence and simultaneity breadth combine into event or string weight.

### V-08 — Action-mode mapping
How the active field maps to:
- `observe`
- `clarify`
- `patch`
- `rebuild`
- `act`
- `hold`

### V-09 — Number of clocks / slices
How many temporal slices are actually useful in a proto version.

### V-10 — Source back-reference usage
How much source information should be retained for action-grounding without overwhelming the choreography logic.

These parameters should be exposed through a config file rather than buried in code.

---

## Minimum scaffold Codex should build

The first Codex implementation should build the smallest runnable scaffold with the following elements.

### 1. Event schema
A compact schema for incoming events.

Suggested fields:
- `event_id`
- `case_id`
- `arrival_tick`
- `source_channel`
- `event_type`
- `content_summary`
- optional `payload_strength`

### 2. Swarm-state schema
A present-state structure containing:
- active events
- choreography strings
- simultaneity families
- event weights
- dominant basin
- unresolved tensions
- plateau state

### 3. Config file
A config file for tunable parameters.

Suggested name:
- `proto_temporal_unit_config.yml`

This should hold:
- simultaneity window
- decay factor
- reinforcement factor
- spread depth
- cutoff threshold
- action-mode thresholds

### 4. Toy simulation engine
A simple simulation loop that:
- clocks events
- attaches them to strings
- forms simultaneity families
- replays strings
- spreads activation
- updates weights
- checks cutoff
- emits an interpretable state summary

### 5. Toy cases
At least 2 or 3 very small cases.

### 6. Output report
Each run should produce:
- event log
- active choreography summary
- simultaneity summary
- cutoff status
- recommended mode
- short evaluation metrics

---

## Toy cases for version 1

Use narrow, interpretable cases only.

### Case A — Document repair
Domain:
document/file repair

Goal:
test whether contamination, replay, and rebuild pressure become visible.

Example event types:
- `task_arrival`
- `instruction_received`
- `clarification_received`
- `patch_attempt`
- `duplication_detected`
- `stale_remnant_detected`
- `evidence_mismatch_detected`
- `coherence_restored`

Likely choreography strings:
- `contamination_rising`
- `coherence_restoration`
- `target_unclear`
- `patch_overreach`
- `rebuild_readiness`

### Case B — Sensor interruption
Domain:
simple multimodal interruption

Goal:
test whether simultaneous sensor-linked events create stronger coupling than isolated ones.

Example event types:
- `visual_change`
- `auditory_alert`
- `touch_signal`
- `context_shift`
- `response_commit`

Likely choreography strings:
- `environmental_shift`
- `urgent_interrupt`
- `stabilization`

### Case C — Narrative / plan drift
Domain:
small task plan

Goal:
test whether longitudinal drift can be detected and whether replay finds the divergence point.

Example event types:
- `goal_set`
- `subtask_started`
- `constraint_change`
- `detour`
- `goal_conflict`
- `replan`

Likely choreography strings:
- `goal_progress`
- `constraint_intrusion`
- `reorientation`

These cases should remain small enough that humans can inspect every step.

---

## Iteration protocol

The build should follow a bounded recursive loop.

### Step 1 — Implement minimal scaffold
Build the smallest runnable version consistent with the stable principles.

### Step 2 — Run toy cases
Use fixed cases so results are comparable.

### Step 3 — Score outcome
Measure:
- replay behavior
- simultaneity coupling
- cutoff timing
- coherence stability
- action-mode suggestion quality

### Step 4 — Identify failure mode
Do not immediately redesign globally.
Name the failure mode precisely.

### Step 5 — Change one or two things only
Adjust:
- one parameter
or
- one local rule

Avoid changing many things at once.

### Step 6 — Run again
Compare with previous run.

### Step 7 — Keep, reject, or defer
Retain only changes that improve the case behavior without obvious degradation elsewhere.

Strong formulation:

> The temporal unit should be improved by bounded recursive variation inside a stable design basin, not by unconstrained reinvention each round.

---

## Evaluation criteria

The first prototype should not be judged by whether it is “intelligent” in a grand sense.

It should be judged by whether it exhibits the beginnings of the right behavior.

### E-01 — Event clocking integrity
Does it create a coherent corridor from task arrival onward?

### E-02 — Longitudinal string formation
Do unique choreography strings emerge in a stable and interpretable way?

### E-03 — Simultaneity coupling
Do simultaneous or near-simultaneous events create meaningful cross-string coupling?

### E-04 — Replay usefulness
Does replay help interpret new events through prior unfolding rather than flat presentism?

### E-05 — Cutoff quality
Does the system avoid both:
- endless replay
- premature collapse

### E-06 — Case interpretability
Can a human inspect the run and understand why the current basin became dominant?

### E-07 — Action-mode plausibility
Does the handoff suggest a plausible mode such as:
- `clarify`
- `patch`
- `rebuild`
- `hold`

### E-08 — Coherence preservation
Does the active field seem to preserve or restore coherence under novelty, rather than merely amplifying noise?

---

## Failure conditions to watch for

The first prototype may fail in many ways. Codex should explicitly watch for these.

### F-01 — String explosion
Too many choreography strings created too easily.

### F-02 — String collapse
Everything gets forced into one string too quickly.

### F-03 — Spurious simultaneity spread
Too many unrelated strings activate due to loose simultaneity windows.

### F-04 — Replay lock
The system keeps replaying without reaching usable cutoff.

### F-05 — Premature cutoff
The system stabilizes before enough relevant coupling has formed.

### F-06 — Static presentism
The system behaves as if only the latest event matters.

### F-07 — Source overload
Too much source detail overwhelms choreography-role formation.

### F-08 — Action arbitrariness
The suggested output mode is unstable or poorly grounded.

These should be recorded per run.

---

## What Codex should not do

Codex should not:

- invent a brand-new architecture outside the stable principles
- over-formalize Φ too early
- hard-code a final resonance equation
- simulate biology too literally
- build a large framework before toy cases work
- optimize many parameters at once
- treat unresolved exploration points as settled truth

In short:

> Build the smallest experimental arena first. Do not jump to the finished organism.

---

## Recommended first file set for Codex

The first build round should ideally create:

- `experiments/pre_metric_extensions/proto_temporal_unit_config.yml`
- `experiments/pre_metric_extensions/event_schema.md`
- `experiments/pre_metric_extensions/swarm_state_schema.md`
- `experiments/pre_metric_extensions/toy_temporal_unit_sim.py`
- `experiments/pre_metric_extensions/toy_cases/`
- `experiments/pre_metric_extensions/toy_cases/document_repair_case.yml`
- `experiments/pre_metric_extensions/toy_cases/sensor_interrupt_case.yml`
- `experiments/pre_metric_extensions/toy_cases/narrative_drift_case.yml`
- `experiments/pre_metric_extensions/evaluation_notes.md`

This is enough to begin real iterative work.

---

## Suggested Codex task style

Codex should be prompted with:
- stable principles
- explicit file targets
- one small build round at a time
- clear instructions to expose uncertainty as config rather than hard-coding it
- a requirement to report observed failure modes after each run

Good prompt principle:

> Treat unresolved design choices as variables to be explored by repeated runs, not as constants to be fixed upfront.

And another:

> Build the arena in which the temporal unit can begin to discover its best local rules.

---

## Strategic note

This build plan is not only a way to organize Codex. It is also a way to protect the branch from drifting into either:
- vague philosophy
or
- premature rigid engineering

It keeps the work in the right basin:
- conceptually grounded
- experimentally constrained
- recursively improvable

That is exactly what this stage requires.

---

## Immediate next step

Once this file is created, the next move is to task Codex for the first scaffold round:
- schemas
- config
- toy engine
- toy cases
- simple report output

Only after that first scaffold exists should parameter exploration begin.

---

## Closing statement

The proto temporal unit will not be discovered by declaring its final equations in advance.

It will be approached by:
- fixing a small set of stable principles
- letting uncertain quantities vary
- running simple cases
- observing where coherence is preserved or lost
- and iterating within a bounded swarm-like design space

This build plan exists to make that recursive convergence possible.
