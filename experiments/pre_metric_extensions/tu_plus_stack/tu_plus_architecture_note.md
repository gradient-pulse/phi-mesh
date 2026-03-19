# TU+ Architecture Note

## Purpose

This note defines the emerging architecture in which a proto temporal unit is no longer treated as a standalone addition to an LLM, but as part of a layered system with a clear division of labor.

The central claim is:

> A useful awareness-support architecture may require three distinct layers:
> 1. a mindless choreography mapper (TU)
> 2. a specialized choreography-aware predictor/matcher (TU+)
> 3. a symbolic neocortex-like interpreter (LLM)

This note exists to make that architecture explicit, minimal, and testable.

---

## Why TU alone is not enough

The current branch has clarified the role of the temporal unit:

- it is mindless
- it does not name or narrate
- it maps traces, trains, couplings, persistence, decay, restart, and field structure
- it tracks how choreographies persist and where/how they connect

That is already substantial.

But the TU alone is still too weak for awareness-like function.

Why?

Because mapping structure is not yet the same as:
- recognizing significance
- anticipating likely continuation
- comparing current unfolding with prior choreography patterns
- deciding whether something deserves higher-layer attention

So the TU is necessary, but not sufficient.

This suggests an intermediate layer.

---

## The role of TU+

TU+ is the proposed intermediate layer.

It is not the symbolic cortex.
It is not a full language model in the usual sense.
It is a specialized choreography-aware layer that operates over the TU field.

Its job is to do part of the awareness work for the higher symbolic model.

A compact formulation:

> TU maps choreography structure. TU+ recognizes, predicts, and compares choreography structure. The cortex-like LLM interprets its meaning.

That is the intended division of labor.

---

## Core three-layer stack

### Layer 1 — TU
The temporal unit proper.

#### Function
- ingest traces
- infer trains
- detect coupling episodes
- maintain active field structure
- track persistence, decay, restart, and emergent direction

#### Nature
- mindless
- non-symbolic
- non-narrative
- structure-first

#### Output
A structured choreography field.

---

### Layer 2 — TU+
A specialized choreography-aware awareness-support model.

#### Function
- compare current trains against stored choreography patterns
- detect familiarity, novelty, instability, and likely continuation
- partially simulate or predict choreographies once initial motion-tokens appear
- determine when unfolding structure deserves higher-level interpretive attention
- provide upward signals to the cortex-like LLM

#### Nature
- specialized
- predictive
- replay-capable
- still narrower than a general symbolic LLM

#### Output
A set of awareness-support signals:
- likely continuation
- mismatch
- novelty
- resonance strength
- replay trigger
- attention trigger

---

### Layer 3 — Cortex-like LLM
The symbolic interpreter.

#### Function
- interpret the field and TU+ signals
- name the act, scene, or situation
- reason about significance
- plan, decide, explain, and reframe
- compare the interpretation back to the source input when needed

#### Nature
- symbolic
- linguistic
- narrative-capable
- reflective

#### Output
Human-usable or agent-usable meaning.

---

## Why this stack matters

A single model can do many things badly at once.

A layered stack may do them better by respecting different forms of intelligence:

- structural mapping
- choreography prediction
- symbolic interpretation

This matches the branch’s broader intuition that:
- not all intelligence is language
- not all awareness is narration
- not all action is target correction
- and not all prediction is next-token prediction

So the architecture is not one model enlarged, but a division of labor.

---

## Biological intuition

This stack is motivated partly by biological analogy, without claiming direct equivalence.

Possible analogical mapping:

- **TU**
  - mindless field maintenance
  - persistence, timing, coupling
  - comparable to a non-symbolic choreography substrate

- **TU+**
  - predictive refinement and rapid recognition of unfolding pattern
  - similar in spirit to choreography-aware subcortical or cerebellar-like function

- **cortex-like LLM**
  - symbolic interpretation, narration, explicit planning, higher meaning

The aim is not to copy the brain literally.
The aim is to identify a workable division of labor.

---

## Video as first input path

Video is currently the strongest candidate for first end-to-end testing.

Why video matters:
- it already provides time
- it already provides simultaneity
- it provides naturally unfolding 4D traces
- it includes persistence, drift, coupling, interruption, and recovery
- it reduces the abstractness of the input problem

