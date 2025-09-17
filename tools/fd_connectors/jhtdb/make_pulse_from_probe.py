#!/usr/bin/env python3
"""
Make a *strict* pulse YAML (minimal fields only) from JHTDB probe meta+analysis.

Outputs to pulse/YYYY-MM-DD_jhtdb-probe_x_y_z[__batchN].yml
Fields included ONLY:
  - title
  - summary
  - tags
  - papers
  - podcasts
"""

import argparse, json
from pathlib import Path
from datetime import date
import yaml


def roundish(x, nd=4):
    try:
        return round(float(x), nd)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--outdir", default="pulse")
    ap.add_argument("--date", default=str(date.today()))
    ap.add_argument("--batch", type=int, default=None)  # only for human-readable title/filename
    args = ap.parse_args()

    meta = json.loads(Path(args.meta).read_text())
    ana  = json.loads(Path(args.analysis).read_text())

    flow = meta.get("flow") or meta.get("dataset") or "unknown_flow"
    pt   = meta.get("point") or {}
    x, y, z = pt.get("x"), pt.get("y"), pt.get("z")
    dt      = meta.get("dt") or ana.get("dt")
    nsteps  = meta.get("nsteps") or ana.get("nsteps")
    fdom    = roundish(ana.get("dominant_freq_hz"))
    period  = roundish(ana.get("approx_period_s"))
    hint    = (ana.get("hint") or "").strip()

    # ---- title (batch number only in human-facing title) ----
    if args.batch is not None:
        title = f"NT Rhythm — FD Probe (batch {args.batch})"
        batch_suffix = f"__batch{args.batch}"
    else:
        title = "NT Rhythm — FD Probe"
        batch_suffix = ""

    # ---- summary (concise, no quotes required) ----
    bits = [
        f'probe on "{flow}"',
        f"n={nsteps}",
        f"dt={dt}",
        f"xyz=({x}, {y}, {z})",
    ]
    if fdom and fdom > 0:
        b2 = f"dominant_freq_hz≈{fdom}"
        if period:
            b2 += f" (~{period}s)"
        bits.append(b2)
    else:
        bits.append("dominant_freq_hz≈0")
    if hint:
        bits.append(f"hint: {hint}")
    summary = " — ".join(bits)

    # ---- strict pulse object ----
    pulse = {
        "title": title,
        "summary": summary,
        "tags": ["navier_stokes", "turbulence", "nt_rhythm", "rgp", "experiments"],
        "papers": [],
        "podcasts": [],
    }

    # ---- write ----
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = f"{args.date}_jhtdb-probe_{x}_{y}_{z}{batch_suffix}.yml"
    path = outdir / fname

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(pulse, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote strict pulse: {path}")


if __name__ == "__main__":
    main()
