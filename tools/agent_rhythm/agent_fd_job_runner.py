#!/usr/bin/env python3
"""
Agent FD Job Runner
- Reads a minimal job spec from inbox/fd_jobs/*.yml
- Fetches a single-point time series from source = {synthetic|nasa|jhtdb}
- Computes NT rhythm metrics (via tools already in the repo)
- Writes metrics JSON under results/fd_probe/, ALWAYS stamping `batch`
- Emits a Φ-Mesh pulse (make_pulse.py) which will be saved as ..._batchN.yml
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import yaml

# Rhythm helpers already present in your repo
from tools.agent_rhythm.rhythm import (
    ticks_from_message_times,
    rhythm_from_events,
)


def parse_triplet_list(x: Any, name: str) -> Tuple[float, float, float]:
    if isinstance(x, (list, tuple)) and len(x) == 3:
        return float(x[0]), float(x[1]), float(x[2])
    if isinstance(x, str):
        parts = [p.strip() for p in x.split(",")]
        if len(parts) == 3:
            return float(parts[0]), float(parts[1]), float(parts[2])
    raise ValueError(f"{name} must be a 3-length list/tuple or 'a,b,c' string")


def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


# ---------- synthetic series used when offline / simple tests -----------------

def synthetic_series(t0: float, t1: float, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    n = max(3, int(round((t1 - t0) / max(dt, 1e-9))))
    t = t0 + np.arange(n) * dt
    v = (
        np.sin(2 * np.pi * 0.40 * (t - t0))
        + 0.12 * np.sin(2 * np.pi * 1.25 * (t - t0))
    )
    return t, v


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="Path to inbox/fd_jobs/<file>.yml")
    args = ap.parse_args()

    with open(args.job, "r", encoding="utf-8") as f:
        job = yaml.safe_load(f) or {}

    required = ["source", "dataset", "var", "xyz", "window", "title", "tags"]
    missing = [k for k in required if k not in job]
    if missing:
        raise ValueError(f"Missing required job keys: {missing}")

    source = str(job["source"]).lower().strip()
    dataset = str(job["dataset"])
    var = str(job["var"])
    xyz = parse_triplet_list(job["xyz"], "xyz")
    window = parse_triplet_list(job["window"], "window")
    title = str(job["title"])
    tags_list = job.get("tags") or []
    if isinstance(tags_list, str):
        tags_list = [t for t in re.split(r"\s+", tags_list.strip()) if t]
    batch = int(job.get("batch", 1))

    t0, t1, dt = window
    x, y, z = xyz

    # Results path
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_json = os.path.join("results", "fd_probe", f"{safe_slug(dataset)}.metrics.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)

    # --- fetch series
    if source == "synthetic":
        ts, vs = synthetic_series(t0, t1, dt)
        source_label = "synthetic"
    elif source == "nasa":
        # Hook into your CSV function if available; fallback to synthetic
        try:
            from tools.fd_connectors.nasa import read_csv_timeseries
            nasa_path = os.getenv("NASA_CSV", "").strip() or dataset
            obj = read_csv_timeseries(nasa_path)
            ts, vs = np.asarray(obj.t, dtype=float), np.asarray(obj.v, dtype=float)
            source_label = "nasa"
        except Exception:
            ts, vs = synthetic_series(t0, t1, dt)
            source_label = "nasa_fallback_synth"
    elif source == "jhtdb":
        try:
            from tools.fd_connectors.jhtdb import fetch_timeseries
            ts_obj = fetch_timeseries(dataset=dataset, var=var, x=x, y=y, z=z, t0=t0, t1=t1, dt=dt)
            ts, vs = np.asarray(ts_obj.t, dtype=float), np.asarray(ts_obj.v, dtype=float)
            source_label = "jhtdb"
        except Exception:
            ts, vs = synthetic_series(t0, t1, dt)
            source_label = "jhtdb_fallback_synth"
    else:
        ts, vs = synthetic_series(t0, t1, dt)
        source_label = f"{source}_fallback_synth"

    # Ensure monotone time
    order = np.argsort(ts)
    ts, vs = ts[order], vs[order]

    # --- derive rhythm metrics using your helper
    tick_times = ticks_from_message_times(ts)
    m = rhythm_from_events(tick_times)  # dataclass or dict depending on your impl

    # normalize into a dict
    def to_dict(obj: Any) -> Dict[str, Any]:
        try:
            from dataclasses import asdict, is_dataclass
            if is_dataclass(obj):
                return asdict(obj)
        except Exception:
            pass
        if isinstance(obj, dict):
            return dict(obj)
        return {}

    metrics_core = to_dict(m)

    # --- ALWAYS include batch in details & meta
    details = {
        "dataset": dataset,
        "var": var,
        "xyz": [x, y, z],
        "window": [t0, t1, dt],
        "batch": int(batch),
    }
    meta = {"batch": int(batch), "timestamp": stamp}

    metrics = dict(metrics_core)
    metrics["source"] = source_label
    metrics["details"] = details
    metrics["meta"] = meta

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"Wrote metrics → {out_json}")

    # --- emit pulse
    dataset_slug = safe_slug(dataset)
    tags_str = " ".join(str(t) for t in tags_list)

    cmd = [
        sys.executable,
        "tools/agent_rhythm/make_pulse.py",
        "--metrics", out_json,
        "--title", title,
        "--dataset", dataset_slug,
        "--tags", tags_str,
        "--outdir", "pulse/auto",
    ]
    print("→ Emitting pulse:", " ".join(cmd))
    rc = os.spawnvp(os.P_WAIT, cmd[0], cmd)  # simple & avoids buffering issues
    if rc != 0:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
