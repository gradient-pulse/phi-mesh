from __future__ import annotations
from pathlib import Path
import json
import numpy as np

# ---------------------------- IO helpers ---------------------------- #

def ensure_dir(p: str | Path) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_json(path: str | Path, obj) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2))

def load_json(path: str | Path):
    return json.loads(Path(path).read_text())

# ------------------------- signal utilities ------------------------ #

def detrend(x: np.ndarray) -> np.ndarray:
    """Remove mean (simple, robust)."""
    return x - np.nanmean(x)

def hann(n: int) -> np.ndarray:
    """Symmetric Hann window."""
    if n <= 1:
        return np.ones(n)
    k = np.arange(n)
    return 0.5 - 0.5 * np.cos(2 * np.pi * k / (n - 1))

def find_peak(freqs: np.ndarray, power: np.ndarray, fmin: float, fmax: float) -> tuple[float, float] | None:
    """Return (f, p) of max power in [fmin,fmax], or None if empty."""
    m = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(m):
        return None
    i = np.argmax(power[m])
    idx = np.flatnonzero(m)[i]
    return float(freqs[idx]), float(power[idx])

def nearest_band(f0: float, rel_bw: float) -> tuple[float, float]:
    """Return +/- relative bandwidth around f0."""
    return (f0 * (1 - rel_bw), f0 * (1 + rel_bw))

# ---------------------------- self-test ---------------------------- #

if __name__ == "__main__":
    import numpy as np
    t = np.linspace(0, 2, 2001)
    x = np.sin(2*np.pi*1.0*t) + 0.1*np.random.randn(t.size)
    y = detrend(x)
    w = hann(y.size)
    print("utils OK:", np.isfinite(y).all(), np.allclose(w[:3], [0., 2.463e-06, 9.853e-06], rtol=1e-3, atol=1e-3))
