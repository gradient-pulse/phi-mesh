#!/usr/bin/env python3
"""
RGP–NS Agent — detect NT events from a probe time series, summarize inter-event
interval ratios, write JSON/CSV results under results/rgp_ns/<stamp>/batchN/,
and emit a Φ-Mesh pulse via tools/agent_rhythm/make_pulse.py.

This version *always* includes `batch` in both metrics.details and metrics.meta
so downstream make_pulse.py will name pulses ..._batchN.yml consistently.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Tuple

import numpy as np
import yaml


# ---------- simple adapters ---------------------------------------------------

@dataclass
class Series:
    t: np.ndarray  # shape (T,)
    v: np.ndarray  # shape (T,)


def synthetic_series(t0: float, t1: float, dt: float) -> Series:
    """Cheap synthetic signal with a clear rhythm and harmonics."""
    n = max(3, int(round((t1 - t0) / max(dt, 1e-9))))
    t = t0 + np.arange(n) * dt
    f0 = 0.36
    v = (
        np.sin(2 * np.pi * f0 * (t - t0))
        + 0.25 * np.sin(2 * np.pi * 2.0 * f0 * (t - t0) + 0.2)
        + 0.12 * np.sin(2 * np.pi * 3.2 * f0 * (t - t0) + 0.7)
    )
    return Series(t=t, v=v)


# ---------- NT event detector & ratio stats -----------------------------------

def find_peaks(v: np.ndarray, prominence: float, min_dist: int) -> np.ndarray:
    """
    Small, SciPy-free peak picker:
      - local maxima
      - min distance in samples
      - simple prominence vs. local baseline
    """
    n = v.size
    if n < 3:
        return np.asarray([], dtype=int)

    # candidate local maxima
    left = v[1:-1] > v[:-2]
    right = v[1:-1] > v[2:]
    cand = np.where(left & right)[0] + 1  # shift by 1

    if cand.size == 0:
        return cand

    # crude prominence: height - local min in a small window
    win = max(3, min(31, n // 40))
    half = win // 2
    good = []
    for i in cand:
        a = max(0, i - half)
        b = min(n, i + half + 1)
        prom = v[i] - float(np.min(v[a:b]))
        if prom >= prominence:
            good.append(i)
    idx = np.asarray(good, dtype=int)

    if idx.size <= 1 or min_dist <= 1:
        return idx

    # enforce spacing by greedy keep-highest
    keep: List[int] = []
    used = np.zeros(n, dtype=bool)
    order = idx[np.argsort(v[idx])[::-1]]  # highest first
    for i in order:
        if used[i]:
            continue
        keep.append(i)
        a = max(0, i - min_dist)
        b = min(n, i + min_dist + 1)
        used[a:b] = True
    keep = sorted(keep)
    return np.asarray(keep, dtype=int)


def interval_ratios(t: np.ndarray, peak_idx: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    if peak_idx.size < 3:
        return np.asarray([]), np.asarray([])
    ev_t = t[peak_idx]
    dts = np.diff(ev_t)                   # Δt_i
    ratios = dts[1:] / np.where(dts[:-1] == 0, np.nan, dts[:-1])
    ratios = ratios[np.isfinite(ratios)]
    return dts, ratios


# ---------- utilities ---------------------------------------------------------

def safe_slug(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def write_csv(path: str, header: Iterable[str], rows: Iterable[Iterable]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(list(header))
        for r in rows:
            w.writerow(list(r))


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="agents/rgp_ns/config.yml", help="YAML config")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # dataset cfg
    ds = cfg.get("dataset", {}) or {}
    kind = str(ds.get("kind", "synthetic")).lower()
    dataset_id = ds.get("id") or ds.get("dataset") or kind
    var_name = str(ds.get("var", "u"))
    xyz = ds.get("xyz", [0.1, 0.1, 0.1])
    window = ds.get("window", [0.0, 10.0, 0.01])
    t0, t1, dt = float(window[0]), float(window[1]), float(window[2])

    # run meta
    batch = int(cfg.get("batch", 1))
    title = str(cfg.get("title", "NT Rhythm — FD Probe"))
    tags = cfg.get("tags", ["nt_rhythm", "turbulence", "navier_stokes", "rgp"])
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # output dirs
    out_root = os.path.join("results", "rgp_ns", stamp, f"batch{batch}")
    os.makedirs(out_root, exist_ok=True)

    # --- load series
    source_label = kind
    if kind == "synthetic":
        s = synthetic_series(t0, t1, dt)
    elif kind == "local_netcdf":
        # Placeholder hook: user provides NetCDF adapter later.
        # For now, we keep a synthetic fallback so smoke tests never fail.
        s = synthetic_series(t0, t1, dt)
        source_label = "local_netcdf_fallback_synth"
    elif kind == "jhtdb":
        # Placeholder hook: JHTDB live adapter (use test token) to be wired.
        s = synthetic_series(t0, t1, dt)
        source_label = "jhtdb_fallback_synth"
    else:
        s = synthetic_series(t0, t1, dt)
        source_label = f"{kind}_fallback_synth"

    # --- detect NT events
    # choose prominence about 0.3*std; min distance ~ 0.3 / dt seconds
    prom = 0.3 * float(np.std(s.v))
    min_dist = max(3, int(round(0.3 / max(dt, 1e-9))))
    peaks = find_peaks(s.v, prominence=prom, min_dist=min_dist)
    dts, ratios = interval_ratios(s.t, peaks)

    # --- summarize
    n_events = int(peaks.size)
    ratio_mean = float(np.nanmean(ratios)) if ratios.size else float("nan")
    ratio_cv = float(np.nanstd(ratios) / np.nanmean(ratios)) if ratios.size else float("nan")
    main_peak_freq = float(1.0 / np.nanmean(dts)) if dts.size else float("nan")
    bpm = float(60.0 * main_peak_freq) if math.isfinite(main_peak_freq) else float("nan")

    # --- write CSV summary
    write_csv(
        os.path.join(out_root, "nt_ratio_summary.csv"),
        header=["n_events", "ratio_mean", "ratio_cv", "main_peak_freq", "bpm"],
        rows=[[n_events, ratio_mean, ratio_cv, main_peak_freq, bpm]],
    )

    # --- assemble metrics (ALWAYS includes batch) -----------------------------
    details = {
        "dataset": str(dataset_id),
        "var": str(var_name),
        "xyz": [float(xyz[0]), float(xyz[1]), float(xyz[2])],
        "window": [float(t0), float(t1), float(dt)],
        "batch": int(batch),
    }
    meta = {
        "batch": int(batch),
        "timestamp": stamp,
    }
    metrics = {
        "n": n_events,
        "ratio_mean": ratio_mean,
        "ratio_cv": ratio_cv,
        "main_peak_freq": main_peak_freq,
        "bpm": bpm,
        "source": source_label,
        "details": details,
        "meta": meta,
        # Optional extras (can help debugging)
        # "peaks": peaks.tolist(),
    }

    metrics_path = os.path.join(out_root, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Wrote metrics: {metrics_path}")

    # --- emit pulse -----------------------------------------------------------
    # The make_pulse.py now always appends _batchN to the filename because we
    # included details.batch/meta.batch above.
    dataset_slug = safe_slug(f"{dataset_id}")
    tags_str = " ".join(str(t) for t in tags)

    cmd = [
        sys.executable,
        "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics_path,
        "--title", title,
        "--dataset", dataset_slug,
        "--tags", tags_str,
        "--outdir", "pulse/auto",
    ]
    print("→ Emitting pulse:", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
