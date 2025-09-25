# tools/agent_rhythm/rhythm.py
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class RhythmMetrics:
    period: float               # seconds per tick
    bpm: float                  # ticks per minute
    confidence: float           # 0..1, how clean the peak is
    main_peak_freq: float       # Hz
    peaks: List[Tuple[float,float]]  # (freq_hz, power)
    divergence_ratio: float     # how bursty vs steady (0 steady, >1 bursty)
    reset_events: List[int]     # indices where gaps look like resets

def _detrend(x: np.ndarray) -> np.ndarray:
    if len(x) < 2:
        return x.astype(float)
    idx = np.arange(len(x))
    return x - np.polyval(np.polyfit(idx, x, 1), idx)

def inter_arrival_times(ts: List[float]) -> np.ndarray:
    t = np.asarray(ts, dtype=float)
    t = t[np.isfinite(t)]
    if t.size == 0:
        return np.asarray([], dtype=float)
    t = np.unique(t)  # monotone, de-dup
    return np.diff(np.sort(t))

def robust_resets(ts: List[float], z: float = 3.5) -> List[int]:
    """MAD outlier detection on gaps: returns indices of the *second* timestamp in a large gap."""
    gaps = inter_arrival_times(ts)
    if gaps.size == 0:
        return []
    med = np.median(gaps)
    mad = np.median(np.abs(gaps - med)) + 1e-9
    scores = 0.6745 * (gaps - med) / mad
    return np.where(scores > z)[0].astype(int).tolist()

def lomb_scargle_period(ts: List[float], fmin=0.02, fmax=3.0, nf=2048) -> Tuple[float,float,List[Tuple[float,float]]]:
    """
    Uneven sampling friendly spectral estimate via FFT on a lightly resampled impulse train.
    Returns (main_peak_freq_hz, peak_power, all_peaks[(f,p)]).
    """
    t = np.asarray(ts, dtype=float)
    t = t[np.isfinite(t)]
    if t.size < 8:
        return (float("nan"), 0.0, [])
    t = np.sort(np.unique(t))

    # Sample to a fine grid (keeps dependencies light)
    dt = np.median(np.diff(t))
    dt = max(float(dt), 0.05)
    grid = np.arange(t.min(), t.max() + dt, dt)
    x = np.zeros_like(grid, dtype=float)
    idx = np.searchsorted(grid, t.clip(grid[0], grid[-1]))
    idx = np.clip(idx, 0, len(grid) - 1)
    np.add.at(x, idx, 1.0)
    x = _detrend(x)

    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(x.size, d=dt)
    mask = (freqs >= fmin) & (freqs <= fmax)
    freqs, P = freqs[mask], (np.abs(X[mask]) ** 2)

    if P.size == 0:
        return (float("nan"), 0.0, [])

    k = int(np.argmax(P))
    main_f, main_p = float(freqs[k]), float(P[k])
    order = np.argsort(P)[::-1][:5]
    peaks = [(float(freqs[i]), float(P[i])) for i in order]
    return (main_f, main_p, peaks)

def rhythm_from_events(ts: List[float]) -> RhythmMetrics:
    """Given event timestamps (seconds), estimate conserved NT rhythm."""
    t = [float(x) for x in ts if np.isfinite(x)]
    if len(t) < 8:
        return RhythmMetrics(float("nan"), float("nan"), 0.0, float("nan"), [], float("nan"), [])

    main_f, main_p, peaks = lomb_scargle_period(t)

    if not np.isfinite(main_f) or main_f <= 0:
        return RhythmMetrics(float("nan"), float("nan"), 0.0, float("nan"), peaks, float("nan"), [])

    period = 1.0 / main_f
    bpm = 60.0 * main_f

    powers = np.array([p for _, p in peaks]) if peaks else np.array([main_p])
    conf = float(main_p / (np.median(powers) + 1e-9))
    conf = 1.0 - np.exp(-conf / 8.0)   # squash to 0..1

    iat = inter_arrival_times(t)
    div = float(np.std(iat) / (np.mean(iat) + 1e-9)) if iat.size > 1 else 0.0

    resets = robust_resets(t)

    return RhythmMetrics(float(period), float(bpm), float(conf), float(main_f), peaks, float(div), resets)

class StreamingRhythm:
    """Online accumulator for events; call push(t) and query metrics() anytime."""
    def __init__(self, max_events: int = 5000):
        self.max = max_events
        self._ts: List[float] = []

    def push(self, t: float) -> None:
        self._ts.append(float(t))
        if len(self._ts) > self.max:
            self._ts = self._ts[-self.max:]

    def metrics(self) -> RhythmMetrics:
        return rhythm_from_events(self._ts)
