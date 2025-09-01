#!/usr/bin/env python3
"""
Read a metrics JSON from tools/agent_rhythm/cli.py and emit a pulse YAML file.
Usage:
  python tools/agent_rhythm/make_pulse.py \
    --metrics results/agent_rhythm/probe.metrics.json \
    --title "NT Rhythm — Probe" \
    --dataset probe \
    --tags "nt_rhythm turbulence navier_stokes rgp" \
    --outdir pulse/auto
"""

import argparse, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # Provided by the workflow (pyyaml)
except Exception as e:
    print("ERROR: pyyaml is required", file=sys.stderr)
    raise

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "pulse"

def load_metrics(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fmt_summary(m: dict) -> str:
    # cli.py should write these keys; we degrade gracefully if missing
    ticks_per_day = m.get("ticks_per_day")
    mean_dt_s     = m.get("mean_dt_s")
    std_dt_s      = m.get("std_dt_s")
    count         = m.get("count")
    bursts        = m.get("bursts")  # list of {'start': iso, 'end': iso, 'count': n}

    parts = []
    if count is not None:
        parts.append(f"observations: {count}")
    if ticks_per_day is not None:
        parts.append(f"ticks/day: {ticks_per_day:.2f}")
    if mean_dt_s is not None and std_dt_s is not None:
        parts.append(f"Δt mean±σ: {mean_dt_s:.1f}±{std_dt_s:.1f}s")
    if bursts:
        # Show up to two burst windows succinctly
        show = bursts[:2]
        burst_txt = "; ".join(
            f"{b.get('count','?')} ticks ({b.get('start','?')} → {b.get('end','?')})"
            for b in show
        )
        parts.append(f"bursts: {burst_txt}")

    msg = "NT rhythm probe — " + ", ".join(parts) if parts else "NT rhythm probe."
    return msg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--title",   required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--tags",    required=True, help="space-separated tags")
    ap.add_argument("--outdir",  required=True)
    args = ap.parse_args()

    metrics = load_metrics(args.metrics)
    summary = fmt_summary(metrics)

    # Date in ISO (UTC) for title/date; filename uses dataset + date
    now = datetime.now(timezone.utc)
    date_str = now.date().isoformat()

    yaml_obj = {
        "title": f"{args.title} — {date_str}",
        "summary": summary,
        "tags": args.tags.split(),
        "dataset": args.dataset,
        "metrics": metrics,  # keep the raw metrics for later analysis
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    fname = f"{slugify(args.dataset)}_{date_str}.yml"
    out_path = outdir / fname

    with open(out_path, "w", encoding="utf-8") as f:
        # Clean/minimal YAML
        yaml.safe_dump(yaml_obj, f, sort_keys=False, width=1000, allow_unicode=True)

    print(f"[make_pulse] wrote {out_path}")

if __name__ == "__main__":
    main()
