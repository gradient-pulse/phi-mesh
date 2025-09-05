#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic | jhtdb | nasa),
compute NT-rhythm metrics, and write a metrics JSON that make_pulse.py
can turn into a Φ-Mesh pulse.

Args (aligned with fd_probe.yml):
  --source     {synthetic,jhtdb,nasa}
  --dataset    dataset name/slug or path (workflow sanitizes when needed)
  --var        variable name (e.g., "u")
  --xyz        "x,y,z"   (probe location)
  --twin       "t0,t1,dt" (time window)
  --json-out   path to write metrics JSON
  --title      (unused here; carried into pulse later)
  --tags       (unused here; carried into pulse later)

Notes
- We intentionally write exactly ONE metrics file (no *_latest twin) to
  keep the results namespace clear and batch-driven.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# rhythm tools (already in your tree)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# source connectors (already in your tree)
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ---------------------------------------------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Recursively coerce to plain Python builtins for JSON/YAML friendliness."""
    try:
        import numpy as np  # noqa: WPS433
        np_scalar = np.generic  # type: ignore[attr-defined]
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
    """Simple multi-tone signal for dry runs."""
    n = max(3, int((t1 - t0) / max(dt, 1e-9)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.4
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True, help="Path to write metrics JSON")
    ap.add_argument("--title")  # unused here (make_pulse handles it)
    ap.add_argument("--tags")   # unused here (make_pulse handles it)
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        # Delegate to your jhtdb connector; it can decide offline/online.
        # (If the JHTDB module is wired to the testing token, this will
        # produce a small time series consistent with the limits.)
        ts_obj = JHT.fetch_timeseries(
            dataset=args.dataset, var=args.var,
            x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
        )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "jhtdb"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)  # CSV / URL / inline
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time (connectors *should* give this, but be safe)
    ts = sorted(ts)

    # --- compute NT rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    mobj = rhythm_from_events(tick_times)

    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = dict(mobj)
    else:
        metrics = {}

    # Augment: simple interval stats (n, mean_dt, cv_dt) from the time vector
    if ts and len(ts) > 2:
        dts = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]
        n_events = len(dts)
        mean_dt = sum(dts) / max(n_events, 1)
        if n_events > 1 and mean_dt > 0:
            var = sum((dt_ - mean_dt) ** 2 for dt_ in dts) / n_events
            std = math.sqrt(var)
            cv_dt = std / mean_dt
        else:
            cv_dt = 0.0
        metrics["n"] = n_events
        metrics["mean_dt"] = mean_dt
        metrics["cv_dt"] = cv_dt

    metrics["source"] = source_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
    }
    metrics = to_builtin(metrics)

    # --- write metrics JSON ----------------------------------------------
    os.makedirs(os.path.dirname(args.json_out) or ".", exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # Friendly notice for workflow logs
    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::{args.source} n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}")
    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
