# 2026-03-15 RGPx LLM Extension Roadmap

## Purpose

This note opens a practical RGPx research path for pre-metric LLM extensions.

The core claim is that the next meaningful extension of LLMs will not be another metric-scale attachment (longer context, larger memory, more retrieval, more tools, deeper verifier loops), but a **pre-metric guidance layer** that shapes latent search before symbolic resolution.

This roadmap translates that claim into a concrete research program for Phi-Mesh.

---

## Why this branch exists

Recent work around `benchmarks/ai_intuition_c08/second_benchmark_pilot/` exposed a recurring failure mode in Codex-style editing:

- local instructions were often satisfied,
- but whole-object coherence repeatedly failed,
- stale remnants survived,
- duplicated sections reappeared,
- and patch-based repair often replaced neither the object nor its morphology.

This was not just a tooling annoyance. It became a live empirical case of the difference between:

- **metric/local repair** — explicit rule satisfaction, narrow compliance, local correction
- **pre-metric / fit-first guidance** — whole-object orientation, morphology-sensitive rebuild, longitudinal coherence

That episode now serves as a small but useful empirical seed for a broader claim about future AI systems.

---

## Core thesis

The next meaningful extension of LLMs will not be another metric-scale attachment, but a **pre-metric guidance layer** that shapes latent search before symbolic resolution.

In RGPx terms, this means:

- local events do not merely accumulate into outputs,
- emerging morphology induces constraints,
- those constraints become context for subsequent events,
- and intelligent behavior depends on sensitivity to **constraint/gradient choreographies**, not just local optimization.

---

## Stronger formulation

A true RGPx-style extension should not merely improve token prediction or post hoc repair. It should support:

1. **whole-object fit before local patching**
2. **emerging morphology as active context**
3. **constraint choreography detection**
4. **detection of relations between choreographies**
5. **translation of constraints into operative gradients**
6. **search steering by longitudinal coherence rather than only local best fit**

---

## What is missing in current LLM extensions

Current extensions mainly improve behavior after symbolic search has already begun:

- longer context windows
- external memory
- retrieval augmentation
- tool use
- recursive decomposition
- self-verification loops
- post hoc reranking

These are valuable, but they are mostly compensatory.

They help systems:
- remember more,
- retrieve more,
- repair more,
- verify more.

But they do not necessarily provide a better **early guidance field** for shaping which symbolic paths should form in the first place.

---

## RGPx distinction

The key RGPx distinction is not simply recursion or context sensitivity. Good ML already has both.

The deeper distinction is this:

- **standard recursive/context-sensitive ML** iterates on states, representations, or forms under explicit or learned objectives
- **RGPx** tracks how evolving constraints organize into choreographies that shape what trajectories can become available, stable, or doomed

Compactly:

> ML can iterate on morphology. RGPx asks what choreography of constraints is making that morphology possible, stable, or doomed.

---

## Working hypotheses

### Hypothesis 1 — Token/weight space already contains evolving choreographies

The world of tokens and weights is unlikely to be a flat statistical field. It is likely full of:

- emergent pathway biases
- attractor tendencies
- instability zones
- branch-collapse patterns
- coherence corridors
- sacrifice-for-later-win trajectories
- local-fit traps

These may be understood as **constraint/gradient choreographies** in latent search.

### Hypothesis 2 — Current models are weak at whole-object guidance

Current systems often:
- satisfy local constraints,
- but fail to preserve global coherence,
- especially when regeneration is better than patching.

This suggests weak internal morphology tracking and weak topology-as-context feedback.

### Hypothesis 3 — Future intelligence depends on choreography sensitivity

A stronger model should:
- detect emerging choreographies,
- detect relations between choreographies,
- translate constraints into gradients,
- and bias search accordingly.

---

## Architectural intuition

A pre-metric extension should likely involve at least six functional layers:

### 1. Event stream layer
Tracks local symbolic events:
- token proposals
- reasoning steps
- edits
- tool calls
- branch expansions

### 2. Morphology tracker
Tracks what whole structure is emerging:
- file shape
- argument shape
- answer shape
- narrative shape
- planning shape

### 3. Topology-as-context layer
Tracks which relations have stabilized enough to constrain what comes next.

This is the crucial shift:
the emerging topology is not just an output of reasoning; it becomes context for subsequent reasoning.

### 4. Constraint extractor
Identifies:
- what is becoming admissible
- what is becoming fragile
- what is becoming incoherent
- what is becoming globally promising
- what local move now carries downstream cost or benefit

### 5. Gradient translator
Converts emerging constraints into operative directional pressures.

Without this bridge, the system can describe coherence but cannot participate in it.

### 6. Search/action biaser
Uses those gradients to shape:
- token search
- branch selection
- rebuild-vs-patch choice
- local sacrifice for downstream coherence
- rejection of globally toxic local moves

---

## Constraint-to-gradient bridge

This is likely the key engineering hinge.

Constraints are not yet guidance. A future model or robot must convert:

- admissibility structures
- fragility structures
- conflict structures
- morphological tendencies

into something like:

- directional weighting
- branch suppression
- branch encouragement
- tempo changes in search
- rebuild pressure
- regime-shift triggers

Compactly:

> constraint field → gradientized guidance signal → search/action bias

