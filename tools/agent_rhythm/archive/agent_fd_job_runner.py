#!/usr/bin/env python3
"""
agent_fd_job_runner.py — run one or many FD probes (no grid logic).
- Short, human filenames derived from dataset basename (e.g., sine_0p8hz).
- Reads fundamental frequency from metrics JSON instead of stdout.
- Emits a Pulse via make_pulse.py and appends fundamentals JSONL.

Usage (single):
  python tools/agent_rhythm/agent_fd_job_runner.py \
    --source nasa \
    --dataset https://example.org/path/to/sine_0p8hz_timeseries.csv \
    --var v \
    --xyz 0.1,0.1,0.1 \
    --twin 0.0,4.0,0.002

Usage (multiple XYZ; semicolon-separated):
  --xyz-list "0.1,0.1,0.1; 0.12,0.1,0.1; 0.1,0.12,0.1"
"""

from __future__ import annotations
import argparse, json, os, pathlib, re, subprocess, datetime as dt
from typing import List, Tuple

# ---------- short-slug helpers ----------------------------------------------

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

# ---------- utils ------------------------------------------------------------

def today_str() -> str:
    return dt.date.today().isoformat()

def next_batch_for(today: str, base: str) -> int:
    root = pathlib.Path("results/fd_probe")
    root.mkdir(parents=True, exist_ok=True)
    paths = sorted(root.glob(f"{today}_{base}_batch*.metrics.json"))
    if not paths:
        return 1
    nums = []
    rx = re.compile(r"_batch(\d+)\.metrics\.json$")
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

def parse_xyz_list(s: str | None) -> List[Tuple[float, float, float]]:
    if not s:
        return []
    out: List[Tuple[float, float, float]] = []
    for chunk in s.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        out.append(parse_xyz(chunk))
    return out

# ---------- core -------------------------------------------------------------

def run_one_probe(source: str, dataset: str, var: str,
                  xyz: Tuple[float, float, float], twin: str,
                  title: str, tags: str) -> Tuple[float | None, str]:
    ds_slug = short_slug_from_dataset(dataset)
    base = f"{ds_slug}_{source.lower()}"
    today = today_str()
    batch = next_batch_for(today, base)

    metrics = f"results/fd_probe/{today}_{base}_batch{batch}.metrics.json"
    pulse_slug = f"{base}_batch{batch}"
    xyz_str = ",".join(map(str, xyz))

    # 1) run probe → metrics
    cmd1 = [
        "python", "tools/fd_connectors/run_fd_probe.py",
        "--source", source, "--dataset", dataset, "--var", var,
        "--xyz", xyz_str, "--twin", twin, "--json-out", metrics,
        "--title", title, "--tags", tags,
    ]
    subprocess.run(cmd1, check=True)

    # 2) emit pulse
    recent = f"results/rgp_ns/{today}_fundamentals.jsonl"
    os.makedirs("results/rgp_ns", exist_ok=True)
    cmd2 = [
        "python", "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics, "--title", title,
        "--dataset", pulse_slug, "--tags", tags,
        "--outdir", "pulse/auto", "--recent", recent,
    ]
    subprocess.run(cmd2, check=True)

    # 3) read f0 from metrics JSON
    try:
        with open(metrics, "r", encoding="utf-8") as fh:
            m = json.load(fh)
        f0 = m.get("main_peak_freq")
        if f0 is None and isinstance(m.get("peaks"), list) and m["peaks"]:
            f0 = float(m["peaks"][0][0])
    except Exception:
        f0 = None

    # convenience append
    if f0 is not None:
        try:
            with open(recent, "a", encoding="utf-8") as fh:
                fh.write(f"{f0}\n")
        except Exception:
            pass

    return f0, metrics

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="synthetic | jhtdb | nasa")
    ap.add_argument("--dataset", required=True, help="slug, path, or URL")
    ap.add_argument("--var", required=True)
    ap.add_argument("--xyz", default="", help="single xyz triplet x,y,z")
    ap.add_argument("--xyz-list", default="", help="semicolon-separated list of triplets")
    ap.add_argument("--twin", required=True, help="t0,t1,dt")
    ap.add_argument("--title", default="NT Rhythm — FD Probe")
    ap.add_argument("--tags", default="nt_rhythm turbulence navier_stokes rgp")
    args = ap.parse_args()

    jobs = parse_xyz_list(args.xyz_list) or ([parse_xyz(args.xyz)] if args.xyz else [])
    if not jobs:
        raise SystemExit("Provide --xyz or --xyz-list")

    for i, xyz in enumerate(jobs, 1):
        print(f"[runner] {i}/{len(jobs)} @ xyz={xyz}")
        try:
            f0, met = run_one_probe(args.source, args.dataset, args.var, xyz, args.twin, args.title, args.tags)
            print(f"[runner] f0={f0} from {met}")
        except subprocess.CalledProcessError as e:
            print(f"[runner] WARN: probe failed ({e}); continuing.")

if __name__ == "__main__":
    main()
