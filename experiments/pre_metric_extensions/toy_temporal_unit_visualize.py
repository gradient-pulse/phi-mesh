#!/usr/bin/env python3
"""Minimal visualization for the proto temporal unit toy case."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from toy_temporal_unit_sim import (
    CASE_PATH,
    CONFIG_PATH,
    build_events,
    group_simultaneity_families,
    load_yaml,
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "toy_temporal_unit_visualization.png"


STRING_ORDER = [
    "target_unclear",
    "contamination_rising",
    "patch_overreach",
    "coherence_restoration",
    "rebuild_readiness",
    "other",
]

STRING_COLORS = {
    "target_unclear": "#4C78A8",
    "contamination_rising": "#E45756",
    "patch_overreach": "#F58518",
    "coherence_restoration": "#54A24B",
    "rebuild_readiness": "#9D755D",
    "other": "#B279A2",
}


def main() -> None:
    case_data = load_yaml(CASE_PATH)
    cfg = load_yaml(CONFIG_PATH)

    events = build_events(case_data)
    families = group_simultaneity_families(events, int(cfg["simultaneity_window"]))

    present_strings = [s for s in STRING_ORDER if any(e.string_id == s for e in events)]
    y_map = {sid: idx for idx, sid in enumerate(present_strings)}

    fig, ax = plt.subplots(figsize=(10, 4 + 0.25 * len(present_strings)))

    for family_id, member_ids in families.items():
        family_events = [e for e in events if e.event_id in set(member_ids)]
        x0 = min(e.arrival_tick for e in family_events) - 0.15
        x1 = max(e.arrival_tick for e in family_events) + 0.15
        y0 = min(y_map[e.string_id] for e in family_events) - 0.3
        y1 = max(y_map[e.string_id] for e in family_events) + 0.3
        ax.add_patch(
            plt.Rectangle(
                (x0, y0),
                x1 - x0,
                y1 - y0,
                edgecolor="#BBBBBB",
                facecolor="none",
                linewidth=1.0,
                linestyle="--",
                alpha=0.7,
            )
        )
        ax.text(x1 + 0.03, (y0 + y1) / 2, f"F{family_id}", fontsize=8, va="center")

    for event in events:
        x = event.arrival_tick
        y = y_map[event.string_id]
        color = STRING_COLORS.get(event.string_id, STRING_COLORS["other"])
        ax.scatter(x, y, s=130, c=color, edgecolors="black", linewidths=0.6, zorder=3)
        ax.text(x + 0.05, y + 0.07, event.event_id, fontsize=8)

    max_tick = max(e.arrival_tick for e in events)
    ax.set_xticks(list(range(0, max_tick + 1)))
    ax.set_xlabel("event tick")
    ax.set_yticks([y_map[s] for s in present_strings])
    ax.set_yticklabels(present_strings)
    ax.set_ylabel("vertical longitudinal strings")
    ax.set_title("Toy temporal unit: strings, simultaneity families, and event positions")
    ax.grid(axis="x", linestyle=":", alpha=0.5)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    plt.close(fig)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
