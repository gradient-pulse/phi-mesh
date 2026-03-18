# Swarm Participant Update Rule

## Purpose

This note defines the minimum local update grammar for a swarm participant in the proto temporal unit branch.

It builds on the corrected ontology already established:

- **participant** = vertical choreography
- **event / emission** = participant output
- **horizontal family** = coupling episode among participants
- **coherence** = viable common temporality among participants

The aim is to specify the simplest possible participant rule-set from which larger temporal-unit behavior might emerge.

The guiding principle is the same one that made LLMs effective:

> do not engineer intelligence directly; engineer a minimal update-bearing unit and the local rules by which larger structure can emerge.

---

## Design goal

The participant should remain nearly mindless.

It should not:
- model the whole
- understand the task semantically
- optimize globally
- reason symbolically

It should only:
- persist or fade
- emit or stay quiet
- couple or decouple
- reinforce or weaken
- restart when conditions allow
- contribute to local coherence if possible

That is enough for the first build basin.

---

## Core ontology

### Participant
A **vertical choreography**:
- a temporally persistent local process
- emitting an ordered train of emissions
- capable of strengthening, weakening, yielding, and restarting

### Emission
A **participant emission**:
- a local temporal trace produced by a participant
- the minimal observable update-bearing unit
- able to enter horizontal coupling with emissions from other participants

### Horizontal family
A **coupling episode**:
- formed when emissions from distinct participants occur in the same or near-time window

### Weight
A participant/emission relevance measure arising from:
- vertical persistence
- horizontal coupling
- local reinforcement
- decay or weakening

### Local coherence
A local estimate of whether neighboring participants are synchronizing into a viable common temporality.

---

## Minimum participant state

A participant should have only a small amount of state.

Suggested minimum:

- `participant_id`
- `activation`
- `prev_activation`
- `last_tick_active`
- `emission_count`
- `cycle_phase`
- `active_horizontal_links`
- `coherence_state`

### Meaning of fields

#### `participant_id`
Stable identifier for the vertical choreography.

#### `activation`
Current strength / salience / viability of the participant.

#### `prev_activation`
Previous activation value, used to detect rise, fall, or stability.

#### `last_tick_active`
Latest tick at which the participant emitted or remained active.

#### `emission_count`
Count of emitted updates over the current cycle window.

#### `cycle_phase`
Very simple local phase, for example:
- `rising`
- `stable`
- `fading`
- `restarting`

#### `active_horizontal_links`
Current coupling links to other participants through recent emissions.

#### `coherence_state`
Simple local label such as:
- `rising`
- `holding`
- `falling`

This should remain local, not global.

---

## Minimum emission structure

Each emission should be small and inspectable.

Suggested minimum:

- `emission_id`
- `participant_id`
- `tick`
- `activation_snapshot`
- `horizontal_links`
- `source_trace`

### Meaning of fields

#### `emission_id`
Unique identifier for the emitted trace.

#### `participant_id`
Which participant emitted it.

#### `tick`
When the emission occurred.

#### `activation_snapshot`
Participant activation at emission time.

#### `horizontal_links`
Which other emissions or participants it coupled with in the current window.

#### `source_trace`
Optional provenance field linking back to sensor, action stream, or prior event source.

---

## Minimum local rules

The participant update rule should remain painfully simple.

### Rule 1 — Clock
Each participant distinguishes only:
- `now`
- `near_now`
- `older`

This can be implemented through:
- current tick
- last active tick
- near-time window threshold

No richer temporal model is required at first.

---

### Rule 2 — Emit
A participant emits when:
- its activation is above a minimum threshold
- or its activation changes enough to matter
- or its local coupling state changes significantly

This prevents silent persistence from being mistaken for active contribution.

Compactly:

> a participant emits when it is active enough or when its local state meaningfully changes.

---

### Rule 3 — Vertical persistence
A participant gains stability when it continues to emit across successive ticks or within an allowable continuity window.

This is the first source of weight.

Simple intuition:
- longer-lived train = stronger participant
- broken train = weaker participant

Compactly:

> vertical persistence increases participant weight.

---

### Rule 4 — Horizontal coupling
When emissions from distinct participants occur in the same or near-time window, a horizontal family may form.

This is the second source of weight.

