#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic|jhtdb|nasa),
compute NT-rhythm metrics, and write metrics JSON into results/fd_probe/.
Auto-assigns a monotonically increasing batch number (_batchN) per
(dataset, source) result group, and also writes a stable *latest* pointer.

- Primary output:
    results/fd_probe/<slug>-<source>_batchN.metrics.json
- Stable pointer (for workflows):
    results/fd_probe/<slug>-<source>_latest.metrics.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import glob
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# --- rhythm tools (repo-local)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# --- optional source connectors (we use tiny wrappers inside)
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ----------------- helpers -----------------

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    try:
        import numpy as np
        np_scalar = np.generic
    except Exception:  # numpy might not be available
        class _S: ...
        np_scalar = _S  # type: ignore

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


def _next_batch_id(results_dir: str, result_base: str) -> int:
    """
    Find the next available batchN for results like:
      {results_dir}/{result_base}_batchN.metrics.json
    Returns the integer N to use (1 if none exist yet).
    """
    pattern = os.path.join(results_dir, f"{result_base}_batch*.metrics.json")
    max_n = 0
    for path in glob.glob(pattern):
        m = re.search(r"_batch(\d+)\.metrics\.json$", path)
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return max_n + 1


def _write_latest_pointer(latest_path: str, payload: Dict[str, Any]) -> None:
    """
    Write the latest pointer JSON. This is a tiny JSON that mirrors the
    last run's metrics so downstream steps can always read a stable path.
    """
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ----------------- main -----------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True, help="Free-text dataset slug/name")
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    # --json-out remains optional; if omitted we compute with auto-batch.
    ap.add_argument("--json-out", required=False, help="Optional: explicit metrics path")
    ap.add_argument("--title")
    ap.add_argument("--tags")
    args = ap.parse_args()

    x, y, z = parse_triplet(args.xyz)
    t0, t1, dtv = parse_triplet(args.twin)

    # --- fetch time series ------------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dtv)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        # Token determines online vs offline. (We keep a tiny offline fallback.)
        token = os.getenv("JHTDB_TOKEN", "").strip()
        if not token or os.getenv("JHTDB_OFFLINE", "0") == "1":
            try:
                ts_obj = JHT.fetch_timeseries(
                    dataset=args.dataset, var=args.var,
                    x=x, y=y, z=z, t0=t0, t1=t1, dt=dtv
                )
                ts, vs = ts_obj.t, ts_obj.v
                source_label = "jhtdb_offline"
            except Exception:
                ts, vs = synthetic_timeseries(t0, t1, dtv)
                source_label = "jhtdb_offline"
        else:
            ts_obj = JHT.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dtv
            )
            ts, vs = ts_obj.t, ts_obj.v
            source_label = "jhtdb"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dtv
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time
    ts = sorted(ts)

    # --- compute NT rhythm metrics ---------------------------------------
    tick_times = ticks_from_message_times(ts)
    mobj = rhythm_from_events(tick_times)
    if is_dataclass(mobj):
        metrics: Dict[str, Any] = asdict(mobj)
    elif isinstance(mobj, dict):
        metrics = dict(mobj)
    else:
        metrics = {}

    metrics["source"] = source_label
    metrics.setdefault("details", {})
    metrics["details"].update({
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dtv],
    })

    # --- decide output path(s) with auto-batch ----------------------------
    results_dir = "results/fd_probe"
    os.makedirs(results_dir, exist_ok=True)

    slug = safe_slug(args.dataset)
    result_base = f"{slug}-{source_label}"

    # If user provided --json-out, treat it as a base and still batch it.
    if args.json_out:
        base_dir = os.path.dirname(args.json_out) or results_dir
        base_name = os.path.basename(args.json_out)
        # strip suffix + any accidental batch
        base_name = re.sub(r"_batch\d+\.metrics\.json$", "", base_name)
        base_name = re.sub(r"\.metrics\.json$", "", base_name)
        result_base = base_name
        results_dir = base_dir
        os.makedirs(results_dir, exist_ok=True)

    batch_id = _next_batch_id(results_dir, result_base)
    metrics["batch"] = batch_id
    metrics["details"]["batch"] = batch_id

    json_out = os.path.join(results_dir, f"{result_base}_batch{batch_id}.metrics.json")
    latest_out = os.path.join(results_dir, f"{result_base}_latest.metrics.json")

    # Save metrics
    payload = to_builtin(metrics)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Stable pointer
    _write_latest_pointer(latest_out, payload)

    # Nicety for logs and for composite actions (if ever used)
    print(f"::notice title=FD Probe::wrote {os.path.relpath(json_out)} (batch={batch_id}, src={source_label})")
    print(f"LATEST_METRICS={os.path.relpath(latest_out)}")  # helpful to parse from logs


if __name__ == "__main__":
    main()
