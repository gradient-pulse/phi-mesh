# tools/fd_connectors/jhtdb.py
# Minimal JHTDB connector scaffold.
# Real API wiring can replace the stubs without changing callers.

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import math
import os
import time

@dataclass
class Timeseries:
    t: List[float]     # seconds (or dataset native units)
    v: List[float]     # sampled scalar value at (x,y,z), e.g., u or |u|

class JHTDBClient:
    """
    Skeleton client. If JHTDB_OFFLINE=1, returns a synthetic sine-with-noise
    series so the pipeline stays testable before API credentials are wired.
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("JHTDB_TOKEN", "")
        self.offline = os.getenv("JHTDB_OFFLINE", "0") == "1"

    def list_datasets(self) -> List[str]:
        if self.offline:
            return ["isotropic1024coarse", "channel", "rotstrat_turb"]
        # TODO: call JHTDB endpoints, return available dataset slugs
        return ["isotropic1024coarse"]  # placeholder

    def fetch_timeseries(
        self,
        dataset: str,
        var: str,
        x: float, y: float, z: float,
        t0: float, t1: float, dt: float
    ) -> Timeseries:
        if self.offline:
            # synthetic NT-like rhythm for testing
            n = max(3, int((t1 - t0) / max(dt, 1e-6)))
            ts = [t0 + i * dt for i in range(n)]
            vs = [
                math.sin(2 * math.pi * 0.4 * (t - t0)) + 0.15 * math.sin(2 * math.pi * 1.2 * (t - t0))
                for t in ts
            ]
            return Timeseries(t=ts, v=vs)

        # TODO: implement real call(s) (requests to JHTDB WS/HTTP), respecting token
        # For now raise to make missing implementation obvious in online mode.
        raise NotImplementedError("Wire JHTDB API here (token: JHTDB_TOKEN).")
