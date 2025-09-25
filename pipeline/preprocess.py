# pipeline/preprocess.py
from __future__ import annotations
from typing import Dict
import numpy as np

def detrend(x: np.ndarray, mode: str = "mean") -> np.ndarray:
    if mode == "none" or x.size == 0:
        return x
    if mode == "mean":
        return x - np.nanmean(x)
    if mode == "linear":
        t = np.arange(x.size, dtype=float)
        A = np.vstack([t, np.ones_like(t)]).T
        m, c = np.linalg.lstsq(A, x, rcond=None)[0]
        return x - (m * t + c)
    raise ValueError(f"Unknown detrend mode: {mode}")

def window(x: np.ndarray, name: str = "hann") -> np.ndarray:
    n = x.size
    if name in ("none", "", None):
        return x
    if name == "hann":
        w = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(n) / (n - 1))
    elif name == "hamming":
        w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(n) / (n - 1))
    elif name == "blackman":
        a0, a1, a2 = 0.42, 0.5, 0.08
        k = np.arange(n)
        w = a0 - a1 * np.cos(2*np.pi*k/(n-1)) + a2*np.cos(4*np.pi*k/(n-1))
    else:
        raise ValueError(f"Unknown window: {name}")
    return x * w

def apply(x: np.ndarray, cfg_pre: Dict) -> np.ndarray:
    x = detrend(x, cfg_pre.get("detrend", "mean"))
    x = window(x,  cfg_pre.get("window", "hann"))
    return x
