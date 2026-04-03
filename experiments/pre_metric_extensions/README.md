# Pre-Metric Extensions

## Purpose

This branch explores a practical RGPx path toward future AI systems that do more than optimize locally over symbolic states.

The working claim is that the next meaningful extension of LLMs will not be another metric-scale attachment — longer context, larger memory, more retrieval, deeper verifier loops, or more tools — but a **pre-metric guidance layer** that shapes latent search before symbolic resolution.

This branch exists to make that claim testable.

---

## Why this branch exists

Recent work in the benchmark area exposed a recurring pattern:

- local instructions were often satisfied
- but whole-object coherence repeatedly failed
- stale remnants survived
- duplication reappeared
- and patch-style repair often replaced neither the object nor its morphology

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

A newer working hypothesis, now tested in bounded dry-run form, is that this may also require a **coherence-driven division of LLM labor** into distinct but connected roles:
- **TU** — unfolding structure mapper
- **TU+** — choreography predictor / comparer / reviser
- **cortexLLM** — symbolic interpreter and context-framing layer

---

## Terminology clarification

In this branch, a few terms have a specific engineering meaning.

- **tick** = a local temporal update index used for participant/emission timing  
  It is **not** the same as the stronger Narrative Tick notion used elsewhere for irreversible structural turns or UD-relevant phase changes.

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

## Current branch structure

The branch currently develops along two connected paths.

### 1. Proto temporal-unit / swarm path
This path explores:
- participants as vertical choreographies
- emissions as local observable outputs
- horizontal coupling episodes
- coherence as viable common temporality
- toy simulation and visualization
- eventual movement-data testing

This is the more explicitly code-facing line.

### 2. TU / TU+ / cortexLLM path
This path explores:
- TU as a mindless choreography mapper
- TU+ as a specialized choreography-aware predictor / comparer / replay layer
- cortexLLM as symbolic interpreter and bounded downward-bias layer
- shared structured state across cycles
- prompt-instantiated role separation before software-instantiated freezing
- bounded disconfirmation tests as architectural evidence

This is currently the strongest bounded architecture line in the branch.

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

### `tu_plus_stack/`
A dedicated subfolder for the emerging coherence-driven division of LLM labor.

It hosts notes on:
- **TU** as a mindless choreography mapper
- **TU+** as a specialized choreography-aware predictor / comparer / replay layer
- **cortexLLM** as symbolic interpreter
- shared structured state across cycles
- bounded dry-run evidence from disconfirmation tests
- prompt-instantiated architecture before software-instantiated architecture

This subfolder marks a shift from general temporal-unit exploration toward a more explicit role-separated architecture for world-model-like behavior.

---

## Related dialogue notes

The conceptual development behind this branch is preserved in the dialogue archive.

Most relevant notes include:

- `dialogues/2026-03-15_pre_metric_guidance_constraint_choreography_dialogue.md`
- `dialogues/2026-03-16_temporal_unit_and_embedded_llm_dialogue.md`
- `dialogues/2026-03-17_temporal_unit_proto_and_ud_swarm_dialogue.md`
- `dialogues/2026-03-18_temporal_unit_agency_and_sleep_dialogue.md`
- `dialogues/2026-03-19_tu_plus_awareness_support_dialogue.md`
- `dialogues/2026-03-20_escaping_the_prompt_prison_dialogue.md`

These notes preserve:
- the transition from Codex failure analysis to pre-metric extension claims
- the emergence of the temporal-unit hypothesis
- the temporal unit as a mindless choreography mapper
- the introduction of TU+ as a specialized awareness-support layer
- the shift toward prompt-instantiated architecture before software-instantiated architecture
- the move from concept to bounded prototype logic

---

## Public fossil

This branch now also underlies the Zenodo note:

**World Model: Toward a Coherence-Driven Division of LLM Labor**  
**Evidence from bounded disconfirmation tests**  
DOI: `10.5281/zenodo.19145919`

That note is the bounded public fossil.
This branch remains the working environment behind it.

