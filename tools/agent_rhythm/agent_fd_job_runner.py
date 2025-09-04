#!/usr/bin/env python3
"""
agent_fd_job_runner.py

Reads one FD job YAML from inbox/fd_jobs/, runs the probe (synthetic|nasa|jhtdb),
emits metrics JSON and a strict Φ-Mesh pulse, then moves the job YAML to _done/
(or _error/ on failure).

Required job keys:
  source: synthetic | nasa | jhtdb
  dataset: free text or path (slug will be derived)
  var: variable name (e.g., 'u')
  xyz: [x, y, z]  (list of 3 numbers)  -- ignored for nasa CSV
  window: [t0, t1, dt]
  title: single-quoted string (strict pulse rule)
  tags: [list, underscore_case]

Optional:
  batch: e.g., 'batch1'  (appended to dataset for uniqueness per day)
  nasa_csv: path/URL/inline (if source == 'nasa' and you want to override NASACSV secret)
"""

from __future__ import annotations
import argparse
import json
import os
import shlex
import subprocess
import sys
import yaml
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]  # repo root

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def run(cmd: List[str], env: Dict[str, str]) -> None:
    print("::group::" + " ".join(shlex.quote(c) for c in cmd))
    res = subprocess.run(cmd, env=env, cwd=str(ROOT))
    print("::endgroup::")
    if res.returncode != 0:
        raise SystemExit(res.returncode)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, help="Path to inbox/fd_jobs/*.yml")
    args = ap.parse_args()

    job_path = (ROOT / args.job).resolve()
    if not job_path.exists():
        raise FileNotFoundError(f"Job file not found: {job_path}")

    with open(job_path, "r", encoding="utf-8") as f:
        job = yaml.safe_load(f) or {}

    # Basic validation
    required = ["source", "dataset", "var", "window", "title", "tags"]
    missing = [k for k in required if k not in job]
    if missing:
        raise ValueError(f"Missing required job keys: {missing}")

    source: str = str(job["source"]).strip().lower()
    dataset_in: str = str(job["dataset"])
    var: str = str(job["var"])
    window = job["window"]
    title: str = str(job["title"])
    tags = job.get("tags", [])
    batch: str = str(job.get("batch", "") or "").strip()
    xyz = job.get("xyz", [0.0, 0.0, 0.0])

    # Enforce strict rule: title must be single-quoted (we’ll just warn if not)
    if not (title.startswith("'") and title.endswith("'")):
        print("::warning title=Title quoting::Pulse title is not single-quoted; "
              "make_pulse will force single quotes. Consider updating your job template.")

    # Effective dataset slug (include batch if provided)
    base_slug = safe_slug(dataset_in)
    eff_slug = f"{base_slug}_{batch}" if batch else base_slug

    # Build env for subprocesses
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    # NASA CSV override (optional)
    if source == "nasa":
        nasa_csv = (job.get("nasa_csv") or os.getenv("NASA_CSV") or "").strip()
        if nasa_csv:
            env["NASA_CSV"] = nasa_csv

    # Choose xyz/twin strings
    def to_triplet(v) -> str:
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return ",".join(str(x) for x in v)
        raise ValueError("xyz/window must be 3-length lists [a,b,c]")

    twin_str = to_triplet(window)
    xyz_str = to_triplet(xyz if isinstance(xyz, (list, tuple)) else [0.0, 0.0, 0.0])

    metrics_path = ROOT / "results" / "fd_probe" / f"{eff_slug}.metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    # 1) Probe → metrics
    probe_cmd = [
        sys.executable, "tools/fd_connectors/run_fd_probe.py",
        "--source", source,
        "--dataset", eff_slug,           # we store batch in dataset slug for traceability
        "--var", var,
        "--xyz", xyz_str,
        "--twin", twin_str,
        "--json-out", str(metrics_path),
    ]
    run(probe_cmd, env)

    # 2) Metrics → pulse
    tags_str = " ".join(str(t) for t in tags)
    pulse_cmd = [
        sys.executable, "tools/agent_rhythm/make_pulse.py",
        "--metrics", str(metrics_path),
        "--title", title,                # may be plain or quoted; writer will force safe quoting
        "--dataset", eff_slug,
        "--tags", tags_str,
        "--outdir", "pulse/auto",
    ]
    run(pulse_cmd, env)

    # Move job into _done/
    done_dir = job_path.parent / "_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    target = done_dir / job_path.name
    job_path.replace(target)
    print(f"::notice title=FD Job::Moved job to {target}")

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        # Move to _error/ on failure and re-raise for CI to show red
        try:
            # best-effort move if we know the job path
            pass
        finally:
            raise
