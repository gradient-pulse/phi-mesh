#!/usr/bin/env python3
"""
agent_fd_job_runner.py — consume an FD job YAML from inbox/fd_jobs, run the probe,
write metrics (results/fd_probe), emit a Φ-Mesh pulse, and move the job to _done/_error.

Job schema (YAML):
  dataset:  free text (e.g. "demo", "data/nasa/demo_timeseries.csv")
  source:   synthetic | jhtdb | nasa
  var:      e.g. "u"
  xyz:      [x, y, z]
  window:   [t0, t1, dt]
  batch:    optional label like "batch1", "batch2" (used to suffix the dataset slug)
  title:    pulse title (single quotes enforced)
  tags:     space separated or list (either accepted)

Outputs:
  results/fd_probe/YYYY-MM-DD_<dataset[_batch]>.metrics.json
  pulse/auto/YYYY-MM-DD_<dataset[_batch]>.yml
"""

from __future__ import annotations
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # repo root

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def to_triplet(v: Any, name: str) -> str:
    """Accepts [a,b,c] list; returns 'a,b,c' string for CLI."""
    if not isinstance(v, (list, tuple)) or len(v) != 3:
        raise ValueError(f"{name} must be a 3-length list like [a,b,c]")
    return ",".join(str(x) for x in v)

def ensure_single_quotes(title: str) -> str:
    t = (title or "").strip()
    if not (t.startswith("'") and t.endswith("'")):
        # escape existing single quotes by doubling them (YAML safe)
        t = "'" + t.replace("'", "''") + "'"
    return t

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="Path to inbox/fd_jobs/<job>.yml")
    args = ap.parse_args()

    job_path = args.job
    with open(job_path, "r", encoding="utf-8") as f:
        job: Dict[str, Any] = yaml.safe_load(f) or {}

    required = ["dataset", "source", "var", "xyz", "window", "title", "tags"]
    missing = [k for k in required if k not in job]
    if missing:
        raise ValueError(f"Missing required job keys: {missing}")

    dataset_raw: str = str(job["dataset"])
    source: str = str(job["source"]).strip().lower()
    var: str = str(job["var"])
    xyz_csv = to_triplet(job["xyz"], "xyz")
    twin_csv = to_triplet(job["window"], "window")
    batch: str = str(job.get("batch", "") or "").strip()

    # Build the dataset slug used for both metrics filename and pulse filename.
    # Convention: <dataset>_batchN  (only include _batchN if provided)
    ds_slug_base = safe_slug(dataset_raw)
    ds_slug = f"{ds_slug_base}_{batch}" if batch else ds_slug_base

    # Title & tags hygiene
    title = ensure_single_quotes(str(job["title"]))
    tags = job["tags"]
    if isinstance(tags, str):
        tag_list = [t for t in re.split(r"\s+", tags.strip()) if t]
    else:
        tag_list = [str(t) for t in (tags or [])]

    # Paths
    today = dt.date.today().isoformat()
    results_dir = os.path.join(ROOT, "results", "fd_probe")
    os.makedirs(results_dir, exist_ok=True)
    metrics_path = os.path.join(results_dir, f"{today}_{ds_slug}.metrics.json")

    # 1) Run the FD probe to produce metrics JSON
    probe = os.path.join(ROOT, "tools", "fd_connectors", "run_fd_probe.py")
    cmd = [
        sys.executable, probe,
        "--source", source,
        "--dataset", ds_slug_base,    # compute metrics for the base dataset (content)
        "--var", var,
        "--xyz", xyz_csv,
        "--twin", twin_csv,
        "--json-out", metrics_path,
    ]
    # env passthrough for connectors
    env = os.environ.copy()
    # (no extra env needed here beyond repository secrets that Actions injects)

    print("::group::Run FD probe")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env, cwd=ROOT)
    print("::endgroup::")

    # 2) Emit pulse from the metrics JSON (using ds_slug with batch for the filename)
    make_pulse = os.path.join(ROOT, "tools", "agent_rhythm", "make_pulse.py")
    cmd2 = [
        sys.executable, make_pulse,
        "--metrics", metrics_path,
        "--title", title,
        "--dataset", ds_slug,        # <- this ensures pulse filename contains _batchN
        "--tags", " ".join(tag_list),
        "--outdir", os.path.join(ROOT, "pulse", "auto"),
    ]
    print("::group::Make pulse")
    print(" ".join(cmd2))
    subprocess.run(cmd2, check=True, env=env, cwd=ROOT)
    print("::endgroup::")

    # 3) Move job file to _done/
    inbox_dir = os.path.dirname(job_path)
    done_dir = os.path.join(inbox_dir, "_done")
    os.makedirs(done_dir, exist_ok=True)
    dest = os.path.join(done_dir, os.path.basename(job_path))
    shutil.move(job_path, dest)
    print(f"Moved job to {dest}")

if __name__ == "__main__":
    main()
