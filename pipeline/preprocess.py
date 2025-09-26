from __future__ import annotations
import numpy as np
from .utils import detrend, hann

__all__ = ["prep_1d"]

def prep_1d(t: np.ndarray, x: np.ndarray) -> dict:
    """
    Minimal pre-processing:
      - drop NaNs
      - detrend (mean removal)
      - apply Hann window (returned for transparency)
    """
    m = np.isfinite(t) & np.isfinite(x)
    t2, x2 = t[m], x[m]
    if t2.size < 4:
        raise ValueError("Series too short after filtering")
    x3 = detrend(x2)
    w = hann(x3.size)
    return {"t": t2, "x": x3, "w": w}

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import numpy as np
    t = np.linspace(0, 1, 1001)
    x = np.sin(2*np.pi*3*t) + 0.01*np.random.randn(t.size)
    out = prep_1d(t, x)
    print("prep_1d OK:", len(out["t"]) == 1001 and np.isfinite(out["w"]).all())
