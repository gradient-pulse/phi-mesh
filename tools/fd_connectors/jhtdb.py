# tools/fd_connectors/jhtdb.py
# Minimal JHTDB connector with safe auto-fallback.
# Real API wiring can replace the online block below without changing callers.

from dataclasses import dataclass
from typing import List, Optional
import math
import os

@dataclass
class Timeseries:
    t: List[float]     # seconds (or dataset native units)
    v: List[float]     # sampled scalar value at (x,y,z), e.g., u or |u|

def _synthetic_series(t0: float, t1: float, dt: float) -> Timeseries:
    n = max(3, int((t1 - t0) / max(dt, 1e-6)))
    ts = [t0 + i * dt for i in range(n)]
    vs = [
        math.sin(2 * math.pi * 0.4 * (t - t0)) + 0.15 * math.sin(2 * math.pi * 1.2 * (t - t0))
        for t in ts
    ]
    return Timeseries(t=ts, v=vs)

def list_datasets() -> List[str]:
    # Keep a stable list for UI/testing; replace with real API listing later.
    return ["isotropic1024coarse", "channel", "rotstrat_turb"]

def fetch_timeseries(
    dataset: str,
    var: str,
    x: float, y: float, z: float,
    t0: float, t1: float, dt: float
) -> Timeseries:
    """
    Returns a Timeseries. Fallback logic:
      1) If JHTDB_OFFLINE=1 -> synthetic
      2) Else if JHTDB_ONLINE=1 and JHTDB_TOKEN present -> try HTTP; on error -> synthetic
      3) Else -> synthetic
    """
    # 1) explicit offline or missing token -> synthetic
    offline = os.getenv("JHTDB_OFFLINE", "0") == "1"
    token = os.getenv("JHTDB_TOKEN", "").strip()
    online_requested = os.getenv("JHTDB_ONLINE", "0") == "1"

    if offline or not token:
        print("::notice title=JHTDB::Using synthetic (offline or no token).")
        return _synthetic_series(t0, t1, dt)

    if not online_requested:
        # Default to safe behavior unless the user explicitly opts in.
        print("::notice title=JHTDB::JHTDB_ONLINE not set; using synthetic fallback.")
        return _synthetic_series(t0, t1, dt)

    # 2) Try real HTTP call (safely). If it fails, fall back.
    try:
        import requests  # lightweight; present on GH runners
        # NOTE: This is a placeholder shape. Replace with the actual JHTDB endpoint/params.
        # Provide an override via JHTDB_URL if you want to experiment.
        base_url = os.getenv("JHTDB_URL", "https://turbulence.pha.jhu.edu/api/timeseries")
        params = {
            "dataset": dataset,
            "var": var,
            "x": x, "y": y, "z": z,
            "t0": t0, "t1": t1, "dt": dt,
        }
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(base_url, params=params, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"::warning title=JHTDB HTTP {resp.status_code}::Falling back to synthetic.")
            return _synthetic_series(t0, t1, dt)

        data = resp.json()
        # Expecting {"t":[...], "v":[...]} — adjust here once the real schema is known.
        ts = data.get("t") or []
        vs = data.get("v") or []
        if not ts or not vs or len(ts) != len(vs):
            print("::warning title=JHTDB schema::Bad/empty payload; falling back to synthetic.")
            return _synthetic_series(t0, t1, dt)

        print("::notice title=JHTDB::Fetched real timeseries.")
        return Timeseries(t=list(map(float, ts)), v=list(map(float, vs)))
    except Exception as e:
        print(f"::warning title=JHTDB exception::{e} — falling back to synthetic.")
        return _synthetic_series(t0, t1, dt)
