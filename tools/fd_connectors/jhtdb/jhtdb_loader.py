#!/usr/bin/env python3
"""
JHTDB probe loader (SOAP-only)
Pull a velocity time series at one probe and save to data/jhtdb/ as CSV (+optional Parquet).
"""

import argparse, gzip, json, sys, time
from pathlib import Path
import pandas as pd
from suds.client import Client
from suds.transport.http import HttpTransport, Reply

OUTDIR = Path("data/jhtdb")
OUTDIR.mkdir(parents=True, exist_ok=True)

# JHTDB has moved to HTTPS; some runners see a 308 from the HTTP endpoint.
WSDL_HTTP  = "http://turbulence.pha.jhu.edu/service/turbulence.asmx?WSDL"
WSDL_HTTPS = "https://turbulence.pha.jhu.edu/service/turbulence.asmx?WSDL"

def _mk_client(wsdl_url: str) -> Client:
    # Suds sometimes needs a slightly longer timeout on GH runners
    return Client(wsdl_url, timeout=180)

def _try_fetch(flow: str, point, t0: float, dt: float, nsteps: int, wsdl: str) -> pd.DataFrame:
    client = _mk_client(wsdl)
    lib = client.service
    x, y, z = point
    rows = []
    for i in range(nsteps):
        t = t0 + i * dt
        vec = lib.GetVelocity(flow, t, x, y, z)  # raises on failure
        u, v, w = float(vec[0]), float(vec[1]), float(vec[2])
        rows.append((t, u, v, w))
    df = pd.DataFrame(rows, columns=["t", "u", "v", "w"])
    # derived
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
    ap.add_argument("--flow", default="isotropic1024coarse")
    ap.add_argument("--x", type=float, default=0.1)
    ap.add_argument("--y", type=float, default=0.2)
    ap.add_argument("--z", type=float, default=0.3)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--dt", type=float, default=0.0005)
    ap.add_argument("--nsteps", type=int, default=2400)
    args = ap.parse_args()

    point = (args.x, args.y, args.z)
    print(f"Fetching flow='{args.flow}' point={point} t0={args.t0} dt={args.dt} nsteps={args.nsteps}")

    # Try HTTPS first; if it ever fails with a redirect-ish error, try the other.
    tried = []
    for wsdl in (WSDL_HTTPS, WSDL_HTTP):
        try:
            df = _try_fetch(args.flow, point, args.t0, args.dt, args.nsteps, wsdl)
            break
        except Exception as e:
            tried.append((wsdl, repr(e)))
            df = None
    if df is None or df.shape[0] == 0:
        print("[ERROR] SOAP fetch failed or returned no rows.")
        for wsdl, err in tried:
            print(f"  - tried {wsdl} -> {err}")
        # still write empty artifacts so downstream steps remain deterministic
        df = pd.DataFrame(columns=["t","u","v","w","speed","du_dt","dv_dt","dw_dt","dspeed_dt"])

    base = f"{safe_name(args.flow)}__x{args.x}_y{args.y}_z{args.z}__t0_{args.t0}_dt{args.dt}_n{args.nsteps}"
    csv_path = OUTDIR / f"{base}.csv.gz"
    pq_path  = OUTDIR / f"{base}.parquet"
    meta_path = OUTDIR / f"{base}.meta.json"

    # write CSV (always)
    df.to_csv(csv_path, index=False, compression="gzip")

    # parquet is optional (avoid failure if pyarrow/fastparquet missing)
    try:
        df.to_parquet(pq_path, index=False)
    except Exception as e:
        print(f"[WARN] parquet save failed ({e}); CSV.gz is written.")

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