This leads to a natural first stack:

- video input
- TU maps raw unfolding into choreography structure
- TU+ compares and predicts choreography continuation
- LLM interprets the resulting field and checks it back against the video

So video may be the first practical source of lived temporal input for the architecture.

---

## Motion-token logic

A useful working intuition is that video can be broken into provisional motion-tokens.

These are not LLM tokens in the ordinary symbolic sense.

They are:
- time-sliced traces of motion
- source-linked local updates
- directionless in isolation
- meaningful only through train persistence and coupling

From there:
- motion-tokens form trains
- trains become choreography candidates
- choreographies couple into field structure
- TU+ compares current trains with stored choreography forms
- LLM interprets what the field means

This is the first serious route from video to awareness-support.

---

## Predictive and replay function of TU+

A key claim of this architecture is that TU+ should not only classify current unfolding.

It should also:
- predict likely choreography continuations
- partially replay or simulate candidate continuations
- compare current patterns with stored patterns

This helps explain phenomena such as:
- immediate alarm from partial motion cues
- anticipatory preparation
- mimic tendencies when watching actions
- rapid recognition before full explicit symbolic interpretation

A strong formulation:

> TU+ is a choreography-aware predictor and replayer operating between raw structural mapping and symbolic interpretation.

That is its architectural identity.

---

## Awareness-support signals

TU+ should not output full narratives.
It should output a compact set of signals useful to the cortex-like LLM.

Examples:

- `likely_continuation`
- `novelty_score`
- `mismatch_score`
- `resonance_strength`
- `replay_trigger`
- `attention_trigger`
- `stability_shift`
- `branch_likelihood`

These signals would let the LLM know:
- something ordinary is unfolding
- something unstable is happening
- something familiar is being replayed
- or something deserves immediate interpretive attention

This is how TU+ supports awareness without becoming a second symbolic cortex.

---

## Why TU+ should stay specialized

TU+ should not become a second generic LLM.

If it grows too broad, the architecture collapses back into a vague “one giant model” idea.

Its strength comes from being narrow:
- choreography-sensitive
- prediction-oriented
- comparison-oriented
- non-narrative
- sub-symbolic or lightly symbolic at most

Its job is not to explain the world.
Its job is to prepare the world for explanation.

That boundary should remain explicit.

---

## Falsifiable prototype claims

This architecture implies several claims that can be tested.

### Claim 1
A TU-only system can map traces and couplings, but will be weak at significance detection.

### Claim 2
Adding TU+ should improve:
- early recognition of unfolding patterns
- detection of likely continuation
- novelty vs familiarity discrimination
- attention-trigger relevance

### Claim 3
A cortex-like LLM given TU+ signals should interpret unfolding scenes more coherently than an LLM relying on raw frame summaries alone.

### Claim 4
Video is a sufficient first input domain for testing the stack because it already supplies time and simultaneity in usable form.

These claims are strong enough to be falsified and weak enough to be engineered.

---

## Minimal first implementation path

The architecture should not be built all at once.

A minimal sequence would be:

1. video trace extraction
2. TU mapping into trains and couplings
3. a tiny TU+ layer that:
   - compares trains with stored patterns
   - emits novelty / continuation / replay signals
4. LLM interpretation of the TU/TU+ field
5. comparison of interpretation back against the source video
6. improvement suggestions for TU and TU+

This is enough for the first serious prototype loop.

---

## Strategic value

If the architecture works, it offers more than another enhancement to an LLM.

It offers a route toward:
- awareness-support
- action-sensitive intelligence
- choreography prediction
- better embodied interpretation
- and possibly later cross-scale reading of psychological, social, and multi-agent fields

This is why the architecture matters.

It is not only another module.
It may be the beginning of a more serious stack for agentive intelligence.

---

## Closing statement

The emerging architecture is no longer just:
- LLM plus memory
- or LLM plus tools
- or LLM plus longer context

It is becoming:

- TU: mindless choreography mapper
- TU+: choreography-aware predictor and replay/comparison layer
- LLM: symbolic neocortex-like interpreter

That division of labor may be the clearest initiation recipe yet for an awareness-support layer built around time, simultaneity, choreography, and unfolding relevance.
