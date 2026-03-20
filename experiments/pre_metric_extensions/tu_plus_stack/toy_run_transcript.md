# Toy TU / TU+ / cortexLLM Loop

## Purpose

This note demonstrates one bounded toy cycle of the prompt-instantiated TU / TU+ / cortexLLM triad.

The goal is not realism yet.
The goal is to show:

- role separation
- shared-state persistence
- structured updates
- bounded recursion

---

## Initial input slice

Frame sequence summary:

- frame 1: object hypothesis A near left edge
- frame 2: A shifts slightly right
- frame 3: A shifts right faster and angle changes
- frame 4: A pauses near central region

---

## Initial shared state

```
json
{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": [
      "frame 1: object hypothesis A near left edge",
      "frame 2: A shifts slightly right",
      "frame 3: A shifts right faster and angle changes",
      "frame 4: A pauses near central region"
    ]
  },
  "source_hypotheses": [],
  "motion_tokens": [],
  "active_trains": [],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "choreography_memory_refs": [],
  "coherence_state": {},
  "mismatch_history": [],
  "attention_state": {},
  "cortex_context": {},
  "downward_bias": {},
  "predicted_trains": [],
  "action_state": {
    "action_mode": "hold",
    "selected_predicted_train": null,
    "operator_status": "inactive",
    "relay_notes": ""
  },
  "returned_traces": [],
  "notes_on_state_quality": {}
}
```

---

## TU stage

**TU reads**

- input_slice
- source_hypotheses
- motion_tokens
- active_trains
- returned_traces

**TU writes**

- source_hypotheses
- motion_tokens
- active_trains
- coupling_state
- coherence_state

**TU output**
```
json
{
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
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "medium",
      "direction": "rightward",
      "angle_change": "moderate",
      "relation_change": "none",
      "confidence": 0.76
    },
    {
      "token_id": "t3",
      "source_id": "A",
      "time_slice": "f3_f4",
      "displacement_delta": "low",
      "direction": "rightward_to_pause",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.71
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2", "t3"],
      "persistence": "rising_then_stabilizing",
      "status": "active",
      "restart_of": null,
      "weight": 0.77
    }
  ],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "coherence_state": {
    "train_persistence_level": 0.77,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.81,
    "fragmentation_level": 0.06,
    "coherence_summary": "single stable train, no fragmentation"
  }
}
```
**Shared state after TU update**
```
json
{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": [
      "frame 1: object hypothesis A near left edge",
      "frame 2: A shifts slightly right",
      "frame 3: A shifts right faster and angle changes",
      "frame 4: A pauses near central region"
    ]
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
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "medium",
      "direction": "rightward",
      "angle_change": "moderate",
      "relation_change": "none",
      "confidence": 0.76
    },
    {
      "token_id": "t3",
      "source_id": "A",
      "time_slice": "f3_f4",
      "displacement_delta": "low",
      "direction": "rightward_to_pause",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.71
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2", "t3"],
      "persistence": "rising_then_stabilizing",
      "status": "active",
      "restart_of": null,
      "weight": 0.77
    }
  ],
  "coupling_state": {
    "coupling_candidates": [],
    "stable_couplings": [],
    "fragmentation_flags": []
  },
  "choreography_memory_refs": [],
  "coherence_state": {
    "train_persistence_level": 0.77,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.81,
    "fragmentation_level": 0.06,
    "coherence_summary": "single stable train, no fragmentation"
  },
  "mismatch_history": [],
  "attention_state": {},
  "cortex_context": {},
  "downward_bias": {},
  "predicted_trains": [],
  "action_state": {
    "action_mode": "hold",
    "selected_predicted_train": null,
    "operator_status": "inactive",
    "relay_notes": ""
  },
  "returned_traces": [],
  "notes_on_state_quality": {}
}
```

---

## TU+ stage

**TU+ reads**

- source_hypotheses
- motion_tokens
- active_trains
- coupling_state
- choreography_memory_refs
- coherence_state
- mismatch_history
- downward_bias

**TU+ writes**

- choreography_memory_refs
- attention_state
- predicted_trains
- coherence_state
- mismatch_history

