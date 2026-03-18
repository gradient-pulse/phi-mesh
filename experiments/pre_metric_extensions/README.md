# Pre-Metric Extensions

## Purpose

This branch explores a practical RGPx path toward future AI systems that do more than optimize locally over symbolic states.

The working claim is that the next meaningful extension of LLMs will not be another metric-scale attachment — longer context, larger memory, more retrieval, deeper verifier loops, or more tools — but a **pre-metric guidance layer** that shapes latent search before symbolic resolution.

This branch exists to make that claim testable.

---

## Why this branch exists

Recent work in the benchmark area exposed a recurring pattern:

- local instructions were often satisfied,
- but whole-object coherence repeatedly failed,
- stale remnants survived,
- duplication reappeared,
- and patch-style repair often replaced neither the object nor its morphology.

That pattern suggested a broader distinction between:

- **metric/local cognition** — explicit rule satisfaction, local repair, narrow optimization
- **pre-metric guidance** — whole-object fit, morphology-sensitive rebuild, longitudinal coherence, and sensitivity to constraint/gradient choreographies

This branch turns that distinction into an engineering program.

---

## Core hypothesis

A future RGPx-style system may require:

- whole-object fit before local patching
- emerging morphology as active context
- sensitivity to constraint/gradient choreographies
- sensitivity to the relations between choreographies
- translation of constraints into operative gradients
- stronger longitudinal guidance than current LLMs typically exhibit

A further working hypothesis is that such guidance may eventually require a **temporal unit** or **time-sensitive substrate** that lets gradients persist, interact, and organize into longitudinal choreographies across multiple temporal slices.

---

## Terminology clarification

In this branch, a few terms have a specific engineering meaning.

- **tick** = a local temporal update index used for participant/emission timing  
  It is **not** the same as o3’s stronger Narrative Tick notion, which marks larger irreversible structural turns or UD-relevant phase changes.

- **participant** = a vertical choreography, i.e. a temporally persistent local process

- **event / emission** = an observable output or trace emitted by a participant

- **horizontal family** = a same-time or near-time coupling episode among participants

- **coherence** = the degree to which participants synchronize into a viable common temporality

---

## What this branch is for

This branch is for:

- diagnosing present model failure modes
- defining proxy experiments
- testing rebuild-over-patch behavior
- specifying candidate pre-metric extensions
- exploring temporal and choreography-sensitive architectures
- turning conceptual RGPx claims into explicit engineering artifacts

It is not yet a full implementation branch. It is the place where the extension path is named, structured, tested, and made cumulative.

---

## Current files

### `2026-03-15_rgpx_llm_extension_roadmap.md`
The main program note for this branch.

It defines:
- the missing layer hypothesis
- why current extensions are mostly compensatory
- key design principles
- proxy experiment directions
- early architecture intuitions
- immediate next steps

### `failure_signatures.md`
A diagnostic ledger of recurring model failure patterns.

It treats failures not merely as mistakes, but as engineering clues indicating missing functions such as:
- whole-object fit
- morphology tracking
- rebuild-over-patch judgment
- longitudinal weighting
- topology-as-context feedback
- choreography sensitivity

### `proto_temporal_unit.md`
Core premise note for the temporal-unit path.

It defines:
- the temporal unit as a candidate time-sensitive substrate
- vertical choreographies and horizontal coupling
- why longitudinal guidance may be required for future AI agency
- the first engineering basin for a proto temporal unit

### `proto_temporal_unit_build_plan.md`
Stepwise build plan for the first proto temporal unit.

It defines:
- the order of implementation
- what to prototype first
- what to postpone
- how to keep the first basin small and inspectable

### `proto_temporal_unit_config.yml`
Initial tunable configuration for the toy temporal-unit prototype.

It currently holds parameters such as:
- simultaneity window
- decay
- spread gain
- replay gain
- coherence thresholds
- action mode thresholds

### `event_schema.md`
Minimal static ledger schema for event records.

It defines:
- what an event record must minimally contain
- how source traces can be preserved
- the separation between static event data and dynamic swarm interpretation

### `swarm_state_schema.md`
Runtime schema for the present-time swarm field.

It defines:
- active strings
- simultaneity families
- event weights
- dominant basin
- coherence score
- and mode suggestion output

### `toy_cases/document_repair_case.yml`
First toy corridor for inspecting temporal-unit behavior.

It provides:
- a short event stream
- clear contamination/recovery structure
- a manageable first case for testing vertical and horizontal coupling

