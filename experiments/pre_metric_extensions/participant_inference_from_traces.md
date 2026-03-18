# Participant Inference from Traces

## Purpose

This note defines the minimum inference grammar by which **participants** may be inferred from raw traces.

It builds directly on the corrected ontology already established in this branch:

- **participant** = vertical choreography
- **emission / trace** = observable output of a participant
- **horizontal family** = coupling episode among participants
- **coherence** = viable common temporality among participants

The key engineering problem is now clear:

> The temporal unit does not receive participants ready-made; it must infer them from persistent, synchronizing trace trains.

This note defines the minimum criteria for doing that.

---

## Why this note is needed

The earlier notes clarified:
- that events are not the true swarm participants
- that the real participants are vertical choreographies
- that emissions may play a role analogous to tokens in the LLM path
- that weight may arise from train persistence plus cross-train synchronization

But to use this on real data, one more step is needed:

> How do participant choreographies appear from raw traces?

That is the purpose of this note.

Without an inference grammar, the branch remains conceptually coherent but cannot touch reality cleanly.

---

## Core starting point

The first requirement is:

> identify the emitter / source

Without source identity, one cannot tell whether repeated traces belong to:
- one continuing participant
- multiple synchronizing participants
- one participant fading while another rises
- or a restart after silence

So participant inference begins with source-linked trace structure.

This does not mean source identity will always be trivial or directly given.
But it does mean that inference must be organized around:
- continuity of source-linked emissions
- their timing
- their recurrence
- their coupling with other trains

---

## Minimum inference spine

Participant inference can be reduced to six practical questions:

1. what counts as a trace  
2. what counts as continuity  
3. what counts as one train  
4. what counts as branching  
5. what counts as decay  
6. what counts as restart  

These six questions define the minimum basin for participant inference.

---

## 1. What counts as a trace

A trace is the smallest observable output that can be attributed to a source or emitter.

A trace may be:
- motor update
- sensor-linked update
- control update
- force adjustment
- message
- tool call
- behavioral micro-act
- institutional act
- social signal

The branch should not over-specify trace type too early.

A trace only needs to satisfy three conditions:

- it occurs at a time
- it is attributable to a source or provisional source
- it is discrete enough to serve as a local unit in a train

Compactly:

> A trace is a time-local, source-attributable observable emission.

This is the starting unit for participant inference.

## Direction is emergent

A trace or emission should not be treated as directional in itself.

An emission is only a local occurrence:
- time-local
- source-attributable
- minimally processable

Direction does not belong to the isolated emission.
It emerges from:
- the persistence of the train
- the ordering of emissions through time
- the coupling of that train with other trains
- and the larger choreography in which the emission participates

So a single emission should not be labeled too quickly as:
- upward
- downward
- stabilizing
- destabilizing
- advancing
- retreating

Those are properties of unfolding choreography, not of isolated traces.

Compactly:

> Events are directionless; direction emerges from temporally connected choreographies.

This is important for inference, because participant discovery should begin from repetition and continuity, not from prematurely assigned directional meaning.

---

## 2. What counts as continuity

Continuity is the condition under which repeated traces are treated as belonging to one ongoing process rather than as isolated emissions.

The simplest first criterion is:

- repeated traces from the same source
- within a viable continuity window
- with enough recurrence to suggest ongoing activity

So continuity is not identity in a metaphysical sense.
It is an operational judgment that:
- the train is still alive
- silence has not yet broken the line
- a participant may still be treated as ongoing

Continuity should therefore be based primarily on:
- repetition
- temporal nearness
- source persistence

Compactly:

> Continuity is repetition from a source sustained within an allowable temporal gap.

---

## 3. What counts as one train

A train is the ordered unfolding of traces from one participant.

A first engineering rule is:

> one train = continuity of repeated traces from the same emitter/process.

This means that a train exists when:
- traces are source-linked
- continuity holds
- no stronger reason exists to split the process into separate participants

A train should therefore be treated as:
- persistent
- ordered
- source-linked
- capable of strengthening or weakening

This is crucial because participant inference is really train inference.

A participant is not inferred from one trace.
It is inferred from the persistence of a train.

Compactly:

> A participant appears when a source-linked trace train persists strongly enough to be treated as one ongoing choreography.

---

## 4. What counts as branching

Branching is the hardest case and should be treated carefully.

A first useful engineering rule is:

> branching appears when simultaneity or near-simultaneity makes one train couple strongly with another or appear to split into parallel active lines.

In other words, branching is not merely repetition.
It is repetition under conditions of:
- overlap
- simultaneity
- coupling spread
- or divergence into parallel continuation paths

This means branching should initially be inferred from:
- same-time or near-time multi-trace episodes
- stronger-than-usual coupling density
- local emergence of parallel active paths

At first, it may be enough to say:

- if repetition is sequential and source-stable, treat it as one continuing train
- if parallel near-time emissions create multiple viable continuation lines, treat it as branching or coupling expansion

Compactly:

> Branching is repetition under simultaneity pressure that creates multiple viable continuation paths or coupling episodes.

This should remain provisional in early prototypes.

---

## 5. What counts as decay

Decay is the weakening of a train.

At first, decay should be treated operationally through:
- falling frequency
- larger gaps between emissions
- weakening recurrence
- shrinking coupling support
- dropping activation or relevance

So decay is not disappearance yet.
It is loss of persistence strength.

The simplest criterion is:

- if a train emits less often
- and/or receives less coupling support
- over a meaningful interval
- it is decaying

This is important because a decaying train may still matter.
It may still be recoverable or become background disposition rather than vanish entirely.

Compactly:

> Decay is the weakening of a source-linked train through reduced recurrence and reduced support.

---

## 6. What counts as restart

Restart is renewed train emergence after a break.

A first engineering rule is:

> restart = renewed emissions after sufficient silence or after a larger phase break.

This means restart should be inferred when:
- a train had become silent or yielded
- the silence exceeds the continuity window
- traces begin again in a way that suggests reactivation rather than mere continuation

The phrase “silence before a narrative tick” points toward a deeper version of this rule, but for the first engineering pass the simpler formulation is better:

- restart follows silence or phase break

Later, stronger structural transitions may be aligned with:
- Narrative Tick logic
- UD-cycle turning points
- or higher-level phase resets

But not yet.

Compactly:

> Restart is the reappearance of a train after silence long enough to break ordinary continuity.

---

## Minimum inference sequence

A simple participant-inference sequence now becomes possible.

### Step 1 — detect traces
Identify discrete, time-local emissions.

### Step 2 — assign or infer source
Group traces provisionally by emitter/process identity.

### Step 3 — test continuity
Determine whether repetition remains within a viable continuity window.

### Step 4 — infer trains
Treat sufficiently persistent source-linked repetitions as ongoing trains.

### Step 5 — detect coupling/branching
Look for same-time or near-time episodes where trains couple or diverge.

### Step 6 — track decay
Detect weakening recurrence and loss of support.

### Step 7 — detect restart
Mark renewed train activity after silence or phase break.

This is likely the minimum viable inference loop.

---

## Why repetition matters so much

This note makes clear that repetition is central.

Repetition underlies:
- trace recognition
- continuity
- train identity
- decay detection
- restart detection

This does not mean raw mechanical sameness.
It means recurrence of source-linked output strongly enough to support participant inference.

A useful summary is:

- **trace** = repetition begins
- **continuity** = repetition persists
- **train** = repetition forms an ongoing line
- **branching** = repetition enters simultaneity-driven parallelization
- **decay** = repetition weakens
- **restart** = repetition returns after silence

This is one of the simplest and strongest reductions yet.

---

## Provisional role of simultaneity

Simultaneity enters mainly in two places:

### 1. Coupling
When trains emit in the same or near-time window, they become horizontally relevant to one another.

### 2. Branching pressure
High same-time or near-time coupling may indicate:
- expansion of one train’s influence
- temporary coupling episode
- or a more serious branching structure

So simultaneity is not the source of participant identity.
It is the source of:
- coupling
- resonance
- branching pressure
- and coherence/disunity dynamics among already inferred trains

This distinction should remain stable.

---

## Minimum data assumptions

The first implementation should assume only that traces provide:

- source or provisional source
- timestamp
- trace type
- optional magnitude / intensity
- optional relation to neighboring traces

That is enough to begin participant inference.

The method should not require:
- full semantic labels
- task understanding
- complete world models
- exact symbolic interpretation

This keeps the branch in the right engineering spirit.

---

## What this note does not yet solve

This note intentionally does not yet define:

- exact emitter-identification algorithms
- exact continuity-window values
- exact similarity metrics for grouping traces
- exact branch/split equations
- exact global coherence formalism
- exact Narrative Tick integration
- exact sleep/reset logic

Those belong later.

The purpose here is only to define the minimum inference grammar.

---

## Suggested engineering consequence

This note suggests that the next code-facing prototype should not start from pre-declared participants if real data is used.

Instead, it should include a first inference pass that:
- reads traces
- groups them by source
- builds provisional trains
- tracks continuity, decay, and restart
- then only later promotes trains to participants

That is likely the correct bridge from raw data to temporal-unit structure.

---

## Closing statement

Participant inference begins not with abstract choreography, but with source-linked emission trains.

The key reduction is:

- **trace** = source-attributable local emission
- **continuity** = repetition within a viable window
- **train** = persistent line of repetition from one source
- **branching** = simultaneity-driven coupling or split into parallel lines
- **decay** = weakening repetition and support
- **restart** = renewed train emergence after silence or phase break

From this basis, participant choreographies may begin to appear.

That is the minimum inference basin now required for real-data contact.
