#!/usr/bin/env python3
"""
agent_fd_job_runner.py — run a one-off FD probe job and fossilize a pulse.

Reads a job YAML with keys:
  - source: synthetic | jhtdb | nasa
  - dataset: free-text dataset name (will be slugified)
  - var: variable name (e.g., "u")
  - xyz: [x, y, z] OR "x,y,z"
  - window: [t0, t1, dt] OR "t0,t1,dt"
  - title: pulse title (single quotes recommended)
  - tags: list of tags
  - batch: optional int; appends -batchN to dataset for uniqueness

Produces:
  - results/fd_probe/<slug[-batchN]>.metrics.json
  - pulse/auto/YYYY-MM-DD_<slug[-batchN]>.yml
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from typing import Any, Dict, List

import yaml

# -------- helpers ----------------------------------------------------------

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def triplet_to_string(x: Any, name: str) -> str:
    """
    Accept list/tuple of len 3 OR a 'a,b,c' string; return canonical 'a,b,c' string.
    Raises ValueError if not 3 items.
    """
    if isinstance(x, (list, tuple)):
        if len(x) != 3:
            raise ValueError(f"{name} must have exactly 3 elements; got {x!r}")
        return ",".join(str(v) for v in x)
    if isinstance(x, str):
        parts = [p.strip() for p in x.split(",") if p.strip() != ""]
        if len(parts) != 3:
            raise ValueError(f"{name} must be a 3-value comma string 'a,b,c'; got {x!r}")
        return ",".join(parts)
    raise ValueError(f"{name} must be list/tuple of 3 or 'a,b,c' string; got {type(x)}")

def load_job(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Job YAML must be a mapping at the top level.")
    return data

# -------- main -------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="Path to job YAML")
    args = ap.parse_args()

    job = load_job(args.job)

    required = ["source", "dataset", "var", "xyz", "window", "title", "tags"]
    missing = [k for k in required if k not in job or job[k] is None]
    if missing:
        raise ValueError(f"Missing required job keys: {missing}")

    source = str(job["source"]).strip()
    dataset_raw = str(job["dataset"]).strip()
    var = str(job["var"]).strip()
    xyz_str = triplet_to_string(job["xyz"], "xyz")
    window_str = triplet_to_string(job["window"], "window")
    title = str(job["title"])
    tags = job["tags"]
    if isinstance(tags, str):
        tags_list = [t for t in re.split(r"\s+", tags.strip()) if t]
    elif isinstance(tags, list):
        tags_list = [str(t) for t in tags]
    else:
        raise ValueError("tags must be a list or space-separated string")

    slug = safe_slug(dataset_raw)

    # Optional batch to force uniqueness (YYYY-MM-DD_<slug>-batchN.yml)
    batch_suffix = ""
    if "batch" in job and job["batch"] is not None:
        try:
            b = int(job["batch"])
            if b > 0:
                batch_suffix = f"-batch{b}"
        except Exception:
            pass

    dataset_with_batch = slug + batch_suffix
    results_dir = os.path.join("results", "fd_probe")
    os.makedirs(results_dir, exist_ok=True)
    metrics_path = os.path.join(results_dir, f"{dataset_with_batch}.metrics.json")

    # Run the FD probe
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()  # so tools.* imports work in the subproc
    # pass through optional creds/secrets if present in environment
    for key in ["JHTDB_TOKEN", "JHTDB_OFFLINE", "NASA_CSV"]:
        if key in os.environ:
            env[key] = os.environ[key]

    probe_cmd: List[str] = [
        sys.executable, "tools/fd_connectors/run_fd_probe.py",
        "--source", source,
        "--dataset", slug,
        "--var", var,
        "--xyz", xyz_str,
        "--twin", window_str,
        "--json-out", metrics_path,
    ]
    print("Running:", " ".join(probe_cmd))
    subprocess.run(probe_cmd, check=True, env=env)

    # Emit the pulse
    make_cmd: List[str] = [
        sys.executable, "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics_path,
        "--title", title,
        "--dataset", dataset_with_batch,  # include -batchN in the pulse filename
        "--tags", " ".join(tags_list),
        "--outdir", "pulse/auto",
    ]
    print("Making pulse:", " ".join(make_cmd))
    subprocess.run(make_cmd, check=True, env=env)

    print("Done. Metrics →", metrics_path)

if __name__ == "__main__":
    main()
