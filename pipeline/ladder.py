from __future__ import annotations
import numpy as np
from .utils import nearest_band

__all__ = ["ladder_1_2_3"]

def _band_energy(freq: np.ndarray, power: np.ndarray, f_center: float, rel_bw: float) -> float:
    if f_center <= 0:
        return 0.0
    fmin, fmax = nearest_band(f_center, rel_bw)
    m = (freq >= fmin) & (freq <= fmax)
    return float(np.trapz(power[m], freq[m])) if np.any(m) else 0.0

def ladder_1_2_3(freq: np.ndarray, power: np.ndarray, f0: float, rel_bw: float = 0.05) -> dict:
    """
    Test for the 1:2:3 harmonic ladder around f0.
    rel_bw is relative bandwidth for integration windows (default ±5%).
    """
    e1 = _band_energy(freq, power, f0*1.0, rel_bw)
    e2 = _band_energy(freq, power, f0*2.0, rel_bw)
    e3 = _band_energy(freq, power, f0*3.0, rel_bw)
    total = e1 + e2 + e3
    ratios = [r for r, e in zip((1,2,3), (e1,e2,e3)) if e > 0]
    present = {"1x": e1 > 0, "2x": e2 > 0, "3x": e3 > 0}
    return {
        "f0": float(f0),
        "rel_bw": float(rel_bw),
        "energy": {"1x": e1, "2x": e2, "3x": e3, "sum": total},
        "present": present,
        "ratios_present": ratios,
    }

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import numpy as np
    # synthetic ladder 0.8, 1.6, 2.4 Hz
    t = np.linspace(0, 6, 6001)
    x = 1.0*np.sin(2*np.pi*0.8*t) + 0.7*np.sin(2*np.pi*1.6*t) + 0.4*np.sin(2*np.pi*2.4*t)
    from .spectrum import rfft_spectrum, dominant_peak
    sp = rfft_spectrum(t, x)
    f0 = dominant_peak(sp["freq"], sp["power"], fmin=0.1)["freq"]
    lad = ladder_1_2_3(sp["freq"], sp["power"], f0)
    print("ladder OK:", lad["present"], "f0≈", round(f0,2))
