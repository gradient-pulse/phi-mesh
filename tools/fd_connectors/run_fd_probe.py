#!/usr/bin/env python3
"""
tools/fd_connectors/run_fd_probe.py

Fetch a 1-point time series from a source (synthetic | jhtdb | nasa),
compute NT-rhythm metrics, and write metrics JSON (for make_pulse.py).

Args (aligned with fd_probe.yml):
  --source   {synthetic,jhtdb,nasa}
  --dataset  free-text dataset name/slug (workflow already sanitizes)
  --var      variable name (e.g., "u")
  --xyz      "x,y,z"
  --twin     "t0,t1,dt"
  --batch    integer batch counter (default 1) for stable, non-overwriting filenames
  --json-out path to write metrics JSON (file OR directory)

Environment (optional):
  JHTDB_OFFLINE=1   → force synthetic in the JHTDB path
  JHTDB_TOKEN       → real token enables online JHTDB when wired
  NASA_CSV          → CSV/URL/inline CSV used for NASA source (if present)
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Tuple

# rhythm tools (repo-local)
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)

# source connectors (repo-local)
from tools.fd_connectors import jhtdb as JHT
from tools.fd_connectors import nasa as NASA


# ---------- small utilities -------------------------------------------------

def parse_triplet(s: str) -> Tuple[float, float, float]:
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected three comma-separated values, got: {s!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def safe_slug(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Coerce dataclasses / numpy / misc types into plain Python types."""
    try:
        import numpy as np
        np_scalar = np.generic
    except Exception:  # numpy not installed
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
    """Clean synthetic rhythm with a weak harmonic."""
    n = max(3, int((t1 - t0) / max(dt, 1e-9)))
    ts = [t0 + i * dt for i in range(n)]
    base = 0.4  # Hz in window units
    vs = [
        math.sin(2 * math.pi * base * (t - t0))
        + 0.15 * math.sin(2 * math.pi * 3 * base * (t - t0))
        for t in ts
    ]
    return ts, vs


def build_slug(dataset: str, source: str, batch: int) -> str:
    """Uniform provenance slug used for results + pulse filenames."""
    return f"{safe_slug(source)}_{safe_slug(dataset)}_batch{int(batch)}"


def resolve_json_out(path: str, final_slug: str) -> str:
    """
    If json_out is a directory, create "<dir>/<final_slug>.metrics.json".
    If json_out looks like a file (endswith .json or path has suffix), use as-is.
    """
    base = os.path.normpath(path)
    if base.endswith(".json") or os.path.splitext(base)[1].lower() == ".json":
        outdir = os.path.dirname(base)
        if outdir:
            os.makedirs(outdir, exist_ok=True)
        return base
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{final_slug}.metrics.json")


# ---------- main -----------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["synthetic", "jhtdb", "nasa"])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", required=True, help="x,y,z")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--batch", type=int, default=1, help="batch counter for non-overwriting outputs")
    ap.add_argument("--json-out", required=True, help="file path OR directory for metrics output")
    # Unused here; passed forward by workflow to make_pulse.py
    ap.add_argument("--title")
    ap.add_argument("--tags")
    args = ap.parse_args()

    # Parse inputs
    x, y, z = parse_triplet(args.xyz)
    t0, t1, dt = parse_triplet(args.twin)

    # Final slug (shared for results + pulses)
    final_slug = build_slug(dataset=args.dataset, source=args.source, batch=args.batch)

    # -------- fetch time series ------------------------------------------
    if args.source == "synthetic":
        ts, vs = synthetic_timeseries(t0, t1, dt)
        source_label = "synthetic"

    elif args.source == "jhtdb":
        # If offline or token missing, attempt JHT's offline helper else synthetic.
        if os.getenv("JHTDB_OFFLINE", "0") == "1" or not os.getenv("JHTDB_TOKEN"):
            try:
                ts_obj = JHT.fetch_timeseries(
                    dataset=args.dataset, var=args.var,
                    x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
                )
                ts, vs = ts_obj.t, ts_obj.v
            except Exception:
                ts, vs = synthetic_timeseries(t0, t1, dt)
            source_label = "jhtdb_offline"
        else:
            # Real call once wired up in jhtdb.py
            ts_obj = JHT.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
            ts, vs = ts_obj.t, ts_obj.v
            source_label = "jhtdb"

    else:  # nasa
        nasa_csv = os.getenv("NASA_CSV", "").strip()
        if nasa_csv:
            ts_obj = NASA.read_csv_timeseries(nasa_csv)  # CSV/URL/inline string
        else:
            ts_obj = NASA.fetch_timeseries(
                dataset=args.dataset, var=args.var,
                x=x, y=y, z=z, t0=t0, t1=t1, dt=dt
            )
        ts, vs = ts_obj.t, ts_obj.v
        source_label = "nasa"

    # Ensure monotonic time (defensive)
    ts = sorted(ts)

    # -------- compute NT rhythm metrics ----------------------------------
    tick_times = ticks_from_message_times(ts)
    m = rhythm_from_events(tick_times)

    if is_dataclass(m):
        metrics: Dict[str, Any] = asdict(m)
    elif isinstance(m, dict):
        metrics = m
    else:
        metrics = {}

    metrics["source"] = source_label
    metrics["details"] = {
        "dataset": args.dataset,
        "var": args.var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
        "slug": final_slug,
        "batch": int(args.batch),
    }
    metrics = to_builtin(metrics)

    # -------- write metrics JSON -----------------------------------------
    out_path = resolve_json_out(args.json_out, final_slug)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    print(f"::notice title=FD Probe::{final_slug}: n={n}, mean_dt={mean_dt}, cv_dt={cv_dt} (src={source_label})")
    print(f"Wrote metrics → {out_path}")


if __name__ == "__main__":
    # Allow PYTHONPATH-less execution in Actions
    if __package__ is None:  # when invoked as a script
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if repo_root not in os.sys.path:
            os.sys.path.insert(0, repo_root)
    main()
