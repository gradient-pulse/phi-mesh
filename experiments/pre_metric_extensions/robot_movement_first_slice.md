# Robot Movement First Slice

## Purpose

This note documents the first narrow real-data contact point for the proto temporal unit branch.

The aim is not yet to validate the temporal unit in full.

The aim is to force the current ontology onto one real embodied movement fragment and see whether it reveals something intelligible.

This note therefore asks:

> Can one real robot movement fragment be described more clearly as interacting choreography-participants than as a plain path with corrections?

That is the immediate test.

---

## Why this file exists

The branch now has:
- a temporal-unit hypothesis
- a participant/emission ontology
- a swarm update grammar
- toy simulators and visualizations
- a robot movement data test plan

What it does not yet have is one concrete real slice where the grammar is applied by hand.

This file fills that gap.

It should remain narrow, inspectable, and modest.

---

## Scope of this first slice

This first slice should be:

- one short robot movement fragment
- preferably one reach / grasp / lift sequence
- from one embodiment
- with as few moving parts as necessary
- short enough to inspect manually

This is not yet a benchmark study.

It is a first interpretive contact between:
- real traces
- and the proto temporal-unit grammar

---

## Source

### Dataset / source name
[Fill in]

### Link / local reference
[Fill in]

### Embodiment / robot type
[Fill in]

### Task label
[Fill in]

### Sequence / episode identifier
[Fill in]

### Why this slice was chosen
[Fill in briefly]

Suggested criteria:
- clear motor traces
- manageable duration
- visible success or failure structure
- likely coordination demands across multiple sub-processes

---

## Baseline description of the movement

Describe the fragment first in ordinary trajectory/control language.

### Baseline summary
[Fill in]

Possible elements:
- start pose
- target object
- approach movement
- grasp attempt
- lift or failed lift
- correction
- success or failure

This is important because the temporal-unit description should be compared against this baseline.

---

## Raw trace view

List the traces actually available in the slice.

### Available trace channels
[Fill in]

Examples:
- joint positions
- joint velocities
- joint torques
- gripper state
- end-effector pose
- force/torque readings
- contact signal
- camera-linked markers
- controller action outputs

### Minimum trace subset used in this slice
[Fill in]

Keep the first slice small.
Use only the traces that are necessary to make participant inference possible.

---

## Emitter / source identification

Participant inference begins with identifying emitters or provisional sources.

### Provisional emitters
[Fill in]

Examples:
- shoulder or proximal joint control stream
- elbow / mid-arm stream
- wrist orientation stream
- gripper closure stream
- lift-force stream
- stabilization stream
- visual alignment stream

This section should remain provisional.
The first slice does not need perfect source metaphysics.
It only needs a workable starting segmentation.

---

## Trace definition for this slice

A trace is treated here as:
- time-local
- source-attributable
- minimally processable

### Trace rule used
[Fill in]

For example:
- a meaningful change in joint angle
- a gripper state transition
- a change in force reading beyond threshold
- a control update from one source stream

Important:
direction should **not** be treated as intrinsic to the isolated trace.
Direction emerges later from connected choreography.

---

## Continuity rule

State what counts as continuity for this slice.

### Continuity rule used
[Fill in]

Possible form:
- repeated source-linked traces within a continuity window
- with no silence long enough to break the train

This section should be explicit, even if approximate.

---

## Provisional trains

List the first inferred trains.

A train is the ordered unfolding of traces from one source/process.

### Train 1
- source:
- traces:
- continuity remarks:

### Train 2
- source:
- traces:
- continuity remarks:

### Train 3
- source:
- traces:
- continuity remarks:

[Add or remove as needed]

The point is not to be exhaustive.
The point is to make visible which source-linked repetitions are beginning to look like ongoing trains.

---

## Candidate participants

Promote only the strongest trains to provisional participant status.

### Participant 1
- inferred from train:
- provisional role:
- why it counts as persistent:

### Participant 2
- inferred from train:
- provisional role:
- why it counts as persistent:

### Participant 3
- inferred from train:
- provisional role:
- why it counts as persistent:

[Add or remove as needed]

Remember:
- participant = vertical choreography
- event / trace = participant emission

This section is the key step from raw data to temporal-unit ontology.

---

## Horizontal coupling episodes

Now mark same-time or near-time coupling among inferred participants.

### Coupling window used
[Fill in]

### Horizontal family A
- participants involved:
- traces involved:
- time window:
- why this counts as a coupling episode:

### Horizontal family B
- participants involved:
- traces involved:
- time window:
- why this counts as a coupling episode:

### Horizontal family C
- participants involved:
- traces involved:
- time window:
- why this counts as a coupling episode:

[Add or remove as needed]

This section should show where common temporality appears.

---

## Coherence observations

Describe where participant coherence appears to rise or fall.

### Coherence rising
[Fill in]

Examples:
- approach smooths into grasp preparation
- wrist and gripper align in time
- stabilization joins lift phase cleanly

### Coherence falling
[Fill in]

Examples:
- gripper closes too early or too late
- lift-force and wrist alignment drift apart
- stabilization lags behind approach
- correction appears but fails to re-synchronize the field

### Late recovery, if present
[Fill in]

### Restart, if present
[Fill in]

This is the heart of the slice.

---

## Direction as emergent choreography

This section is important.

Do **not** assign direction too early to isolated traces.

Instead describe how direction emerges from connected choreography.

### Observed directional emergence
[Fill in]

Examples:
- upward movement emerges from synchronized lift, grip, and stabilization trains
- drift emerges from decoupling among wrist, grip, and balance processes
- correction emerges from a new temporary resonance among previously misaligned participants

A useful reminder:

> Events are directionless; direction emerges from temporally connected choreographies.

---

## Comparison with baseline description

Now compare the two framings.

### What the ordinary trajectory/control view shows
[Fill in]

### What the temporal-unit view additionally shows
[Fill in]

Possible additions:
- which participant lost sync
- whether a failure was fragmentation rather than mere error
- whether recovery emerged late
- whether the act was fluid because multiple trains resonated well
- whether clumsiness was a coherence problem rather than just path error

This section determines whether the temporal-unit framing adds value.

---

## First judgment

Give a modest conclusion.

### Did the temporal-unit framing reveal anything nontrivial?
[Yes / No / Partly]

### What did it reveal?
[Fill in]

### What remained unclear?
[Fill in]

### Does this justify a second slice?
[Fill in]

This should remain sober and specific.

---

## Implications for next engineering step

Based on this slice, what is now needed most?

Possible answers:
- better participant inference rules
- better continuity-window definition
- clearer branching criteria
- a small importer/parser
- richer visualization
- more channels from the source data
- a second slice with clearer grasp/lift dynamics

### Immediate next adjustment
[Fill in]

---

## Closing statement

This file is the first real-data contact point for the proto temporal unit branch.

Its purpose is not to prove the architecture fully.
Its purpose is to test whether one real embodied movement fragment becomes more intelligible when read as:
- source-linked trace trains
- inferred vertical choreography-participants
- horizontal coupling episodes
- and changing coherence

If that framing reveals even one important structure that the plain trajectory/control view flattens, then the temporal-unit branch has crossed an important threshold.
