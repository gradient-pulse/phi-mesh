# tools/fd_connectors/run_fd_probe.py
import os
import sys
import json
import argparse
from dataclasses import asdict, is_dataclass
from typing import Tuple

import numpy as np

# ---- add repo root to sys.path so "tools.*" imports work in Actions ----
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import rhythm utilities (object or dict returns are both supported)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

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
    if m is None:
        return {"n": 0, "mean_dt": None, "cv_dt": None}
    if isinstance(m, dict):
        return {"n": m.get("n"), "mean_dt": m.get("mean_dt"), "cv_dt": m.get("cv_dt")}
    if is_dataclass(m):
        d = asdict(m)
        return {"n": d.get("n"), "mean_dt": d.get("mean_dt"), "cv_dt": d.get("cv_dt")}
    return {
        "n": getattr(m, "n", None),
        "mean_dt": getattr(m, "mean_dt", None),
        "cv_dt": getattr(m, "cv_dt", None),
    }

def fetch_timeseries_synthetic(t0: float, t1: float, dt: float, base_period: float = 0.7) -> np.ndarray:
    t = np.arange(t0, t1 + 1e-9, dt)
    # Only need timestamps; a dummy signal is fine for cadence detection
    _ = np.sin(2 * np.pi * t / base_period) + 0.05 * np.random.randn(t.size)
    return t

def fetch_timeseries_jhtdb(dataset: str, var: str, xyz: Tuple[float, float, float],
                           t0: float, t1: float, dt: float) -> np.ndarray:
    if os.environ.get("JHTDB_OFFLINE", "0") == "1":
        return fetch_timeseries_synthetic(t0, t1, dt)
    # TODO: real JHTDB call
    return fetch_timeseries_synthetic(t0, t1, dt)

def fetch_timeseries_nasa(dataset: str, var: str, xyz: Tuple[float, float, float],
                          t0: float, t1: float, dt: float) -> np.ndarray:
    # TODO: real NASA call
    return fetch_timeseries_synthetic(t0, t1, dt)

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

    if args.source == "synthetic":
        times = fetch_timeseries_synthetic(t0, t1, dt)
    elif args.source == "jhtdb":
        times = fetch_timeseries_jhtdb(args.dataset, args.var, (x, y, z), t0, t1, dt)
    else:
        times = fetch_timeseries_nasa(args.dataset, args.var, (x, y, z), t0, t1, dt)

    _ticks = ticks_from_message_times(times)
    metrics_obj = rhythm_from_events(times)
    metrics = metrics_to_dict(metrics_obj)

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
