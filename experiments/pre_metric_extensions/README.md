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

---

## Related dialogue notes

The conceptual development behind this branch is preserved in the dialogue archive.

Most relevant notes include:

- `dialogues/2026-03-15_pre_metric_guidance_constraint_choreography_dialogue.md`
- `dialogues/2026-03-16_temporal_unit_and_embedded_llm_dialogue.md`

These notes preserve:
- the transition from Codex failure analysis to pre-metric extension claims
- the distinction between local compliance and whole-object fit
- the emergence of the temporal-unit hypothesis
- the idea that the LLM may live within a time-sensitive partner rather than rule above it

---

## Planned files

The following artifacts are expected next:

### `proxy_01_patch_vs_rebuild.md`
First proxy experiment for testing when a system should rebuild a contaminated object instead of continuing to patch it.

### `rgpx_extension_sketch.md`
A first explicit architecture sketch for an RGPx-style extension.

Likely components include:
- event stream
- morphology tracker
- topology-as-context layer
- constraint extractor
- gradient translator
- search/action biaser

### `criteria_for_premetric_extensions.md`
Evaluation criteria for deciding whether a candidate extension genuinely improves pre-metric guidance rather than only adding metric scaffolding.

### future temporal-unit notes
Likely notes on:
- endogenous temporality
- internal clocks
- rhythm coding
- weighted temporal slices
- embedded symbolic layers inside time-sensitive substrates

---

## Working sequence

The current working sequence for this branch is:

1. establish the roadmap
2. record recurring failure signatures
3. define patch-vs-rebuild and whole-object proxy tests
4. sketch the first candidate extension architecture
5. clarify the role of temporality and temporal weighting
6. test whether any small coupled scaffolds improve coherence in practice

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
