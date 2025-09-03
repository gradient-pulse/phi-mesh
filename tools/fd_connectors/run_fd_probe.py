# tools/fd_connectors/run_fd_probe.py
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

# --- make repo root importable ------------------------------------------------
HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]          # <repo>/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# now this works even when called as a script
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

def synthetic_series(var: str, t0: float, t1: float, dt: float):
    import math
    t = t0
    out = []
    while t <= t1 + 1e-12:
        # simple quasi-periodic signal for offline mode
        val = (
            0.7 * math.sin(2.0 * math.pi * 0.5 * t)
            + 0.3 * math.sin(2.0 * math.pi * 0.13 * t + 0.4)
        )
        out.append((t, val))
        t += dt
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["jhtdb", "nasa", "synthetic"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    args = ap.parse_args()

    x, y, z = [float(v) for v in args.xyz.split(",")]
    t0, t1, dt = [float(v) for v in args.twin.split(",")]

    # until real APIs are wired, always use synthetic
    series = synthetic_series(args.var, t0, t1, dt)

    # we only need event times for NT rhythm; use time stamps directly
    times = [t for (t, _) in series]
    ticks = ticks_from_message_times(times)
    metrics = rhythm_from_events(ticks)

    payload = {
        "source": args.source,
        "dataset": args.dataset,
        "var": args.var,
        "point": [x, y, z],
        "twin": [t0, t1, dt],
        "n": len(ticks),
        "mean_dt": metrics.get("mean_dt"),
        "cv_dt": metrics.get("cv_dt"),
    }
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w") as f:
        json.dump(payload, f, indent=2)

if __name__ == "__main__":
    main()
