#!/usr/bin/env python3
"""
Analyze a JHTDB probe CSV (gz ok) and emit compact metrics JSON.

- Computes speed from (u,v,w) if present.
- Detrends + Hann windows series before FFT.
- Reports dominant_freq_hz (>0 bin), approx_period_s, and per-channel stats.
- Emits a short 'hint' if spectrum looks flat/weak (may explain 0 peaks).
"""

import argparse, gzip, io, json, math, os
from pathlib import Path
from datetime import date
import numpy as np
import pandas as pd


def read_csv_any(p: str) -> pd.DataFrame:
    pth = Path(p)
    if pth.suffix == ".gz":
        with gzip.open(pth, "rb") as f:
            return pd.read_csv(io.BytesIO(f.read()))
    return pd.read_csv(pth)


def series_stats(x: np.ndarray):
    x = x[np.isfinite(x)]
    if x.size == 0:
        return None
    mu = float(np.mean(x))
    sd = float(np.std(x))
    cv = float(sd / (abs(mu) + 1e-12))
    return {"mean": mu, "std": sd, "min": float(np.min(x)), "max": float(np.max(x)), "cv": cv}


def dominant_freq(x: np.ndarray, dt: float):
    """Return (f_dom, power_dom, hint). If no meaningful peak, f_dom=0."""
    x = x[np.isfinite(x)]
    n = x.size
    if n < 16 or dt <= 0:
        return 0.0, 0.0, "too_short"
    x = x - np.mean(x)
    if not np.any(np.abs(x) > 0):
        return 0.0, 0.0, "flat"
    # Hann window to reduce leakage
    w = np.hanning(n)
    xw = x * w
    Y = np.fft.rfft(xw)
    P = np.abs(Y) ** 2
    freqs = np.fft.rfftfreq(n, d=float(dt))
    # ignore DC
    if P.size <= 1:
        return 0.0, 0.0, "no_bins"
    k = int(np.argmax(P[1:])) + 1
    f = float(freqs[k])
    p = float(P[k])
    # Heuristic: if peak is tiny vs median, call it "weak"
    med = float(np.median(P[1:])) if P.size > 2 else 0.0
    if f <= 0 or p <= 1e-14 or (med > 0 and p/med < 2.5):
        return 0.0, p, "weak_peak"
    return f, p, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="path to CSV/CSV.GZ produced by loader")
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()

    df = read_csv_any(args.inp)
    # Expected columns: t,u,v,w (t optional)
    cols = {c.lower(): c for c in df.columns}
    u = df[cols.get("u")] if "u" in cols else None
    v = df[cols.get("v")] if "v" in cols else None
    w = df[cols.get("w")] if "w" in cols else None

    if u is None or v is None or w is None:
        # If components missing, try 'speed' only
        speed = df[cols["speed"]].to_numpy(dtype=float) if "speed" in cols else None
    else:
        U = u.to_numpy(dtype=float)
        V = v.to_numpy(dtype=float)
        W = w.to_numpy(dtype=float)
        speed = np.sqrt(U*U + V*V + W*W)

    # FFT on speed if available, else on 'u' as fallback
    x_for_fft = speed if speed is not None else (u.to_numpy(dtype=float) if u is not None else None)
    f_dom, p_dom, spectral_hint = (0.0, 0.0, "no_signal")
    if x_for_fft is not None:
        f_dom, p_dom, spectral_hint = dominant_freq(x_for_fft, args.dt)

    # Stats
    out = {
        "date": str(date.today()),
        "dt": float(args.dt),
        "nsteps": int(len(df)),
        "duration_s": float(len(df) * args.dt),
        "dominant_freq_hz": float(f_dom),
        "approx_period_s": (float(1.0/f_dom) if f_dom > 0 else None),
        "peak_power": float(p_dom),
        "hint": spectral_hint or "",
        "channels": {}
    }
    if u is not None: out["channels"]["u"] = series_stats(U)
    if v is not None: out["channels"]["v"] = series_stats(V)
    if w is not None: out["channels"]["w"] = series_stats(W)
    if speed is not None: out["channels"]["speed"] = series_stats(speed)

    Path(args.outp).write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
