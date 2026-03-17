# Proto Temporal Unit

## Purpose

This note defines the first minimal engineering basin for a temporal unit in the RGPx pre-metric extensions branch.

The temporal unit is not yet treated here as a full world model, a full robotics substrate, or a finished cognitive architecture.

It is treated as a **minimal temporal interpretation swarm** whose job is to turn incoming events into an active field of:
- longitudinal choreography strings
- simultaneity families
- changing weights
- replay dynamics
- coherence-sensitive cutoff states

This note exists so that future implementation work can begin from a stable nucleus rather than from drifting intuition.

---

## Why this unit is needed

Current LLMs are powerful at:
- pattern recognition
- symbolic interpretation
- linguistic compression
- explicit reasoning
- response generation

But they largely operate in a kind of eternal present.

They can model time, but they do not strongly live through unfolding time. They do not naturally maintain a temporally active field of:
- persistence
- decay
- unresolvedness
- simultaneous pressures
- longitudinal drift
- coherence formation
- replay of becoming

The temporal unit is proposed as the missing substrate that provides:
- perspective rather than only context
- becoming rather than only representation
- active choreography rather than only static relation

A concise formulation is:

> The temporal unit lives the unfolding; the LLM cortex reads and articulates its patterns.

---

## Design bias

The temporal unit should not be designed as a centralized controller with hand-crafted global intelligence.

It should be designed in the same spirit that makes LLMs powerful:
- simple process elements
- repeated local updates
- light-weight representations
- global structure emerging from distributed interactions

So this proto design follows a swarm bias:

> The temporal unit is best treated as a swarm of simple temporal processes whose collective behavior yields replay, association, weighting, cutoff, and perspective.

This note therefore aims for the smallest set of primitives that can produce meaningful temporal behavior.

---

## Core role of the temporal unit

The temporal unit has five high-level responsibilities:

1. **clock task arrival and subsequent events**
2. **maintain unique longitudinal choreography strings**
3. **form simultaneity families across strings**
4. **replay and spread activation through the active event universe**
5. **cut off broad replay when a sufficient coherence basin forms**

The temporal unit does not itself need to produce rich language.
Its job is to maintain the active temporal field from which the LLM can interpret and respond.

---

## First primitive: clock the corridor

The first thing the temporal unit does is not to reason, but to clock.

When a task arrives, the temporal unit creates a case corridor:
- a new temporal line of unfolding
- a place in which later events can be clocked
- a live spacetime corridor that can later be re-walked

Then every subsequent event is clocked relative to that corridor.

Strong formulation:

> No temporal intelligence without a clocked corridor.

This is what later makes possible:
- retrospective traversal
- replay
- association
- weighting
- drift detection
- coherence cutoff

---

## Event transduction

Incoming events do not remain primary as isolated source-events once inside the temporal unit.

Outside the temporal unit, an event may still be described as:
- visual input
- auditory input
- touch signal
- instruction
- interruption
- contradiction
- model action

Inside the temporal unit, that event is re-identified by participation:
- what choreography it joins
- what simultaneity family it enters
- what pressure it contributes
- what role it plays in coherence or disunity

So the event is not erased, but transformed.

Strong formulation:

> In the temporal unit, events stop being things and start being functions in becoming.

At the same time, source identity should remain recoverable when action is required.

So the design principle is:

- **foreground identity**: role in active choreography
- **background identity**: recoverable source trace for action and grounding

Another compact formulation:

> Choreography determines what matters; source trace determines where action lands.

---

## Uniform event interface

Future sensors may eventually produce events in pulse-like or burst-like forms closer to biological signaling.

But the first engineering version should remain simpler.

Sensors or upstream systems should provide events in a uniform interface format. Internally, the temporal unit can then treat them as temporal perturbations.

So the rule is:

- externally: events arrive as simple structured packets
- internally: events behave like uniform temporal perturbations in the swarm

Compact formulation:

> Externally, events may be simple structured packets. Internally, they should behave like uniform temporal perturbations.

---

## Minimum event record

The event record should remain minimal and mostly static.

It should not try to store changing swarm interpretations as fixed event properties.

### Minimum event fields

- `event_id`
- `case_id`
- `arrival_tick`
- `source_channel`
- `event_type`
- `content_summary`

Optional minimal anchors:
- `source_reference`
- `payload_strength`

That is enough for version 1.

Fields such as:
- status
- choreography membership
- simultaneity family
- drift significance
- current importance

should **not** be treated as stable event fields.

Those should emerge from the present swarm state.

---

## Static event layer vs dynamic swarm layer

A crucial design split:

### Static layer
The event ledger stores minimally specified historical events.

### Dynamic layer
The swarm continuously generates, at the present clock instant:
- active/inactive status
- choreography participation
- simultaneity grouping
- event weighting
- drift significance
- dominant basin
- replay frontier

So the temporal unit should not mainly store dynamic labels on events.  
It should continuously generate those labels through swarm behavior.

Strong formulation:

> Events should remain minimally specified historical occurrences; choreography membership, simultaneity coupling, drift relevance, and weight should be emergent present-state functions of the temporal swarm, not fixed stored properties of the event itself.

