#!/usr/bin/env python3
"""
make_pulse_from_probe.py
Create a strict-format pulse YAML from a JHTDB probe run.

File name:  pulse/auto/YYYY-MM-DD_<slug>_batch<batch>.yml
Minimal fields: title, summary, tags, papers, podcasts

Slug is sanitized and truncated to max 32 chars.
Batch defaults to 1 when not provided.
"""

import argparse, json, re
from datetime import date
from pathlib import Path

PULSE_DIR = Path("pulse/auto")
DATA_DIR  = Path("data/jhtdb")
RESULTS_DIR = Path("results/fd_probe")

MAX_SLUG = 32

def canon_slug(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:MAX_SLUG] or "probe"

def find_artifacts(flow, x, y, z, t0, dt, nsteps, slug):
    # Compose the shared stem produced by jhtdb_loader/analyze
    # isotropic1024coarse__x0.1_y0.2_z0.3__t00.0_dt0.002_n2000
    def fnum(v):
        # preserve canonical formatting used earlier
        return str(v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
    stem = f"{flow}__x{fnum(x)}_y{fnum(y)}_z{fnum(z)}__t{fnum(t0)}_dt{fnum(dt)}_n{int(nsteps)}"
    csv  = next(DATA_DIR.glob(f"{stem}.csv.gz"), None)
    meta = next(DATA_DIR.glob(f"{stem}.meta.json"), None)
    anal = next(DATA_DIR.glob(f"{stem}.analysis.json"), None)
    return stem, csv, meta, anal

def load_dominant_freq(analysis_json):
    try:
        obj = json.loads(Path(analysis_json).read_text(encoding="utf-8"))
        return float(obj.get("dominant_freq_hz", 0.0))
    except Exception:
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--nsteps", type=int, required=True)
    ap.add_argument("--slug", default="isotropic")
    ap.add_argument("--batch", type=int, default=1)
    args = ap.parse_args()

    slug = canon_slug(args.slug)
    batch = max(1, int(args.batch))

    stem, csv, meta, anal = find_artifacts(
        args.flow, args.x, args.y, args.z, args.t0, args.dt, args.nsteps, slug
    )

    # Strict pulse file name
    today = date.today().isoformat()
    pulse_path = PULSE_DIR / f"{today}_{slug}_batch{batch}.yml"
    PULSE_DIR.mkdir(parents=True, exist_ok=True)

    # Minimal strict fields only
    dominant = load_dominant_freq(anal) if anal else 0.0
    title = f"NT Rhythm — FD Probe ({today})"
    summary = (
        f'NT rhythm probe on "{args.flow}" — n={args.nsteps}, dt={args.dt}. '
        f"Probe: xyz=({args.x}, {args.y}, {args.z}). "
        f"dominant_freq_hz≈{dominant:.2f}."
    )

    # Your requested canonical tags
    tags = ["navier_stokes", "turbulence", "nt_rhythm", "rgp", "experiments"]

    # Minimal required keys: papers/podcasts as lists (empty for now)
    yaml_text = (
        f"title: {title}\n"
        f"date: '{today}'\n"
        f"tags:\n" + "".join([f"  - {t}\n" for t in tags]) +
        f"summary: '{summary}'\n"
        f"papers: []\n"
        f"podcasts: []\n"
    )

    pulse_path.write_text(yaml_text, encoding="utf-8")
    print(f"✅ Wrote pulse: {pulse_path}")

if __name__ == "__main__":
    main()
