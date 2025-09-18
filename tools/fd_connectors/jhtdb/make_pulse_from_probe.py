#!/usr/bin/env python3
import argparse, json, os, datetime as dt, pathlib, yaml

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--nsteps", type=int, required=True)
    ap.add_argument("--slug", default="isotropic")
    args = ap.parse_args()

    # detect analysis JSON
    stem = f"{args.flow}__x{args.x}_y{args.y}_z{args.z}__t0_{args.t0}_dt{args.dt}_n{args.nsteps}"
    analysis = f"results/fd_probe/{stem}.analysis.json"
    analysis_abs = os.path.abspath(analysis)
    f0 = None
    try:
        with open(analysis, "r", encoding="utf-8") as fh:
            a = json.load(fh)
        # try dominant, else 0
        f0 = float(a.get("dominant_freq_hz") or 0.0)
    except Exception:
        pass

    today = dt.date.today().isoformat()
    # filename = date + slug + batchN is handled by workflow commit cadence; we keep it simple:
    outdir = pathlib.Path("pulse/auto"); outdir.mkdir(parents=True, exist_ok=True)
    # monotonically increasing batch number per day
    existing = sorted(outdir.glob(f"{today}_{args.slug}_batch*.yml"))
    batch = (max([int(p.stem.rsplit("batch",1)[-1]) for p in existing], default=0) + 1)

    pulse_path = outdir / f"{today}_{args.slug}_batch{batch}.yml"

    hint = "no fundamental detected" if not f0 or f0 <= 0 else f"fundamental ≈ {f0:.4g} Hz"
    payload = {
        "title": f"'{args.slug.upper()} — JHTDB Probe'",
        "summary": f"Probe at (x={args.x}, y={args.y}, z={args.z}) over n={args.nsteps} samples; {hint}.",
        "tags": ["nt_rhythm", "turbulence", "navier_stokes", "jhtdb"],
        "papers": [],
        "podcasts": [],
        "meta": {
            "flow": args.flow,
            "point": {"x": args.x, "y": args.y, "z": args.z},
            "t0": args.t0, "dt": args.dt, "nsteps": args.nsteps,
            "analysis_json": analysis_abs,
        },
        "hint": hint,
    }

    with open(pulse_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, sort_keys=False)

    print(f"wrote pulse: {pulse_path}")

if __name__ == "__main__":
    main()
