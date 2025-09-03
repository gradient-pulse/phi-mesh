# tools/fd_connectors/run_fd_probe.py
import os
import json
import argparse
from dataclasses import asdict, is_dataclass
from typing import Tuple, List

import numpy as np

# Import rhythm utilities
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,  # expected to return object or dict with n, mean_dt, cv_dt
)

# --- Helpers --------------------------------------------------------------

def parse_xyz(s: str) -> Tuple[float, float, float]:
    try:
        x, y, z = (float(v.strip()) for v in s.split(","))
        return x, y, z
    except Exception:
        raise argparse.ArgumentTypeError("xyz must be 'x,y,z' (floats)")

def parse_twin(s: str) -> Tuple[float, float, float]:
    try:
        t0, t1, dt = (float(v.strip()) for v in s.split(","))
        if dt <= 0 or t1 <= t0:
            raise ValueError
        return t0, t1, dt
    except Exception:
        raise argparse.ArgumentTypeError("twin must be 't0,t1,dt' with t1>t0 and dt>0")

def metrics_to_dict(m) -> dict:
    """Accept dataclass, object with attrs, or dict; return plain dict."""
    if m is None:
        return {"n": 0, "mean_dt": None, "cv_dt": None}
    if isinstance(m, dict):
        # Normalize keys
        return {
            "n": m.get("n"),
            "mean_dt": m.get("mean_dt"),
            "cv_dt": m.get("cv_dt"),
        }
    if is_dataclass(m):
        d = asdict(m)
        return {"n": d.get("n"), "mean_dt": d.get("mean_dt"), "cv_dt": d.get("cv_dt")}
    # Fallback: attribute access
    return {
        "n": getattr(m, "n", None),
        "mean_dt": getattr(m, "mean_dt", None),
        "cv_dt": getattr(m, "cv_dt", None),
    }

# --- Fake/placeholder connectors -----------------------------------------

def fetch_timeseries_synthetic(t0: float, t1: float, dt: float, base_period: float = 0.7) -> np.ndarray:
    """Create a synthetic time series with a gently jittered cadence."""
    t = np.arange(t0, t1 + 1e-9, dt)
    # Example ‘signal’: a noisy sine—only used to demonstrate cadence extraction.
    _ = np.sin(2 * np.pi * t / base_period) + 0.05 * np.random.randn(t.size)
    return t  # We only need timestamps for NT rhythm

def fetch_timeseries_jhtdb(dataset: str, var: str, xyz: Tuple[float, float, float],
                           t0: float, t1: float, dt: float) -> np.ndarray:
    """
    Placeholder JHTDB connector.
    If JHTDB_OFFLINE=1 or no real connector is wired yet, return synthetic timestamps.
    """
    if os.environ.get("JHTDB_OFFLINE", "0") == "1":
        return fetch_timeseries_synthetic(t0, t1, dt)
    # TODO: replace with real JHTDB API calls
    return fetch_timeseries_synthetic(t0, t1, dt)

def fetch_timeseries_nasa(dataset: str, var: str, xyz: Tuple[float, float, float],
                          t0: float, t1: float, dt: float) -> np.ndarray:
    """
    Placeholder NASA CFD connector.
    """
    return fetch_timeseries_synthetic(t0, t1, dt)

# --- Main ----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["jhtdb", "nasa", "synthetic"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, type=parse_xyz, help="x,y,z")
    ap.add_argument("--twin", required=True, type=parse_twin, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True, help="Output JSON path for metrics")
    args = ap.parse_args()

    x, y, z = args.xyz
    t0, t1, dt = args.twin

    # 1) Fetch timestamps
    if args.source == "synthetic":
        times = fetch_timeseries_synthetic(t0, t1, dt)
    elif args.source == "jhtdb":
        times = fetch_timeseries_jhtdb(args.dataset, args.var, (x, y, z), t0, t1, dt)
    else:  # nasa
        times = fetch_timeseries_nasa(args.dataset, args.var, (x, y, z), t0, t1, dt)

    # 2) Compute rhythm metrics
    #    (If your rhythm_from_events expects raw times, pass times;
    #     if it expects tick intervals, use ticks_from_message_times first.)
    _ticks = ticks_from_message_times(times)  # keep for potential future use
    metrics_obj = rhythm_from_events(times)

    metrics = metrics_to_dict(metrics_obj)

    # 3) Write JSON
    out = {
        "source": args.source,
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "twin": {"t0": t0, "t1": t1, "dt": dt},
        "n": metrics["n"],
        "mean_dt": metrics["mean_dt"],
        "cv_dt": metrics["cv_dt"],
    }

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
