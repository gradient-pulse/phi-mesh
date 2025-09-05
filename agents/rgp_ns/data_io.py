  #!/usr/bin/env python3
# Dataset adapters: synthetic (built-in) + Local NetCDF skeleton.

from __future__ import annotations
from typing import Dict, Tuple, Iterable
import numpy as np

class SyntheticAdapter:
    """
    Generates a few probes of synthetic velocity along time.
    """
    def __init__(self, duration: float = 10.0, dt: float = 0.01, n_probes: int = 1, seed: int = 0):
        self.duration = float(duration)
        self.dt = float(dt)
        self.n_probes = int(n_probes)
        self.rng = np.random.default_rng(seed)

    def iter_probes(self) -> Iterable[Tuple[str, np.ndarray, np.ndarray]]:
        n = max(3, int(self.duration / max(self.dt, 1e-9)))
        t = np.linspace(0.0, self.duration, n, endpoint=False)
        base_f = 0.4
        for k in range(self.n_probes):
            sig = np.sin(2*np.pi*base_f*t) + 0.2*np.sin(2*np.pi*1.1*base_f*t)
            sig += 0.05 * self.rng.standard_normal(size=t.shape)
            probe_id = f"p{k:02d}"
            yield probe_id, t, sig

class LocalNetCDFAdapter:
    """
    Skeleton: load a single point (probe) time series (|u|) from a NetCDF/HDF5 file.
    Fill this when you have a local export. We keep it optional to avoid new deps.
    """
    def __init__(self, path: str, u_var: str = "u", v_var: str = "v", w_var: str = "w", t_var: str = "time"):
        self.path = path
        self.u_var, self.v_var, self.w_var, self.t_var = u_var, v_var, w_var, t_var

    def iter_probes(self):
        raise NotImplementedError(
            "LocalNetCDFAdapter is a placeholder. When you have a local file, "
            "we’ll wire this with netCDF4/xarray and return (probe_id, t, |u|)."
        )
