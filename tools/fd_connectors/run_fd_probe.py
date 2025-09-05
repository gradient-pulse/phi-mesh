#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic | jhtdb | nasa),
compute NT-rhythm metrics, and write a metrics JSON (consumed by make_pulse.py).

CLI:
  --source    {synthetic,jhtdb,nasa}
  --dataset   free-text dataset name/slug (workflow already sanitizes)
  --var       variable name (e.g., "u")
  --xyz       "x,y,z"
  --twin      "t0,t1,dt"
  --json-out  path to write metrics JSON
  --title     (unused here; carried by make_pulse)
  --tags      (unused here; carried by make_pulse)
"""

from __future__ import annotations

# --- ensure repo-root is on sys.path so "tools.*" imports resolve ----------
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# rhythm tools
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# source connectors
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ------------------------------- utils ------------------------------------- #

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Recursively coerce common scientific types into plain Python builtins."""
    try:
        import numpy as np
        np_generic = np.generic  # type: ignore[attr-defined]
        np_ndarray = np.ndarray  # type: ignore[attr-defined]
    except Exception:
        class _NP: ...
        np_generic = _NP  # sentinel
        np_ndarray = _NP  # sentinel

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):  # numpy scalar
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, np_ndarray):  # numpy array -> list
        return [to_builtin(v) for v in x.tolist()]
    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


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


# ------------------------------- main -------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title")  # carried by make_pulse
    ap.add_argument("--tags")   # carried by make_pulse
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        ts_obj = JHT.fetch_timeseries(
            dataset=args.dataset, var=args.var,
            x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
        )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "jhtdb"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time
    if ts and any(ts[i] > ts[i + 1] for i in range(len(ts) - 1)):
        order = sorted(range(len(ts)), key=lambda i: ts[i])
        ts = [ts[i] for i in order]
        vs = [vs[i] for i in order]

    # --- compute NT rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    mobj = rhythm_from_events(tick_times)

    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = dict(mobj)
    else:
        metrics = {}

    metrics.setdefault("source", source_label)
    metrics.setdefault("details", {})
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
        **(metrics.get("details") or {}),
    }

    metrics = to_builtin(metrics)

    # --- write metrics JSON ----------------------------------------------
    out_path = args.json_out
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::{args.source} n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}")
    print(f"Wrote metrics → {out_path}")


if __name__ == "__main__":
    main()
