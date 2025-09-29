#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

from pipeline.io_loaders import load_series
from pipeline.spectrum import rfft_spectrum
from pipeline.figures import plot_time_and_spectrum


def simple_detrend_and_window(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    """
    Minimal, robust pre-processing:
      1) subtract linear trend (least squares fit a + b*t)
      2) apply Hann window to reduce spectral leakage
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if t.size != x.size or t.size < 3:
        return x.copy()

    # linear fit
    A = np.vstack([np.ones_like(t), t]).T
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    trend = A @ coef
    y = x - trend

    # Hann window
    w = np.hanning(t.size)
    # preserve overall energy scale
    w = w / (w.mean() if w.mean() != 0 else 1.0)
    return y * w


def pick_component(series: dict[str, np.ndarray], want: str | None) -> tuple[str, np.ndarray]:
    """
    Choose a component from `series`. Prefer `want` if present;
    otherwise fall back to the first available channel.
    """
    keys = [k for k, v in series.items() if isinstance(v, np.ndarray) and v.size > 1]
    if not keys:
        raise ValueError("No usable channels found in series (empty data).")
    if want and want in series and series[want] is not None and series[want].size > 1:
        return want, series[want]
    return keys[0], series[keys[0]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True, help="Princeton subset file (.csv/.parquet/.h5)")
    ap.add_argument("--out",     required=True, help="Output analysis JSON path")
    ap.add_argument("--probe",   default=None,  help="Probe ID if dataset has multiple (e.g., Q1)")
    ap.add_argument("--component", default="u", help="Channel (u|v|w|speed|Z|z); falls back if missing")
    args = ap.parse_args()

    # Load standardized dict: {label, t, dt, series{...}, meta{...}}
    D = load_series("princeton", {"subset_path": args.subset, "probe": args.probe})
    t = np.asarray(D["t"], dtype=float)
    comp, x = pick_component(D["series"], args.component)

    # Pre-process
    xw = simple_detrend_and_window(t, x)

    # Spectrum
    sp = rfft_spectrum(t, xw)  # -> {"freq","power","f0","p0",...}

    # Figures (saved under a folder named after output stem)
    out_path = Path(args.out)
    fig_dir = out_path.with_suffix("").as_posix()  # e.g., results/princeton/demo.analysis -> folder
    figs = plot_time_and_spectrum(fig_dir, t, {comp: x}, sp["freq"], sp["power"], f0=sp.get("f0"))

    # Write minimal analysis JSON
    out = {
        "label": D.get("label"),
        "meta":  D.get("meta", {}),
        "n": int(t.size),
        "dt": float(D.get("dt") or (np.median(np.diff(t)) if t.size > 1 else float("nan"))),
        "component": comp,
        "dominant": {
            "freq_hz": float(sp.get("f0") or 0.0),
            "power": float(sp.get("p0") or 0.0),
        },
        "figures": figs,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"✅ Wrote analysis: {out_path}")
    for k, v in figs.items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
