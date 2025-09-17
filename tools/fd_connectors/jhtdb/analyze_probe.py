#!/usr/bin/env python3
import argparse, gzip, io, json, numpy as np, pandas as pd
from pathlib import Path

def load_csv_gz(p):
    with gzip.open(p, "rb") as f:
        return pd.read_csv(io.BytesIO(f.read()))

def analyze(df, dt):
    out = {}
    cols = ["u","v","w","speed","dspeed_dt"]
    for c in cols:
        if c in df:
            s = df[c].to_numpy(dtype=float)
            s = s[np.isfinite(s)]
            if s.size:
                out[c] = {
                    "mean": float(s.mean()),
                    "std": float(s.std()),
                    "min": float(s.min()),
                    "max": float(s.max()),
                    "cv": float(s.std()/max(1e-12,abs(s.mean()))),
                }
    dom = 0.0
    if "speed" in df and len(df["speed"]) > 8:
        x = df["speed"].to_numpy(dtype=float)
        x = x - np.mean(x)
        Y = np.fft.rfft(x)
        freqs = np.fft.rfftfreq(len(x), d=float(dt))
        if Y.size > 1:
            k = int(np.argmax(np.abs(Y[1:]))) + 1
            dom = float(freqs[k])
    out["dominant_freq_hz"] = dom
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--out", dest="outp", required=True)
    a = ap.parse_args()
    df = load_csv_gz(a.inp)
    res = analyze(df, a.dt)
    Path(a.outp).write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
