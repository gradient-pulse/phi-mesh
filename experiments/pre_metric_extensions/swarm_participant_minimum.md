# Swarm Participant Minimum

## Purpose

This note defines the minimum ontology and rule grammar for a swarm participant in the proto temporal unit branch.

It exists to correct a key ambiguity in earlier sketches:

> The swarm participant should not be treated as an event.

An event is better understood as something a participant emits.

The true participant is the **vertical choreography**.

This note defines the smallest useful way to think about:
- what a participant is
- what an event is
- how participants couple
- what coherence means between participants
- and what minimum local rules might be sufficient for swarm behavior to emerge

---

## Core correction

Earlier sketches risked treating events as if they were the active swarm units.

That is now treated as incorrect.

A participant must be something that can:
- persist through time
- emit updates
- strengthen or weaken
- couple to others
- restart after failure
- pass through a UD cycle

An isolated event cannot do this.

A **vertical choreography** can.

So the corrected architecture is:

- **participant** = vertical choreography
- **event** = emission or observable update of a participant
- **horizontal family** = coupling episode among participants through same-time or near-time emissions

This is the minimum ontology going forward.

---

## Participant

A participant is a **vertical choreography**:
- a temporally persistent local process
- unfolding through time
- producing events as traces of its activity
- capable of entering and leaving coupling relations
- capable of strengthening, weakening, yielding, and restarting

Examples in embodied action may include:
- shoulder adjustment choreography
- forearm rotation choreography
- wrist alignment choreography
- finger shaping choreography
- grip-force choreography
- eye-hand coupling choreography
- balance compensation choreography

The participant is not one event inside these lines.  
It is the line of becoming itself.

---

## Event

An event is an **emission** of a participant.

It is not the agent of swarm behavior.
It is the trace or discharge by which a participant becomes observable, measurable, or coupled.

Events may be:
- observational
- participatory
- corrective
- stabilizing
- destabilizing
- confirming
- mismatch-revealing

But regardless of kind, an event should be treated as:
- local output
- temporal mark
- coupling opportunity
- evidence of participant state

Compactly:

> Events are not the swarm participants; they are the expressions of swarm participants.

---

## Horizontal family

A horizontal family is a **coupling episode** among participants.

It forms when emitted events from distinct participants occur:
- at the same tick
- or within the same near-time window

A horizontal family therefore does not define identity.
It defines temporal encounter.

This means:
- vertical choreographies persist as participants
- horizontal families appear as episodes of common temporality among those participants

So the horizontal layer is not a second kind of participant.
It is the coupling space through which participants synchronize.

---

## Coherence

Once the participant is correctly identified as the vertical choreography, coherence becomes much clearer.

Coherence is not primarily event-to-event agreement.

It is:

> the degree to which vertical choreographies synchronize into a viable common temporality.

This means coherence rises when participants:
- line up sufficiently in time
- support rather than destructively disrupt one another
- maintain a shared unfolding
- remain coupled strongly enough to preserve common temporality

And coherence falls when participants:
- drift out of sync
- lose mutual support
- fragment into isolated trajectories
- or force incompatible local timings on one another

Compactly:

> Coherence between participants is the quality of temporal synchronization among vertical choreographies through the events they emit.

---

## Why this matters for movement

This correction makes coordinated movement easier to understand.

Movement need not be modeled as one command sent downward.
It can be understood as resonance among many participant-choreographies.

For example, a fluid grab may involve:
- shoulder choreography
- elbow choreography
- wrist choreography
- finger choreography
- grip-force choreography
- balance choreography
- eye-hand choreography

Each is a vertical participant.

Their events couple horizontally.
When the coupling is good, the act feels fluid.

This leads to a strong formulation:

> Movement is not issued as a single order; it emerges as resonance among many temporally unfolding choreographies.

This also clarifies:
- clumsiness = poor synchronization among participants
- grace = high coherence among participants
- skill = stable resonant patterns that can be re-entered quickly
- muscle memory = retained dispositions for re-forming resonant participant couplings

---

## Minimum participant state

A first swarm participant does not need rich intelligence.

It needs only minimal local state.

Suggested minimum state:

- `participant_id`
- `activation`
- `last_tick_active`
- `emission_count`
- `cycle_phase`
- `vertical_history`
- `active_horizontal_links`

Where:

- `activation` = current strength or salience
- `last_tick_active` = most recent active emission tick
- `emission_count` = number or rate of emitted updates
- `cycle_phase` = rough local phase such as rising, stabilizing, fading, restarting
- `vertical_history` = minimal memory of its own unfolding
- `active_horizontal_links` = current coupling episodes with other participants

That is enough for a first local rule grammar.

---

## Minimum local rules

A participant should remain nearly mindless.
It should not try to understand the whole.

Its rules should be simple and local.

### 1. Clock
A participant knows:
- now
- near-now
- older-than-now

### 2. Emit
A participant may emit an event when its activation is high enough or changing enough.

### 3. Couple
A participant couples horizontally when its emissions coincide or near-coincide with those of other participants.

### 4. Reinforce
A participant’s activation rises when:
- its own emissions persist
- its neighboring participants are synchronizing with it
- mutual support is sustained

### 5. Decay
A participant’s activation falls when:
- emissions dry up
- support from neighboring participants weakens
- local timing becomes unstable

### 6. Yield
A participant quiets when activation falls below a viability threshold.

### 7. Restart
A participant can re-enter with a new cycle when local conditions again support activation.

### 8. Track local coherence
A participant does not detect “the whole.”  
It only tracks whether:
- neighboring participants are supporting it
- support persists
- timing remains viable
- fragmentation is rising or falling

These rules are intentionally simple.

---

## Operational local coherence

Local coherence should not be defined semantically at first.

It should be defined operationally.

A participant experiences higher local coherence when:
- vertical continuity persists
- horizontal couplings are active
- neighboring participant activity is mutually sustaining
- support lasts more than one tick
- instability does not explode

So a first approximation is:

- good spread = activity propagates and stabilizes
- bad spread = activity propagates and fragments

This gives a simple working distinction without requiring full semantic understanding.

Compactly:

> Local coherence can be defined operationally as sustained, mutually reinforcing activity among neighboring participants with limited instability.

---

## Relation to PoLA, coherence conservation, and UD

The participant does not need to know these principles abstractly.

But its local behavior may instantiate them.

### PoLA
Participants tend toward viable low-strain continuation paths.

### Conservation of coherence
Participants avoid destructive over-dominance and seek supportable synchronization.

### UD cycles
Participants rise, differentiate, couple, destabilize, yield, and restart.

So the participant need not reason about these principles.
It only needs to follow local update rules whose global consequences approximate them.

---

## Readout to the LLM

The LLM should not inspect raw events only.
It should read participant-field summaries.

The minimum useful readout is:
- most active participants
- strongest horizontal couplings
- current coherence level
- rising vs fading participant clusters
- suggested action mode

This preserves the division of labor:

- temporal unit = nearly mindless coherence-seeking swarm of participants
- LLM = symbolic interpreter of the participant field

---

## Closing statement

This note establishes the minimum correction required for the temporal-unit architecture:

> The swarm participant is not the event.  
> The swarm participant is the vertical choreography that emits events as it unfolds.

From this correction follows a much cleaner build logic:
- events become emissions
- horizontal families become coupling episodes
- coherence becomes common temporality among participants
- and movement becomes resonance among many participant-choreographies rather than execution of a single command

This is the correct minimum basin for future participant-level engineering.
