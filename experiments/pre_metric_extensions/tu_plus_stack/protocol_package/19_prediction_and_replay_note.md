# T-Protocol — Prediction and Replay Note v1

## Purpose

This note clarifies what prediction means inside T-Protocol, especially at the level of TU+.

Its purpose is to prevent confusion between TU+ prediction and more familiar forms of prediction such as:

- ordinary next-token continuation
- symbolic forecasting
- generic planning
- reflex-policy output
- model-predictive control style command simulation

T-Protocol uses prediction in a narrower and more structured sense.

---

## Core principle

TU+ does not predict by inventing a likely story.

It predicts by comparing the current live choreography field against stored choreography patterns and projecting likely next train continuations.

Compactly:

> TU+ prediction is comparison-driven continuation forecasting over the live choreography field.

---

## What TU+ prediction is

TU+ prediction is the production of candidate next continuations based on:

- current trains
- current couplings or decouplings
- current coherence state
- mismatch history
- stored choreography memory
- bounded downward contextual bias where present

TU+ therefore predicts from the question:

- what kind of unfolding does this field most resemble?
- what continuation typically follows from this kind of structure?
- is the field stable, weakening, branching, reopening, or restarting?
- should one continuation be favored, or should several remain live?

This makes TU+ prediction:
- field-sensitive
- continuity-sensitive
- weighted rather than absolute
- revisable under returned evidence

---

## What TU+ prediction is not

TU+ prediction is **not**:

### 1. Ordinary next-token prediction
TU+ does not predict the next token in a language stream as such.

It predicts likely next structured continuation in the choreography field.

### 2. Broad symbolic forecasting
TU+ does not generate a high-level narrative about what will happen “in general.”

That belongs, if anywhere, to cortexLLM at a later symbolic level.

### 3. Generic planning
TU+ is not a planner choosing goals, utilities, or broad strategies.

It remains close to unfolding structure and continuation pressure.

### 4. Reflex output
TU+ does not directly produce a reflex action.

It produces candidate continuation structures that may later inform action-linked processes.

### 5. Pure simulation for command issuance
TU+ is not merely running an internal motor simulation in order to emit control commands.

Its role is broader and more basic:
- compare
- replay
- predict continuation
- register mismatch
- preserve contested alternatives when support is insufficient

---

## How TU+ predicts

TU+ prediction proceeds in a bounded sequence.

### Step 1 — Read the live field
TU+ reads the current field state, including:
- active trains
- coupling state
- coherence state
- mismatch history
- downward bias where present

### Step 2 — Compare against choreography memory
TU+ compares the current field against stored choreography patterns.

This may yield:
- familiarity
- partial familiarity
- novelty
- instability
- mismatch pressure
- replay relevance

### Step 3 — Generate candidate train continuations
TU+ proposes one or more likely next train candidates.

These candidates are weighted by:
- persistence
- coupling strength
- coherence viability
- mismatch pressure
- prior pattern similarity
- bounded contextual bias

### Step 4 — Preserve revisability
If support is weak or contradictory, TU+ should not force one dominant future.

It may preserve:
- one favored continuation
- several weighted continuations
- explicit instability or mismatch flags
- replay triggers for higher scrutiny

Compactly:

> TU+ predicts by matching the present field to stored choreography forms and projecting weighted next-train candidates.

---

## Replay and its role

Replay is central to TU+.

Replay does not mean theatrical reenactment.
It means structured reactivation of relevant choreography memory for comparison against the current field.

Replay helps TU+ answer:
- have we seen a field like this before?
- what continuation followed then?
- what differences matter now?
- is the present field close enough to support a continuation forecast?
- or is novelty / instability too high?

Replay therefore gives TU+ a continuity-sensitive basis for prediction.

Compactly:

> Replay is the reactivation of relevant choreography memory in support of comparison and continuation judgment.

---

## Prediction, mismatch, and correction

TU+ prediction is never final by itself.

It must remain answerable to returned traces.

This means:
- predicted train candidates may later be supported
- they may weaken
- they may split into branches
- they may collapse under mismatch
- they may trigger revision, de-confirmation, or restart

This is why TU+ prediction is not mere speculation.

It is prediction under correction pressure.

Compactly:

> TU+ predicts under the expectation that returned traces may confirm, weaken, or overturn the forecast.

---

## Why this differs from state-of-the-art reflex models

Many current robotics or autonomy systems use prediction in a more reflex-linked sense.

Typically, prediction there is closely tied to:
- immediate control simulation
- action selection
- command optimization
- policy execution under short-horizon uncertainty

That is useful, but it is not the same as TU+.

TU+ is not primarily:
- a motor reflex predictor
- a low-level controller
- a command optimizer

It is a choreography-aware continuation layer that preserves:
- temporal continuity
- pattern comparison
- replay relevance
- mismatch accountability
- branch sensitivity
- restart and reopening discipline

So the difference is not merely technical detail.
It is a difference in level and purpose.

### Reflex-oriented prediction
- optimized for immediate action
- often short-horizon
- often tightly tied to output or control

### TU+ prediction
- optimized for structured continuation judgment
- preserves ambiguity where warranted
- remains answerable to replay and mismatch
- supports supervisory and recursive coordination rather than raw reflex control

Compactly:

> Reflex models predict in order to act immediately; TU+ predicts in order to keep the field oriented, revisable, and continuity-sensitive.

---

## Why this matters

Without this distinction, TU+ may be misunderstood as:
- a planner
- a controller
- a motor simulator
- or just another predictive model

But TU+ is none of those in the ordinary sense.

Its role is to preserve the protocol’s middle layer:
- between raw mapping and symbolic interpretation
- between local structure and contextual judgment
- between unfolding continuity and premature closure

That is why TU+ is indispensable.

---

## Closing statement

TU+ prediction should be understood as a replay-grounded, mismatch-accountable, continuity-sensitive projection of likely next train structure.

It is neither generic forecasting nor reflex command simulation.

A compact final formulation:

> TU+ predicts by replaying relevant choreography memory against the current live field and generating weighted next-train continuations that remain revisable under returned evidence.
