"""
ratio_analyze.py – compute successive NT-distance ratios
"""

import numpy as np

def ratios(nt_idx: np.ndarray | list[int]) -> np.ndarray:
    """
    Given an ordered array of Narrative-Tick indices,
    return r_i =  Δt_{i+1} / Δt_i  (len = len(nt_idx)-2).
    """
    nt_idx = np.asarray(nt_idx, dtype=float)
    if nt_idx.size < 3:
        return np.array([], dtype=float)

    d = np.diff(nt_idx)          # Δt sequence
    return d[1:] / d[:-1]        # element-wise ratio