### `toy_temporal_unit_sim.py`
Current toy simulator for the proto temporal unit.

It currently:
- loads the toy case and config
- maps events into vertical choreographies
- builds horizontal simultaneity families
- computes weights, coherence, and recommended mode
- exposes the current field in JSON form

### `toy_temporal_unit_visualize.py`
Minimal visualization script for the toy temporal unit.

It produces a static visual view of:
- vertical longitudinal strings
- horizontal simultaneity families
- event positions across ticks

### `swarm_participant_minimum.md`
Minimum ontology correction for swarm participants.

It establishes:
- participant = vertical choreography
- event/emission = participant output
- horizontal family = coupling episode
- coherence = viable common temporality among participants

### `emission_as_token_analogy.md`
Engineering bridge from the LLM path into the temporal-unit path.

It defines:
- participant emission as the closest analogue of the token
- vertical choreography as the persistent generator/process
- emission weight as arising from train persistence plus cross-train synchronization

### `swarm_participant_update_rule.md`
First code-facing local rule grammar for swarm participants.

It defines:
- participant state
- emission rule
- coupling rule
- weight update logic
- yield/restart logic
- local coherence update
- LLM-facing readout

### `robot_movement_data_test_plan.md`
First plan for testing the proto temporal unit on real robot movement data.

It defines:
- why robot movement traces are the right first external test
- what counts as participant and emission in that context
- how to compare trajectory/control descriptions with choreography descriptions
- what would count as first operational success

---

## Related dialogue notes

The conceptual development behind this branch is preserved in the dialogue archive.

Most relevant notes include:

- `dialogues/2026-03-15_pre_metric_guidance_constraint_choreography_dialogue.md`
- `dialogues/2026-03-16_temporal_unit_and_embedded_llm_dialogue.md`
- `dialogues/2026-03-17_temporal_unit_proto_and_ud_swarm_dialogue`
- `dialogues/2026-03-18_temporal_unit_agency_and_sleep_dialogue.md`

These notes preserve:
- the transition from Codex failure analysis to pre-metric extension claims
- the distinction between local compliance and whole-object fit
- the emergence of the temporal-unit hypothesis
- the temporal unit as a nearly mindless coherence-seeking swarm
- the link from temporal grounding to action and AI agency
- the possibility that a temporally rich intelligence may require sleep-like reset phases

---

## Likely next directions

This branch is evolving iteratively rather than through a fixed predetermined file plan.

Near-term work is likely to continue along three paths:

- refining the participant/emission update grammar
- improving toy prototype behavior and visualization
- testing the temporal-unit framing on real movement data

New files are therefore expected to emerge opportunistically as the architecture clarifies.

---

## Working sequence

The current working sequence for this branch is:

1. establish the roadmap
2. record recurring failure signatures
3. define proxy tests for rebuild, coherence, and whole-object fit
4. specify the proto temporal unit
5. define participant, emission, coupling, and update-rule grammar
6. prototype and inspect toy swarm behavior
7. use toy cases to check whether the ontology, update rules, and readout machinery are internally coherent
8. move toward narrow real-data tests on embodied movement traces
9. only then ask whether the temporal-unit framing yields operational advantage over plain trajectory/control descriptions

---

## Engineering orientation

This branch assumes that the main question is no longer simply:

- how do we add more memory?
- how do we add more retrieval?
- how do we add more tools?

The sharper question is:

> How do we create a guidance layer that lets evolving gradients persist, interact, and organize into longitudinal choreographies strong enough to steer later symbolic search?

That question is treated here as an engineering question, not only a philosophical one.

---

## Strategic value

Phi-Mesh can become more than a memory archive or conceptual staging ground.

This branch aims to make it:

- a classification environment for model extensions
- a ledger of failure signatures
- a testing ground for morphology-sensitive prompting and proxy architectures
- and a seedbed for true pre-metric intelligence design

Strong formulation:

> Phi-Mesh should become the well of pre-metric model extensions.

---

## Current stance

This branch does **not** claim the finished architecture yet.

It claims something narrower and more useful:

- there is likely a missing layer below current architectural surface tweaks,
- that layer has identifiable functions,
- present failures already point toward those missing functions,
- and the first step is to define and test them rigorously.

---

## Closing note

This branch begins from a practical insight:

A system can satisfy explicit local rules and still fail to preserve the coherence of the evolving whole.

That recurring gap may be one of the clearest signs that future intelligence will require more than metric/local optimization.

This branch exists to name that gap, diagnose it, and turn it into a buildable path.
