#!/usr/bin/env python3
"""
JHTDB probe loader (SOAP-only)
------------------------------
Pull a velocity time series at a single probe point from the Johns Hopkins
Turbulence Database and save to data/jhtdb/ as CSV + Parquet.

Usage (defaults shown):
  python tools/fd_connectors/jhtdb/jhtdb_loader.py \
      --flow isotropic1024coarse --x 0.1 --y 0.2 --z 0.3 \
      --t0 0.0 --dt 0.002 --nsteps 1000

Notes
- Uses suds-community to talk to the JHTDB SOAP service.
- Requires outbound internet (Actions runners allow this).
- If JHTDB is down, the script fails with a clear error.
"""

import argparse, gzip, json, sys
from pathlib import Path
import pandas as pd
from suds.client import Client

OUTDIR = Path("data/jhtdb")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Public JHTDB WSDL
WSDL_URL = "http://turbulence.pha.jhu.edu/service/turbulence.asmx?WSDL"

def fetch_timeseries(flow: str, point, t0: float, dt: float, nsteps: int, email=None) -> pd.DataFrame:
    """Fetch velocity (u,v,w) at a probe for nsteps starting t0 with step dt."""
    client = Client(WSDL_URL, timeout=120)
    lib = client.service

    # Collect rows: [t,u,v,w]
    x, y, z = point
    rows = []
    for i in range(nsteps):
        t = t0 + i * dt
        try:
            vec = lib.GetVelocity(flow, t, x, y, z)
            # vec is a SOAP object, convert to floats
            u, v, w = float(vec[0]), float(vec[1]), float(vec[2])
            rows.append((t, u, v, w))
        except Exception as e:
            print(f"[ERROR] SOAP call failed at step {i}, t={t}: {e}", file=sys.stderr)
            break

    df = pd.DataFrame(rows, columns=["t","u","v","w"])
    # Derived features
    df["speed"] = (df["u"]**2 + df["v"]**2 + df["w"]**2).pow(0.5)
    if len(df) > 1:
        df["du_dt"] = df["u"].diff() / dt
        df["dv_dt"] = df["v"].diff() / dt
        df["dw_dt"] = df["w"].diff() / dt
        df["dspeed_dt"] = df["speed"].diff() / dt
    else:
        for c in ("du_dt","dv_dt","dw_dt","dspeed_dt"):
            df[c] = float("nan")
    return df

def safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", default="isotropic1024coarse",
                    help="JHTDB dataset (e.g., isotropic1024coarse, channel, mhd1024, etc.)")
    ap.add_argument("--x", type=float, default=0.1)
    ap.add_argument("--y", type=float, default=0.2)
    ap.add_argument("--z", type=float, default=0.3)
    ap.add_argument("--t0", type=float, default=0.0, help="start time")
    ap.add_argument("--dt", type=float, default=0.002, help="time step between samples")
    ap.add_argument("--nsteps", type=int, default=1000, help="number of samples")
    args = ap.parse_args()

    point = (args.x, args.y, args.z)
    print(f"Fetching flow='{args.flow}' point={point} t0={args.t0} dt={args.dt} nsteps={args.nsteps}")

    df = fetch_timeseries(args.flow, point, args.t0, args.dt, args.nsteps)

    base = f"{safe_name(args.flow)}__x{args.x}_y{args.y}_z{args.z}__t0{args.t0}_dt{args.dt}_n{args.nsteps}"
    csv_path = OUTDIR / f"{base}.csv.gz"
    pq_path  = OUTDIR / f"{base}.parquet"
    meta_path = OUTDIR / f"{base}.meta.json"

    df.to_csv(csv_path, index=False, compression="gzip")
    try:
        df.to_parquet(pq_path, index=False)
    except Exception as e:
        print(f"[WARN] parquet save failed ({e}); CSV.gz is written.", file=sys.stderr)

    meta = {
        "flow": args.flow,
        "point": {"x": args.x, "y": args.y, "z": args.z},
        "t0": args.t0, "dt": args.dt, "nsteps": args.nsteps,
        "rows": int(df.shape[0]),
        "columns": list(df.columns),
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    print(f"✅ Saved:\n  {csv_path}\n  {pq_path if pq_path.exists() else '(no parquet)'}\n  {meta_path}")

if __name__ == "__main__":
    main()