---

## Longitudinal choreography strings

A choreography string is a unique longitudinal family of events.

It is not just a sequence. It is a temporally unfolding organization of:
- tensions
- reinforcements
- decays
- transitions
- divergence points
- stabilization patterns

So an event string is best understood as a **gradient choreography**.

### Properties of choreography strings
- each string is longitudinally unique
- events do not casually belong to many strings
- each string has its own becoming
- each string has its own unfolding identity

This gives the diachronic axis of the temporal unit.

---

## Simultaneity families

Cross-choreography coupling does not occur because one event belongs to many strings.

It occurs because distinct events in distinct strings may be clocked within the same or nearly the same temporal slice.

These form **simultaneity families**.

### Simultaneity family
A simultaneity family is the set of distinct events that occur:
- at the same timestamp
- or in the same active temporal window

This gives the synchronic axis of the temporal unit.

So the architecture has two core organizations:

- **longitudinal strings** = unique unfolding lines
- **simultaneity families** = cross-string temporal coupling

Strong formulation:

> A choreography string is a unique longitudinal family of events. Cross-choreography coupling does not occur because one event belongs to many strings, but because distinct events are clocked within the same temporal slice.

---

## Minimum temporal slices

Version 1 does not need many clocks, but it does need more than one present.

Use at least these temporal slices:
- `immediate_now`
- `short_now`
- `task_now`
- `longer_arc_now`

These slices allow the swarm to maintain:
- immediate perturbation
- short persistence
- task-level structure
- longer-arc drift or coherence

This is enough to prevent complete flat presentism.

---

## Minimum process rules

The proto temporal unit should begin with a small set of local rules.

### Rule 1 — Clock all arrivals
Every task arrival and every later event is clocked into the corridor.

### Rule 2 — Attach longitudinally
Each new event attaches to one active choreography string or starts a new one.

### Rule 3 — Group synchronically
Events arriving in the same or near-same temporal slice form simultaneity families.

### Rule 4 — Maintain changing weight
Weights are not fixed. They are updated by:
- persistence
- decay
- reinforcement
- suppression
- simultaneity boost

### Rule 5 — Replay on new arrival
A new event triggers replay of its choreography string.

### Rule 6 — Spread through simultaneity
During replay, events in the same simultaneity family activate their own choreography strings.

### Rule 7 — Track coherence formation
The swarm monitors whether active strings are:
- reinforcing
- conflicting
- fading
- stabilizing
- reorganizing

### Rule 8 — Cut off when coherence stabilizes
Replay stops broadening when a sufficiently stable resonance plateau forms.

### Rule 9 — Hand off to LLM
The LLM receives the active field summary and interprets:
- what pattern dominates
- what relation is active
- what action mode is implied

---

## Dynamic memory through replay

The temporal unit should not treat memory as static storage alone.

When a new event arrives:
- it attaches to a choreography string
- that string is replayed
- the new event is interpreted through how it perturbs the replayed line

So memory is dynamic.

Strong formulation:

> Dynamic memory may consist not in storing prior events statically, but in reactivating their corridor when a new event arrives that resonates with them.

This replay is one of the central functions of the temporal unit.

---

## Association through simultaneity

Replay does not stop at one string.

As replay encounters an event, that event’s simultaneity family may activate events in other strings. Those strings then become active as well.

So association emerges not through shared event identity, but through temporal co-presence.

This gives:
- cross-case linkage
- transfer
- resonance
- broader active fields
- richer interpretation

Strong formulation:

> Replay spreads through simultaneity families, not through a crude notion of shared-event ownership.

---

## Retrospective corridor traversal

The temporal unit must also be able to walk backward through the corridor.

This is important for:
- holism
- debugging
- drift detection
- reinterpretation

A holistic view is not a static top-down snapshot. It is built by re-walking the spacetime corridor of the task.

So the temporal unit should support:
- task-arrival recall
- replay from earlier corridor segments
- re-weighting of earlier events in light of later ones
- divergence-point identification

Strong formulation:

> The temporal unit is not only a forward-weighting device. It is also a case-unravelling engine: it reconstructs the becoming of the present by re-walking the event corridor and re-weighting each step in light of the whole.

---

## Weight

Weight should not be treated as one simple scalar only, though version 1 may approximate it that way.

Two broad components matter:

### Longitudinal weight
Within a choreography string:
- persistence
- repetition
- reinforcement
- resistance to decay
- rate of change

### Simultaneity weight
Across strings:
- co-firing breadth
- simultaneity density
- cross-string resonance
- slice coupling

This means weight is partly vertical within strings and partly horizontal across strings.

This is important because simultaneity itself contributes to coherence and therefore to significance.

---

## Simultaneity, non-simultaneity, and the UD premise

The temporal unit naturally yields two opposed but necessary tendencies:

### Non-simultaneity gives
- differentiation
- unfolding
- sequence
- individuality of strings

### Simultaneity gives
- coherence
- coupling
- shared presence
- resonance

This is the temporal basis of the UD cycle.

Strong formulation:

