# Proto Temporal Unit Event Schema (Minimal)

This schema is the static ledger layer only.
Dynamic labels (status, choreography membership, family links) are not fixed event properties.

## Required fields

- `event_id` (string): unique event key within a run.
- `case_id` (string): case corridor identifier.
- `arrival_tick` (integer): tick when the event enters the corridor.
- `source_channel` (string): source stream (user, system, detector, etc).
- `event_type` (string): compact event classifier.
- `content_summary` (string): short human-readable summary.

## Optional anchors

- `source_reference` (string): original trace pointer for action grounding.
- `payload_strength` (number, default `1.0`): source-side confidence/intensity.

## Example

```yaml
- event_id: docfix-e3
  case_id: document_repair_case
  arrival_tick: 3
  source_channel: detector
  event_type: duplication_detected
  content_summary: Duplicate section appears in output draft.
  source_reference: logs/diff-17
  payload_strength: 0.8
```
