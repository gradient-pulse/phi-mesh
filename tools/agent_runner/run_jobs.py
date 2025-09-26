#!/usr/bin/env python3
"""
run_jobs.py — batch FD jobs runner over CSV or JSONL.
- Uses short, human slugs for filenames.
- Reads f0 from metrics JSON.
- Emits a Pulse for each job and appends to the daily fundamentals JSONL.

CSV header:  source,dataset,var,xyz,twin,title,tags
JSONL keys:  source,dataset,var,xyz,twin,title,tags
"""

from __future__ import annotations
import argparse, csv, json, os, subprocess, sys, datetime as dt
from typing import Dict, Iterable, Tuple, List

# Reuse the same short-slug logic via a tiny internal helper import
# (duplicate small functions to keep file self-contained)
def _slug(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def _basename_no_ext(path_or_url: str) -> str:
    import os, re
    s = (path_or_url or "").split("#", 1)[0].split("?", 1)[0]
    base = os.path.basename(s.rstrip("/"))
    base = re.sub(r"\.(csv|json|txt|zip|xz|gz|bz2|tar)$", "", base, flags=re.I)
    return base

def _tidy_stem(stem: str) -> str:
    import re
    s = (stem or "").strip()
    s = re.sub(r"_(rows|timeseries|dataset|data)$", "", s, flags=re.I)
    return s

def short_slug_from_dataset(dataset: str) -> str:
    return _slug(_tidy_stem(_basename_no_ext(dataset)))

def today_str() -> str:
    return dt.date.today().isoformat()

def next_batch_for(today: str, base: str) -> int:
    from pathlib import Path
    import re as _re
    root = Path("results/fd_probe")
    root.mkdir(parents=True, exist_ok=True)
    paths = sorted(root.glob(f"{today}_{base}_batch*.metrics.json"))
    if not paths:
        return 1
    nums = []
    rx = _re.compile(r"_batch(\d+)\.metrics\.json$")
    for p in paths:
        m = rx.search(p.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

def parse_xyz(s: str) -> Tuple[float, float, float]:
    xs = [float(v) for v in s.split(",")]
    if len(xs) != 3:
        raise ValueError("xyz must be 'x,y,z'")
    return (xs[0], xs[1], xs[2])

# ---------- core single job --------------------------------------------------

def run_job(job: Dict[str, str]) -> float | None:
    source = job["source"]
    dataset = job["dataset"]
    var = job["var"]
    xyz = parse_xyz(job["xyz"])
    twin = job["twin"]
    title = job.get("title", "NT Rhythm — FD Probe")
    tags = job.get("tags", "nt_rhythm turbulence navier_stokes rgp")

    ds_slug = short_slug_from_dataset(dataset)
    base = f"{ds_slug}_{source.lower()}"
    today = today_str()
    batch = next_batch_for(today, base)

    metrics = f"results/fd_probe/{today}_{base}_batch{batch}.metrics.json"
    pulse_slug = f"{base}_batch{batch}"
    xyz_str = ",".join(map(str, xyz))

    # 1) probe
    cmd1 = [
        "python", "tools/fd_connectors/run_fd_probe.py",
        "--source", source, "--dataset", dataset, "--var", var,
        "--xyz", xyz_str, "--twin", twin, "--json-out", metrics,
        "--title", title, "--tags", tags,
    ]
    subprocess.run(cmd1, check=True)

    # 2) pulse
    recent = f"results/rgp_ns/{today}_fundamentals.jsonl"
    os.makedirs("results/rgp_ns", exist_ok=True)
    cmd2 = [
        "python", "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics, "--title", title,
        "--dataset", pulse_slug, "--tags", tags,
        "--outdir", "pulse/auto", "--recent", recent,
    ]
    subprocess.run(cmd2, check=True)

    # 3) read f0
    try:
        with open(metrics, "r", encoding="utf-8") as fh:
            m = json.load(fh)
        f0 = m.get("main_peak_freq")
        if f0 is None and isinstance(m.get("peaks"), list) and m["peaks"]:
            f0 = float(m["peaks"][0][0])
        return f0
    except Exception:
        return None

# ---------- IO loaders -------------------------------------------------------

def iter_csv(path: str) -> Iterable[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def iter_jsonl(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

# ---------- main -------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="CSV file with jobs")
    ap.add_argument("--jsonl", help="JSONL file with jobs")
    args = ap.parse_args()

    if not args.csv and not args.jsonl:
        print("Provide --csv or --jsonl", file=sys.stderr)
        raise SystemExit(2)

    it = iter_csv(args.csv) if args.csv else iter_jsonl(args.jsonl)

    for i, job in enumerate(it, 1):
        try:
            f0 = run_job(job)
            print(f"[run_jobs] {i}: f0={f0}")
        except subprocess.CalledProcessError as e:
            print(f"[run_jobs] WARN: job {i} failed: {e}")

if __name__ == "__main__":
    import sys
    main()
