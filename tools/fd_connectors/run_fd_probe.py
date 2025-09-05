#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series (synthetic | jhtdb | nasa), detect EVENT times
(peaks in v(t)), compute NT rhythm from event-to-event intervals, and write
metrics JSON for downstream pulse creation.

CLI (aligned with fd_probe.yml):
  --source   {synthetic,jhtdb,nasa}
  --dataset  dataset slug (workflow already sanitizes)
  --var      variable name (e.g., "u")
  --xyz      "x,y,z"
  --twin     "t0,t1,dt"
  --json-out path for metrics JSON
  [--title]  (unused here; carried by make_pulse)
  [--tags]   (unused here; carried by make_pulse)
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Dict, Any, Tuple, List

import numpy as np

# Optional SciPy peak finder (preferred)
try:
    from scipy.signal import find_peaks as _scipy_find_peaks  # type: ignore
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False

# rhythm tools (already in your repo)
from tools.agent_rhythm.rhythm import (
    rhythm_from_events,  # expects a list of event timestamps
)

# source connectors
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ------------------------- helpers -----------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np.generic):
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, dict):
        return {str(k): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


def synthetic_timeseries(t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    n = max(3, int((t1 - t0) / max(dt, 1e-12)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.7  # Hz
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.18 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


def simple_peaks(y: np.ndarray, min_prom: float = 0.0, min_sep: int = 5) -> np.ndarray:
    """
    Ultra-light peak picker:
      - local maxima y[i-1] < y[i] > y[i+1]
      - optional tiny 'prominence' via immediate neighbors
      - enforce min_sep (samples) between accepted peaks
    """
    N = len(y)
    if N < 3:
        return np.array([], dtype=int)
    cand = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
    if cand.size == 0:
        return cand
    if min_prom > 0:
        left  = y[cand] - y[np.maximum(cand - 1, 0)]
        right = y[cand] - y[np.minimum(cand + 1, N - 1)]
        prom  = np.minimum(left, right)
        cand  = cand[prom >= min_prom]
        if cand.size == 0:
            return cand
    if min_sep > 1 and cand.size:
        keep = [cand[0]]
        for i in cand[1:]:
            if i - keep[-1] >= min_sep:
                keep.append(i)
        cand = np.array(keep, dtype=int)
    return cand


def rough_main_freq(ts: List[float], vs: List[float]) -> float | None:
    """Crude dominant frequency (exclude DC)."""
    if len(ts) < 4:
        return None
    dt = (ts[-1] - ts[0]) / max(1, (len(ts) - 1))
    y = np.asarray(vs, dtype=float) - np.mean(vs)
    spec = np.abs(np.fft.rfft(y))
    freq = np.fft.rfftfreq(len(y), d=dt)
    if len(spec) > 0:
        spec[0] = 0.0  # drop DC
    if spec.size == 0:
        return None
    k = int(np.argmax(spec))
    f0 = float(freq[k])
    return f0 if f0 > 0 else None


def spectrum_peaks(ts: List[float], vs: List[float], max_peaks: int = 5) -> Dict[str, Any]:
    """Basic spectrum summary for context (dominant freq/period, top peaks)."""
    if len(ts) < 4:
        return {"period": None, "bpm": None, "main_peak_freq": None, "peaks": []}
    dt = (ts[-1] - ts[0]) / max(1, (len(ts) - 1))
    y = np.asarray(vs, dtype=float) - np.mean(vs)
    spec = np.abs(np.fft.rfft(y))
    freq = np.fft.rfftfreq(len(y), d=dt)
    if len(spec) > 0:
        spec[0] = 0.0
    order = np.argsort(spec)[::-1][:max_peaks]
    pk = [[float(freq[i]), float(spec[i])] for i in order if i < len(freq)]
    f0 = float(freq[order[0]]) if len(order) else None
    period = (1.0 / f0) if (f0 and f0 > 0) else None
    bpm = (60.0 * f0) if (f0 and f0 > 0) else None
    return {"period": period, "bpm": bpm, "main_peak_freq": f0, "peaks": pk}


def detect_event_times(ts: List[float], vs: List[float]) -> List[float]:
    """
    Peak-pick v(t) to produce event (tick) times.
    Uses SciPy if present; otherwise falls back to a simple local-max picker.
    """
    if len(ts) < 3:
        return []
    y = np.asarray(vs, dtype=float)
    dt = (ts[-1] - ts[0]) / max(1, (len(ts) - 1))

    # Estimate a reasonable separation from rough main frequency (¼ period)
    f0 = rough_main_freq(ts, vs)
    if f0 and f0 > 0:
        min_sep_samples = int(max(3, 0.25 / f0 / max(dt, 1e-12)))
    else:
        min_sep_samples = max(3, int(0.01 * len(y)))  # 1% of samples

    # Prominence via robust scale (MAD)
    med = np.median(y)
    mad = np.median(np.abs(y - med))
    prom = 0.0 if mad == 0 else 0.3 * (1.4826 * mad)

    if _HAVE_SCIPY:
        idx, _ = _scipy_find_peaks(y, distance=min_sep_samples, prominence=prom if prom > 0 else None)
    else:
        idx = simple_peaks(y, min_prom=float(prom), min_sep=min_sep_samples)

    return [ts[i] for i in np.asarray(idx, dtype=int)]


# ------------------------- main --------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--title")
    ap.add_argument("--tags")
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        try:
            # Expect JHTDB_TOKEN in env for the real call.
            ts_obj = JHT.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
            ts, vs = ts_obj.t, ts_obj.v
            source_label = "jhtdb"
        except NotImplementedError:
            # While wiring up the real API, keep progress via synthetic fallback.
            ts, vs = synthetic_timeseries(t0, t1, dt)
            source_label = "jhtdb_offline"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)  # CSV/URL/inline text
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time & shape
    ts = sorted(ts)
    if len(ts) != len(vs):
        raise ValueError("Time and value arrays must be the same length.")

    # --- detect EVENT times (peaks) --------------------------------------
    tick_times = detect_event_times(ts, vs)

    # Guardrail: if no peaks found, fallback to sparse pseudo-events
    if len(tick_times) < 2:
        stride = max(2, len(ts) // 20)
        tick_times = ts[::stride][:20]

    # --- compute NT rhythm on event intervals ----------------------------
    mobj = rhythm_from_events(tick_times)
    metrics: Dict[str, Any] = asdict(mobj) if is_dataclass(mobj) else dict(mobj or {})

    # add spectrum context (over raw v(t))
    spec = spectrum_peaks(ts, vs, max_peaks=5)

    # add provenance
    metrics.update({
        "source": source_label,
        "details": {
            "dataset": args.dataset,
            "var": args.var,
            "xyz": [x, y, z],
            "window": [t0, t1, dt],
        },
        "period": spec["period"],
        "bpm": spec["bpm"],
        "main_peak_freq": spec["main_peak_freq"],
        "peaks": spec["peaks"],
    })

    metrics = to_builtin(metrics)

    # --- write metrics JSON ----------------------------------------------
    out_dir = os.path.dirname(args.json_out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    n = metrics.get("n", "?")           # number of event intervals used
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::events={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={source_label}, scipy={_HAVE_SCIPY})")
    print(f"Wrote metrics → {args.json_out}")


if __name__ == "__main__":
    main()
