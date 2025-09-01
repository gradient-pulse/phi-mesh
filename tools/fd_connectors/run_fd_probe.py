# tools/fd_connectors/run_fd_probe.py
# Fetch an FD time series, compute NT rhythm metrics, emit JSON and a pulse.

import argparse, json, subprocess, tempfile
from pathlib import Path

from tools.agent_rhythm.rhythm import ticks_from_message_times, rhythm_from_events

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--t1", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--title", default="NT Rhythm — FD Probe")
    ap.add_argument("--tags", nargs="+", default=["nt_rhythm","turbulence","navier_stokes","rgp"])
    ap.add_argument("--outdir", default="results/agent_rhythm")
    ap.add_argument("--pulse_dir", default="pulse/auto")
    args = ap.parse_args()

    if args.source == "jhtdb":
        from tools.fd_connectors.jhtdb import JHTDBClient
        cli = JHTDBClient()
        ts = cli.fetch_timeseries(args.dataset, args.var, args.x, args.y, args.z, args.t0, args.t1, args.dt)
    else:
        from tools.fd_connectors.nasa import fetch_timeseries
        ts = fetch_timeseries(args.dataset, args.var, args.x, args.y, args.z, args.t0, args.t1, args.dt)

    # Compute NT rhythm
    ticks = ticks_from_message_times(ts.t)
    stats = rhythm_from_events(ticks)

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    metrics_path = Path(args.outdir) / f"{args.dataset}.metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(stats, f)

    # Reuse make_pulse script to generate strict YAML pulse
    subprocess.check_call([
        "python",
        "tools/agent_rhythm/make_pulse.py",
        "--metrics", str(metrics_path),
        "--title", args.title,
        "--dataset", args.dataset,
        "--tags", *args.tags,
        "--outdir", args.pulse_dir,
    ])

if __name__ == "__main__":
    main()
