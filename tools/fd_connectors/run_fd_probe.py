#!/usr/bin/env python3
"""
run_fd_probe.py — fetch a 1-point time series from JHTDB,
compute minimal NT-rhythm metrics, and write *metrics JSON only*.

Args:
  --dataset  JHTDB dataset slug (e.g., isotropic1024coarse)
  --var      velocity component (u|v|w)
  --xyz      "x,y,z"
  --twin     "t0,t1,dt"
  --json-out path to write metrics JSON
  --title    (unused here; carried by make_pulse)
  --tags     (unused here; carried by make_pulse)
"""

from __future__ import annotations

# --- ensure the repo root is importable even if PYTHONPATH is unset ----------
import os, sys
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[2]  # .../phi-mesh/phi-mesh
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# ------------------------------------------------------------------------------

import argparse
import json
import math
from statistics import pstdev
from typing import Any, Dict, List, Tuple

# JHTDB connector (lives in the repo)
from tools.fd_connectors import jhtdb as JHT


# --------- tiny, inlined NT-metrics (no external import needed) --------------

def ticks_from_message_times(ts: List[float]) -> List[float]:
    """Return the same list (monotonic pairs are handled upstream)."""
    return list(ts or [])

def rhythm_from_events(ticks: List[float]) -> Dict[str, Any]:
    """
    Minimal metrics:
      - n, duration
      - mean_dt, cv_dt
      - period (=mean_dt), main_peak_freq (=1/period)
      - peaks: [[f0, 1.0]] if f0 is defined (a lightweight hint for downstream)
    """
    ticks = list(ticks or [])
    n = len(ticks)
    m: Dict[str, Any] = {"n": n}

    if n >= 2:
        dts = [ticks[i+1] - ticks[i] for i in range(n - 1)]
        dts = [dt for dt in dts if math.isfinite(dt) and dt > 0]
        if dts:
            duration = ticks[-1] - ticks[0]
            mean_dt = sum(dts) / len(dts)
            std_dt = pstdev(dts) if len(dts) > 1 else 0.0
            cv_dt = (std_dt / mean_dt) if mean_dt > 0 else None
            period = mean_dt if mean_dt > 0 else None
            f0 = (1.0 / period) if period and period > 0 else None

            m.update({
                "duration": duration,
                "mean_dt": mean_dt,
                "cv_dt": cv_dt,
                "period": period,
                "main_peak_freq": f0,
                "peaks": [[f0, 1.0]] if f0 else [],
            })
            return m

    # Fallback when we don't have enough points
    m.update({
        "duration": 0.0,
        "mean_dt": None,
        "cv_dt": None,
        "period": None,
        "main_peak_freq": None,
        "peaks": [],
    })
    return m


# ---------- helpers -----------------------------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])

def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    try:
        import numpy as np  # type: ignore
        np_scalar = np.generic  # type: ignore[attr-defined]
    except Exception:  # numpy not installed
        class _NP: ...
        np_scalar = _NP  # type: ignore

    from dataclasses import asdict, is_dataclass
    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_scalar):
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, dict):
        return {str(k): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title")  # ignored here (used downstream by make_pulse)
    ap.add_argument("--tags")   # ignored here (used downstream by make_pulse)
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series from JHTDB -------------------------------------
    ts_obj = JHT.fetch_timeseries(
        dataset=args.dataset, var=args.var,
        x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
    )
    ts, vs = ts_obj.t, ts_obj.v  # vs is unused by current NT metrics
    src_label = "jhtdb"

    # Ensure monotonic time, preserving (t,v) pairing
    if ts and any(ts[i] > ts[i+1] for i in range(len(ts)-1)):
        pairs = sorted(zip(ts, vs), key=lambda p: p[0])
        ts, vs = [p[0] for p in pairs], [p[1] for p in pairs]

    # --- compute NT-rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    metrics = rhythm_from_events(tick_times)

    # attach provenance
    metrics["source"] = src_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
    }

    # coerce to JSON-safe builtins
    metrics = to_builtin(metrics)

    # --- write metrics JSON ONLY -----------------------------------------
    out_dir = os.path.dirname(os.path.abspath(args.json_out)) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # concise notice for GH Actions
    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe Metrics::n={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={src_label})")
    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
