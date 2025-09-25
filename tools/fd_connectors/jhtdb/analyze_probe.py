#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

from pipeline import io_loaders, preprocess, spectrum, ladder

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, help="Path to *.meta.json created by jhtdb_loader.py")
    ap.add_argument("--out",  required=True, help="Path to write analysis JSON")
    args = ap.parse_args()

    tsmap = io_loaders.load_jhtdb_series_from_meta(args.meta)
    # single probe
    (probe_id, series), = tsmap.items()

    # prefer 'u' if present; else first available
    var = "u" if "u" in series else next(iter(series.keys()))
    t, x = series[var]
    if t is None or len(t) < 8:
        result = {"note": "no data", "n": int(len(t) if t is not None else 0)}
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print("No data — wrote minimal analysis JSON.")
        return

    dt = float(np.median(np.diff(t)))
    xw = preprocess.apply(x, {"detrend": "mean", "window": "hann"})
    Pxx, f = spectrum.psd(xw, dt, {"welch_segments": 4})
    det = ladder.detect(f, Pxx, {"min_snr_db": 6.0, "ladder_tolerance": 0.03, "peak_prominence": 0.05})

    out = {
        "probe": probe_id,
        "component": var,
        "dt": dt,
        "n": int(x.size),
        "duration_s": float(x.size * dt),
        "dominant": {
            "component": var,
            "freq_hz": det.f_base,
            "power": float(np.max(Pxx)) if Pxx.size else None,
            "snr_db": det.snr_base_db,
            "ratios": {"f2_over_f1": det.f2_over_f1, "f3_over_f1": det.f3_over_f1},
        },
        "passed": det.passed,
        "note": det.notes,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote analysis: {args.out}")

if __name__ == "__main__":
    main()
