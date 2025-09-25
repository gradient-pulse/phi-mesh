# pipeline/ladder.py
from __future__ import annotations
from typing import Dict, NamedTuple, Optional
import numpy as np

class LadderDetection(NamedTuple):
    f_base: Optional[float]
    f2_over_f1: Optional[float]
    f3_over_f1: Optional[float]
    snr_base_db: Optional[float]
    snr_2f_db: Optional[float]
    snr_3f_db: Optional[float]
    passed: bool
    notes: str

def detect(f: np.ndarray, Pxx: np.ndarray, cfg_fft: Dict) -> LadderDetection:
    if f.size == 0 or Pxx.size == 0:
        return LadderDetection(None, None, None, None, None, None, False, "empty spectrum")

    tol = float(cfg_fft.get("ladder_tolerance", 0.03))
    min_snr = float(cfg_fft.get("min_snr_db", 6.0))
    prom = float(cfg_fft.get("peak_prominence", 0.05))

    # exclude DC
    mask = f > 0
    f1 = f[mask]
    P1 = Pxx[mask]
    if f1.size == 0:
        return LadderDetection(None, None, None, None, None, None, False, "no positive frequencies")

    # noise floor & SNR
    from .spectrum import local_noise_floor, snr_db
    floor = local_noise_floor(P1, span=7)
    S = snr_db(P1, floor)

    # base peak by prominence over local floor
    rel = (P1 - floor) / (np.max(P1) + 1e-16)
    candidates = np.where(rel > prom)[0]
    if candidates.size == 0:
        # fallback: global max
        base_idx = int(np.argmax(P1))
    else:
        base_idx = int(candidates[np.argmax(P1[candidates])])

    f0 = float(f1[base_idx])
    snr0 = float(S[base_idx])

    # locate ~2f0 and ~3f0 (nearest bins)
    def nearest(target):
        idx = int(np.argmin(np.abs(f1 - target)))
        return idx, float(f1[idx]), float(S[idx])

    i2, f2, snr2 = nearest(2.0 * f0)
    i3, f3, snr3 = nearest(3.0 * f0)

    r2 = f2 / f0 if f0 > 0 else None
    r3 = f3 / f0 if f0 > 0 else None

    ok = (
        f0 > 0
        and abs(r2 - 2.0) <= tol
        and abs(r3 - 3.0) <= tol
        and snr0 >= min_snr
        and snr2 >= min_snr
        and snr3 >= min_snr
    )

    note = ""
    if not ok:
        note = f"criteria: tol={tol}, min_snr_db={min_snr}, prom={prom}"

    return LadderDetection(f0, r2, r3, snr0, snr2, snr3, bool(ok), note)
