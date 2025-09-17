#!/usr/bin/env python3
import argparse, json, os, re, yaml
from datetime import date
from pathlib import Path

def detect_batch(stem):
    m = re.search(r"__n(\d+)", stem)  # use nsteps as batch proxy if nothing else
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)       # path to .meta.json
    ap.add_argument("--analysis", required=True)   # path to .analysis.json
    ap.add_argument("--outdir", default="pulse/experiments")
    ap.add_argument("--date", default=str(date.today()))
    args = ap.parse_args()

    meta = json.loads(Path(args.meta).read_text())
    analysis = json.loads(Path(args.analysis).read_text())

    flow = meta["flow"]
    pt = meta["point"]
    dt = meta["dt"]
    nsteps = meta["nsteps"]
    batch = detect_batch(Path(args.meta).stem)

    title = f"NT Rhythm — FD Probe ({args.date})"
    tags = ["navier_stokes","turbulence","nt_rhythm","rgp","experiments"]

    summary = (
        f"NT rhythm probe on \"{flow}\" — n={nsteps}, dt={dt}. "
        f"Probe: xyz=({pt['x']}, {pt['y']}, {pt['z']}). "
        f"dominant_freq_hz≈{analysis.get('dominant_freq_hz',0):.4g}."
    )
    if batch is not None:
        summary += f" batch={batch}."

    # Links (relative repo paths)
    base = Path(args.meta).with_suffix("")  # …meta
    csv_gz = str(re.sub(r"\.meta$", "", str(base))).replace(".json","") + ".csv.gz"
    pulse = {
        "title": title,
        "date": args.date,
        "tags": tags,
        "summary": summary,
        "papers": [],
        "podcasts": [],
        "batch": batch,
        "links": [csv_gz, args.meta, args.analysis],
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    # filename carries date for sort fallback
    fn = outdir / f"{args.date}_jhtdb_probe_{pt['x']}_{pt['y']}_{pt['z']}.yml"
    with open(fn, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(pulse, f, sort_keys=False, allow_unicode=True)
    print(f"Wrote pulse: {fn}")

if __name__ == "__main__":
    main()
