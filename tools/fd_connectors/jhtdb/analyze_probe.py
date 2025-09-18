#!/usr/bin/env python3
"""
analyze_probe.py — analyze a single JHTDB probe time series.

Inputs
------
--meta : path to the .meta.json written by the loader (contains flow, point, dt, nsteps)
--out  : path to write analysis JSON (this path is authoritative; we do not re-slug it)
--slug : optional short identifier (saved in the JSON for provenance; does not affect filenames)

What it does
------------
- Finds the matching data file next to the meta (prefers .csv.gz, then .csv, then .parquet)
- Loads columns t, u, v, w (if t is present we can infer dt if missing)
- For each component (u, v, w):
    * mean, std, rms
    * dominant frequency via FFT (hann + rfft; ignore DC)
- Writes metrics JSON exactly to --out (no internal renaming)

Output JSON (keys of interest)
------------------------------
{
  "slug": "your-slug-if-given",
  "n": 2400,
  "dt": 0.0005,
  "duration_s": 1.2,
  "csv_path": "data/jhtdb/....csv.gz",
  "dominant": {"component": "u", "freq_hz": 0.125, "power": 123.4},
  "dominant_freq_hz": 0.125,
  "components": { "u": {...}, "v": {...}, "w": {...} }
}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

try:
    import pandas as pd  # type: ignore
except Exception as e:
    raise SystemExit("pandas is required for analyze_probe.py") from e


# --------------------------- io helpers ---------------------------

def _load_meta(meta_path: Path) -> Dict:
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _find_data_file(stem: str) -> Optional[Path]:
    """
    Given a base stem (no extension), return the first existing data file:
    .csv.gz > .csv > .parquet
    """
    root = Path("data/jhtdb")
    for ext in (".csv.gz", ".csv", ".parquet"):
        p = root / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def _load_timeseries(path: Path) -> pd.DataFrame:
    """Load t,u,v,w from CSV/Parquet. If 't' is missing we can still analyze using dt from meta."""
    if path.suffix == ".gz" or path.suffixes[-2:] == [".csv", ".gz"]:
        df = pd.read_csv(path)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    df.columns = [str(c).strip().lower() for c in df.columns]
    cols = [c for c in ("t", "u", "v", "w") if c in df.columns]
    if not cols:
        raise ValueError(f"No usable columns found in {path}. Expect one of t,u,v,w.")
    return df[cols].copy()


# --------------------------- dsp helpers ---------------------------

def _dominant_freq(x: np.ndarray, dt: float) -> Tuple[float, float]:
    """
    Estimate dominant frequency (Hz) and its power for a real signal x sampled at dt seconds.
    Steps: demean -> Hann window -> rfft -> power spectrum -> peak (ignore DC bin).
    """
    x = np.asarray(x, dtype=float)
    n = int(x.shape[0])
    if n < 8 or dt <= 0:
        return 0.0, 0.0

    x = x - np.mean(x)
    w = np.hanning(n)
    xw = x * w

    X = np.fft.rfft(xw)
    power = np.abs(X) ** 2
    freqs = np.fft.rfftfreq(n, d=dt)

    if power.size <= 1:
        return 0.0, 0.0
    idx = int(np.argmax(power[1:])) + 1
    return float(freqs[idx]), float(power[idx])


def _stats_and_peak(x: np.ndarray, dt: float) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    mean = float(np.mean(x))
    std = float(np.std(x, ddof=0))
    rms = float(np.sqrt(np.mean(x * x)))
    f, p = _dominant_freq(x, dt)
    return {"mean": mean, "std": std, "rms": rms, "dom_freq_hz": f, "dom_power": p}


# --------------------------- main work ---------------------------

def analyze(meta_path: Path, out_path: Path, slug: Optional[str]) -> None:
    meta = _load_meta(meta_path)

    # figure base stem from meta filename (loader writes *... .meta.json)
    stem = meta_path.name
    if stem.endswith(".meta.json"):
        stem = stem[: -len(".meta.json")]

    data_file = _find_data_file(stem)
    if data_file is None:
        # Write minimal JSON so the pipeline can proceed (no crash)
        nsteps = int(meta.get("nsteps") or meta.get("n") or 0)
        dt = float(meta.get("dt") or 0.0)
        result = {
            "slug": slug,
            "n": nsteps,
            "dt": dt,
            "duration_s": float(nsteps * dt),
            "csv_path": None,
            "dominant": {"component": None, "freq_hz": 0.0, "power": 0.0},
            "components": {},
        }
        result["dominant_freq_hz"] = result["dominant"]["freq_hz"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"wrote {out_path}  (dominant: {result['dominant']})")
        return

    df = _load_timeseries(data_file)

    # dt from meta if provided; else infer from t column if present
    dt = float(meta.get("dt") or 0.0)
    if (dt <= 0.0) and ("t" in df.columns):
        t = df["t"].to_numpy()
        if t.size >= 2:
            dt_est = np.median(np.diff(t.astype(float)))
            if dt_est > 0:
                dt = float(dt_est)

    n = int(meta.get("nsteps") or df.shape[0])
    duration_s = float(n * dt) if dt > 0 else float(df.shape[0])

    comps: Dict[str, Dict[str, float]] = {}
    best = ("", 0.0, 0.0)  # (comp, freq, power)

    for comp in ("u", "v", "w"):
        if comp in df.columns:
            stats = _stats_and_peak(df[comp].to_numpy(), dt if dt > 0 else 1.0)
            comps[comp] = stats
            if stats["dom_power"] > best[2]:
                best = (comp, stats["dom_freq_hz"], stats["dom_power"])

    result = {
        "slug": slug,
        "n": n,
        "dt": dt,
        "duration_s": duration_s,
        "csv_path": data_file.as_posix(),
        "dominant": {
            "component": best[0] or None,
            "freq_hz": float(best[1]) if best[0] else 0.0,
            "power": float(best[2]) if best[0] else 0.0,
        },
        "components": comps,
    }
    result["dominant_freq_hz"] = result["dominant"]["freq_hz"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {out_path}  (dominant: {result['dominant']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, help="Path to .meta.json")
    ap.add_argument("--out", required=True, help="Where to write analysis JSON")
    ap.add_argument("--slug", default=None, help="Optional identifier to store in the JSON")
    args = ap.parse_args()
    analyze(Path(args.meta), Path(args.out), args.slug)


if __name__ == "__main__":
    main()
