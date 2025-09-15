#!/usr/bin/env python3
"""
JHTDB probe loader
------------------
Pull a velocity time series at a single probe point from the Johns Hopkins
Turbulence Database and save to data/jhtdb/ as CSV + Parquet.

Usage (defaults shown):
  python tools/fd_connectors/jhtdb/jhtdb_loader.py \
      --flow isotropic1024coarse --x 0.1 --y 0.2 --z 0.3 \
      --t0 0.0 --dt 0.002 --nsteps 1000

Notes
- You need outbound internet (GitHub Actions allows it).
- We install pyJHTDB and suds-community in the workflow.
- If JHTDB is down or credentials required, the script fails with a clear message.
"""

import argparse
from pathlib import Path
import sys
import pandas as pd

# JHTDB client (SOAP); we use suds-community backend pulled by pyJHTDB
try:
    import pyJHTDB
except Exception as e:
    print("ERROR: pyJHTDB not available. Did you pip install pyJHTDB?",
          file=sys.stderr)
    raise

OUTDIR = Path("data/jhtdb")
OUTDIR.mkdir(parents=True, exist_ok=True)

def fetch_timeseries(flow: str, point, t0: float, dt: float, nsteps: int) -> pd.DataFrame:
    """Fetch velocity (u,v,w) at a probe for nsteps starting t0 with step dt."""
    lib = pyJHTDB.libJHTDB()
    # If you have an email registered with JHTDB you can set it here; many flows work w/o.
    # lib.add_email('your_email@example.com')

    try:
        lib.initialize()

        # collect rows: [t, u, v, w]
        rows = []
        x, y, z = point
        for i in range(nsteps):
            t = t0 + i * dt
            # getData signature varies by flow; getData returns [u,v,w] for 'u' query
            vec = lib.getData(flow, t, (x, y, z), 'u')
            rows.append((t, vec[0], vec[1], vec[2]))

    except Exception as e:
        print(f"ERROR: JHTDB request failed: {e}", file=sys.stderr)
        raise
    finally:
        try:
            lib.finalize()
        except Exception:
            pass

    df = pd.DataFrame(rows, columns=["t", "u", "v", "w"])
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
    print(f"Fetching JHTDB flow='{args.flow}' point={point} t0={args.t0} dt={args.dt} nsteps={args.nsteps}")

    df = fetch_timeseries(args.flow, point, args.t0, args.dt, args.nsteps)

    base = f"{safe_name(args.flow)}__x{args.x}_y{args.y}_z{args.z}__t0{args.t0}_dt{args.dt}_n{args.nsteps}"
    csv_path = OUTDIR / f"{base}.csv"
    pq_path  = OUTDIR / f"{base}.parquet"
    meta_path = OUTDIR / f"{base}.meta.txt"

    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(pq_path, index=False)
    except Exception as e:
        print(f"Note: parquet save failed ({e}); CSV is still written.", file=sys.stderr)

    meta = (
        f"flow: {args.flow}\n"
        f"point: {point}\n"
        f"t0: {args.t0}\n"
        f"dt: {args.dt}\n"
        f"nsteps: {args.nsteps}\n"
        f"rows: {len(df)}\n"
        f"columns: {list(df.columns)}\n"
    )
    meta_path.write_text(meta)

    print(f"✅ Saved:\n  {csv_path}\n  {pq_path if pq_path.exists() else '(no parquet)'}\n  {meta_path}")

if __name__ == "__main__":
    main()
