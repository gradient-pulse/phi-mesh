# Shared State Schema

## Purpose

This note defines the shared state object used by the prompt-instantiated TU / TU+ / cortexLLM triad.

The purpose of the shared state is to let the triad escape one-shot prompt prison without collapsing role boundaries.

Each layer sees only the fields it needs.
Each layer updates only the fields it is responsible for.

The shared state is therefore:
- persistent across cycles
- structured rather than free-form
- role-bounded
- recursion-friendly

---

## Design principle

The shared state should preserve only what is needed for:

- current unfolding input
- active choreography mapping
- predictive comparison
- symbolic context
- mismatch and correction
- repeated recursive cycles

It should not become a dumping ground for prose.

Compactly:

> The shared state is the live choreography field as seen through role-bounded structured memory.

---

## Top-level schema

The shared state contains the following top-level fields:

```json
{
  "cycle_id": 0,
  "input_slice": {},
  "source_hypotheses": [],
  "motion_tokens": [],
  "active_trains": [],
  "coupling_state": {},
  "choreography_memory_refs": [],
  "coherence_state": {},
  "mismatch_history": [],
  "attention_state": {},
  "cortex_context": {},
  "downward_bias": {},
  "predicted_trains": [],
  "action_state": {},
  "returned_traces": [],
  "notes_on_state_quality": {}
}
```

This is not yet the final machine schema.
It is the minimum shared basin for the prompt-instantiated prototype.

⸻

## 	Field definitions

### cycle_id

The current recursive cycle number.

Purpose
Allows all three layers to know whether they are:
	•	initializing
	•	continuing
	•	correcting
	•	stabilizing
	•	or restarting

⸻

### input_slice

The current externally supplied unfolding input.

Purpose
Represents the raw or pre-shaped current slice of the world.

Examples
	•	hand-authored frame-sequence summary
	•	image-derived scene summary
	•	later, video-derived spatiotemporal slice
	•	later still, agent-output slice or societal-event slice

Structure
```
{
  "source_type": "frame_sequence_summary",
  "time_window": "frames_1_4",
  "content": []
}
```

⸻

### source_hypotheses

Provisional object/source identities.

Purpose
Represents persistent emitter/carrier guesses, not final truths.

Structure
Each entry may include:
	•	source_id
	•	hypothesis_type
	•	confidence
	•	stability
	•	notes

Example
```
[
  {
    "source_id": "A",
    "hypothesis_type": "moving_object",
    "confidence": 0.74,
    "stability": "provisional",
    "notes": "persistent source near left edge"
  }
]
```

⸻

### motion_tokens

Primitive spatiotemporal trace bundles.

Purpose
The minimum processable units over which TU and TU+ operate.

Structure
Each token may include:
	•	token_id
	•	source_id
	•	time_slice
	•	displacement_delta
	•	direction
	•	angle_change
	•	relation_change
	•	confidence

Example
```
[
  {
    "token_id": "t1",
    "source_id": "A",
    "time_slice": "f1_f2",
    "displacement_delta": "small",
    "direction": "rightward",
    "angle_change": "low",
    "relation_change": "none",
    "confidence": 0.68
  }
]
```

⸻

### active_trains

Persistent sequences of motion-tokens.

Purpose
Represents train structure currently active in the field.

Structure
Each train may include:
	•	train_id
	•	source_id
	•	token_ids
	•	persistence
	•	status
	•	restart_of
	•	weight

Example
```
[
  {
    "train_id": "train_A_1",
    "source_id": "A",
    "token_ids": ["t1", "t2", "t3"],
    "persistence": "rising",
    "status": "active",
    "restart_of": null,
    "weight": 0.77
  }
]
```

⸻

### coupling_state

Current horizontal relations among trains.

Purpose
Represents where/how trains connect, reinforce, or fragment.

Structure
```
{
  "coupling_candidates": [],
  "stable_couplings": [],
  "fragmentation_flags": []
}

Example

{
  "coupling_candidates": [
    {
      "train_a": "train_A_1",
      "train_b": "train_B_1",
      "strength": 0.42
    }
  ],
  "stable_couplings": [],
  "fragmentation_flags": []
}
```

