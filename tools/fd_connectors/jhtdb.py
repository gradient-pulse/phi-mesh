# tools/fd_connectors/jhtdb.py
# Minimal JHTDB connector scaffold with a thin JHTDBClient shim so callers
# can use either function-style or class-style access.

from dataclasses import dataclass
from typing import List, Optional
import math
import os

@dataclass
class Timeseries:
    t: List[float]     # time samples (dataset-native or arbitrary units)
    v: List[float]     # scalar value at (x,y,z), e.g., u or |u|

# --- function-style API ----------------------------------------------------

def list_datasets() -> List[str]:
    """
    Return available dataset slugs. In offline mode we just expose a few
    common names so the UI looks familiar.
    """
    if os.getenv("JHTDB_OFFLINE", "0") == "1":
        return ["isotropic1024coarse", "channel", "rotstrat_turb"]
    # TODO: call the real JHTDB endpoint to enumerate datasets
    return ["isotropic1024coarse"]

def fetch_timeseries(
    dataset: str,
    var: str,
    x: float, y: float, z: float,
    t0: float, t1: float, dt: float
) -> Timeseries:
    """
    Fetch a 1-point time series. In offline mode we synthesize a clean
    multi-tone signal. Online wiring can replace this body with real calls.
    """
    offline = os.getenv("JHTDB_OFFLINE", "0") == "1" or not os.getenv("JHTDB_TOKEN", "")
    if offline:
        n = max(3, int((t1 - t0) / max(dt, 1e-9)))
        ts = [t0 + i * dt for i in range(n)]
        base = 0.4
        vs = [
            math.sin(2 * math.pi * base * (t - t0))
            + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
            for t in ts
        ]
        return Timeseries(t=ts, v=vs)

    # TODO: implement real HTTP/SOAP call to JHTDB using JHTDB_TOKEN
    raise NotImplementedError("Wire JHTDB API here (requires JHTDB_TOKEN).")

# --- class-style shim (for existing callers) -------------------------------

class JHTDBClient:
    """
    Thin wrapper so older code can use client.fetch_timeseries(...).
    Respects JHTDB_OFFLINE and JHTDB_TOKEN via environment.
    """
    def __init__(self, token: Optional[str] = None):
        # kept for compatibility; function impl reads env directly
        self.token = token or os.getenv("JHTDB_TOKEN", "")
        self.offline = os.getenv("JHTDB_OFFLINE", "0") == "1"

    def list_datasets(self) -> List[str]:
        return list_datasets()

    def fetch_timeseries(
        self,
        dataset: str,
        var: str,
        x: float, y: float, z: float,
        t0: float, t1: float, dt: float
    ) -> Timeseries:
        return fetch_timeseries(dataset=dataset, var=var, x=x, y=y, z=z, t0=t0, t1=t1, dt=dt)