**TU+ output**
```
json
{
  "choreography_memory_refs": [
    {
      "choreography_id": "approach_then_pause",
      "match_type": "partial",
      "similarity": 0.66,
      "memory_scope": "tu_near_store"
    }
  ],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.28,
    "watch_targets": ["A"]
  },
  "predicted_trains": [
    {
      "predicted_train_id": "train_A_pred_1",
      "choreography_id": "approach_then_pause",
      "source_id": "A",
      "predicted_token_sequence": ["tp4", "tp5"],
      "confidence": 0.64,
      "continuation_type": "hold_or_resume"
    }
  ],
  "coherence_state": {
    "train_persistence_level": 0.77,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.81,
    "fragmentation_level": 0.06,
    "coherence_summary": "single stable train, matched to approach_then_pause with medium confidence"
  },
  "mismatch_history": []
}
```
**Shared state after TU+ update**
```
json
{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": [
      "frame 1: object hypothesis A near left edge",
      "frame 2: A shifts slightly right",
      "frame 3: A shifts right faster and angle changes",
      "frame 4: A pauses near central region"
    ]
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
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "medium",
      "direction": "rightward",
      "angle_change": "moderate",
      "relation_change": "none",
      "confidence": 0.76
    },
    {
      "token_id": "t3",
      "source_id": "A",
      "time_slice": "f3_f4",
      "displacement_delta": "low",
      "direction": "rightward_to_pause",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.71
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2", "t3"],
      "persistence": "rising_then_stabilizing",
      "status": "active",
      "restart_of": null,
      "weight": 0.77
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
      "similarity": 0.66,
      "memory_scope": "tu_near_store"
    }
  ],
  "coherence_state": {
    "train_persistence_level": 0.77,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.81,
    "fragmentation_level": 0.06,
    "coherence_summary": "single stable train, matched to approach_then_pause with medium confidence"
  },
  "mismatch_history": [],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.28,
    "watch_targets": ["A"]
  },
  "cortex_context": {},
  "downward_bias": {},
  "predicted_trains": [
    {
      "predicted_train_id": "train_A_pred_1",
      "choreography_id": "approach_then_pause",
      "source_id": "A",
      "predicted_token_sequence": ["tp4", "tp5"],
      "confidence": 0.64,
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
  "notes_on_state_quality": {}
}
```

---

## cortexLLM stage

**cortexLLM reads**

- coherence_state
- attention_state
- predicted_trains
- mismatch_history
- notes_on_state_quality

**cortexLLM writes**

- cortex_context
- downward_bias
- attention_state
- notes_on_state_quality

**cortexLLM output**
```
json
{
  "cortex_context": {
    "task_frame": "monitor unfolding source",
    "interpretive_context": "one persistent source shows approach-like movement followed by pause",
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
    "salience_level": 0.31,
    "watch_targets": ["A"]
  },
  "notes_on_state_quality": {
    "state_quality": "stable_and_readable",
    "uncertainty_notes": [
      "source A remains provisional",
      "continuation still ambiguous between hold and resume"
    ],
    "reset_recommendation": false
  }
}

Shared state after cortexLLM update

{
  "cycle_id": 1,
  "input_slice": {
    "source_type": "frame_sequence_summary",
    "time_window": "frames_1_4",
    "content": [
      "frame 1: object hypothesis A near left edge",
      "frame 2: A shifts slightly right",
      "frame 3: A shifts right faster and angle changes",
      "frame 4: A pauses near central region"
    ]
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
    },
    {
      "token_id": "t2",
      "source_id": "A",
      "time_slice": "f2_f3",
      "displacement_delta": "medium",
      "direction": "rightward",
      "angle_change": "moderate",
      "relation_change": "none",
      "confidence": 0.76
    },
    {
      "token_id": "t3",
      "source_id": "A",
      "time_slice": "f3_f4",
      "displacement_delta": "low",
      "direction": "rightward_to_pause",
      "angle_change": "low",
      "relation_change": "none",
      "confidence": 0.71
    }
  ],
  "active_trains": [
    {
      "train_id": "train_A_1",
      "source_id": "A",
      "token_ids": ["t1", "t2", "t3"],
      "persistence": "rising_then_stabilizing",
      "status": "active",
      "restart_of": null,
      "weight": 0.77
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
      "similarity": 0.66,
      "memory_scope": "tu_near_store"
    }
  ],
  "coherence_state": {
    "train_persistence_level": 0.77,
    "coupling_stability_level": 0.00,
    "motion_observation_agreement": 0.81,
    "fragmentation_level": 0.06,
    "coherence_summary": "single stable train, matched to approach_then_pause with medium confidence"
  },
  "mismatch_history": [],
  "attention_state": {
    "attention_trigger": false,
    "trigger_reason": "",
    "salience_level": 0.31,
    "watch_targets": ["A"]
  },
  "cortex_context": {
    "task_frame": "monitor unfolding source",
    "interpretive_context": "one persistent source shows approach-like movement followed by pause",
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
      "predicted_token_sequence": ["tp4", "tp5"],
      "confidence": 0.64,
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
    "state_quality": "stable_and_readable",
    "uncertainty_notes": [
      "source A remains provisional",
      "continuation still ambiguous between hold and resume"
    ],
    "reset_recommendation": false
  }
}
```

---

## Summary of this toy loop

This toy loop shows that:

- TU can map unfolding structure without narrating
- TU+ can compare and predict without becoming cortexLLM
- cortexLLM can interpret and bias without remapping low-level structure
- the shared state can persist across a full cycle without collapsing into free prose

This is the minimal bounded behavior the prototype must preserve.

