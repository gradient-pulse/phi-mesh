#!/usr/bin/env python3
"""Minimal, inspectable proto temporal unit toy simulation."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import yaml

BASE_DIR = Path(__file__).resolve().parent
CASE_PATH = BASE_DIR / "toy_cases" / "document_repair_case.yml"
CONFIG_PATH = BASE_DIR / "proto_temporal_unit_config.yml"


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    arrival_tick: int
    string_id: str


def load_yaml(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def assign_string(event_type: str) -> str:
    """Minimal fixed mapping to preserve one-event-to-one-string attachment."""
    if event_type in {"task_arrival", "instruction_received"}:
        return "target_unclear"
    if event_type == "clarification_received":
        return "coherence_restoration"
    if event_type in {"duplication_detected", "stale_remnant_detected", "evidence_mismatch_detected"}:
        return "contamination_rising"
    if event_type == "patch_attempt":
        return "patch_overreach"
    if event_type == "rebuild_triggered":
        return "rebuild_readiness"
    if event_type == "coherence_restored":
        return "coherence_restoration"
    return "other"


def build_events(case_data: Dict[str, object]) -> List[Event]:
    raw_events = case_data.get("events", [])
    return [
        Event(
            event_id=raw["event_id"],
            event_type=raw["event_type"],
            arrival_tick=int(raw["arrival_tick"]),
            string_id=assign_string(raw["event_type"]),
        )
        for raw in raw_events
    ]


def validate_one_event_one_string(events: Iterable[Event]) -> Dict[str, str]:
    event_to_string: Dict[str, str] = {}
    for event in events:
        prior = event_to_string.get(event.event_id)
        if prior is not None and prior != event.string_id:
            raise ValueError(f"Event {event.event_id} has conflicting strings: {prior} vs {event.string_id}")
        event_to_string[event.event_id] = event.string_id
    return event_to_string


def group_simultaneity_families(events: Iterable[Event], simultaneity_window: int) -> Dict[int, List[str]]:
    by_tick: Dict[int, List[str]] = defaultdict(list)
    for event in events:
        by_tick[event.arrival_tick].append(event.event_id)

    ticks = sorted(by_tick)
    families: Dict[int, List[str]] = {}
    family_id = 1
    for idx, tick in enumerate(ticks):
        members = set(by_tick[tick])
        j = idx + 1
        while j < len(ticks) and ticks[j] - tick <= simultaneity_window:
            members.update(by_tick[ticks[j]])
            j += 1
        if len(members) > 1:
            families[family_id] = sorted(members)
            family_id += 1
    return families


def replay_activation(events: List[Event], event_to_string: Dict[str, str], families: Dict[int, List[str]], cfg: Dict[str, object]) -> Dict[str, object]:
    events_by_string: Dict[str, List[str]] = defaultdict(list)
    string_weights: Dict[str, float] = defaultdict(float)

    decay_factor = float(cfg["decay_factor"])
    spread_gain = float(cfg["simultaneity_spread_gain"])
    replay_gain = float(cfg["replay_gain"])
    coherence_cutoff = float(cfg["coherence_cutoff_threshold"])

    latest_tick = max(e.arrival_tick for e in events)
    for event in events:
        events_by_string[event.string_id].append(event.event_id)
        age = latest_tick - event.arrival_tick
        string_weights[event.string_id] += decay_factor**age

    active_family_ids: List[int] = []
    for family_id, member_ids in families.items():
        member_strings = {event_to_string[mid] for mid in member_ids}
        if len(member_strings) > 1:
            active_family_ids.append(family_id)
            for sid in member_strings:
                string_weights[sid] += spread_gain

    dominant_string = max(string_weights, key=string_weights.get)
    coherence_score = min(1.0, replay_gain * string_weights.get("coherence_restoration", 0.0))
    plateau_or_cutoff = "cutoff" if coherence_score >= coherence_cutoff else "plateau"

    if dominant_string == "coherence_restoration" and coherence_score >= coherence_cutoff:
        mode = "patch"
        reason = "Coherence restoration is dominant and exceeds cutoff; incremental patching is preferred."
    elif dominant_string in {"contamination_rising", "patch_overreach"}:
        mode = "rebuild"
        reason = "Contamination-related activity dominates despite coupling; clean rebuild is safer."
    else:
        mode = "clarify"
        reason = "No decisive coherence cutoff; clarify intent before additional edits."

    return {
        "string_weights": dict(sorted(string_weights.items())),
        "dominant_longitudinal_string": dominant_string,
        "active_simultaneity_families": active_family_ids,
        "coherence_score": round(coherence_score, 4),
        "plateau_cutoff_status": plateau_or_cutoff,
        "recommended_mode": mode,
        "recommended_mode_reason": reason,
        "inspectable": {
            "events_by_string": dict(events_by_string),
            "families": families,
            "arrival_tick_mapping": {e.event_id: e.arrival_tick for e in events},
        },
    }


def main() -> None:
    case_data = load_yaml(CASE_PATH)
    cfg = load_yaml(CONFIG_PATH)

    events = build_events(case_data)
    event_to_string = validate_one_event_one_string(events)
    families = group_simultaneity_families(events, int(cfg["simultaneity_window"]))
    summary = replay_activation(events, event_to_string, families, cfg)

    print(json.dumps({"events": [e.__dict__ for e in events], "event_to_string": event_to_string, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