---

## Likely next directions

This branch is evolving iteratively rather than through a fixed predetermined file plan.

Near-term work is likely to continue along four paths:

- refining participant/emission update grammar
- improving toy prototype behavior and visualization
- extending bounded TU / TU+ / cortexLLM disconfirmation tests
- testing temporal-unit framing on real movement data

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
7. specify TU / TU+ / cortexLLM role separation and shared-state architecture
8. run bounded disconfirmation tests on the triad
9. move toward narrow real-data tests on embodied movement traces
10. only then ask whether these architectures yield operational advantage over plain trajectory/control descriptions or monolithic LLM orchestration

---

## Engineering orientation

This branch assumes that the main question is no longer simply:

- how do we add more memory?
- how do we add more retrieval?
- how do we add more tools?

The sharper question is:

> How do we create a guidance layer that lets evolving gradients persist, interact, and organize into longitudinal choreographies strong enough to steer later symbolic search?

And, more specifically:

> How do we implement that guidance either as a temporal-unit-like substrate, or as a coherence-driven division of LLM labor, without collapsing everything back into one generic symbolic assistant?

That question is treated here as an engineering question, not only a philosophical one.

---

## Strategic value

Phi-Mesh can become more than a memory archive or conceptual staging ground.

This branch aims to make it:

- a classification environment for model extensions
- a ledger of failure signatures
- a testing ground for morphology-sensitive prompting and proxy architectures
- a seedbed for true pre-metric intelligence design
- and a proof environment for coherence-sensitive world-model architectures

Strong formulation:

> Phi-Mesh should become the well of pre-metric model extensions.

---
---

## Positioning: What this “World Model” Is (and Is Not)

The TRIAD experiments do not aim to build a conventional “world model” in the sense of predictive control or task optimization.

Most current systems referred to as world models learn mappings of the form:

state → action → reward

and are evaluated by:
-	task success
-	adaptation speed
-	generalization across environments

In that framing, a “world model” is a tool for improving behavior under variation.

---

### TRIAD framing

The TRIAD experiments operate at a different layer.

They investigate:

how coherent structure is formed, maintained, degraded, and re-established under interaction.

The focus is not:
-	which action to take

but:

-	which coherent regimes exist
-	how systems transition between regimes
-	and under what conditions coherence persists or collapses

This is expressed in the extracted laws (Cycles 1–120), including:

-	closure / activation / collapse / re-entry
-	multi-stability and unification
-	fracture and reorganization
-	hierarchical coupling and tension stabilization
-	relational coherence and connectivity dominance

---

### Key distinction

Conventional systems:

learn to act within a world

TRIAD:

models how coherent worlds emerge, persist, and transform under pressure

---

### Implication

The TRIAD framework does not replace control or learning systems.

It provides a complementary layer:

a grammar of coherence and regime transition

which may help explain:
-	failure modes under contradiction or drift
-	recovery after breakdown
-	coexistence of competing strategies
-	stability without global alignment

---

### Scope note

These results are derived from bounded multi-agent LLM interaction (TU, TU+, cortexLLM) and should be treated as:

empirically extracted structural regularities

whose domain of validity is under active falsification.

---

This will sit well in the README because it:
-	anchors your work without overclaiming
-	clearly separates it from mainstream narratives
-	ties directly to your laws and experiments
-	keeps the door open for falsification (important credibility signal)

---
---

## Current stance

This branch does **not** claim the finished architecture yet.

It claims something narrower and more useful:

- there is likely a missing layer below current architectural surface tweaks
- that layer has identifiable functions
- present failures already point toward those missing functions
- bounded prototype logic can now be run against some of those functions
- and the first step is to define and test them rigorously

---

## Closing note

This branch begins from a practical insight:

A system can satisfy explicit local rules and still fail to preserve the coherence of the evolving whole.

That recurring gap may be one of the clearest signs that future intelligence will require more than metric/local optimization.

This branch exists to name that gap, diagnose it, and turn it into a buildable path.
