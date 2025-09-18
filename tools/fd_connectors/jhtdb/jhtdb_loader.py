#!/usr/bin/env python3
"""
JHTDB probe loader (SOAP-only)
------------------------------
Pull a velocity time series at a single probe point from the Johns Hopkins
Turbulence Database and save to data/jhtdb/ as CSV (+Parquet if available).

Usage (defaults shown):
  python tools/fd_connectors/jhtdb/jhtdb_loader.py \
      --flow isotropic1024coarse --x 0.1 --y 0.2 --z 0.3 \
      --t0 0.0 --dt 0.0005 --nsteps 2400 --slug isotropic
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from suds.client import Client

OUTDIR = Path("data/jhtdb")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Public JHTDB WSDL (HTTPS to avoid 308 redirects)
WSDL_URL = "https://turbulence.pha.jhu.edu/service/turbulence.asmx?WSDL"


def fetch_timeseries(flow: str, point, t0: float, dt: float, nsteps: int) -> pd.DataFrame:
    """Fetch velocity (u, v, w) at a probe for nsteps starting t0 with step dt."""
    client = Client(WSDL_URL, timeout=120)

    # Some environments still default to http; nudge to https explicitly if present
    try:
        client.options.location = client.wsdl.services[0].ports[0].location.replace("http://", "https://")
    except Exception:
        pass

    lib = client.service

    x, y, z = point
    rows = []
    for i in range(int(nsteps)):
        t = t0 + i * dt
        try:
            vec = lib.GetVelocity(flow, t, x, y, z)  # returns (u,v,w)-like SOAP array
            u, v, w = float(vec[0]), float(vec[1]), float(vec[2])
            rows.append((t, u, v, w))
        except Exception as e:
            # If JHTDB is flaky mid-stream, stop cleanly; downstream will see short/empty series
            print(f"[WARN] SOAP call failed at step {i} (t={t}): {e}")
            break

    df = pd.DataFrame(rows, columns=["t", "u", "v", "w"])

    # Derived features (safe on empty frames)
    if not df.empty:
        df["speed"] = (df["u"] ** 2 + df["v"] ** 2 + df["w"] ** 2) ** 0.5
        df["du_dt"] = df["u"].diff() / dt
        df["dv_dt"] = df["v"].diff() / dt
        df["dw_dt"] = df["w"].diff() / dt
        df["dspeed_dt"] = df["speed"].diff() / dt
    else:
        print("[WARN] No rows fetched from JHTDB — writing empty CSV + meta so downstream can tag 'no data'.")

    return df


def safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in str(s))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", default="isotropic1024coarse", help="JHTDB dataset (e.g., isotropic1024coarse, channel)")
    ap.add_argument("--x", type=float, default=0.1)
    ap.add_argument("--y", type=float, default=0.2)
    ap.add_argument("--z", type=float, default=0.3)
    ap.add_argument("--t0", type=float, default=0.0, help="start time")
    ap.add_argument("--dt", type=float, default=0.0005, help="time step between samples")
    ap.add_argument("--nsteps", type=int, default=2400, help="number of samples")
    ap.add_argument("--slug", default="isotropic", help="short slug used elsewhere")
    args = ap.parse_args()

    point = (args.x, args.y, args.z)
    print(
        f"Fetching flow='{args.flow}' point={point} t0={args.t0} dt={args.dt} nsteps={args.nsteps}"
    )

    df = fetch_timeseries(args.flow, point, args.t0, args.dt, args.nsteps)

    base = f"{safe_name(args.flow)}__x{args.x}_y{args.y}_z{args.z}__t{args.t0}_dt{args.dt}_n{args.nsteps}"
    csv_path = OUTDIR / f"{base}.csv.gz"
    pq_path = OUTDIR / f"{base}.parquet"
    meta_path = OUTDIR / f"{base}.meta.json"

    df.to_csv(csv_path, index=False, compression="gzip")
    try:
        # Optional; fine if pyarrow/fastparquet is missing
        df.to_parquet(pq_path, index=False)
    except Exception as e:
        print(f"[WARN] parquet save skipped/failed ({e}); CSV.gz is written.")

    meta = {
        "flow": args.flow,
        "point": {"x": args.x, "y": args.y, "z": args.z},
        "t0": float(args.t0),
        "dt": float(args.dt),
        "nsteps": int(args.nsteps),
        "rows": int(df.shape[0]),
        "columns": list(map(str, df.columns)),
        "slug": args.slug,
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    print("✅ Saved:")
    print(f"  {csv_path}")
    if pq_path.exists():
        print(f"  {pq_path}")
    else:
        print("  (no parquet)")
    print(f"  {meta_path}")


if __name__ == "__main__":
    main()
