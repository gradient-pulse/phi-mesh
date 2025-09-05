#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic|jhtdb|nasa),
DETECT EVENTS FROM THE SIGNAL (not the sample clock), compute NT-rhythm
metrics, and write a metrics JSON that downstream make_pulse.py will read.

Args (aligned with fd_probe.yml):
  --source       {synthetic,jhtdb,nasa}
  --dataset      free-text dataset name/slug (workflow already sanitizes)
  --var          variable name (e.g., "u")
  --xyz          "x,y,z"
  --twin         "t0,t1,dt"
  --json-out     path to write metrics JSON (results/fd_probe/<...>.metrics.json)
  --title        (unused here; carried by make_pulse)
  --tags         (unused here; carried by make_pulse)
  --also-latest  also write <slug>_latest.metrics.json next to main file

Detector knobs (optional, sensible defaults):
  --smooth-k       int, moving-average window on |u| (default 5; 0 disables)
  --peak-mag-k     float, magnitude threshold = mu + k*sig  (default 0.75)
  --peak-prom-k    float, prominence proxy  = k*sig         (default 0.25)
  --min-sep-ms     float, min separation between peaks in milliseconds (default 2.0)

Notes
- Previously this script measured the sampler’s rhythm (events = timestamps).
- Now we detect events from |u(t)| with a tiny, SciPy-free peak detector.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# rhythm tools
from tools.agent_rhythm.rhythm import rhythm_from_events

# source connectors
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ---------- tiny utilities ---------------------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    try:
        import numpy as np
        np_scalar = np.generic  # type: ignore[attr-defined]
    except Exception:  # numpy not installed
        class _S: ...
        np_scalar = _S  # type: ignore

    if is_dataclass(x):
        return {k: to_builtin(v) for k, v in asdict(x).items()}
    if isinstance(x, (str, int, float, bool))) or x is None:
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


# ---------- synthetic generator (unchanged) ----------------------------------

def synthetic_timeseries(t0: float, t1: float, dt: float) -> Tuple[List[float], List[float]]:
    n = max(3, int((t1 - t0) / max(dt, 1e-9)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.4
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


# ---------- NEW: event detector from the signal ------------------------------

def events_from_signal(
    ts: List[float],
    vs: List[float],
    smooth_k: int = 5,
    peak_mag_k: float = 0.75,
    peak_prom_k: float = 0.25,
    min_sep_ms: float = 2.0,
) -> List[float]:
    """
    Turn a scalar probe time-series into event times.
    Simple, SciPy-free peak detector on |u| with magnitude + small prominence
    check + min separation. Tuned conservatively to avoid over-triggering.
    """
    try:
        import numpy as np
    except Exception:
        return []

    if len(ts) != len(vs) or len(ts) < 5:
        return []

    t = np.asarray(ts, dtype=float)
    u = np.asarray(vs, dtype=float)
    s = np.abs(u)

    # smoothing
    if smooth_k and smooth_k > 1 and len(s) >= smooth_k:
        s = np.convolve(s, np.ones(smooth_k, dtype=float) / smooth_k, mode="same")

    mu = float(np.mean(s))
    sig = float(np.std(s)) + 1e-12
    mag_th = mu + peak_mag_k * sig
    prom_th = peak_prom_k * sig

    # min separation in samples
    if len(t) >= 2:
        dt_est = max(1e-12, float(t[1] - t[0]))
        min_sep = max(1, int((min_sep_ms / 1000.0) / dt_est))
    else:
        min_sep = 5

    peaks_idx: List[int] = []
    last_idx = -10**9
    N = len(s)

    for i in range(1, N - 1):
        if s[i] <= mag_th:
            continue
        if not (s[i - 1] < s[i] > s[i + 1]):  # strict local max
            continue

        # crude "prominence": height above local min in a small window
        w = 8
        lo = max(0, i - w)
        hi = min(N, i + w + 1)
        local_min = float(np.min(s[lo:hi]))
        if (s[i] - local_min) < prom_th:
            continue

        if (i - last_idx) < min_sep:
            continue

        peaks_idx.append(i)
        last_idx = i

    return [float(t[i]) for i in peaks_idx]


# ---------- main -------------------------------------------------------------

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
    ap.add_argument("--also-latest", action="store_true",
                    help="Also write <slug>_latest.metrics.json next to main file")

    # detector knobs
    ap.add_argument("--smooth-k", type=int, default=5,
                    help="Moving-average window on |u| (0 disables). Default: 5")
    ap.add_argument("--peak-mag-k", type=float, default=0.75,
                    help="Magnitude threshold = mu + k*sig. Default: 0.75")
    ap.add_argument("--peak-prom-k", type=float, default=0.25,
                    help="Prominence proxy = k*sig. Default: 0.25")
    ap.add_argument("--min-sep-ms", type=float, default=2.0,
                    help="Min separation between peaks in milliseconds. Default: 2.0")

    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        token = os.environ.get("JHTDB_TOKEN", "").strip()
        if not token:
            try:
                ts_obj = JHT.fetch_timeseries(
                    dataset=args.dataset, var=args.var,
                    x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
                )
                ts, vs = ts_obj.t, ts_obj.v
            except NotImplementedError:
                ts, vs = synthetic_timeseries(t0, t1, dt)
                source_label = "jhtdb_offline"
            else:
                source_label = "jhtdb"
        else:
            ts_obj = JHT.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
            ts, vs = ts_obj.t, ts_obj.v
            source_label = "jhtdb"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)
            ts, vs = ts_obj.t, ts_obj.v
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
            ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # --- detect events FROM SIGNAL ---------------------------------------
    event_times = events_from_signal(
        ts, vs,
        smooth_k=args.smooth_k,
        peak_mag_k=args.peak_mag_k,
        peak_prom_k=args.peak_prom_k,
        min_sep_ms=args.min_sep_ms,
    )

    if len(event_times) < 3:
        # fallback: every 200th sample if long enough, else none
        if len(ts) >= 600:
            event_times = [ts[i] for i in range(0, len(ts), 200)]
        else:
            event_times = []

    # --- compute NT rhythm metrics ---------------------------------------
    mobj = rhythm_from_events(event_times)
    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = mobj
    else:
        metrics = {}

    metrics["source"] = source_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
    }
    metrics = to_builtin(metrics)

    # --- write metrics JSON ----------------------------------------------
    out_path = args.json_out
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    if args.also-latest:
        base = os.path.basename(out_path)
        if base.endswith(".metrics.json"):
            latest_name = base.replace(".metrics.json", "_latest.metrics.json")
        else:
            stem, ext = os.path.splitext(base)
            latest_name = f"{stem}_latest.metrics.json"
        latest_path = os.path.join(os.path.dirname(out_path), latest_name)
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::events={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={source_label})")
    print(f"Wrote metrics → {out_path}")


if __name__ == "__main__":
    main()
