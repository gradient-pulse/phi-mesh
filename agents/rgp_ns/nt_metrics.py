#!/usr/bin/env python3
# Lightweight NT-event detection + ratio metrics (no SciPy needed)

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict
import numpy as np

@dataclass
class NTMetrics:
    n_events: int
    n_intervals: int
    n_ratios: int
    mean_ratio: float | None
    std_ratio: float | None
    cv_ratio: float | None
    median_ratio: float | None
    q25_ratio: float | None
    q75_ratio: float | None

def _moving_mean(x: np.ndarray, k: int) -> np.ndarray:
    k = max(1, int(k))
    if k == 1:
        return x.copy()
    c = np.cumsum(np.pad(x, (k-1, 0), mode="edge"))
    return (c[k:] - c[:-k]) / k

def signal_proxy(u: np.ndarray, win: int = 5) -> np.ndarray:
    """
    Cheap turbulence-event proxy: roughness of |u| after light smoothing.
    Works on 1D velocity magnitude |u| time series.
    """
    u = np.asarray(u, dtype=float)
    mag = np.abs(u)
    sm = _moving_mean(mag, win)
    # pad back to original length
    pad_left = len(mag) - len(sm)
    sm = np.pad(sm, (pad_left, 0), mode="edge")
    rough = np.abs(mag - sm)
    return rough

def detect_events(sig: np.ndarray, min_sep: int = 5, rel_prom: float = 0.2) -> List[int]:
    """
    Simple peak detector:
    - min_sep: minimum sample separation between successive peaks
    - rel_prom: relative prominence threshold as a fraction of max(sig)
    """
    x = np.asarray(sig, dtype=float)
    if len(x) < 3:
        return []
    thr = rel_prom * (x.max() if np.isfinite(x).all() else 0.0)
    peaks: List[int] = []
    last = -10**9
    for i in range(1, len(x)-1):
        if x[i] > x[i-1] and x[i] >= x[i+1] and x[i] >= thr:
            if i - last >= min_sep:
                peaks.append(i)
                last = i
    return peaks

def intervals_and_ratios(t: np.ndarray, event_idx: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    if len(event_idx) < 2:
        return np.array([]), np.array([])
    te = t[np.asarray(event_idx, dtype=int)]
    dt = np.diff(te)
    if len(dt) < 2:
        return dt, np.array([])
    ratios = dt[1:] / dt[:-1]
    return dt, ratios

def summarize_ratios(r: np.ndarray) -> NTMetrics:
    r = np.asarray(r, dtype=float)
    if r.size == 0:
        return NTMetrics(0, 0, 0, None, None, None, None, None, None)
    mean = float(np.nanmean(r))
    std  = float(np.nanstd(r))
    cv   = float(std / mean) if mean not in (0.0, float("nan")) else None
    med  = float(np.nanmedian(r))
    q25  = float(np.nanpercentile(r, 25))
    q75  = float(np.nanpercentile(r, 75))
    return NTMetrics(
        n_events=0,           # filled by caller
        n_intervals=0,        # filled by caller
        n_ratios=r.size,
        mean_ratio=mean,
        std_ratio=std,
        cv_ratio=cv,
        median_ratio=med,
        q25_ratio=q25,
        q75_ratio=q75,
    )