⸻

### choreography_memory_refs

References to stored choreography patterns.

Purpose
Lets TU+ compare current trains against previously stored choreography forms without requiring the full memory store to be copied into every cycle.

Structure
Each entry may include:
	•	choreography_id
	•	match_type
	•	similarity
	•	memory_scope

Example
```
[
  {
    "choreography_id": "approach_then_pause",
    "match_type": "partial",
    "similarity": 0.63,
    "memory_scope": "tu_near_store"
  }
]
```

⸻

### coherence_state

Current whole-field coherence summary.

Purpose
Represents how viable the current field is as a coupled whole.

Structure
```
{
  "train_persistence_level": 0.0,
  "coupling_stability_level": 0.0,
  "motion_observation_agreement": 0.0,
  "fragmentation_level": 0.0,
  "coherence_summary": ""
}
```
Example
```
{
  "train_persistence_level": 0.71,
  "coupling_stability_level": 0.54,
  "motion_observation_agreement": 0.80,
  "fragmentation_level": 0.12,
  "coherence_summary": "single stable train, low fragmentation"
}
```

⸻

### mismatch_history

Accumulated deltas between predicted and returned unfolding.

Purpose
Supports recursive correction.

Structure
Each entry may include:
	•	cycle_id
	•	predicted_train_id
	•	returned_trace_ref
	•	delta_type
	•	delta_strength
	•	coherence_impact

Example
```
[
  {
    "cycle_id": 3,
    "predicted_train_id": "train_A_pred_1",
    "returned_trace_ref": "rt3",
    "delta_type": "timing_divergence",
    "delta_strength": 0.31,
    "coherence_impact": "moderate"
  }
]
```

⸻

### attention_state

Current recruitment and salience state.

Purpose
Tracks whether the field should remain background, be monitored, or recruit cortexLLM attention.

Structure
```
{
  "attention_trigger": false,
  "trigger_reason": "",
  "salience_level": 0.0,
  "watch_targets": []
}
```

⸻

### cortex_context

Current symbolic framing from cortexLLM.

Purpose
Holds the current high-level interpretive context.

Structure
```
{
  "task_frame": "",
  "interpretive_context": "",
  "current_goal_pressure": "",
  "hold_or_act": ""
}
```

⸻

### downward_bias

Contextual pressure sent from cortexLLM downward.

Purpose
Lets cortexLLM influence TU+ without directly micromanaging low-level structure.

Structure
Possible fields:
	•	initiate
	•	sustain
	•	suppress
	•	reorient
	•	attend
	•	compare
	•	act
	•	hold

Example
```
{
  "attend": ["A"],
  "hold": true,
  "reorient": null,
  "compare": ["approach_then_pause"]
}
```

⸻

### predicted_trains

Candidate continuation structures proposed by TU+.

Purpose
Represents likely unfolding under current field and coherence pressure.

Structure
Each entry may include:
	•	predicted_train_id
	•	choreography_id
	•	source_id
	•	predicted_token_sequence
	•	confidence
	•	continuation_type

Example
```
[
  {
    "predicted_train_id": "train_A_pred_1",
    "choreography_id": "approach_then_pause",
    "source_id": "A",
    "predicted_token_sequence": ["tp4", "tp5"],
    "confidence": 0.66,
    "continuation_type": "hold_or_resume"
  }
]
```

⸻

### action_state

Bridge state between predicted train and enacted motion.

Purpose
Represents whether a predicted train has been held, translated, enacted, or suppressed.

Structure
```
{
  "action_mode": "hold",
  "selected_predicted_train": null,
  "operator_status": "inactive",
  "relay_notes": ""
}
```
Later this field may become richer if the action operator is formalized further.

⸻

### returned_traces

Actual traces coming back from world/body/video/agent after continuation or enactment.

Purpose
Supplies recursive influence back into the field.

