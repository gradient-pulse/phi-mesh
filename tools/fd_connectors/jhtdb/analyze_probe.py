#!/usr/bin/env python3
"""
Analyze a JHTDB probe and emit compact metrics JSON.

Preferred:
  python analyze_probe.py --meta path/to/....meta.json --out results/fd_probe/....analysis.json

Overrides:
  --csv path/to/....csv.gz  (use explicit CSV)
  --dt 0.002                (override dt)
"""

import argparse, gzip, io, json
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd


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
    return {"mean": mu, "std": sd, "min": float(np.min(x)), "max": float(np.max(x)), "cv": cv}


def _dominant_freq(x: np.ndarray, dt: float):
    """Detrend, Hann window, rFFT; ignore DC; return (f_dom, p_dom, hint)."""
    x = x[np.isfinite(x)]
    n = x.size
    if n < 32 or not (dt and dt > 0):
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

    k = int(np.argmax(P[1:])) + 1  # skip DC
    fpk = float(f[k]); ppk = float(P[k])
    med = float(np.median(P[1:])) if P.size > 2 else 0.0
    if fpk <= 0 or ppk <= 1e-14 or (med > 0 and ppk / med < 2.5):
        return 0.0, ppk, "weak_peak"
    return fpk, ppk, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta")
    ap.add_argument("--csv")
    ap.add_argument("--dt", type=float)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    meta = {}
    if args.meta:
        mp = Path(args.meta)
        if not mp.exists():
            raise FileNotFoundError(f"meta not found: {mp}")
        meta = json.loads(mp.read_text(encoding="utf-8"))

    # Resolve CSV
    csv_path = Path(args.csv) if args.csv else None
    if not csv_path and args.meta:
        stem = Path(args.meta).with_suffix("").name  # drop .json
        p1 = Path(args.meta).parent / f"{stem}.csv.gz"
        p2 = Path(args.meta).parent / f"{stem}.csv"
        csv_path = p1 if p1.exists() else (p2 if p2.exists() else None)
    if not csv_path or not csv_path.exists():
        raise FileNotFoundError("CSV not found. Pass --csv or provide valid --meta.")

    # Resolve params
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

    U = u.to_numpy(float) if u is not None else None
    V = v.to_numpy(float) if v is not None else None
    W = w.to_numpy(float) if w is not None else None
    speed = np.sqrt(U*U + V*V + W*W) if (U is not None and V is not None and W is not None) else None

    # FFT target
    target = speed if speed is not None else (U if U is not None else None)
    fdom, pdom, hint = (0.0, 0.0, "no_signal")
    if target is not None and (dt and dt > 0):
        fdom, pdom, hint = _dominant_freq(target, dt)

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
