# tools/agent_rhythm/rhythm.py
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

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
    return x - np.polyval(np.polyfit(np.arange(len(x)), x, 1), np.arange(len(x)))

def inter_arrival_times(ts: List[float]) -> np.ndarray:
    t = np.asarray(ts, dtype=float)
    t = t[np.isfinite(t)]
    t = np.unique(t)  # monotone, de-dup
    return np.diff(np.sort(t))

def robust_resets(ts: List[float], z=3.5) -> List[int]:
    """MAD outlier detection on gaps: returns indices of the *second* timestamp in a large gap."""
    gaps = inter_arrival_times(ts)
    if len(gaps) == 0:
        return []
    med = np.median(gaps)
    mad = np.median(np.abs(gaps - med)) + 1e-9
    scores = 0.6745 * (gaps - med) / mad
    return np.where(scores > z)[0].astype(int).tolist()

def lomb_scargle_period(ts: List[float], fmin=0.02, fmax=3.0, nf=2048) -> Tuple[float,float,List[Tuple[float,float]]]:
    """
    Uneven sampling friendly spectral estimate.
    Returns (main_peak_freq_hz, peak_power, all_peaks[(f,p)])."""
    t = np.asarray(ts, dtype=float)
    if len(t) < 8:
        return (np.nan, 0.0, [])
    # Convert events to impulse train
    # Sample onto a fine grid to keep it dependency-light
    dt = np.median(np.diff(np.sort(t)))
    dt = max(dt, 0.05)
    grid = np.arange(t.min(), t.max()+dt, dt)
    x = np.zeros_like(grid)
    idx = np.searchsorted(grid, t.clip(grid[0], grid[-1]))
    idx = np.clip(idx, 0, len(grid)-1)
    x[idx] = 1.0
    x = _detrend(x)

    # FFT power spectrum
    fs = 1.0/dt
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), d=dt)
    # keep within [fmin,fmax]
    mask = (freqs >= fmin) & (freqs <= fmax)
    freqs, P = freqs[mask], (np.abs(X[mask])**2)

    if len(P) == 0:
        return (np.nan, 0.0, [])

    k = int(np.argmax(P))
    main_f, main_p = float(freqs[k]), float(P[k])
    # top peaks (up to 5)
    order = np.argsort(P)[::-1][:5]
    peaks = [(float(freqs[i]), float(P[i])) for i in order]
    return (main_f, main_p, peaks)

def rhythm_from_events(ts: List[float]) -> RhythmMetrics:
    """Given event timestamps (seconds), estimate conserved NT rhythm."""
    if len(ts) < 8:
        return RhythmMetrics(np.nan, np.nan, 0.0, np.nan, [], np.nan, [])
    ts = sorted(set(float(x) for x in ts if np.isfinite(x)))
    main_f, main_p, peaks = lomb_scargle_period(ts)

    if not np.isfinite(main_f) or main_f <= 0:
        return RhythmMetrics(np.nan, np.nan, 0.0, np.nan, peaks, np.nan, [])

    period = 1.0 / main_f
    bpm = 60.0 * main_f
    # Confidence: top peak vs median power among candidates
    powers = np.array([p for _, p in peaks]) if peaks else np.array([main_p])
    conf = float(main_p / (np.median(powers) + 1e-9))
    conf = 1.0 - np.exp(-conf/8.0)   # squash to 0..1

    # Divergence (burstiness): CV of inter-arrival times
    iat = inter_arrival_times(ts)
    div = float(np.std(iat)/(np.mean(iat)+1e-9)) if len(iat) > 1 else 0.0

    resets = robust_resets(ts)

    return RhythmMetrics(period, bpm, conf, main_f, peaks, div, resets)

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

def ticks_from_message_times(times: List[float]) -> List[float]:
    """If you only have message timestamps, treat each as an event tick."""
    return [float(t) for t in times if np.isfinite(t)]

def ticks_from_token_log(token_times: List[Tuple[str,float]]) -> List[float]:
    """
    token_times: list of (token, t_sec) pairs.
    Returns times of *meaningful* events (e.g., sentence ends).
    """
    events = []
    end_marks = {".", "!", "?", ":"}
    for tok, t in token_times:
        if any(tok.endswith(ch) for ch in end_marks):
            events.append(float(t))
    if not events and token_times:
        # fallback: every N tokens
        N = max(1, len(token_times)//20)
        events = [float(t) for i, (_, t) in enumerate(token_times) if i % N == 0]
    return events
