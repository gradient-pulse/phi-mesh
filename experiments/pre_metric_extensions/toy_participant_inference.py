#!/usr/bin/env python3
"""Minimal toy prototype for participant inference from source-linked traces.

This script keeps the branch ontology deliberately small and inspectable:
- each trace is treated as time-local, source-attributable, and directionless
- repeated source-linked traces within a continuity window form provisional trains
- a participant may own multiple trains when a train restarts after silence
- near-time emissions from different sources become horizontal coupling candidates
- participant weight uses only train persistence and horizontal coupling candidates

It prints a compact JSON summary suitable for quick inspection.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

CONTINUITY_WINDOW = 3
DECAY_GAP = 2
RESTART_GAP = 4
HORIZONTAL_WINDOW = 1

TOY_TRACES = [
    {"trace_id": "t1", "tick": 0, "source": "sensor.alpha", "kind": "ping"},
    {"trace_id": "t2", "tick": 1, "source": "sensor.beta", "kind": "ping"},
    {"trace_id": "t3", "tick": 2, "source": "sensor.alpha", "kind": "ping"},
    {"trace_id": "t4", "tick": 4, "source": "sensor.alpha", "kind": "ping"},
    {"trace_id": "t5", "tick": 5, "source": "sensor.beta", "kind": "ping"},
    {"trace_id": "t6", "tick": 9, "source": "sensor.alpha", "kind": "ping"},
    {"trace_id": "t7", "tick": 10, "source": "sensor.alpha", "kind": "ping"},
    {"trace_id": "t8", "tick": 11, "source": "sensor.gamma", "kind": "ping"},
]


@dataclass
class Train:
    train_id: str
    source: str
    start_tick: int
    end_tick: int
    trace_ids: list[str]
    continuity: bool
    decay: bool = False
    restart: bool = False
    restart_of: str | None = None
    participant_relation_to_previous_train: str | None = None
    previous_train_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "train_id": self.train_id,
            "source": self.source,
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "trace_ids": self.trace_ids,
            "continuity": self.continuity,
            "decay": self.decay,
            "restart": self.restart,
            "restart_of": self.restart_of,
            "participant_relation_to_previous_train": self.participant_relation_to_previous_train,
            "previous_train_id": self.previous_train_id,
        }


def normalize_traces(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for trace in sorted(traces, key=lambda item: (item["tick"], item["trace_id"])):
        normalized.append(
            {
                "trace_id": trace["trace_id"],
                "tick": trace["tick"],
                "source": trace["source"],
                "kind": trace.get("kind", "trace"),
                "time_local": True,
                "source_attributable": True,
                "directionless": True,
            }
        )
    return normalized


def attach_horizontal_coupling_candidates(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched = []
    for trace in traces:
        candidates = [
            other["trace_id"]
            for other in traces
            if other["source"] != trace["source"]
            and abs(other["tick"] - trace["tick"]) <= HORIZONTAL_WINDOW
        ]
        enriched.append({**trace, "horizontal_coupling_candidates": sorted(candidates)})
    return enriched


def infer_trains(traces: list[dict[str, Any]]) -> list[Train]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trace in traces:
        by_source[trace["source"]].append(trace)

    trains: list[Train] = []
    source_train_index: dict[str, int] = defaultdict(int)

    for source, source_traces in by_source.items():
        current: Train | None = None
        previous_train: Train | None = None

        for trace in source_traces:
            if current is None:
                source_train_index[source] += 1
                current = Train(
                    train_id=f"train.{source}.{source_train_index[source]}",
                    source=source,
                    start_tick=trace["tick"],
                    end_tick=trace["tick"],
                    trace_ids=[trace["trace_id"]],
                    continuity=False,
                )
                if previous_train is not None:
                    gap = trace["tick"] - previous_train.end_tick
                    if gap >= RESTART_GAP:
                        current.restart = True
                        current.restart_of = previous_train.train_id
                continue

            gap = trace["tick"] - current.end_tick
            if gap <= CONTINUITY_WINDOW:
                current.end_tick = trace["tick"]
                current.trace_ids.append(trace["trace_id"])
                current.continuity = len(current.trace_ids) >= 2
                continue

            if gap >= DECAY_GAP:
                current.decay = True
            trains.append(current)
            previous_train = current

            source_train_index[source] += 1
            current = Train(
                train_id=f"train.{source}.{source_train_index[source]}",
                source=source,
                start_tick=trace["tick"],
                end_tick=trace["tick"],
                trace_ids=[trace["trace_id"]],
                continuity=False,
                restart=gap >= RESTART_GAP,
                restart_of=previous_train.train_id if gap >= RESTART_GAP else None,
            )

        if current is not None:
            trains.append(current)

    return sorted(trains, key=lambda train: (train.start_tick, train.train_id))


def infer_participants(
    trains: list[Train], traces: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    trace_lookup = {trace["trace_id"]: trace for trace in traces}
    trains_by_source: dict[str, list[Train]] = defaultdict(list)
    for train in trains:
        trains_by_source[train.source].append(train)

    participant_specs: list[tuple[str, list[Train]]] = []
    for source in sorted(trains_by_source):
        source_trains = sorted(trains_by_source[source], key=lambda train: (train.start_tick, train.train_id))
        current_group: list[Train] = []
        for train in source_trains:
            if not current_group:
                current_group = [train]
                continue

            previous_train = current_group[-1]
            relation = "tentative_same_participant" if train.restart else "same_participant"
            train.participant_relation_to_previous_train = relation
            train.previous_train_id = previous_train.train_id

            if relation == "same_participant":
                current_group.append(train)
                continue

            participant_specs.append((source, current_group))
            current_group = [train]

        if current_group:
            participant_specs.append((source, current_group))

    participants: list[dict[str, Any]] = []
    for index, (source, owned_trains) in enumerate(participant_specs, start=1):
        trace_ids = [trace_id for train in owned_trains for trace_id in train.trace_ids]
        coupling_candidates = sorted(
            {
                candidate
                for trace_id in trace_ids
                for candidate in trace_lookup[trace_id]["horizontal_coupling_candidates"]
            }
        )
        persistence = sum(len(train.trace_ids) for train in owned_trains)
        participant_id = f"participant.{index}"
        participants.append(
            {
                "participant_id": participant_id,
                "source": source,
                "train_ids": [train.train_id for train in owned_trains],
                "continuity": any(train.continuity for train in owned_trains),
                "decay": any(train.decay for train in owned_trains),
                "restart": any(train.restart for train in owned_trains),
                "horizontal_coupling_candidates": coupling_candidates,
                "weight": persistence + len(coupling_candidates),
            }
        )

    return participants


def build_train_participant_links(trains: list[Train]) -> list[dict[str, Any]]:
    links = []
    trains_by_source: dict[str, list[Train]] = defaultdict(list)
    for train in trains:
        trains_by_source[train.source].append(train)

    for source in sorted(trains_by_source):
        ordered_trains = sorted(trains_by_source[source], key=lambda train: (train.start_tick, train.train_id))
        for previous_train, current_train in zip(ordered_trains, ordered_trains[1:]):
            relation = (
                "tentative_same_participant"
                if current_train.restart
                else "same_participant"
            )
            links.append(
                {
                    "source": source,
                    "from_train_id": previous_train.train_id,
                    "to_train_id": current_train.train_id,
                    "relation": relation,
                }
            )
    return links


def build_summary() -> dict[str, Any]:
    traces = attach_horizontal_coupling_candidates(normalize_traces(TOY_TRACES))
    trains = infer_trains(traces)
    participants = infer_participants(trains, traces)
    train_participant_links = build_train_participant_links(trains)

    return {
        "traces": traces,
        "inferred_trains": [train.to_dict() for train in trains],
        "train_participant_links": train_participant_links,
        "inferred_participants": participants,
        "decay_flags": [participant["participant_id"] for participant in participants if participant["decay"]],
        "restart_flags": [participant["participant_id"] for participant in participants if participant["restart"]],
    }


if __name__ == "__main__":
    print(json.dumps(build_summary(), indent=2, sort_keys=False))