Simple intuition:
- synchronized trains matter more than isolated traces
- coupling is evidence of field relevance

Compactly:

> horizontal synchronization increases participant relevance.

---

### Rule 5 — Weight update
A participant’s weight should rise or fall through a very small update rule.

A simple conceptual form is:

`new_activation = old_activation + persistence_gain + coupling_gain - decay - mismatch_penalty`

This is only a structural guide, not yet a fixed equation.

### Components

#### `persistence_gain`
Added when the participant continues its train.

#### `coupling_gain`
Added when the participant synchronizes with others.

#### `decay`
Always present unless countered by persistence/coupling.

#### `mismatch_penalty`
Applied when local timing becomes destructive, unstable, or poorly supported.

This is enough for a first prototype.

---

### Rule 6 — Yield
A participant yields when:
- activation falls below threshold
- support dries up
- coupling collapses
- its train loses continuity

Yield does not mean deletion.
It means temporary quieting or drop-out.

Compactly:

> a participant yields when its train can no longer sustain viable local coherence.

---

### Rule 7 — Restart
A participant may restart when:
- relevant conditions reappear
- new emissions begin again
- sufficient local support returns

This is the minimal UD-like cycle logic.

The participant does not “decide” to restart intelligently.
It simply becomes activatable again under suitable conditions.

Compactly:

> restart is re-entry into emission after viable support returns.

---

### Rule 8 — Local coherence update
Local coherence should not be treated as semantic understanding.

It should be computed operationally.

A participant’s local coherence rises when:
- its own train persists
- neighboring participants are also active
- horizontal coupling is sustained
- activation changes are not wildly unstable

A participant’s local coherence falls when:
- neighboring support disappears
- train continuity breaks
- coupling becomes sparse or chaotic
- activation collapses suddenly

Compactly:

> local coherence is sustained, mutually reinforcing, temporally aligned neighboring activity with limited instability.

---

## Minimal operational signals

A first implementation only needs a few local signals.

Suggested minimum signals:

- `vertical_support`
- `horizontal_support`
- `activation_delta`
- `continuity_flag`
- `yield_flag`
- `restart_flag`

### Meanings

#### `vertical_support`
Whether the participant’s own train has persisted recently.

#### `horizontal_support`
How many other participants it is currently coupling with.

#### `activation_delta`
Whether activation rose, held, or fell since the previous step.

#### `continuity_flag`
Whether the participant remained within its continuity window.

#### `yield_flag`
Whether activation dropped below viability.

#### `restart_flag`
Whether a previously quiet participant became active again.

This is likely enough to build a first update loop.

---

## Weight and train logic

A useful engineering refinement is to think of each participant as producing an **emission train**.

This means:
- the participant persists
- its emissions form an ordered train
- train persistence matters
- train synchronization with other trains matters

So the central weight rule becomes:

> emissions gain weight through train persistence and cross-train synchronization.

This should guide implementation more than any semantic classification rule.

---

## Minimum readout for the LLM

The LLM should not read every raw emission if that can be avoided.

It should receive a compressed participant-field summary.

Suggested minimum readout:

- most active participants
- strongest horizontal families
- participants rising
- participants fading
- local coherence estimate
- likely mode suggestion:
  - hold
  - observe
  - clarify
  - patch
  - rebuild
  - act

This preserves the architecture:
- swarm does the coherence-seeking
- LLM does the symbolic interpretation

---

## What this rule-set does not yet include

This first note intentionally does **not** attempt to define:
- exact equations
- exact threshold values
- global optimization
- sleep/reset phase
- exact PoLA formalism
- exact UD formalism
- exact participant discovery algorithm from raw sensor data

Those belong later.

For now, the goal is to define a stable local rule grammar.

---

## Recommended code-facing interpretation

A first code prototype should likely implement:

1. participant state object
2. emission object
3. tick update loop
4. persistence/coupling-based activation update
5. yield and restart behavior
6. minimal readout summary

That is enough to test whether participant-level swarm behavior begins to emerge.

---

## Closing statement

This note defines the simplest viable participant grammar now available in the branch.

Its central claim is:

> A swarm participant is a vertical choreography that emits a train of traces, gains weight through persistence and synchronization, yields when support collapses, and restarts when viable local coherence returns.

That is the minimum update basin from which the proto temporal unit should now be engineered.
