#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JHTDB probe loader — robust
- Retries with backoff
- Metadata JSON + TXT
- CSV.gz + optional Parquet
- Derived features: speed, du/dt approx, step d|u|/dt
- Evidence hash in filenames
"""
import argparse, sys, json, time, math, hashlib, os
from pathlib import Path
import pandas as pd

try:
    import pyJHTDB
except Exception as e:
    print("ERROR: pyJHTDB not available. pip install pyJHTDB suds-community", file=sys.stderr)
    raise

OUTDIR = Path("data/jhtdb")
OUTDIR.mkdir(parents=True, exist_ok=True)

def _retry(fn, tries=5, base=0.5, factor=2.0):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(base * (factor ** i))

def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in s)

def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]

def fetch_timeseries(flow: str, point, t0: float, dt: float, nsteps: int, email: str | None) -> pd.DataFrame:
    lib = pyJHTDB.libJHTDB()
    if email:
        try:
            lib.add_email(email)
        except Exception:
            pass
    lib.initialize()
    try:
        rows = []
        x, y, z = point
        def one(i):
            t = t0 + i * dt
            vec = lib.getData(flow, t, (x, y, z), 'u')  # returns [u,v,w]
            return (t, float(vec[0]), float(vec[1]), float(vec[2]))
        for i in range(nsteps):
            rows.append(_retry(lambda i=i: one(i)))
    finally:
        try: lib.finalize()
        except Exception: pass
    df = pd.DataFrame(rows, columns=["t","u","v","w"])
    # Derived features
    speed = (df["u"]**2 + df["v"]**2 + df["w"]**2).pow(0.5)
    df["speed"] = speed
    if len(df) > 1:
        df["du_dt"] = df["u"].diff() / dt
        df["dv_dt"] = df["v"].diff() / dt
        df["dw_dt"] = df["w"].diff() / dt
        df["dspeed_dt"] = df["speed"].diff() / dt
    else:
        for c in ("du_dt","dv_dt","dw_dt","dspeed_dt"):
            df[c] = float("nan")
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", default="isotropic1024coarse")
    ap.add_argument("--x", type=float, default=0.1)
    ap.add_argument("--y", type=float, default=0.2)
    ap.add_argument("--z", type=float, default=0.3)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--dt", type=float, default=0.002)
    ap.add_argument("--nsteps", type=int, default=1000)
    ap.add_argument("--email_env", default="JHTDB_EMAIL",
                    help="Env var name holding registered JHTDB email (optional)")
    args = ap.parse_args()

    point = (args.x, args.y, args.z)
    # Light sanity checks (dataset-specific bounds vary; keep permissive but explicit)
    if args.nsteps <= 0 or args.dt <= 0:
        print("ERROR: nsteps and dt must be positive.", file=sys.stderr); sys.exit(2)

    email = os.environ.get(args.email_env, "").strip() or None
    print(f"Fetching JHTDB flow='{args.flow}' point={point} t0={args.t0} dt={args.dt} nsteps={args.nsteps} email={'yes' if email else 'no'}")

    df = fetch_timeseries(args.flow, point, args.t0, args.dt, args.nsteps, email)

    # Stable metadata
    meta = {
        "flow": args.flow,
        "point": {"x": args.x, "y": args.y, "z": args.z},
        "t0": args.t0, "dt": args.dt, "nsteps": args.nsteps,
        "rows": int(df.shape[0]),
        "columns": list(df.columns),
        "email_used": bool(email),
    }
    meta_bytes = json.dumps(meta, sort_keys=True).encode("utf-8")
    h = _hash_bytes(meta_bytes + df.head(min(50, len(df))).to_csv(index=False).encode("utf-8"))

    base = f"{_safe_name(args.flow)}__x{args.x}_y{args.y}_z{args.z}__t0{args.t0}_dt{args.dt}_n{args.nsteps}__h{h}"
    csv_path = OUTDIR / f"{base}.csv.gz"
    pq_path  = OUTDIR / f"{base}.parquet"
    meta_txt = OUTDIR / f"{base}.meta.txt"
    meta_json = OUTDIR / f"{base}.meta.json"

    # Writes
    df.to_csv(csv_path, index=False, compression="gzip")
    try:
        df.to_parquet(pq_path, index=False)
    except Exception as e:
        print(f"Note: parquet save failed ({e}); CSV.gz written.", file=sys.stderr)

    meta_txt.write_text(
        f"flow: {args.flow}\npoint: {point}\nt0: {args.t0}\ndt: {args.dt}\n"
        f"nsteps: {args.nsteps}\nrows: {len(df)}\ncolumns: {list(df.columns)}\n"
        f"hash: {h}\n"
    )
    meta_json.write_text(json.dumps({**meta, "hash": h}, indent=2))

    print("✅ Saved:\n ", csv_path, "\n ", pq_path if pq_path.exists() else "(no parquet)", "\n ", meta_txt, "\n ", meta_json)

if __name__ == "__main__":
    main()
