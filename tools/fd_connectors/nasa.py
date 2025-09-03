# tools/fd_connectors/nasa.py
"""
NASA CFD connector (stub).

Return shape matches run_fd_probe.py expectations:
  - list_datasets() -> list[str]
  - fetch_timeseries(dataset, var, xyz, t0, t1, dt, token=None) -> (t_list, y_list)

Modes
-----
1) Offline synthetic (default):
   Set NASA_OFFLINE=1 to produce a sine-with-bursts signal so the FD→pulse
   pipeline can be tested without credentials or remote calls.

2) CSV override (optional):
   If NASA_CSV is set to a readable CSV file, this module will load that file,
   pick column <var> (or 'value' as fallback), and resample onto [t0..t1] with step dt.
   CSV format: header row, a 't' column, and a value column named either <var> or 'value'.

3) Online (future):
   When NASA_OFFLINE != 1 and NASA_CSV is not set, this stub raises
   NotImplementedError — replace the TODO with a real NASA CFD datasource.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
import os
import math
import csv
import bisect

def list_datasets() -> List[str]:
    """
    Return available dataset slugs. In offline mode we expose a tiny menu.
    In online mode, replace with a real query.
    """
    if os.getenv("NASA_OFFLINE", "1") == "1":
        return ["cfd_demo", "cavity_flow", "shock_tube"]
    # TODO: fetch live list from a NASA endpoint or catalog
    return ["cfd_demo"]

# ----------------------------- helpers -------------------------------------

def _synthetic_series(t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    """Smooth base oscillation with intermittent burst envelopes (good NT testbed)."""
    n = max(3, int(round((t1 - t0) / max(dt, 1e-12))) + 1)
    ts = [t0 + i * dt for i in range(n)]
    base_f1 = 0.35
    base_f2 = 0.92
    # Burst envelope centered near 40% and 80% of the window
    c1, c2 = t0 + 0.40 * (t1 - t0), t0 + 0.80 * (t1 - t0)
    s1, s2 = 0.08 * (t1 - t0), 0.05 * (t1 - t0)

    def burst(t: float) -> float:
        g1 = math.exp(-0.5 * ((t - c1)/max(s1, 1e-9))**2)
        g2 = math.exp(-0.5 * ((t - c2)/max(s2, 1e-9))**2)
        return 0.6 * g1 + 0.8 * g2

    ys = [
        (math.sin(2 * math.pi * base_f1 * (t - t0))
         + 0.25 * math.sin(2 * math.pi * base_f2 * (t - t0))
         + burst(t))
        for t in ts
    ]
    return ts, ys

def _load_csv_series(path: str, var: str) -> Tuple[List[float], List[float]]:
    """Load (t, value) pairs from CSV. Expects header with 't' and var or 'value'."""
    tt: List[float] = []
    vv: List[float] = []
    use_col = None
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        hdr = [h.strip() for h in (r.fieldnames or [])]
        if "t" not in hdr:
            raise ValueError(f"CSV {path} must have a 't' column; got {hdr}")
        if var in hdr:
            use_col = var
        elif "value" in hdr:
            use_col = "value"
        else:
            # try first non-'t' column
            candidates = [h for h in hdr if h != "t"]
            if not candidates:
                raise ValueError(f"CSV {path} has no value column besides 't'.")
            use_col = candidates[0]
        for row in r:
            try:
                t = float(row["t"])
                v = float(row[use_col])
            except Exception:
                # skip bad rows silently
                continue
            tt.append(t)
            vv.append(v)

    if len(tt) < 2:
        raise ValueError(f"CSV {path} yielded insufficient points.")
    # Ensure strictly increasing time for bisect
    pairs = sorted(zip(tt, vv), key=lambda p: p[0])
    tt = [p[0] for p in pairs]
    vv = [p[1] for p in pairs]
    return tt, vv

def _resample_linear(tt: List[float], vv: List[float], t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    """Resample irregular (tt,vv) onto uniform grid [t0..t1] using linear interpolation."""
    if t1 <= t0 or dt <= 0:
        raise ValueError("Invalid resample window or step.")
    grid: List[float] = []
    vals: List[float] = []
    n = max(2, int(round((t1 - t0) / dt)) + 1)
    for i in range(n):
        t = t0 + i * dt
        grid.append(t)
        # clamp to edges
        if t <= tt[0]:
            vals.append(vv[0]); continue
        if t >= tt[-1]:
            vals.append(vv[-1]); continue
        j = bisect.bisect_left(tt, t)
        t0i, t1i = tt[j-1], tt[j]
        v0i, v1i = vv[j-1], vv[j]
        # linear interp
        w = (t - t0i) / (t1i - t0i) if t1i != t0i else 0.0
        vals.append(v0i * (1 - w) + v1i * w)
    return grid, vals

# ----------------------------- public API ----------------------------------

def fetch_timeseries(
    dataset: str,
    var: str,
    xyz: Tuple[float, float, float],
    t0: float,
    t1: float,
    dt: float,
    token: Optional[str] = None,
) -> Tuple[List[float], List[float]]:
    """
    Return (t, y) for a scalar at point (x,y,z) over [t0..t1:dt].

    Offline precedence:
      1) If NASA_CSV is set → load CSV and resample.
      2) Else if NASA_OFFLINE=1 → return synthetic.
      3) Else → raise NotImplementedError (wire real API here).
    """
    csv_path = os.getenv("NASA_CSV", "").strip()
    offline = os.getenv("NASA_OFFLINE", "1") == "1"

    if csv_path:
        tt, vv = _load_csv_series(csv_path, var)
        return _resample_linear(tt, vv, t0, t1, dt)

    if offline:
        return _synthetic_series(t0, t1, dt)

    # TODO: Implement real NASA CFD access here (REST, file service, etc.)
    # Use `dataset`, `var`, `xyz`, `t0,t1,dt`, and an auth `token` if required.
    raise NotImplementedError("Wire NASA CFD source here (set NASA_OFFLINE=1 for synthetic or NASA_CSV for local CSV).")