> The UD cycle may be grounded in the temporal unit itself: non-simultaneity drives differentiation and unfolding, while simultaneity drives coherence and shared resonance. Intelligence lives in the managed tension between them.

Too much non-simultaneity leads to fragmentation.  
Too much simultaneity leads to over-collapse or rigidity.  
Viable intelligence requires dynamic balance.

---

## Coherence and cutoff

The swarm should not replay forever.

It needs a cutoff rule.

Cutoff should not be based merely on exhaustion or arbitrary step count. It should be based on **coherence stabilization**.

Broad activation and replay should continue until:
- one active field becomes dominant enough
- conflict drops enough
- reinforcement persists long enough
- and a resonance plateau forms

Strong formulation:

> The cutoff of broad associative replay may be governed by conservation of coherence: replay continues until the active choreography field settles into a resonance basin that preserves enough coherence to support action, interpretation, or further learning.

This gives the temporal unit a principled stopping condition.

---

## Φ interpretation in the proto unit

In this architecture, Φ may be approximated as a measure of how strongly distinct longitudinal choreography strings are coupled through simultaneity families relative to how independently they are unfolding.

This means:
- non-simultaneity preserves differentiation
- simultaneity generates coherence
- Φ tracks meaningful temporal coupling across distinct lines

Strong formulation:

> Coherence is not the collapse of many choreography strings into one, but the sustained simultaneity relation among distinct strings that remain longitudinally differentiated while temporally coupled.

Version 1 does not need a final mathematical Φ definition, but it should preserve this intuition.

---

## LLM handoff interface

The LLM should not do the temporal work itself.

The temporal unit hands it a present field summary.

### Minimum handoff contents
- dominant choreography string
- linked choreography strings
- current simultaneity emphasis
- coherence score or plateau state
- unresolved tensions
- suggested mode

### Suggested modes
- `observe`
- `clarify`
- `patch`
- `rebuild`
- `act`
- `hold`

The LLM then:
- identifies the active pattern
- articulates its meaning
- proposes action
- translates temporal perspective into language and plan

Strong formulations:

> The temporal unit gives perspective; the LLM gives interpretation.

and

> The temporal unit lives the unfolding; the LLM cortex reads and articulates its patterns.

---

## Toy environment for version 1

Start with one narrow use case only:
**document / file repair**

Why:
- event stream is easy to simulate
- contamination is observable
- replay logic is testable
- patch / rebuild / clarify decisions are concrete

### Example event types
- `task_arrival`
- `instruction_received`
- `clarification_received`
- `patch_attempt`
- `duplication_detected`
- `stale_remnant_detected`
- `evidence_mismatch_detected`
- `coherence_restored`
- `rebuild_triggered`

### Example choreography strings
- `contamination_rising`
- `coherence_restoration`
- `target_unclear`
- `patch_overreach`
- `rebuild_readiness`

### Example simultaneity families
- same-turn instruction + contradiction signal
- patch attempt + stale-remnant persistence
- evidence report + rendered mismatch

That is enough to prototype the unit without full sensor complexity.

---

## Minimal implementation path

The proto-temporal-unit engineering should begin with:

### 1. Event ledger
A simple file or structure that stores minimally specified events.

### 2. Swarm state
A dynamic present-state structure that stores:
- active events
- choreography strings
- simultaneity families
- weights
- dominant basin
- unresolved tensions

### 3. Replay engine
Given a new event:
- attach longitudinally
- replay main string
- spread by simultaneity
- update weights

### 4. Cutoff rule
Stop when coherence plateau is strong enough.

### 5. LLM interpreter interface
Summarize the active field for symbolic articulation.

That is enough for a first prototype.

---

## What version 1 should avoid

Do not start with:
- full biological neuron imitation
- detailed spike-train realism
- full robotic sensory stack
- rich affect simulation
- exact Φ formalization
- complex multi-agent world modeling

These may come later.

Version 1 should prove that:
- simple clocked events
- unique strings
- simultaneity families
- replay
- swarm weighting
- coherence cutoff
can already produce useful temporal perspective.

---

## Open questions

The following remain open and should not be over-fixed in version 1:

- exact event-to-string attachment rule
- exact simultaneity window size
- exact weight update equation
- exact resonance threshold
- exact Φ formalization
- exact mapping from coherence field to action modes
- how many clocks are ultimately needed
- how source back-reference should be represented for real sensors

These are exploration points, not blockers.

---

## Immediate next engineering use

This file should be used to task Codex toward small scaffolds such as:
- event schema
- swarm-state schema
- toy simulation loop
- replay function
- simultaneity grouping function
- cutoff detector
- LLM handoff summary format

It is intended as a launchpad, not a finished theory.

---

## Closing statement

The proto temporal unit is the first practical attempt to specify a time-sensitive substrate for RGPx-style AI.

It is intentionally minimal.

It does not try to encode full intelligence directly. Instead, it defines a small swarm of temporal processes whose collective behavior may yield:
- dynamic memory
- association
- case-unravelling
- perspective
- coherence-sensitive cutoff
- and a meaningful temporal field for the LLM cortex to interpret

If this proto design works even in simple form, it would mark a genuine step from static representational systems toward architectures that participate in becoming rather than only describing it.