This bridge may be one of the deepest practical requirements of an RGPx-style extension.

---

## Choreographies and relations between choreographies

A future system must do more than detect single gradient/constraint choreographies.

It should also detect **relations between choreographies**, including:

- resonance
- interference
- nesting
- inhibition
- handoff
- phase alignment
- structural analogy across domains

This matters because transfer and deeper intelligence may depend less on isolated patterns than on the relations among such patterns.

This is also where the Navier–Stokes line of work matters: nature may hinge on common choreographies across seemingly different substrates.

---

## Why this matters for robots

A narrow robot can still function without this.

But robust, self-motivated, open-ended agents likely cannot rely only on:
- object decomposition,
- explicit goals,
- local optimization,
- and metric repair.

The stronger claim is:

> Cartesian robotics may suffice for bounded task execution, but it is unlikely to ground robust, open-ended, self-motivated agency, because such agency depends on sensitivity to evolving constraint choreographies rather than only object-centered world modeling and local optimization.

A future robot should not be a better mechanical doll. It should become closer to a **walking RGPx syntax processor**:
- identifying evolving constraints,
- anticipating favorable and adverse morphologies,
- translating constraints into gradients,
- and steering longitudinally.

---

## Why this matters for LLMs

An LLM extension along this path would not merely:
- store more,
- retrieve more,
- reason longer,
- or verify more.

It would instead:
- shape early search,
- reduce stale-remnant failure,
- prefer rebuild over accretion when appropriate,
- tolerate local sacrifice for downstream coherence,
- and become better at whole-object fit.

This would mark a move from:
- symbolic continuation under local constraints,
toward
- morphology-sensitive guidance under evolving topology.

---

## Immediate research direction

We should begin with **proxy experiments**, not with weight-level modification yet.

The first goal is to detect whether pre-metric-like behavior can be induced, measured, and categorized before full architectural intervention.

---

## Proposed experiment track

### Proxy 01 — Patch vs rebuild
Test when models keep patching locally instead of regenerating globally.

Question:
Can the model recognize contaminated objects and choose rebuild over repair?

### Proxy 02 — Whole-object invariants
Measure whether the model can preserve:
- section roles
- non-duplication
- one-to-one mapping between headings and content
- consistency between evidence and rendered object

### Proxy 03 — Constraint-to-gradient prompting
Test whether prompts can induce the model to:
- identify emerging constraints,
- convert them into directional search guidance,
- and use that to bias next steps.

### Proxy 04 — Longitudinal sacrifice tests
Test whether the model can prefer a locally inferior move that improves downstream coherence.

Chess-sacrifice logic is the motivating analogy here.

### Proxy 05 — Choreography relation detection
Test whether the model can identify structural relations between:
- editing failures,
- narrative turns,
- planning shifts,
- fluid transitions,
- and other domains.

---

## Suggested future folder structure

Recommended branch root:

`experiments/pre_metric_extensions/`

Recommended files to follow this roadmap:

- `README.md`
- `2026-03-15_rgpx_llm_extension_roadmap.md`
- `proxy_01_patch_vs_rebuild.md`
- `proxy_02_whole_object_invariants.md`
- `proxy_03_constraint_to_gradient_prompts.md`
- `proxy_04_longitudinal_sacrifice_tests.md`
- `proxy_05_choreography_relation_detection.md`
- `rgpx_extension_sketch.md`
- `failure_signatures.md`
- `criteria_for_premetric_extensions.md`

---

## First practical question

The first practical question is:

> How do we represent emerging constraints in a form that can later be translated into gradients?

This should be treated as the hinge question for the whole branch.

Because once constraints can be represented in a disciplined way, we can begin:
- comparing choreographies,
- relating choreographies,
- and steering search with them.

---

## Working evaluation criteria

A candidate pre-metric extension should improve some combination of:

- earlier narrowing of valid trajectories
- fewer stale remnants after edits
- better rebuild-over-patch judgment
- fewer post hoc cleanup loops
- more stable first-direction quality
- better local-sacrifice / downstream-gain behavior
- better cross-domain recognition of choreography relations
- better whole-object coherence under ambiguous or contaminated tasks

---

## Strategic value for Phi-Mesh

Phi-Mesh can become more than a memory archive or philosophical staging ground.

It can become:
- a classification environment for model extensions,
- a testing ground for morphology-sensitive prompting,
- a ledger of failure signatures,
- and a seedbed for true pre-metric intelligence architecture.

Strong formulation:

> Phi-Mesh should become the well of pre-metric model extensions.

---

## Immediate next steps

1. Create `experiments/pre_metric_extensions/README.md`
2. Create `failure_signatures.md` using the Codex benchmark episode as the first case
3. Create the first proxy note: `proxy_01_patch_vs_rebuild.md`
4. Draft `rgpx_extension_sketch.md`
5. Begin explicit study of how gradients may develop in token/weight space and how those latent choreographies might be detected or proxied

---

## Closing statement

This roadmap begins from a simple but consequential insight:

Future intelligence will not be secured merely by adding more metric scaffolding to current models. It will depend on whether we can discover and engineer a layer that senses evolving morphology, treats topology as context, detects constraint/gradient choreographies and their relations, and translates emerging constraints into operative gradients for search and action.

That is the practical RGPx path opened here.
