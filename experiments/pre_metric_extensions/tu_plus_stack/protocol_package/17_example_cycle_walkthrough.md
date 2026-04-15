# T-Protocol — Example Cycle Walkthrough v1

## Purpose

This document provides a concrete end-to-end walkthrough of one simplified T-Protocol cycle.

Its purpose is to make the protocol easier to understand operationally by showing:

- what enters the field
- what TU does
- what TU+ does
- what cortexLLM does
- how the shared state changes
- how returned traces later correct or strengthen the field

This is not a full benchmark example and not a domain-specific implementation manual.

It is a minimal illustrative walkthrough of the protocol logic.

---

## Core principle

T-Protocol is easier to grasp when seen as a live recursive field rather than as a set of abstract documents.

This walkthrough therefore shows one concrete cycle moving through:

- input
- structural mapping
- comparative prediction
- symbolic framing
- state update
- later returned-trace correction

Compactly:

> One cycle is enough to show how T-Protocol differs from one-shot prompting.

---

## Scenario

Assume a simple unfolding field:

- one provisional source, **A**
- current input suggests A shifts slightly right, then appears to pause
- no second source is yet clearly present
- no strong contradiction is present
- the current task frame is observation rather than action

This is a calm, minimal scenario intended only to show the protocol mechanics.

---

## Step 1 — Input slice arrives

### Example input slice

```json
{
  "source_type": "frame_sequence_summary",
  "time_window": "frames_1_4",
  "content": [
    "object A shifts slightly right",
    "movement slows",
    "A appears to pause near center-right"
  ]
}
```

What this means

The protocol does not begin by asking for a narrative answer.

It begins with a structured slice of unfolding input.

This slice becomes available to TU as the current field material.

---

## Step 2 — TU maps structure

### TU reads
-	input_slice
-	prior source_hypotheses if any
-	prior motion_tokens if any
-	prior active_trains if any
-	returned_traces if any

### TU task

TU maps:
-	provisional source identity
-	primitive motion/process traces
-	train continuity
-	early persistence status
-	low-level coherence snapshot

### Example TU output

```json
{
  "source_hypotheses": [
    {
      "source_id": "A",
      "hypothesis_type": "moving_object",
      "confidence": 0.74,
      "stability": "provisional",
      "notes": "persistent source near left-to-center path"
    }
  ],
  "motion_tokens": [
    {
      "token_id": "t1",
      "source_id": "A",
      "time_slice": "f1_f2",
      "displacement_delta": "small",
      "direction": "rightward",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.68
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "smaller",
      "direction": "rightward",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.66
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2"],
      "persistence": "rising",
      "status": "active",
      "restart_of": null,
      "weight": 0.71
    }
  ],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "coherence_state": {
    "train_persistence_level": 0.71,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.79,
    "fragmentation_level": 0.09,
    "coherence_summary": "single stable train forming, low fragmentation"
  }
}
```

### What TU has done

TU has:
-	preserved A as a hypothesis, not a certainty
-	emitted primitive trace bundles
-	formed an active train
-	avoided symbolic interpretation
-	kept the field sparse and structural

---

## Step 3 — TU+ compares and predicts

### TU+ reads
-	source_hypotheses
-	motion_tokens
-	active_trains
-	coupling_state
-	choreography_memory_refs
-	coherence_state
-	mismatch_history
-	downward_bias

### TU+ task

TU+:
-	compares the current train against choreography memory
-	detects whether the pattern looks familiar
-	predicts likely continuation
-	flags whether instability or higher attention is needed

### Example TU+ output

```json
{
  "choreography_memory_refs": [
    {
      "choreography_id": "approach_then_pause",
      "match_type": "partial",
      "similarity": 0.63,
      "memory_scope": "tu_near_store"
    }
  ],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.24,
    "watch_targets": ["A"]
  },
  "predicted_trains": [
    {
      "predicted_train_id": "train_A_pred_1",
      "choreography_id": "approach_then_pause",
      "source_id": "A",
      "predicted_token_sequence": ["tp3", "tp4"],
      "confidence": 0.66,
      "continuation_type": "hold_or_resume"
    }
  ],
  "coherence_state": {
    "train_persistence_level": 0.73,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.80,
    "fragmentation_level": 0.08,
    "coherence_summary": "single stable train, likely pause or hold continuation"
  },
  "mismatch_history": []
}
```

## What TU+ has done

TU+ has:
-	recognized a partial pattern resemblance
-	proposed a likely continuation
-	not overcommitted
-	not forced symbolic explanation
-	preserved the field as predictive rather than merely descriptive

---

## Step 4 — cortexLLM interprets and biases

### cortexLLM reads
-	coherence_state
-	attention_state
-	predicted_trains
-	mismatch_history
-	notes_on_state_quality

### cortexLLM task

cortexLLM:
-	frames the current field symbolically
-	decides whether to hold, act, or request more attention
-	sends bounded downward guidance

### Example cortexLLM output

