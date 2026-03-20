# Toy TU / TU+ / cortexLLM Loop

## Input slice
Frame sequence summary:
- frame 1: object hypothesis A near left edge
- frame 2: A shifts slightly right
- frame 3: A shifts right faster and angle changes
- frame 4: A pauses near central region

## TU output
- source_hypotheses:
  - A: provisional persistent source
- motion_tokens:
  - t1: A, frame1->2, small rightward delta
  - t2: A, frame2->3, larger rightward delta, angle shift
  - t3: A, frame3->4, low displacement, pause tendency
- train_updates:
  - train_A_1: [t1, t2, t3]
- coupling_updates:
  - none
- persistence_decay_restart:
  - A persistent
- field_coherence_snapshot:
  - single stable train, no fragmentation

## TU+ output
- matched_choreographies:
  - approach_then_pause: medium confidence
- likely_continuations:
  - resume movement
  - hold position
- novelty_flags:
  - low
- instability_flags:
  - low
- mismatch_flags:
  - none
- replay_triggers:
  - weak
- attention_triggers:
  - low
- predicted_train_candidates:
  - continue_hold_or_resume cluster

## cortexLLM output
- interpretation:
  - one persistent source shows approach-like movement followed by pause
- context_frame:
  - likely ordinary movement, not high alert
- act_or_hold:
  - hold
- downward_bias:
  - continue monitoring source A for reacceleration or branch
- request_for_more_input:
  - yes
- notes_on_mapping_quality:
  - mapping appears stable for current slice
