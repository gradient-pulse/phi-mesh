#!/usr/bin/env python3
"""
make_pulse_from_probe.py
------------------------
Build a standardized Φ-Mesh pulse from a probe analysis JSON. Also writes a
mirrored "metrics" file name so results and pulses align:

  pulse/auto/YYYY-MM-DD_<slug>_batchN.yml
  results/fd_probe/YYYY-MM-DD_<slug>_batchN.metrics.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path


def next_batch_for(today: str, slug: str) -> int:
    """Scan pulse/auto for today's pulses for this slug and return next batch number."""
    root = Path("pulse/auto")
    root.mkdir(parents=True, exist_ok=True)
    rx = re.compile(rf"^{re.escape(today)}_{re.escape(slug)}_batch(\d+)\.yml$")
    nums = []
    for p in root.glob(f"{today}_{slug}_batch*.yml"):
        m = rx.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def yaml_quote_single(s: str) -> str:
    """Wrap in single quotes and escape internal single quotes."""
    return "'" + str(s).replace("'", "''") + "'"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--nsteps", type=int, required=True)
    ap.add_argument("--slug", default="isotropic")
    args = ap.parse_args()

    # detect analysis JSON (named by the loader/analyzer stem)
    stem = f"{args.flow}__x{args.x}_y{args.y}_z{args.z}__t{args.t0}_dt{args.dt}_n{args.nsteps}"
    analysis = f"results/fd_probe/{stem}.analysis.json"
    analysis_abs = Path(analysis).absolute().as_posix()

    # read analysis
    try:
        with open(analysis, "r", encoding="utf-8") as fh:
            a = json.load(fh)
    except Exception:
        a = {}

    # meta for summary
    comp = a.get("dominant", {}).get("component")
    f0 = float(a.get("dominant", {}).get("freq_hz") or 0.0)
    power = float(a.get("dominant", {}).get("power") or 0.0)
    nrows = int(a.get("n") or 0)
    dt_s = float(a.get("dt") or args.dt or 0.0)
    duration = float(a.get("duration_s") or (args.nsteps * args.dt))
    note = a.get("note") or ("no fundamental detected" if f0 <= 0 else "")

    today = dt.date.today().isoformat()
    batch = next_batch_for(today, args.slug)

    # pulse path
    pulse_dir = Path("pulse/auto")
    pulse_dir.mkdir(parents=True, exist_ok=True)
    pulse_name = f"{today}_{args.slug}_batch{batch}.yml"
    pulse_path = pulse_dir / pulse_name

    # also copy the analysis JSON to a friendly "metrics" filename
    metrics_dir = Path("results/fd_probe")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_name = f"{today}_{args.slug}_batch{batch}.metrics.json"
    metrics_path = metrics_dir / metrics_name
    try:
        shutil.copyfile(analysis_abs, metrics_path.as_posix())
        print(f"copied analysis -> {metrics_path}")
    except Exception as e:
        print(f"[WARN] could not copy analysis to metrics name: {e}")

    # Build pulse YAML
    title = yaml_quote_single("NT Rhythm — FD Probe")

    probe_meta = {
        "flow": args.flow,
        "point": {"x": args.x, "y": args.y, "z": args.z},
        "t0": args.t0,
        "dt": args.dt,
        "nsteps": args.nsteps,
    }
    hint_bits = []
    if comp:
        hint_bits.append(f"dominant={comp}@{f0:.4f}Hz")
    if note:
        hint_bits.append(note)

    summary = (
        f"NT rhythm probe on '{args.slug}' — analysis: '{analysis_abs}'. "
        f"n={nrows}, dt={dt_s}, duration_s={duration:.4f}. "
        f"Probe: {probe_meta}. "
        f"hint: {'; '.join(hint_bits) if hint_bits else 'none'}"
    )

    yaml_lines = []
    yaml_lines.append(f"title: {title}")
    yaml_lines.append("summary: >-")
    yaml_lines.append(f"  {summary}")
    yaml_lines.append("tags:")
    yaml_lines.append("  - nt_rhythm")
    yaml_lines.append("  - turbulence")
    yaml_lines.append("  - navier_stokes")
    yaml_lines.append("  - rgp")
    yaml_lines.append("papers:")
    yaml_lines.append("  - https://doi.org/10.5281/zenodo.15830659")
    yaml_lines.append("podcasts:")
    yaml_lines.append("  - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a")

    pulse_path.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    print(f"wrote pulse: {pulse_path}")


if __name__ == "__main__":
    main()