```json
{
  "cortex_context": {
    "task_frame": "monitor unfolding source",
    "interpretive_context": "ordinary movement with likely pause",
    "current_goal_pressure": "observe",
    "hold_or_act": "hold"
  },
  "downward_bias": {
    "attend": ["A"],
    "hold": true,
    "compare": ["approach_then_pause"]
  },
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.26,
    "watch_targets": ["A"]
  },
  "notes_on_state_quality": {
    "state_quality": "stable_but_sparse",
    "uncertainty_notes": ["source remains provisional"],
    "reset_recommendation": false
  }
}
```

### What cortexLLM has done

cortexLLM has:
-	framed the situation symbolically
-	preserved a hold stance
-	sent bounded downward guidance
-	not overwritten TU or TU+
-	not forced closure beyond what the field supports

---

## Step 5 — Shared state updates

After the three role passes, the shared state is updated.

### Example updated state (simplified)

```json
{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": [
      "object A shifts slightly right",
      "movement slows",
      "A appears to pause near center-right"
    ]
  },
  "source_hypotheses": [
    {
      "source_id": "A",
      "hypothesis_type": "moving_object",
      "confidence": 0.74,
      "stability": "provisional",
      "notes": "persistent source near left-to-center path"
    }
  ],
  "motion_tokens": [
    {
      "token_id": "t1",
      "source_id": "A",
      "time_slice": "f1_f2",
      "displacement_delta": "small",
      "direction": "rightward",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.68
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "smaller",
      "direction": "rightward",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.66
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2"],
      "persistence": "rising",
      "status": "active",
      "restart_of": null,
      "weight": 0.71
    }
  ],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "choreography_memory_refs": [
    {
      "choreography_id": "approach_then_pause",
      "match_type": "partial",
      "similarity": 0.63,
      "memory_scope": "tu_near_store"
    }
  ],
  "coherence_state": {
    "train_persistence_level": 0.73,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.80,
    "fragmentation_level": 0.08,
    "coherence_summary": "single stable train, likely pause or hold continuation"
  },
  "mismatch_history": [],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.26,
    "watch_targets": ["A"]
  },
  "cortex_context": {
    "task_frame": "monitor unfolding source",
    "interpretive_context": "ordinary movement with likely pause",
    "current_goal_pressure": "observe",
    "hold_or_act": "hold"
  },
  "downward_bias": {
    "attend": ["A"],
    "hold": true,
    "compare": ["approach_then_pause"]
  },
  "predicted_trains": [
    {
      "predicted_train_id": "train_A_pred_1",
      "choreography_id": "approach_then_pause",
      "source_id": "A",
      "predicted_token_sequence": ["tp3", "tp4"],
      "confidence": 0.66,
      "continuation_type": "hold_or_resume"
    }
  ],
  "action_state": {
    "action_mode": "hold",
    "selected_predicted_train": null,
    "operator_status": "inactive",
    "relay_notes": ""
  },
  "returned_traces": [],
  "notes_on_state_quality": {
    "state_quality": "stable_but_sparse",
    "uncertainty_notes": ["source remains provisional"],
    "reset_recommendation": false
  }
}
```

### What the update has done

The field now preserves:
-	current structural state
-	a predicted continuation
-	a contextual hold stance
-	readiness for the next cycle

It has not:
-	collapsed into prose
-	reset itself
-	forced stronger certainty than the field warrants

---

## Step 6 — Returned trace arrives later

Suppose the next observed return evidence is:

```json
{
  "trace_id": "rt1",
  "source_id": "A",
  "time_slice": "f4_f5",
  "observed_change": "held_position",
  "confidence": 0.82
}
```

This returned trace is then integrated into the next cycle.

### Case A — prediction broadly supported

If the returned trace fits the predicted “pause/hold” continuation:
	•	confidence in the relevant predicted train may rise
	•	mismatch remains low
	•	the pattern may strengthen toward provisional confirmation

### Case B — prediction weakened

If instead the returned trace showed sudden leftward motion:
	•	mismatch would be logged
	•	the predicted train would weaken
	•	a mild revision or branch split might follow

This is the core difference between:
	•	ordinary one-shot generation
and
	•	T-Protocol’s recursive accountability

---

## What this walkthrough shows

This single example shows that T-Protocol is not just:
	•	three prompts
	•	three voices
	•	a summarization trick

It is:
	•	a structured live field
	•	with differentiated roles
	•	acting on bounded state
	•	across cycles
	•	with prediction accountable to return evidence

---

## Minimal lessons for licensees

A licensee should take from this example that:
	1.	TU, TU+, and cortexLLM do different work
	2.	the shared state is the real memory field of the protocol
	3.	prediction matters
	4.	returned traces matter
	5.	symbolic framing must remain bounded
	6.	continuity is preserved through structured update, not prose recap

---

## Closing statement

This example is deliberately simple, but it shows the operational difference clearly.

A compact final formulation:

One T-Protocol cycle begins with structured input, passes through mapping, comparison, and interpretation, updates a live shared field, and remains answerable to later returned evidence rather than ending as disposable output.

