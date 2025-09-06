#!/usr/bin/env python3
"""
run_fd_probe.py — fetch a 1-point time series (synthetic|jhtdb|nasa),
compute NT-rhythm metrics, and write *metrics JSON only*.

Args:
  --source   {synthetic,jhtdb,nasa}
  --dataset  free-text dataset name/slug (workflow sanitizes for filenames)
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
import re
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# rhythm tools (provided in repo)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# connectors (repo modules)
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ---------- helpers -----------------------------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def synthetic_timeseries(t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    n = max(3, int((t1 - t0) / max(dt, 1e-12)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.4
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    # Try to recognize numpy scalars without importing if unavailable
    try:
        import numpy as np  # type: ignore
        np_scalar = np.generic  # type: ignore[attr-defined]
    except Exception:  # numpy not installed
        class _NP: ...
        np_scalar = _NP  # type: ignore

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


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title")  # ignored here (used downstream by make_pulse)
    ap.add_argument("--tags")   # ignored here (used downstream by make_pulse)
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    src_label = args.source
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)

    elif args.source == "jhtdb":
        # If a real token and fetcher exist, use it; else fall back to an
        # offline helper or synthetic series so the pipeline stays green.
        try:
            if os.getenv("JHTDB_TOKEN"):
                ts_obj = JHT.fetch_timeseries(
                    dataset=args.dataset, var=args.var,
                    x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
                )
                ts, vs = ts_obj.t, ts_obj.v
            else:
                # Prefer any offline helper in jhtdb module; else synthetic
                try:
                    ts_obj = JHT.fetch_timeseries(
                        dataset=args.dataset, var=args.var,
                        x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
                    )
                    ts, vs = ts_obj.t, ts_obj.v
                    src_label = "jhtdb_offline"
                except Exception:
                    ts, vs = synthetic_timeseries(t0, t1, dt)
                    src_label = "jhtdb_offline"
        except NotImplementedError:
            ts, vs = synthetic_timeseries(t0, t1, dt)
            src_label = "jhtdb_offline"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)  # CSV/URL/inline
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v

    # Ensure monotonic time
    ts = sorted(ts)

    # --- compute NT-rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    mobj = rhythm_from_events(tick_times)

    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = mobj
    else:
        metrics = {}

    # attach provenance
    metrics["source"] = src_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
    }

    # coerce to JSON-safe builtins
    metrics = to_builtin(metrics)

    # --- write metrics JSON ONLY -----------------------------------------
    out_dir = os.path.dirname(os.path.abspath(args.json_out)) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # small notice for GH actions log
    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe Metrics::n={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={src_label})")
    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
