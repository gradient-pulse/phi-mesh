# pipeline/spectrum.py
from __future__ import annotations
from typing import Dict, Tuple, Union
import numpy as np

def psd(x: np.ndarray, t_or_dt: Union[float, np.ndarray], cfg_fft: Dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple periodogram or Welch PSD depending on cfg.
    Returns (Pxx, f) with f in Hz.
    """
    x = np.asarray(x, float)
    n = x.size
    if n < 8:
        return np.array([]), np.array([])

    if np.isscalar(t_or_dt):
        dt = float(t_or_dt)
    else:
        t = np.asarray(t_or_dt, float)
        dt = np.nanmedian(np.diff(t))

    # Welch segments if requested
    segs = int(cfg_fft.get("welch_segments", 1))
    if segs <= 1:
        X = np.fft.rfft(x)
        Pxx = (np.abs(X) ** 2) / (n ** 2)
        f = np.fft.rfftfreq(n, d=dt)
    else:
        step = n // segs
        acc = None
        for i in range(segs):
            sli = slice(i*step, (i+1)*step)
            xi = x[sli]
            if xi.size < 8:
                continue
            Xi = np.fft.rfft(xi)
            Pi = (np.abs(Xi) ** 2) / (xi.size ** 2)
            if acc is None:
                acc = Pi
            else:
                acc = acc + Pi
        if acc is None:
            return np.array([]), np.array([])
        Pxx = acc / segs
        f = np.fft.rfftfreq(step, d=dt)

    return Pxx, f

def local_noise_floor(Pxx: np.ndarray, span: int = 5) -> np.ndarray:
    if Pxx.size == 0:
        return Pxx
    span = max(1, int(span))
    pad = span // 2
    ext = np.pad(Pxx, (pad, pad), mode="edge")
    out = np.empty_like(Pxx)
    for i in range(Pxx.size):
        win = ext[i:i+span]
        out[i] = np.median(win)
    return out

def snr_db(Pxx: np.ndarray, floor: np.ndarray) -> np.ndarray:
    eps = 1e-16
    return 10.0 * np.log10((Pxx + eps) / (floor + eps))
