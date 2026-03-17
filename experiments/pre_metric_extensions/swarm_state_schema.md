# Proto Temporal Unit Swarm State Schema (Present-Time Layer)

This schema is generated at runtime from the event ledger.
It represents the active temporal field for interpretation.

## Core state object

- `clock_tick` (integer): current simulation tick.
- `case_id` (string): active case corridor.
- `active_string_id` (string): most-recently replayed longitudinal string.
- `choreography_strings` (map):
  - key: `string_id`
  - value:
    - `event_ids` (ordered list)
    - `weight` (number)
    - `last_tick` (integer)
- `simultaneity_families` (list): each family is:
  - `slice_tick` (integer)
  - `member_event_ids` (list)
  - `member_string_ids` (list)
- `event_weights` (map `event_id -> number`)
- `active_events` (list of `event_id` above small activity floor)
- `dominant_basin` (object):
  - `string_id`
  - `weight`
- `unresolved_tensions` (list of strings): short descriptors inferred from low coherence.
- `coherence_score` (number in `[0,1]`)
- `plateau_state` (boolean): true when coherence cutoff condition is met.
- `recommended_mode` (string): one of `hold | observe | clarify | patch | rebuild | act`.

## Notes

- Event records remain minimal and static.
- Membership in strings/families is computed in swarm state, not stored as fixed event fields.
- This state is intentionally inspectable over complete.
