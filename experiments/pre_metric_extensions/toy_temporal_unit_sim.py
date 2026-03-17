#!/usr/bin/env python3
"""Minimal proto temporal unit simulator for one inspectable toy case."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import argparse
import json

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for this toy simulator.") from exc


KEYWORDS = {
    "task_arrival": {"target_unclear"},
    "instruction_received": {"target_unclear", "coherence_restoration"},
    "clarification_received": {"target_unclear", "coherence_restoration"},
    "patch_attempt": {"patch_overreach", "coherence_restoration"},
    "duplication_detected": {"contamination_rising"},
    "stale_remnant_detected": {"contamination_rising"},
    "evidence_mismatch_detected": {"patch_overreach", "rebuild_readiness"},
    "coherence_restored": {"coherence_restoration", "rebuild_readiness"},
}


@dataclass
class StringState:
    event_ids: list[str] = field(default_factory=list)
    weight: float = 0.0
    last_tick: int = 0


class ProtoTemporalUnit:
    def __init__(self, config: dict):
        self.cfg = config
        self.strings: dict[str, StringState] = {}
        self.event_weights: dict[str, float] = {}
        self.event_to_strings: dict[str, set[str]] = {}
        self.simultaneity_families: list[dict] = []
        self.tick = 0
        self.active_string_id = ""
        self.coherence_history: list[float] = []
        self.processed_events = 0

    def _event_tags(self, event: dict) -> set[str]:
        return KEYWORDS.get(event["event_type"], {event["event_type"]})

    def _string_tags(self, string_id: str) -> set[str]:
        return set(string_id.split("+"))

    def _score_attachment(self, event: dict, string_id: str) -> float:
        event_tags = self._event_tags(event)
        string_tags = self._string_tags(string_id)
        overlap = len(event_tags & string_tags) / max(len(event_tags | string_tags), 1)
        near_bonus = self.cfg["near_tick_bonus"] if self.tick - self.strings[string_id].last_tick <= 1 else 0.0
        return overlap + near_bonus

    def _pick_strings_for_event(self, event: dict) -> list[str]:
        if not self.strings:
            seed = next(iter(self._event_tags(event)))
            return [seed]
        scored = [(sid, self._score_attachment(event, sid)) for sid in self.strings]
        scored.sort(key=lambda x: x[1], reverse=True)
        best_id, best_score = scored[0]
        if best_score >= self.cfg["attachment_similarity_threshold"]:
            return [best_id]
        return sorted(self._event_tags(event))

    def _apply_decay(self):
        for eid in list(self.event_weights):
            self.event_weights[eid] *= self.cfg["decay_factor"]

    def _add_to_simultaneity(self, event: dict):
        window = self.cfg["simultaneity_window"]
        family_members = [event["event_id"]]
        family_strings = set(self.event_to_strings[event["event_id"]])

        for eid, weight in self.event_weights.items():
            if eid == event["event_id"] or weight <= 0:
                continue
            ev_tick = int(eid.split("-e")[-1]) - 1
            if abs(ev_tick - event["arrival_tick"]) <= window:
                family_members.append(eid)
                family_strings.update(self.event_to_strings.get(eid, set()))

        self.simultaneity_families.append(
            {
                "slice_tick": event["arrival_tick"],
                "member_event_ids": sorted(set(family_members)),
                "member_string_ids": sorted(family_strings),
            }
        )

    def _replay(self, start_string: str) -> set[str]:
        active = {start_string}
        frontier = {start_string}
        for _ in range(self.cfg["spread_depth"]):
            expanded = set()
            for family in reversed(self.simultaneity_families):
                if frontier & set(family["member_string_ids"]):
                    expanded.update(family["member_string_ids"])
            expanded -= active
            if not expanded:
                break
            active.update(expanded)
            frontier = expanded

        for sid in active:
            self.strings[sid].weight += self.cfg["replay_gain"]
            for eid in self.strings[sid].event_ids:
                self.event_weights[eid] = self.event_weights.get(eid, 0.0) + self.cfg["simultaneity_spread_gain"]
        return active

    def _coherence_score(self) -> float:
        total = sum(max(s.weight, 0.0) for s in self.strings.values())
        if total <= 0:
            return 0.0
        dominant = max(s.weight for s in self.strings.values())
        return dominant / total

    def _mode_from_score(self, score: float) -> str:
        mode = "hold"
        for name, threshold in sorted(self.cfg["action_mode_thresholds"].items(), key=lambda kv: kv[1]):
            if score >= threshold:
                mode = name
        return mode

    def ingest(self, case_id: str, event: dict):
        self.tick = max(self.tick, event["arrival_tick"])
        self._apply_decay()
        self.processed_events += 1

        for sid in self._pick_strings_for_event(event):
            self.strings.setdefault(sid, StringState())
            self.strings[sid].event_ids.append(event["event_id"])
            self.strings[sid].weight += event.get("payload_strength", 1.0)
            self.strings[sid].last_tick = event["arrival_tick"]
            self.event_to_strings.setdefault(event["event_id"], set()).add(sid)

        self.event_weights[event["event_id"]] = event.get("payload_strength", 1.0)
        self.active_string_id = sorted(self.event_to_strings[event["event_id"]])[0]

        self._add_to_simultaneity(event)
        self._replay(self.active_string_id)

        coherence = self._coherence_score()
        self.coherence_history.append(coherence)
        plateau = (
            self.processed_events >= self.cfg["coherence_min_events"]
            and len(self.coherence_history) >= self.cfg["coherence_min_steps"]
            and all(c >= self.cfg["coherence_cutoff_threshold"] for c in self.coherence_history[-self.cfg["coherence_min_steps"] :])
        )

        if plateau:
            return

    def summary(self, case_id: str) -> dict:
        coherence = self._coherence_score()
        dominant_id = max(self.strings, key=lambda sid: self.strings[sid].weight)
        active_events = [eid for eid, w in self.event_weights.items() if w >= 0.4]
        tensions = []
        if coherence < 0.55:
            tensions.append("field is fragmented across competing strings")
        if any("contamination_rising" in s for s in self.strings):
            tensions.append("contamination pressure still present")

        plateau = (
            self.processed_events >= self.cfg["coherence_min_events"]
            and len(self.coherence_history) >= self.cfg["coherence_min_steps"]
            and all(c >= self.cfg["coherence_cutoff_threshold"] for c in self.coherence_history[-self.cfg["coherence_min_steps"] :])
        )

        return {
            "clock_tick": self.tick,
            "case_id": case_id,
            "active_string_id": self.active_string_id,
            "choreography_strings": {
                sid: {
                    "event_ids": st.event_ids,
                    "weight": round(st.weight, 3),
                    "last_tick": st.last_tick,
                }
                for sid, st in self.strings.items()
            },
            "simultaneity_families": self.simultaneity_families,
            "event_weights": {eid: round(w, 3) for eid, w in self.event_weights.items()},
            "active_events": sorted(active_events),
            "dominant_basin": {"string_id": dominant_id, "weight": round(self.strings[dominant_id].weight, 3)},
            "unresolved_tensions": tensions,
            "coherence_score": round(coherence, 3),
            "plateau_state": plateau,
            "recommended_mode": self._mode_from_score(coherence),
        }


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run minimal proto temporal unit simulation.")
    parser.add_argument(
        "--config",
        default="experiments/pre_metric_extensions/proto_temporal_unit_config.yml",
    )
    parser.add_argument(
        "--case",
        default="experiments/pre_metric_extensions/toy_cases/document_repair_case.yml",
    )
    args = parser.parse_args()

    cfg = load_yaml(Path(args.config))
    case = load_yaml(Path(args.case))

    unit = ProtoTemporalUnit(cfg)
    ordered_events = sorted(case["events"], key=lambda e: e["arrival_tick"])

    for event in ordered_events:
        event = {**event, "case_id": case["case_id"]}
        unit.ingest(case["case_id"], event)
        if unit.processed_events >= cfg["coherence_min_events"] and len(unit.coherence_history) >= cfg["coherence_min_steps"] and all(
            c >= cfg["coherence_cutoff_threshold"] for c in unit.coherence_history[-cfg["coherence_min_steps"] :]
        ):
            break

    print(json.dumps(unit.summary(case["case_id"]), indent=2))


if __name__ == "__main__":
    main()
