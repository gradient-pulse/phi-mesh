#!/usr/bin/env python3
"""
run_fd_probe.py — fetch a 1-point time series from (synthetic | JHTDB | NASA CSV),
compute NT rhythm metrics, and write a metrics JSON file.

Usage:
  python tools/fd_connectors/run_fd_probe.py \
    --source synthetic \
    --dataset demo \
    --var u \
    --point 0.1,0.1,0.1 \
    --window 0.0,10.0,0.01 \
    --json-out results/fd_probe/demo.metrics.json
"""

from __future__ import annotations
import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# Local imports (repo root added to PYTHONPATH in workflow)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,   # returns a dataclass or dict with n / mean_dt / cv_dt
)

from tools.fd_connectors.jhtdb import JHTDBClient
from tools.fd_connectors.nasa import read_csv_timeseries


# ------------------------ parsing helpers ---------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected triplet like 'a,b,c', got {s!r}")
    return (float(parts[0]), float(parts[1]), float(parts[2]))

def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / paths into plain builtin types for JSON."""
    try:
        import numpy as np
        np_generic = np.generic
    except Exception:
        class _NP: ...
        np_generic = _NP

    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)  # fallback


# ------------------------ sources -----------------------------------------

def fetch_synthetic(var: str, x: float, y: float, z: float, t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    """Simple multi-tone signal — enough structure to let NT rhythm pop out."""
    n = max(3, int((t1 - t0) / max(dt, 1e-9)))
    t = [t0 + i * dt for i in range(n)]
    base = 0.4  # Hz-ish in arbitrary units
    v = [
        math.sin(2 * math.pi * base * (ti - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (ti - t0))
        for ti in t
    ]
    return t, v


def fetch_timeseries(
    source: str,
    dataset: str,
    var: str,
    x: float, y: float, z: float,
    t0: float, t1: float, dt: float
) -> Tuple[List[float], List[float], Dict[str, Any]]:
    """
    Returns (t, v, details), where details holds provenance we include in metrics JSON.
    """
    source = (source or "").strip().lower()
    if source == "synthetic":
        t, v = fetch_synthetic(var, x, y, z, t0, t1, dt)
        details = {"var": var, "xyz": [x, y, z], "window": {"t0": t0, "t1": t1, "dt": dt}}
        return t, v, details

    if source == "jhtdb":
        client = JHTDBClient()  # respects JHTDB_OFFLINE and JHTDB_TOKEN
        ts = client.fetch_timeseries(dataset=dataset, var=var, x=x, y=y, z=z, t0=t0, t1=t1, dt=dt)
        details = {"var": var, "xyz": [x, y, z], "window": {"t0": t0, "t1": t1, "dt": dt}}
        return ts.t, ts.v, details

    if source == "nasa":
        csv_path = os.getenv("NASA_CSV", "")
        if not csv_path:
            raise RuntimeError("NASA_CSV repo secret not set; cannot read NASA CSV.")
        ts = read_csv_timeseries(csv_path)
        details = {"var": var, "xyz": [x, y, z], "window": {"t0": t0, "t1": t1, "dt": dt}, "csv": os.path.basename(csv_path)}
        return ts.t, ts.v, details

    raise ValueError(f"Unknown source: {source!r}")


# ------------------------ main --------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=("synthetic", "jhtdb", "nasa"))
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--point", required=True, help="x,y,z")
    ap.add_argument("--window", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title", default="NT Rhythm — FD Probe")  # forwarded by workflow (not used here)
    ap.add_argument("--tags", default="nt_rhythm")
    args = ap.parse_args()

    x, y, z = parse_triplet(args.point)
    t0, t1, dt = parse_triplet(args.window)

    # 1) Fetch timeseries
    t, v, details = fetch_timeseries(
        source=args.source,
        dataset=args.dataset,
        var=args.var,
        x=x, y=y, z=z,
        t0=t0, t1=t1, dt=dt,
    )

    # 2) Convert to NT tick intervals and measure rhythm
    #    (Use timestamps directly as "event times" for the simple probe.)
    #    If you want threshold-crossing events instead, derive events from v[] first.
    events = t  # one event per sample; okay for now
    ticks = ticks_from_message_times(events)
    metrics = rhythm_from_events(ticks)

    # 3) Normalize metrics (dataclass or dict) → plain JSON + provenance
    if is_dataclass(metrics):
        md = asdict(metrics)
    elif isinstance(metrics, dict):
        md = metrics
    else:
        # last resort: try attribute access
        md = {
            "n": getattr(metrics, "n", None),
            "mean_dt": getattr(metrics, "mean_dt", None),
            "cv_dt": getattr(metrics, "cv_dt", None),
        }

    out = {
        "source": args.source,
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "twin": {"t0": t0, "t1": t1, "dt": dt},
        "n": md.get("n"),
        "mean_dt": md.get("mean_dt"),
        "cv_dt": md.get("cv_dt"),
        "details": details,
    }

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(to_builtin(out), f, ensure_ascii=False, indent=2)

    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
