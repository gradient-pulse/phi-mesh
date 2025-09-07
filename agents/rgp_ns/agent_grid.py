#!/usr/bin/env python3
"""
RGP–NS Agent Grid Runner
- Fans out small spatial offsets around a seed xyz.
- For each probe: run fd_probe -> make_pulse (with --recent) -> parse fundamental_hz.
- Stops early when at least k fundamentals agree within tol (relative).
- Writes normal metrics + pulses and appends fundamentals to results/rgp_ns/<YYYY-MM-DD>_fundamentals.jsonl.
"""

from __future__ import annotations
import argparse, datetime as dt, json, os, pathlib, re, subprocess, sys
from typing import Iterable, List, Tuple

# ---------- utils ------------------------------------------------------------

def slugify(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def today_str() -> str:
    return dt.date.today().isoformat()  # UTC on GH runners

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

def run_one(
    source: str, dataset: str, var: str,
    xyz: Tuple[float, float, float],
    twin: str, title: str, tags: str
) -> Tuple[float | None, str]:
    """
    Returns (f0, metrics_path). Also emits the pulse and appends f0 to the daily JSONL if present.
    """
    # naming (mirror your workflow)
    base = f"{slugify(dataset)}_{source.lower()}"
    today = today_str()
    batch = next_batch_for(today, base)

    metrics = f"results/fd_probe/{today}_{base}_batch{batch}.metrics.json"
    pulse_slug = f"{base}_batch{batch}"
    xyz_str = ",".join(map(str, xyz))

    # 1) run fd probe to produce metrics
    cmd1 = [
        "python", "tools/fd_connectors/run_fd_probe.py",
        "--source", source, "--dataset", dataset, "--var", var,
        "--xyz", xyz_str, "--twin", twin, "--json-out", metrics,
        "--title", title, "--tags", tags,
    ]
    subprocess.run(cmd1, check=True)

    # 2) emit pulse & capture fundamental_hz from stdout
    recent = f"results/rgp_ns/{today}_fundamentals.jsonl"
    os.makedirs("results/rgp_ns", exist_ok=True)
    cmd2 = [
        "python", "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics, "--title", title,
        "--dataset", pulse_slug, "--tags", tags,
        "--outdir", "pulse/auto", "--recent", recent,
    ]
    out = subprocess.run(cmd2, check=True, capture_output=True, text=True).stdout
    m = re.search(r"fundamental_hz=([0-9.]+)", out)
    f0 = float(m.group(1)) if m else None
    if f0 is not None:
        with open(recent, "a", encoding="utf-8") as fh:
            fh.write(f"{f0}\n")
    return f0, metrics

def parse_xyz(s: str) -> Tuple[float, float, float]:
    xs = [float(v) for v in s.split(",")]
    if len(xs) != 3:
        raise ValueError("xyz must be 'x,y,z'")
    return (xs[0], xs[1], xs[2])

def parse_offsets(s: str) -> List[Tuple[float, float, float]]:
    """
    Offsets are a ; separated list of triplets, each triplet comma-separated.
    Example: "0,0,0; 0.02,0,0; 0,0.02,0; 0,0,0.02; -0.02,0,0"
    """
    out: List[Tuple[float, float, float]] = []
    s = s.strip()
    if not s:
        return [(0.0, 0.0, 0.0)]
    for chunk in s.split(";"):
        vals = [float(v) for v in chunk.strip().split(",")]
        if len(vals) != 3:
            raise ValueError(f"Bad offset triplet: {chunk}")
        out.append((vals[0], vals[1], vals[2]))
    return out

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def add(xyz: Tuple[float, float, float], d: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (clamp01(xyz[0] + d[0]), clamp01(xyz[1] + d[1]), clamp01(xyz[2] + d[2]))

def best_agreement(f0s: List[float], tol: float) -> Tuple[float | None, int]:
    """
    Returns (center_frequency, inlier_count) under relative tolerance 'tol'.
    """
    if not f0s:
        return None, 0
    best_count, best_center = 0, None
    for i, f in enumerate(f0s):
        if f <= 0:
            continue
        count = sum(1 for g in f0s if g > 0 and abs(g - f) <= tol * f)
        if count > best_count:
            best_count, best_center = count, f
    return best_center, best_count

# ---------- main -------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="RGP–NS agent grid runner")
    ap.add_argument("--source", default="jhtdb", help="synthetic | jhtdb | nasa")
    ap.add_argument("--dataset", default="isotropic1024coarse")
    ap.add_argument("--var", default="u")
    ap.add_argument("--seed_xyz", default="0.1,0.1,0.1")
    ap.add_argument("--offsets", default="0,0,0; 0.02,0,0; 0,0.02,0; 0,0,0.02; -0.02,0,0; 0,-0.02,0; 0,0,-0.02",
                    help="; separated list of dx,dy,dz triplets")
    ap.add_argument("--twin", default="0.0,1.2,0.0001", help="time window t0,t1,dt")
    ap.add_argument("--title", default="NT Rhythm — FD Probe")
    ap.add_argument("--tags", default="nt_rhythm turbulence navier_stokes rgp")
    ap.add_argument("--k", type=int, default=5, help="stop when at least k agree")
    ap.add_argument("--tol", type=float, default=0.05, help="relative tolerance for agreement")
    ap.add_argument("--nmax", type=int, default=9, help="maximum number of probes")
    args = ap.parse_args()

    seed = parse_xyz(args.seed_xyz)
    offsets = parse_offsets(args.offsets)

    tried = 0
    f0s: List[float] = []
    print(f"[agent] starting grid from seed {seed} with {len(offsets)} offsets; k={args.k}, tol={args.tol}, nmax={args.nmax}")
    for off in offsets:
        if tried >= args.nmax:
            break
        xyz = add(seed, off)
        print(f"[agent] probe #{tried+1} @ xyz={xyz} twin={args.twin}")
        try:
            f0, _ = run_one(
                source=args.source, dataset=args.dataset, var=args.var,
                xyz=xyz, twin=args.twin, title=args.title, tags=args.tags
            )
        except subprocess.CalledProcessError as e:
            print(f"[agent] WARN: probe failed ({e}); continuing.")
            f0 = None
        if f0 is not None:
            f0s.append(f0)
            c, n_in = best_agreement(f0s, args.tol)
            print(f"[agent] fundamentals so far: {f0s} -> best={c} Hz with {n_in} inliers")
            if n_in >= args.k:
                print(f"[agent] decisive: k={args.k} inliers within {args.tol*100:.1f}% → fundamental≈{c} Hz")
                return
        tried += 1

    c, n_in = best_agreement(f0s, args.tol)
    if c is not None:
        print(f"[agent] finished n={tried}; best agreement≈{c} Hz with {n_in} inliers (k={args.k}).")
    else:
        print(f"[agent] finished n={tried}; insufficient signal.")

if __name__ == "__main__":
    main()
