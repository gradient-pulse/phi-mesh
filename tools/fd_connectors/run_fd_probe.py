#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic|jhtdb|nasa),
compute NT-rhythm metrics, and write metrics JSON (for make_pulse.py).

Args (aligned with fd_probe.yml):
  --source   {synthetic,jhtdb,nasa}
  --dataset  free-text dataset name/slug OR path/URL for nasa
  --var      variable name (e.g., "u")
  --xyz      "x,y,z"
  --twin     "t0,t1,dt"
  --json-out path to write metrics JSON
  --title    (unused here; carried by make_pulse)
  --tags     (unused here; carried by make_pulse)
"""
from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Dict, Any, Tuple, List

# rhythm tools
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# source connectors
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ---------------------------- helpers --------------------------------------
def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    try:
        import numpy as np
        np_scalar = np.generic
    except Exception:  # numpy not installed
        class _S: ...
        np_scalar = _S  # type: ignore

    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_scalar):
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, dict):
        return {str(k): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


def synthetic_timeseries(t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    n = max(3, int((t1 - t0) / max(dt, 1e-9)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.4
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


def looks_like_path_or_url(s: str) -> bool:
    """Heuristic: decide if a string is a repo path or URL."""
    s = (s or "").strip().lower()
    return (
        "/" in s
        or s.endswith(".csv")
        or s.startswith("http://")
        or s.startswith("https://")
        or s.startswith("s3://")
        or s.startswith("gs://")
    )


# ------------------------------ main ---------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title")
    ap.add_argument("--tags")
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        # offline synthetic inside JHT for now unless token is present
        if os.getenv("JHTDB_OFFLINE", "0") == "1" or not os.getenv("JHTDB_TOKEN"):
            try:
                ts_obj = JHT.fetch_timeseries(
                    dataset=args.dataset, var=args.var,
                    x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
                )
                ts, vs = ts_obj.t, ts_obj.v
            except Exception:
                ts, vs = synthetic_timeseries(t0, t1, dt)
            source_label = "jhtdb_offline"
        else:
            ts_obj = JHT.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
            ts, vs = ts_obj.t, ts_obj.v
            source_label = "jhtdb"

    else:  # nasa
        # Prefer the UI 'dataset' when it looks like a path/URL;
        # otherwise fall back to the NASA_CSV secret if present.
        ui = args.dataset.strip()
        secret_csv = os.getenv("NASA_CSV", "").strip()

        if looks_like_path_or_url(ui):
            nasa_csv = ui
        elif secret_csv:
            nasa_csv = secret_csv
        else:
            nasa_csv = ""

        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)  # CSV/URL/inline
        else:
            # Fallback: call the (stub) fetch_timeseries; this will raise until wired.
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time (some sources may not guarantee order)
    ts = sorted(ts)

    # --- compute NT rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    mobj = rhythm_from_events(tick_times)
    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = mobj
    else:
        metrics = {}

    metrics["source"] = source_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
    }
    metrics = to_builtin(metrics)

    # --- write metrics JSON ----------------------------------------------
    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::n={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={source_label})")
    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
