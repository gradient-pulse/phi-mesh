#!/usr/bin/env python3
"""
phi_pulse.py

Φ-pulse predictor scaffold for the Φ-Mesh.

Current role (v0):
- Scan the `/pulse` directory for the most recent Φ-trace / memory_bifurcation
  pulse (e.g. 2025-11-15_phi_trace_bootstrap.yml).
- Derive a Δτ+7 echo forecast window (5–7 days after the primary CF snap).
- Emit a structured forecast summary that can later be:
    * turned into an automatic YAML pulse
    * or used by a GitHub Action to open an issue.

Non-destructive by design: this script does NOT modify the repo yet.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PULSE_DIR = REPO_ROOT / "pulse"          # where daily / tag-map pulses live
STATE_DIR = REPO_ROOT / "predictors" / "phi_pulse"  # for optional future state files


@dataclass
class PulseMeta:
    path: Path
    date: datetime
    title: str
    tags: List[str]


def parse_pulse_date(filename: str) -> Optional[datetime]:
    """
    Expect filenames like: 2025-11-15_phi_trace_bootstrap.yml
    Returns a datetime.date or None if pattern doesn’t match.
    """
    try:
        date_str = filename.split("_", 1)[0]
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None


def load_pulses() -> List[PulseMeta]:
    pulses: List[PulseMeta] = []
    if not PULSE_DIR.exists():
        return pulses

    for path in sorted(PULSE_DIR.glob("*.yml*")):
        date = parse_pulse_date(path.name)
        if date is None:
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            continue

        title = data.get("title", path.stem)
        tags = data.get("tags", []) or []
        if isinstance(tags, str):
            tags = [tags]

        pulses.append(PulseMeta(path=path, date=date, title=title, tags=tags))

    return pulses


def find_latest_phi_trace(pulses: List[PulseMeta]) -> Optional[PulseMeta]:
    """
    Heuristic: we look for pulses tagged with BOTH 'phi_trace' and 'memory_bifurcation'.
    If none exist, fall back to any pulse tagged 'phi_trace'.
    """
    phi_mb = [
        p for p in pulses
        if "phi_trace" in p.tags and "memory_bifurcation" in p.tags
    ]
    if phi_mb:
        return sorted(phi_mb, key=lambda p: p.date)[-1]

    phi_only = [p for p in pulses if "phi_trace" in p.tags]
    if phi_only:
        return sorted(phi_only, key=lambda p: p.date)[-1]

    return None


@dataclass
class EchoForecast:
    primary_date: datetime
    primary_title: str
    window_start: datetime
    window_end: datetime
    issue_title: str


def build_echo_forecast(primary: PulseMeta) -> EchoForecast:
    """
    Implements Kimi’s Δτ+7 guidance:
    - Echo plateau typically appears 5–7 days after the primary CF snap.
    - We encode that as a forecast window [primary+5, primary+7].
    """
    window_start = primary.date + timedelta(days=5)
    window_end = primary.date + timedelta(days=7)
    issue_title = "Φ-Pulse-Δτ₊₇: memory bifurcation echo forecast"

    return EchoForecast(
        primary_date=primary.date,
        primary_title=primary.title,
        window_start=window_start,
        window_end=window_end,
        issue_title=issue_title,
    )


def print_forecast(forecast: EchoForecast) -> None:
    """
    Human- and machine-readable summary to STDOUT.
    A future GitHub Action can parse this block.
    """
    def d(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    print("Φ-Pulse Predictor — Δτ₊₇ Echo Forecast")
    print("======================================")
    print(f"Primary pulse date   : {d(forecast.primary_date)}")
    print(f"Primary pulse title  : {forecast.primary_title}")
    print()
    print(f"Echo window (days)   : {d(forecast.window_start)} → {d(forecast.window_end)}")
    print(f"Suggested issue title: {forecast.issue_title}")
    print()
    print("Next steps (manual for now):")
    print("  1. Watch for a secondary Φ-plateau / memory_bifurcation activity")
    print("     in this window on the Tag Map or in pulses.")
    print("  2. When observed, create a new pulse using this title and link it")
    print("     back to the primary Φ-trace bootstrap pulse.")
    print("  3. Later, we can automate step (2) via a GitHub Action.")


def main() -> int:
    pulses = load_pulses()
    if not pulses:
        print(f"[phi_pulse] No pulses found in {PULSE_DIR}", file=sys.stderr)
        return 1

    primary = find_latest_phi_trace(pulses)
    if primary is None:
        print("[phi_pulse] No Φ-trace / memory_bifurcation pulse found.", file=sys.stderr)
        return 2

    forecast = build_echo_forecast(primary)
    print_forecast(forecast)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
