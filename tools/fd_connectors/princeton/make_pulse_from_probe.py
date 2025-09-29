#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path

def next_batch_for(today: str, slug: str) -> int:
    root = Path("pulse/auto"); root.mkdir(parents=True, exist_ok=True)
    rx = re.compile(rf"^{re.escape(today)}_{re.escape(slug)}_batch(\d+)\.yml$")
    nums = [int(m.group(1)) for p in root.glob(f"{today}_{slug}_batch*.yml")
            if (m := rx.match(p.name))]
    return (max(nums) + 1) if nums else 1

def yamlq(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"

def resolve_analysis(args) -> Path:
    if args.analysis:
        return Path(args.analysis)
    # derive the default analysis path if only subset/slug were passed
    if not args.slug:
        raise SystemExit("When --analysis is omitted, --slug is required.")
    return Path(f"results/princeton/{args.slug}.analysis.json")

def main():
    ap = argparse.ArgumentParser(description="Build Φ-Mesh pulse from Princeton analysis JSON.")
    ap.add_argument("--analysis", help="results/princeton/<slug>.analysis.json")
    ap.add_argument("--subset", help="optional, for metadata note only")
    ap.add_argument("--probe",  help="optional, for metadata note only", default=None)
    ap.add_argument("--slug",   help="short slug for filename, e.g. 'princeton_subset'")
    args = ap.parse_args()

    analysis_path = resolve_analysis(args)
    if not analysis_path.exists():
        raise SystemExit(f"analysis JSON not found: {analysis_path}")

    with open(analysis_path, "r", encoding="utf-8") as fh:
        a = json.load(fh)

    comp   = a.get("component")
    f0     = float(a.get("dominant", {}).get("freq_hz") or 0.0)
    power  = float(a.get("dominant", {}).get("power")   or 0.0)
    nrows  = int(a.get("n") or 0)
    dt_s   = float(a.get("dt") or 0.0)
    dur    = nrows * dt_s if (nrows and dt_s) else 0.0
    note   = a.get("note") or ("no fundamental detected" if f0 <= 0 else "")

    slug = args.slug or Path(analysis_path).stem.replace(".analysis","")
    today = dt.date.today().isoformat()
    batch = next_batch_for(today, slug)

    # mirror metrics file name for convenience
    metrics_dir = Path("results/fd_probe"); metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_name = f"{today}_{slug}_batch{batch}.metrics.json"
    try:
        shutil.copyfile(analysis_path.as_posix(), (metrics_dir/metrics_name).as_posix())
    except Exception as e:
        print(f"[WARN] could not write metrics mirror: {e}")

    pulse_dir = Path("pulse/auto"); pulse_dir.mkdir(parents=True, exist_ok=True)
    pulse_name = f"{today}_{slug}_batch{batch}.yml"
    pulse_path = pulse_dir / pulse_name

    summary = (
        f"NT rhythm probe on '{slug}' — analysis: '{analysis_path.absolute()}'. "
        f"n={nrows}, dt={dt_s}, duration_s={dur:.4f}. "
        f"probe={args.probe or a.get('meta',{}).get('probe')}, subset={args.subset or a.get('meta',{}).get('subset_path')}. "
        f"hint: " + (f"dominant={comp}@{f0:.4f}Hz; power={power:.3g}" if f0 > 0 else "none")
    )

    y = []
    y.append(f"title: {yamlq('NT Rhythm — Princeton Probe')}")
    y.append("summary: >-")
    y.append(f"  {summary}")
    y.append("tags:")
    y.append("  - nt_rhythm")
    y.append("  - turbulence")
    y.append("  - navier_stokes")
    y.append("  - princeton_probe")
    y.append("  - rgp")
    y.append("papers:")
    y.append("  - https://doi.org/10.5281/zenodo.15830659")
    y.append("podcasts:")
    y.append("  - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a")

    pulse_path.write_text("\n".join(y) + "\n", encoding="utf-8")
    print(f"wrote pulse: {pulse_path}")

if __name__ == "__main__":
    main()
