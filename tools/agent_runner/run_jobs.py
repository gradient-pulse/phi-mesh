#!/usr/bin/env python3
"""
tools/agent_runner/run_jobs.py

Scan a folder for FD probe jobs (YAML), run each via tools/fd_connectors/run_fd_probe.py,
then emit a strict Φ-Mesh pulse via tools/agent_rhythm/make_pulse.py.

- Auto-sanitizes dataset to a safe slug.
- Auto-assigns batch numbers per (date, slug): _batch1, _batch2, ...
- Moves processed jobs to inbox/fd_jobs/_done/ (or _error/ on failure).

Job YAML shape (minimal):
  source: synthetic | jhtdb | nasa
  dataset: isotropic1024 | demo | ...
  var: u
  xyz: 0.1,0.1,0.1
  twin: 0,10,0.01
  title: "NT Rhythm — FD Probe"
  tags: "nt_rhythm turbulence navier_stokes rgp"
  nasa_csv: "https://..."   # optional (for NASA mode only)
"""

from __future__ import annotations
import argparse, datetime as dt, glob, json, os, re, shutil, subprocess, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]   # repo root

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def next_batch_id(pulse_dir: Path, today: str, base_slug: str) -> int:
    """
    Look for pulse files: pulse/auto/YYYY-MM-DD_<slug>_batchN.yml
    Return the next N (starting at 1).
    """
    pattern = str(pulse_dir / f"{today}_{base_slug}_batch*.yml")
    existing = list(glob.glob(pattern))
    if not existing:
        # also consider pre-existing file without batch suffix (legacy):
        legacy = pulse_dir / f"{today}_{base_slug}.yml"
        if legacy.exists():
            return 2
        return 1
    # extract highest N
    mx = 0
    for p in existing:
        m = re.search(r"_batch(\d+)\.yml$", p)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1 if mx > 0 else 1

def run(cmd: list[str], extra_env: dict[str,str] | None = None) -> None:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd)}")

def process_job(job_path: Path, metrics_dir: Path, pulse_dir: Path) -> None:
    data = yaml.safe_load(job_path.read_text(encoding="utf-8")) or {}
    source  = str(data.get("source", "")).strip()
    dataset = str(data.get("dataset", "")).strip()
    var     = str(data.get("var", "")).strip()
    xyz     = str(data.get("xyz", "")).strip()
    twin    = str(data.get("twin", "")).strip()
    title   = str(data.get("title", "NT Rhythm — FD Probe")).strip()
    tags    = str(data.get("tags", "nt_rhythm turbulence navier_stokes rgp")).strip()
    nasa_csv = str(data.get("nasa_csv", "")).strip()

    if source not in {"synthetic", "jhtdb", "nasa"}:
        raise SystemExit(f"Invalid source in {job_path}: {source!r}")

    base_slug = safe_slug(dataset)
    today = dt.date.today().isoformat()
    batch = next_batch_id(pulse_dir, today, base_slug)
    final_slug = f"{base_slug}_batch{batch}"

    metrics_dir.mkdir(parents=True, exist_ok=True)
    pulse_dir.mkdir(parents=True, exist_ok=True)

    # Build metrics path
    metrics_out = metrics_dir / f"{today}_{final_slug}.metrics.json"

    # Env for NASA CSV (if provided)
    extra_env = {}
    if source == "nasa" and nasa_csv:
        extra_env["NASA_CSV"] = nasa_csv

    # 1) FD probe → metrics
    run([
        sys.executable, "tools/fd_connectors/run_fd_probe.py",
        "--source", source,
        "--dataset", base_slug,          # probe uses base slug (batch applied at pulse)
        "--var", var,
        "--xyz", xyz,
        "--twin", twin,
        "--json-out", str(metrics_out),
    ], extra_env=extra_env)

    # 2) metrics → pulse (apply batch in dataset for filename)
    run([
        sys.executable, "tools/agent_rhythm/make_pulse.py",
        "--metrics", str(metrics_out),
        "--title", title,
        "--dataset", final_slug,         # <- ensures _batchN in pulse filename
        "--tags", tags,
        "--outdir", str(pulse_dir),
    ])

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="inbox/fd_jobs/*.yml", help="Job glob")
    ap.add_argument("--metrics-dir", default="results/fd_probe", help="Where to write metrics JSON")
    ap.add_argument("--pulse-dir", default="pulse/auto", help="Where to write pulses")
    args = ap.parse_args()

    job_paths = sorted(Path(".").glob(args.glob))
    if not job_paths:
        print("No jobs found; nothing to do.")
        return

    metrics_dir = Path(args.metrics_dir)
    pulse_dir = Path(args.pulse_dir)

    done_dir = Path("inbox/fd_jobs/_done")
    err_dir  = Path("inbox/fd_jobs/_error")
    done_dir.mkdir(parents=True, exist_ok=True)
    err_dir.mkdir(parents=True, exist_ok=True)

    for jp in job_paths:
        try:
            print(f"Processing job: {jp}")
            process_job(jp, metrics_dir, pulse_dir)
            stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.move(str(jp), str(done_dir / f"{stamp}__{jp.name}"))
        except SystemExit as e:
            sys.stderr.write(f"[ERROR] {jp}: {e}\n")
            stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.move(str(jp), str(err_dir / f"{stamp}__{jp.name}"))

if __name__ == "__main__":
    main()
