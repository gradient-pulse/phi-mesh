#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

from pipeline.io_loaders import load_series
from pipeline.preprocess import detrend_and_window  # safe no-op if already clean
from pipeline.spectrum import rfft_spectrum
from pipeline.figures import plot_time_and_spectrum

def pick_component(series: dict[str, np.ndarray], want: str | None) -> tuple[str, np.ndarray]:
    """
    Choose a component from `series`. Prefer `want` if present;
    otherwise fall back to the first available channel.
    """
    keys = [k for k, v in series.items() if isinstance(v, np.ndarray) and v.size > 0]
    if not keys:
        raise ValueError("No usable channels found in series (empty data).")
    if want and want in series and series[want] is not None and series[want].size > 1:
        return want, series[want]
    # soft fallback
    k0 = keys[0]
    return k0, series[k0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True, help="Princeton subset file (.csv/.parquet/.h5)")
    ap.add_argument("--out",     required=True, help="Output analysis JSON")
    ap.add_argument("--probe",   default=None,  help="Probe ID if dataset has multiple (e.g., Q1)")
    ap.add_argument("--component", default="u", help="Channel to analyze (u|v|w|speed|Z|z)")
    args = ap.parse_args()

    # Load standardized dict: {label, t, dt, series{...}, meta{...}}
    D = load_series("princeton", {"subset_path": args.subset, "probe": args.probe})
    t = np.asarray(D["t"], dtype=float)
    series = D["series"]

    comp, x = pick_component(series, args.component)

    # Basic pre-processing (lightweight, safe)
    xw = detrend_and_window(t, x)

    # Spectrum
    sp = rfft_spectrum(t, xw)  # returns {"freq","power","f0","p0",...}

    # Figures (saved under a folder named after output stem)
    out_path = Path(args.out)
    fig_dir = out_path.with_suffix("").as_posix()  # e.g., results/princeton/demo.analysis -> folder
    figs = plot_time_and_spectrum(fig_dir, t, {comp: x}, sp["freq"], sp["power"], f0=sp.get("f0"))

    # Write minimal analysis JSON
    out = {
        "label": D["label"],
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
