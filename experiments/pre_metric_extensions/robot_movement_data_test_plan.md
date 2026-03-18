# Robot Movement Data Test Plan

## Purpose

This note defines the first practical plan for testing the proto temporal unit on real robot movement data.

The aim is not to outperform existing robotics pipelines immediately.

The aim is to test whether the temporal-unit framing can extract a more useful coherence structure from robot movement traces than a plain trajectory/control description can.

The working hypothesis is:

> Real robot movement data may reveal vertical choreography-participants, participant emissions, and horizontal coupling episodes that ordinary trajectory descriptions flatten or miss.

This note defines the smallest disciplined path for testing that claim.

---

## Why this test matters

The proto temporal unit has so far been explored through:
- conceptual notes
- toy event streams
- a small toy simulator
- and a minimal visualization

That was necessary.

But the next step is to force the architecture into contact with real embodied traces.

Robot movement data is the right first contact point because it already contains:
- unfolding action
- sensor-linked updates
- correction under constraint
- success and failure structure
- temporally organized behavior

This makes it the first suitable arena for asking whether the temporal unit captures something operationally useful.

---

## Test question

The first test question is:

> Can the temporal-unit framing reveal coherence structure in robot movement data that a standard trajectory/control view does not make equally visible?

This can be made more specific:

- Can vertical participant-choreographies be identified in movement traces?
- Can horizontal coupling episodes be detected across these participants?
- Can late recovery, drift, clumsiness, fluidity, or restart be seen earlier or more clearly?
- Can the temporal-unit view produce a more actionable diagnosis of what the robot is doing?

This is the first operational question.

---

## Candidate data sources

The first version of this plan should remain narrow, but it is useful to identify candidate public sources.

### Candidate source types
- manipulation trajectories with robot actions over time
- synchronized sensor observations
- successful and unsuccessful episodes
- preferably reaching, grasping, lifting, or placing tasks

### Strong dataset candidates
- DROID
- BridgeData V2
- Open X-Embodiment subsets

These are not yet commitments for a large-scale study.
They are candidate sources for one carefully chosen first slice.

The key is to begin with:
- one task
- one embodiment
- one short sequence
- one coherence interpretation

---

## First recommended task slice

The first test should use a task simple enough to inspect by eye.

Recommended first slice:
- reach
- grasp
- lift
- possibly place

Why this slice:
- it contains obvious coordination demands
- it includes approach, contact, force adjustment, and post-contact stabilization
- it is rich enough to show choreography, but small enough to inspect manually

This is better than beginning with highly composite tasks.

---

## Ontology for the test

The temporal-unit interpretation should use the corrected ontology already established in this branch.

### Participant
A **vertical choreography**:
- a persistent local process unfolding through time

Examples in a robot movement context may include:
- end-effector approach choreography
- wrist orientation choreography
- gripper closure choreography
- lift-force choreography
- stabilization choreography
- visual alignment choreography

### Emission
A **participant emission**:
- a minimal observable update emitted by a participant

Examples may include:
- change in position
- change in velocity
- change in gripper state
- change in force/torque
- state transition in a local control thread
- sensor-linked update tied to one participant

### Horizontal family
A **coupling episode**:
- when emissions from distinct participants align in same-time or near-time windows

### Coherence
The degree to which participants synchronize into a viable common temporality.

This ontology must remain stable during the first test.

---

## Testable contrast

The first experiment should compare two descriptions of the same movement fragment.

### Baseline description
A standard trajectory/control description:
- path
- state updates
- correction events
- success/failure outcome

### Temporal-unit description
A choreography-based description:
- participant-choreographies
- emissions
- horizontal families
- coherence changes
- local recovery or fragmentation
- possible UD-like restart behavior

The aim is not yet quantitative superiority.
The aim is diagnostic contrast.

---

## Minimum success criterion

The first proof-of-concept is successful if the temporal-unit description can do at least one of the following better than the baseline description:

- identify emerging fragmentation earlier
- identify late recovery more clearly
- show why fluid motion is fluid
- show why clumsy motion is clumsy
- reveal a restart structure
- reveal which participant-choreographies lost synchronization
- suggest a more useful intervention point

If none of these happen, the framing needs revision.

---

## First practical workflow

### Step 1 — Select one short sequence
Choose one robot movement sequence of manageable length.

### Step 2 — Identify provisional participants
Map the sequence into a small set of vertical choreography-participants.

Do not aim for perfection.
Aim for a workable first segmentation.

### Step 3 — Define emissions
Choose the minimal update-bearing units emitted by participants.

These should be:
- temporally explicit
- inspectable
- comparable across participants

### Step 4 — Define horizontal coupling rule
Use a same-time or near-time window to detect coupling episodes.

### Step 5 — Compute a first coherence sketch
Track:
- participant persistence
- horizontal coupling density
- synchronization stability
- local fragmentation
- recovery behavior

### Step 6 — Compare with baseline
Describe the same fragment in ordinary trajectory/control language and compare what each framing makes visible.

---

## What to measure first

The first pass should stay light.

Suggested first measures:
- number of active participants
- number of participant emissions
- horizontal coupling count
- coupling density over time
- participant persistence
- participant dropout / restart
- coherence rise or fall around key moments
- whether late recovery appears

These are enough for a first proof-of-concept.

---

## Operational-advantage angle

This test is not only conceptual.

It opens the path toward operational advantage.

If the temporal-unit framing works, it may later help answer questions like:
- how many active participants are ideal for a task?
- when is the participant field too thin?
- when is it too crowded?
- when does coherence degrade under excess differentiated participation?
- what participant density best supports fluid task completion?

This is where the test connects to the larger RGPx aim.

A strong formulation:

> RGPx becomes operational when it can say not just what coherence is, but how much differentiated participation a task can sustain before coherence degrades.

That is the long-term horizon of this test path.

---

## What not to do yet

The first experiment should not:
- attempt full robotics redesign
- attempt policy learning
- claim benchmark superiority
- overfit to one dataset
- define too many participants
- force exact equations too early

The first test is interpretive and diagnostic.
Its value lies in disciplined reframing.

---

## Recommended immediate next file

After this note, the next practical file should probably be:

`experiments/pre_metric_extensions/robot_movement_first_slice.md`

That file should document one actual sequence:
- source
- task
- provisional participants
- emissions
- horizontal families
- coherence observations
- baseline comparison

That will turn this plan into a live proof-of-concept.

---

## Closing statement

The proto temporal unit is ready to encounter real embodied traces.

The first real test is not whether it can control a robot better end to end.
The first real test is whether it can reveal the living coherence structure of movement better than a plain trajectory/control description can.

If it can, even in one short grasp/lift sequence, then the architecture begins to cross from conceptual possibility into operational relevance.
