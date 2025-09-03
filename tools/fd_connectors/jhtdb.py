#!/usr/bin/env python3
"""
JHTDB connector (safe-by-default).

- list_datasets(): quick-known slugs (informational).
- fetch_timeseries(...): returns (t, y) 1D arrays.
  * If JHTDB_OFFLINE is truthy or no token is provided, returns a synthetic signal.
  * Otherwise, the function shows the call shape you’ll wire to the real API.

Env:
  JHTDB_TOKEN     : optional API token
  JHTDB_OFFLINE   : "1" (default) to use synthetic data, "0" to attempt online

Notes:
  The real JHTDB service historically exposed SOAP/REST endpoints for
  isotropic/ channel flows. When you’re ready, replace the TODO block with
  the actual request(s) and parsing.
"""

from __future__ import annotations
import math
import os
from typing import Iterable, Tuple, List

def list_datasets() -> List[str]:
    # A few common names you’ll likely probe first.
    return [
        "isotropic1024",          # isotropic turbulence (DNS)
        "isotropic1024coarse",
        "channel",
        "channel5200",
        "boundary_layer",
    ]

def _linspace(t0: float, t1: float, dt: float):
    n = max(1, int(round((t1 - t0) / dt)) + 1)
    return [t0 + i * dt for i in range(n)]

def _synthetic_series(t: Iterable[float]) -> Tuple[List[float], List[float]]:
    # Smooth + micro jitter, good enough to exercise the rhythm path.
    y: List[float] = []
    for i, ti in enumerate(t):
        y.append(
            0.7 * math.sin(2.0 * math.pi * 0.22 * ti)
            + 0.3 * math.sin(2.0 * math.pi * 0.47 * ti + 1.2)
            + 0.05 * math.sin(2.0 * math.pi * 2.7 * ti + 0.3 * i)
        )
    return list(t), y

def fetch_timeseries(
    *,
    dataset: str,
    var: str,
    xyz: Tuple[float, float, float],
    t0: float,
    t1: float,
    dt: float,
    token: str | None = None,
):
    """
    Return (t, y) for the requested dataset/variable at a spatial point and time window.

    If JHTDB_OFFLINE is true or no token is given, returns a synthetic signal.
    Otherwise this shows the expected call shape; wire the real HTTP call here.
    """
    offline = os.getenv("JHTDB_OFFLINE", "1").strip() not in ("", "0", "false", "False")

    # Always build the grid deterministically (synthetic or real)
    t = _linspace(float(t0), float(t1), float(dt))

    if offline or not token:
        return _synthetic_series(t)

    # --- TODO: real HTTP wiring (kept explicit so it’s easy to fill in) ----
    # Example shape (pseudocode):
    #
    # import requests
    # base = "https://turbulence.pha.jhu.edu"     # check current host
    # endpoint = f"{base}/api/{dataset}/timeseries"
    # payload = {
    #     "var": var,                # e.g., "u", "v", "w", "p"
    #     "x": xyz[0], "y": xyz[1], "z": xyz[2],
    #     "t0": float(t0), "t1": float(t1), "dt": float(dt),
    # }
    # headers = {"Authorization": f"Bearer {token}"}
    # r = requests.get(endpoint, params=payload, headers=headers, timeout=60)
    # r.raise_for_status()
    # data = r.json()               # or r.content if binary; adapt as needed
    #
    # # Expect data like {"t":[...], "y":[...]} or a flat array—normalize to 1D here.
    # t = data["t"]
    # y = data["y"]
    # return t, y
    #
    # For now, keep fail-safe:
    raise NotImplementedError(
        "Online JHTDB call not wired yet. Set JHTDB_OFFLINE=1 or add the HTTP request."
    )
