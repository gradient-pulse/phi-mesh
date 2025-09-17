#!/usr/bin/env python3
"""
Analyze a JHTDB probe and emit compact metrics JSON.

Usage (preferred):
  python analyze_probe.py --meta path/to/....meta.json --out results/fd_probe/....analysis.json

Overrides:
  --csv path/to/....csv.gz  (if you want to point directly to the CSV)
  --dt 0.002                (to override dt from meta)

What it does
- Loads meta to discover CSV/point/dt/nsteps when not overridden
- Reads CSV (gz ok) with columns [t,u,v,w] (t optional)
- Builds 'speed' = sqrt(u^2+v^2+w^2) when components available
- Detrends + Hann window, rFFT on speed (or 'u' as fallback)
- Reports dominant_freq_hz (> DC), approx_period_s, peak_power
- Per-channel stats: mean/std/min/max/cv
"""

import argparse, gzip, io, json, math
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd


# ----------------- IO helpers -----------------

def _read_csv_maybe_gz(p: Path) -> pd.DataFrame:
    if str(p).endswith(".gz"):
        with gzip.open(p, "rb") as f:
            return pd.read_csv(io.BytesIO(f.read()))
    return pd.read_csv(p)


def _series_stats(x: np.ndarray):
    x = x[np.isfinite(x)]
    if x.size == 0:
        return None
    mu  = float(np.mean(x))
    sd  = float(np.std(x))
    cv  = float(sd / (abs(mu) + 1e-12))
    return {
        "mean": mu,
        "std": sd,
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "cv":  cv,
    }


# ----------------- signal analysis -----------------

def _dominant_freq(x: np.ndarray, dt: float):
    """
    Return (f_dom, p_dom, hint).
    - Detrend (remove mean), Hann window, rFFT.
    - Ignore DC, choose max power bin.
    - If peak is weak vs median or trivial, return f=0 with a hint.
    """
    x = x[np.isfinite(x)]
    n = x.size
    if n < 32 or dt <= 0:
        return 0.0, 0.0, "too_short"
    x = x - np.mean(x)
    if not np.any(np.abs(x) > 0):
        return 0.0, 0.0, "flat"

    w = np.hanning(n)
    y = x * w
    Y = np.fft.rfft(y)
    P = np.abs(Y) ** 2
    f = np.fft.rfftfreq(n, d=float(dt))

    if P.size <= 1:
        return 0.0, 0.0, "no_bins"

    # ignore DC
    k = int(np.argmax(P[1:])) + 1
    fpk = float(f[k])
    ppk = float(P[k])

    med = float(np.median(P[1:])) if P.size > 2 else 0.0
    if fpk <= 0 or ppk <= 1e-14 or (med > 0 and ppk / med < 2.5):
        return 0.0, ppk, "weak_peak"

    return fpk, ppk, ""


# ----------------- main -----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", help="loader meta json (preferred)")
    ap.add_argument("--csv", help="optional explicit csv/csv.gz path")
    ap.add_argument("--dt", type=float, help="optional dt override")
    ap.add_argument("--out", required=True, help="output metrics json")
    args = ap.parse_args()

    meta = {}
    if args.meta:
        meta_path = Path(args.meta)
        if not meta_path.exists():
            raise FileNotFoundError(f"meta not found: {meta_path}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    # Resolve CSV path
    csv_path = None
    if args.csv:
        csv_path = Path(args.csv)
    elif args.meta:
        # meta "<stem>.meta.json" => data file "<stem>.csv.gz"
        stem = Path(args.meta).with_suffix("").name  # drop .json
        # prefer .csv.gz; fall back to .csv
        p1 = meta_path.parent / f"{stem}.csv.gz"
        p2 = meta_path.parent / f"{stem}.csv"
        csv_path = p1 if p1.exists() else (p2 if p2.exists() else None)

    if not csv_path or not csv_path.exists():
        raise FileNotFoundError("Could not resolve probe CSV. Pass --csv explicitly or provide a valid --meta.")

    # Resolve dt, nsteps, flow, point
    dt = args.dt if args.dt is not None else float(meta.get("dt", 0.0))
    nsteps = int(meta.get("nsteps", 0)) if meta else 0
    flow   = meta.get("flow") or meta.get("dataset") or "unknown_flow"
    point  = meta.get("point") or {}
    px, py, pz = point.get("x"), point.get("y"), point.get("z")

    # Load CSV
    df = _read_csv_maybe_gz(csv_path)
    cols = {c.lower(): c for c in df.columns}

    def col(name): return df[cols[name]] if name in cols else None
    u, v, w = col("u"), col("v"), col("w")

    U = u.to_numpy(dtype=float) if u is not None else None
    V = v.to_numpy(dtype=float) if v is not None else None
    W = w.to_numpy(dtype=float) if w is not None else None

    speed = None
    if U is not None and V is not None and W is not None:
        speed = np.sqrt(U*U + V*V + W*W)

    # FFT target
    x_for_fft = speed if speed is not None else (U if U is not None else None)
    fdom, pdom, hint = (0.0, 0.0, "no_signal")
    if x_for_fft is not None and (dt or 0) > 0:
        fdom, pdom, hint = _dominant_freq(x_for_fft, dt)

    # Build output
    out = {
        "date": str(date.today()),
        "flow": flow,
        "point": {"x": px, "y": py, "z": pz},
        "dt": float(dt) if dt else None,
        "nsteps": int(nsteps) if nsteps else int(len(df)),
        "duration_s": float((int(nsteps) if nsteps else len(df)) * (float(dt) if dt else 0.0)),
        "dominant_freq_hz": float(fdom),
        "approx_period_s": (float(1.0/fdom) if fdom > 0 else None),
        "peak_power": float(pdom),
        "hint": hint or "",
        "channels": {}
    }
    if U is not None:     out["channels"]["u"] = _series_stats(U)
    if V is not None:     out["channels"]["v"] = _series_stats(V)
    if W is not None:     out["channels"]["w"] = _series_stats(W)
    if speed is not None: out["channels"]["speed"] = _series_stats(speed)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
