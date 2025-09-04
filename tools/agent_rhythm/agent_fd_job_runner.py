#!/usr/bin/env python3
"""
Agent FD Job Runner
-------------------
Consumes a single job spec from inbox/fd_jobs/*.yml, fetches a 1-point time series
via the fd_connectors runner, computes NT-rhythm metrics, and emits:

- results/fd_probe/YYYY-MM-DD_<dataset>_batchN.metrics.json
- pulse/auto/YYYY-MM-DD_<dataset>_batchN.yml

If the job does not specify `batch`, we auto-assign `batchN` by scanning existing
metrics/pulse files for the same date+dataset.

Job YAML shape (lists or comma-strings are both ok for xyz/window):

source: synthetic | nasa | jhtdb
dataset: <free text, will be slugged>
var: u
xyz: [0.1, 0.1, 0.1]   # or "0.1,0.1,0.1"
window: [0.0, 10.0, 0.01]  # or "0.0,10.0,0.01"
title: 'NT Rhythm — FD Probe'
tags: ['nt_rhythm','turbulence','navier_stokes','rgp']
# batch: batch3   # optional; if omitted we auto-assign batch1/batch2/...

"""

from __future__ import annotations
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List

import yaml


# ----------------- utils -----------------

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_list3(val: Any, name: str) -> List[float]:
    if isinstance(val, str):
        parts = [p.strip() for p in val.split(",")]
    elif isinstance(val, (list, tuple)):
        parts = list(val)
    else:
        raise ValueError(f"{name} must be list-of-3 or 'a,b,c' string")
    if len(parts) != 3:
        raise ValueError(f"{name} must be 3-length list/CSV")
    try:
        return [float(p) for p in parts]
    except Exception:
        raise ValueError(f"{name} values must be numeric")


def find_next_batch_label(date_str: str, dataset_slug: str) -> str:
    """
    Look for existing results for this date+dataset and pick the next batchN.
    We scan both results and pulses to be robust.
    """
    candidates = []
    patt_res = f"results/fd_probe/{date_str}_{dataset_slug}_batch*.metrics.json"
    patt_pul = f"pulse/auto/{date_str}_{dataset_slug}_batch*.yml"

    for path in glob.glob(patt_res) + glob.glob(patt_pul):
        m = re.search(r"_batch(\d+)\.", os.path.basename(path))
        if m:
            try:
                candidates.append(int(m.group(1)))
            except Exception:
                pass

    n = (max(candidates) + 1) if candidates else 1
    return f"batch{n}"


def sh(args: List[str]) -> None:
    subprocess.run(args, check=True)


# ----------------- main -----------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="Path to inbox/fd_jobs/<job>.yml")
    args = ap.parse_args()

    with open(args.job, "r", encoding="utf-8") as f:
        job = yaml.safe_load(f) or {}

    # Required keys
    required = ["source", "dataset", "var", "xyz", "window", "title", "tags"]
    missing = [k for k in required if k not in job]
    if missing:
        raise ValueError(f"Missing required job keys: {missing}")

    source = str(job["source"]).strip().lower()
    dataset_slug = safe_slug(str(job["dataset"]))
    var = str(job["var"]).strip()
    xyz = to_list3(job["xyz"], "xyz")
    window = to_list3(job["window"], "window")
    title = str(job["title"])
    tags = job.get("tags", [])
    if isinstance(tags, str):
        tags = [t for t in re.split(r"\s+", tags.strip()) if t]

    # Batch: use provided, or auto-assign by scanning existing outputs
    today = dt.date.today().isoformat()
    batch_label = str(job.get("batch", "")).strip()
    if not batch_label:
        batch_label = find_next_batch_label(today, dataset_slug)

    print(f"::notice title=FD Job:: dataset={dataset_slug}, source={source}, "
          f"xyz={xyz}, window={window}, batch={batch_label}")

    # Paths
    os.makedirs("results/fd_probe", exist_ok=True)
    metrics_out = f"results/fd_probe/{today}_{dataset_slug}_{batch_label}.metrics.json"

    # Prepare connector args
    xyz_str = ",".join(str(v) for v in xyz)
    win_str = ",".join(str(v) for v in window)

    # 1) Run the FD probe (writes metrics JSON)
    #    We don't depend on run_fd_probe's own --batch; the filename we pass
    #    already encodes the batch label.
    sh([
        sys.executable, "tools/fd_connectors/run_fd_probe.py",
        "--source", source,
        "--dataset", dataset_slug,
        "--var", var,
        "--xyz", xyz_str,
        "--twin", win_str,
        "--json-out", metrics_out,
    ])

    # 2) Emit a pulse for this metrics file
    #    Pass dataset with the batch suffix so the pulse filename includes it.
    dataset_for_pulse = f"{dataset_slug}_{batch_label}"
    sh([
        sys.executable, "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics_out,
        "--title", title,
        "--dataset", dataset_for_pulse,
        "--tags", " ".join(tags),
        "--outdir", "pulse/auto",
    ])

    print(f"::notice title=Outputs:: metrics={metrics_out} "
          f"pulse=pulse/auto/{today}_{dataset_for_pulse}.yml")


if __name__ == "__main__":
    main()