Structure
Each entry may include:
	•	trace_id
	•	source_id
	•	time_slice
	•	observed_change
	•	confidence

Example
```
[
  {
    "trace_id": "rt1",
    "source_id": "A",
    "time_slice": "f4_f5",
    "observed_change": "held_position",
    "confidence": 0.82
  }
]
```

⸻

### notes_on_state_quality

State hygiene notes.

Purpose
Provides compact meta-comments on whether the state is:
	•	sparse
	•	uncertain
	•	stable
	•	fragmented
	•	overgrown
	•	in need of reset or clarification

Structure
```
{
  "state_quality": "",
  "uncertainty_notes": [],
  "reset_recommendation": false
}
```

⸻

## Visibility by role

The whole state exists, but each role should focus only on what it needs.

TU reads primarily
	•	input_slice
	•	source_hypotheses
	•	motion_tokens
	•	active_trains
	•	returned_traces

TU writes primarily
	•	source_hypotheses
	•	motion_tokens
	•	active_trains
	•	coupling_state
	•	coherence_state

TU+ reads primarily
	•	source_hypotheses
	•	motion_tokens
	•	active_trains
	•	coupling_state
	•	choreography_memory_refs
	•	coherence_state
	•	mismatch_history
	•	downward_bias

TU+ writes primarily
	•	choreography_memory_refs
	•	attention_state
	•	predicted_trains
	•	coherence_state
	•	mismatch_history (through comparison pressure)

cortexLLM reads primarily
	•	coherence_state
	•	attention_state
	•	predicted_trains
	•	mismatch_history
	•	notes_on_state_quality

cortexLLM writes primarily
	•	cortex_context
	•	downward_bias
	•	attention_state
	•	notes_on_state_quality

This role-bounded access is essential.
Without it, the triad collapses into one blurred assistant.

⸻

State evolution across cycles

Each cycle should:
	1.	preserve prior structured state
	2.	update only changed fields
	3.	avoid replacing the entire state with prose
	4.	let returned traces reshape active trains and coherence
	5.	allow restart/splitting when persistent mismatch appears

Compactly:

The state should evolve by structured reweighting and partial update, not by total rewrite.

⸻

Minimal example state
```
{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": ["object A shifts right, then pauses"]
  },
  "source_hypotheses": [
    {
      "source_id": "A",
      "hypothesis_type": "moving_object",
      "confidence": 0.74,
      "stability": "provisional",
      "notes": "persistent source near left edge"
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
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1"],
      "persistence": "rising",
      "status": "active",
      "restart_of": null,
      "weight": 0.61
    }
  ],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "choreography_memory_refs": [],
  "coherence_state": {
    "train_persistence_level": 0.61,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.72,
    "fragmentation_level": 0.08,
    "coherence_summary": "single stable train forming"
  },
  "mismatch_history": [],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.22,
    "watch_targets": ["A"]
  },
  "cortex_context": {
    "task_frame": "monitor unfolding source",
    "interpretive_context": "ordinary movement",
    "current_goal_pressure": "observe",
    "hold_or_act": "hold"
  },
  "downward_bias": {
    "attend": ["A"],
    "hold": true
  },
  "predicted_trains": [],
  "action_state": {
    "action_mode": "hold",
    "selected_predicted_train": null,
    "operator_status": "inactive",
    "relay_notes": ""
  },
  "returned_traces": [],
  "notes_on_state_quality": {
    "state_quality": "stable_but_sparse",
    "uncertainty_notes": ["object still provisional"],
    "reset_recommendation": false
  }
}
```

⸻

Closing statement

The shared state schema is the first practical bridge from architecture notes to a runnable prompt-instantiated triad.

It lets TU, TU+, and cortexLLM:
	•	share a live field
	•	remain role-bounded
	•	recurse across cycles
	•	and escape one-shot prompt prison without dissolving into noise

A compact final formulation:

The shared state is the live structured memory of the choreography field, preserved across cycles and read differently by TU, TU+, and cortexLLM.
