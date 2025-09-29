#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

from pipeline.io_loaders import load_series
from pipeline.spectrum import rfft_spectrum
from pipeline.figures import plot_time_and_spectrum


def simple_detrend_and_window(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if t.size != x.size or t.size < 3:
        return x.copy()
    A = np.vstack([np.ones_like(t), t]).T
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    trend = A @ coef
    y = x - trend
    w = np.hanning(t.size)
    w = w / (w.mean() if w.mean() else 1.0)
    return y * w


def pick_component(series: dict[str, np.ndarray], want: str | None) -> tuple[str, np.ndarray]:
    keys = [k for k, v in series.items() if isinstance(v, np.ndarray) and v.size > 1]
    if not keys:
        raise ValueError("No usable channels found in series (empty data).")
    if want and want in series and getattr(series[want], "size", 0) > 1:
        return want, series[want]
    return keys[0], series[keys[0]]


def fallback_load_plain(subset_path: str | Path) -> dict:
    """
    Fallback reader for simple CSV/HDF with columns t,u,v,w[,Z].
    Returns dict with keys: label, t, dt, series, meta.
    """
    p = Path(subset_path)
    ext = p.suffix.lower()
    if ext in {".csv", ".gz"}:
        df = pd.read_csv(p)
    elif ext in {".h5", ".hdf5"}:
        df = pd.read_hdf(p)
    else:
        raise ValueError(f"Unsupported subset format for fallback: {ext}")

    cols_lower = {c.lower() for c in df.columns}
    if "t" not in cols_lower:
        raise ValueError("Fallback: no 't' column present.")
    tcol = next(c for c in df.columns if c.lower() == "t")
    df = df.sort_values(tcol)

    series: dict[str, np.ndarray] = {}
    for k in ("u", "v", "w", "z", "Z"):
        if any(c.lower() == k for c in df.columns):
            col = next(c for c in df.columns if c.lower() == k)
            series[k.lower()] = df[col].to_numpy(float)

    t = df[tcol].to_numpy(float)
    dt = float(np.median(np.diff(t))) if t.size > 1 else float("nan")
    return {
        "label": f"Princeton:{p.name}:fallback",
        "t": t,
        "dt": dt,
        "series": series,
        "meta": {"subset_path": p.as_posix(), "probe": "Q0"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True, help="Princeton subset file (.csv/.parquet/.h5)")
    ap.add_argument("--out",     required=True, help="Output analysis JSON path")
    ap.add_argument("--probe",   default=None,  help="Probe ID if dataset has multiple (e.g., Q1)")
    ap.add_argument("--component", default="u", help="Channel (u|v|w|speed|Z|z); falls back if missing")
    args = ap.parse_args()

    # First try the canonical loader
    try:
        D = load_series("princeton", {"subset_path": args.subset, "probe": args.probe})
    except Exception as e:
        print(f"[WARN] load_series failed ({e}). Falling back to plain reader.")
        D = fallback_load_plain(args.subset)

    # If loader succeeded but series is empty, fall back
    if not D.get("series") or all((getattr(v, "size", 0) <= 1) for v in D["series"].values()):
        print("[WARN] series empty or unusable; using fallback reader.")
        D = fallback_load_plain(args.subset)

    t = np.asarray(D["t"], dtype=float)
    comp, x = pick_component(D["series"], args.component)

    # Pre-process
    xw = simple_detrend_and_window(t, x)

    # Spectrum
    sp = rfft_spectrum(t, xw)  # -> {"freq","power","f0","p0",...}

    # Figures
    out_path = Path(args.out)
    fig_dir = out_path.with_suffix("").as_posix()
    figs = plot_time_and_spectrum(fig_dir, t, {comp: x}, sp["freq"], sp["power"], f0=sp.get("f0"))

    # Write JSON
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
