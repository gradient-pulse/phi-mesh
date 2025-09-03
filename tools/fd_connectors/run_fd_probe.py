#!/usr/bin/env python3
"""
FD probe → rhythm metrics → pulse (auto).

Supports:
  --source synthetic | jhtdb | nasa
For jhtdb: uses tools.fd_connectors.jhtdb.fetch_timeseries (offline by default).
"""

from __future__ import annotations
import argparse
import json
import os
from typing import Tuple

# import rhythm utils
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# connectors
from tools.fd_connectors.jhtdb import fetch_timeseries as jhtdb_fetch

def _parse_xyz(s: str) -> Tuple[float, float, float]:
    x, y, z = (v.strip() for v in s.split(","))
    return float(x), float(y), float(z)

def _parse_window(s: str) -> Tuple[float, float, float]:
    t0, t1, dt = (v.strip() for v in s.split(","))
    return float(t0), float(t1), float(dt)

def _synthetic_timeseries(dataset: str, var: str, xyz, t0, t1, dt):
    # delegate to jhtdb offline generator via env if you like;
    # here keep a tiny local fallback:
    os.environ.setdefault("JHTDB_OFFLINE", "1")
    return jhtdb_fetch(dataset=dataset, var=var, xyz=xyz, t0=t0, t1=t1, dt=dt, token=None)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["synthetic", "jhtdb", "nasa"], required=True)
    ap.add_argument("--dataset", required=True, help="dataset slug (e.g., isotropic1024)")
    ap.add_argument("--var", required=True, default="u")
    ap.add_argument("--point", required=True, help="x,y,z (e.g., 0.1,0.1,0.1)")
    ap.add_argument("--window", required=True, help="t0,t1,dt (e.g., 0.0,10.0,0.01)")
    ap.add_argument("--json-out", default=None, help="Write metrics JSON here (optional)")
    ap.add_argument("--title", default="NT Rhythm — FD Probe")
    ap.add_argument("--tags", default="nt_rhythm turbulence navier_stokes rgp")
    args = ap.parse_args()

    xyz = _parse_xyz(args.point)
    t0, t1, dtv = _parse_window(args.window)

    # ---- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        t, y = _synthetic_timeseries(args.dataset, args.var, xyz, t0, t1, dtv)
    elif args.source == "jhtdb":
        token = os.getenv("JHTDB_TOKEN")
        t, y = jhtdb_fetch(dataset=args.dataset, var=args.var, xyz=xyz,
                           t0=t0, t1=t1, dt=dtv, token=token)
    else:
        # placeholder for future NASA wiring
        t, y = _synthetic_timeseries(args.dataset, args.var, xyz, t0, t1, dtv)

    # ---- compute rhythm metrics ------------------------------------------
    # Convert to ticks: here we use sample times directly.
    ticks = ticks_from_message_times(t)
    metrics = rhythm_from_events(ticks)

    # include provenance for the pulse summary
    metrics_out = {
        "source": args.source,
        "dataset": args.dataset,
        "var": args.var,
        "xyz": list(xyz),
        "twin": {"t0": t0, "t1": t1, "dt": dtv},
        "n": metrics.get("n"),
        "mean_dt": metrics.get("mean_dt"),
        "cv_dt": metrics.get("cv_dt"),
    }

    # optional debug artifact
    out_json = args.json_out or os.path.join("results", "fd_probe", f"{args.dataset}.metrics.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(metrics_out, f, indent=2)

    # emit pulse via make_pulse.py
    from tools.agent_rhythm.make_pulse import safe_slug  # reuse helper
    dataset_slug = safe_slug(args.dataset)
    os.makedirs("pulse/auto", exist_ok=True)

    # Call the pulse maker as a library to avoid another process
    from tools.agent_rhythm import make_pulse
    make_pulse_main = getattr(make_pulse, "main", None)

    if make_pulse_main is None:
        # Fallback: invoke via subprocess if needed (shouldn’t happen the way repo is laid out)
        import subprocess, sys
        subprocess.check_call([
            sys.executable, "tools/agent_rhythm/make_pulse.py",
            "--metrics", out_json,
            "--title", args.title,
            "--dataset", dataset_slug,
            "--tags", args.tags,
            "--outdir", "pulse/auto",
        ])
    else:
        # mimic CLI call by building argv for make_pulse.main
        import sys
        old_argv = sys.argv[:]
        try:
            sys.argv = [
                "make_pulse.py",
                "--metrics", out_json,
                "--title", args.title,
                "--dataset", dataset_slug,
                "--tags", args.tags,
                "--outdir", "pulse/auto",
            ]
            make_pulse_main()
        finally:
            sys.argv = old_argv

if __name__ == "__main__":
    main()
