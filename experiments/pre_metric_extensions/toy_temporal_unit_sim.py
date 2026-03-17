#!/usr/bin/env python3
"""Minimal, inspectable proto temporal unit toy simulation.

Design constraints encoded here:
- events carry explicit `arrival_tick` values (no tick parsing from event_id)
- each event attaches to exactly one longitudinal string
- cross-string coupling only occurs through simultaneity families
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set


SIMULTANEITY_WINDOW = 0  # same-tick families for maximal inspectability


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    arrival_tick: int
    string_id: str


def build_events() -> List[Event]:
    """Toy, clocked stream for document/file-repair choreography."""
    return [
        Event("e1", "task_arrival", 1, "target_unclear"),
        Event("e2", "instruction_received", 1, "target_unclear"),
        Event("e3", "patch_attempt", 2, "patch_overreach"),
        Event("e4", "stale_remnant_detected", 2, "contamination_rising"),
        Event("e5", "evidence_mismatch_detected", 3, "contamination_rising"),
        Event("e6", "clarification_received", 3, "coherence_restoration"),
        Event("e7", "rebuild_triggered", 4, "rebuild_readiness"),
        Event("e8", "coherence_restored", 4, "coherence_restoration"),
    ]


def validate_one_event_one_string(events: Iterable[Event]) -> Dict[str, str]:
    """Ensure strict one-event-to-one-string attachment."""
    event_to_string: Dict[str, str] = {}
    for event in events:
        prior = event_to_string.get(event.event_id)
        if prior is not None and prior != event.string_id:
            raise ValueError(
                f"Event {event.event_id} has conflicting strings: {prior} vs {event.string_id}"
            )
        event_to_string[event.event_id] = event.string_id
    return event_to_string


def group_simultaneity_families(events: Iterable[Event]) -> Dict[int, List[str]]:
    """Build same/near-same tick families from explicit arrival_tick values."""
    by_tick: Dict[int, List[str]] = defaultdict(list)
    for event in events:
        by_tick[event.arrival_tick].append(event.event_id)

    if SIMULTANEITY_WINDOW <= 0:
        return {tick: ids for tick, ids in by_tick.items() if len(ids) > 1}

    families: Dict[int, List[str]] = {}
    ticks = sorted(by_tick)
    for family_id, tick in enumerate(ticks, start=1):
        members: List[str] = []
        for other_tick in ticks:
            if abs(other_tick - tick) <= SIMULTANEITY_WINDOW:
                members.extend(by_tick[other_tick])
        if len(members) > 1:
            families[family_id] = sorted(set(members))
    return families


def replay_activation(
    events: List[Event],
    event_to_string: Dict[str, str],
    families: Dict[int, List[str]],
) -> Dict[str, object]:
    """Replay dominant activity with cross-string spread only via families."""
    events_by_id = {e.event_id: e for e in events}
    events_by_string: Dict[str, List[str]] = defaultdict(list)
    string_weights: Dict[str, float] = defaultdict(float)

    for event in events:
        events_by_string[event.string_id].append(event.event_id)

    # Longitudinal weighting inside each string.
    for event in events:
        recency_weight = 1.0 / (1 + (events[-1].arrival_tick - event.arrival_tick))
        string_weights[event.string_id] += recency_weight

    # Horizontal coupling only via simultaneity families.
    active_family_ids: List[int] = []
    for family_id, member_ids in families.items():
        member_strings = {event_to_string[mid] for mid in member_ids}
        if len(member_strings) > 1:
            active_family_ids.append(family_id)
            for sid in member_strings:
                string_weights[sid] += 0.5

    dominant_string = max(string_weights, key=string_weights.get)

    # Determine suggestion with simple inspectable rule.
    if dominant_string == "coherence_restoration":
        mode = "patch"
        reason = (
            "coherence_restoration dominates and is reinforced by active cross-string "
            "simultaneity families, so incremental repair is preferred"
        )
    elif dominant_string in {"contamination_rising", "patch_overreach"}:
        mode = "rebuild"
        reason = (
            "contamination-focused longitudinal activity dominates despite coupling, "
            "so a clean rebuild is safer"
        )
    else:
        mode = "clarify"
        reason = (
            "no contamination-dominant basin; preserve optionality with clarification "
            "before major edits"
        )

    return {
        "string_weights": dict(sorted(string_weights.items())),
        "dominant_longitudinal_string": dominant_string,
        "active_simultaneity_families": active_family_ids,
        "recommended_mode": mode,
        "recommended_mode_reason": reason,
        "inspectable": {
            "events_by_string": dict(events_by_string),
            "families": families,
            "arrival_tick_mapping": {e.event_id: e.arrival_tick for e in events},
        },
    }


def main() -> None:
    events = build_events()
    event_to_string = validate_one_event_one_string(events)
    families = group_simultaneity_families(events)
    summary = replay_activation(events, event_to_string, families)

    print(
        json.dumps(
            {
                "events": [e.__dict__ for e in events],
                "event_to_string": event_to_string,
                "summary": summary,
            },
            indent=2,
            sort_keys=False,
        )
    )


if __name__ == "__main__":
    main()
