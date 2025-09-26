from __future__ import annotations
import numpy as np
from .utils import find_peak, nearest_band

__all__ = ["rfft_spectrum", "dominant_peak"]

def rfft_spectrum(t: np.ndarray, x: np.ndarray, w: np.ndarray | None = None) -> dict:
    """
    Real FFT amplitude/power spectrum.
    Returns: {freq, amp, power, df}
    """
    n = x.size
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt

    xx = x.copy()
    if w is not None:
        xx = xx * w

    yf = np.fft.rfft(xx)
    freq = np.fft.rfftfreq(n, dt)
    amp = (2.0 / n) * np.abs(yf)            # two-sided -> single sided amplitude
    power = (amp ** 2) / 2.0                # proportional; fine for relative detection
    df = freq[1] - freq[0] if freq.size > 1 else 0.0
    return {"freq": freq, "amp": amp, "power": power, "df": df, "fs": fs}

def dominant_peak(freq: np.ndarray, power: np.ndarray, fmin: float = 0.0, fmax: float | None = None) -> dict | None:
    """Return {'freq': f0, 'power': p0} or None."""
    if fmax is None:
        fmax = np.max(freq) if freq.size else 0.0
    fp = find_peak(freq, power, fmin, fmax)
    if fp is None:
        return None
    return {"freq": fp[0], "power": fp[1]}

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import numpy as np
    t = np.linspace(0, 6, 6001)
    x = 1.0*np.sin(2*np.pi*0.8*t) + 0.7*np.sin(2*np.pi*1.6*t) + 0.4*np.sin(2*np.pi*2.4*t)
    sp = rfft_spectrum(t, x)
    dp = dominant_peak(sp["freq"], sp["power"], fmin=0.1)
    print("spectrum OK: f0≈", round(dp["freq"], 2))
