#!/usr/bin/env python3
"""
make_pulse_from_probe.py
Create a Φ-Mesh pulse from a single JHTDB probe analysis JSON.

Inputs (match loader/analyzer):
  --flow     JHTDB dataset slug (e.g., isotropic1024coarse)
  --x --y --z  probe coordinates
  --t0 --dt --nsteps  time window / sampling
  --slug     short dataset label to appear in filename (default: 'isotropic')

Outputs:
  pulse/auto/YYYY-MM-DD_<slug>_batchN.yml
Schema (strict):
  title: '...'
  summary: >-
    ...
  tags:
    - nt_rhythm
    - turbulence
    - navier_stokes
    - rgp
  papers:
    - https://doi.org/10.5281/zenodo.15830659
  podcasts:
    - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a
"""

from __future__ import annotations
import argparse, json, os
from pathlib import Path
from datetime import date


def _stem(flow: str, x: float, y: float, z: float, t0: float, dt: float, n: int) -> str:
    # Mirrors analyzer/loader naming (round xyz for tidy filenames; keep dt exact text)
    def r3(v: float) -> str:
        s = f"{v:.3f}"
        s = s.rstrip("0").rstrip(".") if "." in s else s
        return s
    return f"{flow}__x{r3(x)}_y{r3(y)}_z{r3(z)}__t{r3(t0)}_dt{dt}_n{n}"


def _next_batch(outdir: Path, slug: str) -> int:
    today = date.today().isoformat()
    prefix = f"{today}_{slug}_batch"
    nums = []
    if outdir.exists():
        for p in outdir.glob(f"{today}_{slug}_batch*.yml"):
            name = p.stem
            try:
                n = int(name.split("batch", 1)[1])
                nums.append(n)
            except Exception:
                pass
    return (max(nums) + 1) if nums else 1


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

    # Locate analysis JSON produced by analyze_probe.py
    stem = _stem(args.flow, args.x, args.y, args.z, args.t0, args.dt, args.nsteps)
    analysis_rel = f"results/fd_probe/{stem}.analysis.json"
    analysis_abs = Path(analysis_rel).resolve()

    dominant = {"component": None, "freq_hz": 0.0, "power": 0.0}
    try:
        with open(analysis_rel, "r", encoding="utf-8") as fh:
            a = json.load(fh)
        # tolerate missing keys
        dom = a.get("dominant") or {}
        dominant["component"] = dom.get("component")
        dominant["freq_hz"] = float(dom.get("freq_hz") or 0.0)
        dominant["power"] = float(dom.get("power") or 0.0)
    except Exception:
        # keep defaults; pulse will say no fundamental detected
        pass

    # Compose title (YAML single-quoted; escape internal single quotes by doubling)
    title = "NT Rhythm — FD Probe"
    safe_title = title.replace("'", "''")

    # Human hint
    if dominant["freq_hz"] > 0.0:
        hint = f"fundamental detected — f0≈{dominant['freq_hz']:.4g} Hz (comp={dominant['component'] or 'n/a'})"
    else:
        hint = "no fundamental detected"

    # Meta line for summary (include probe & window like your canonical pulses)
    meta = {
        "dataset": args.flow,
        "var": "u",  # loader/analyzer use u/v/w; if you prefer 'v' here, tweak.
        "xyz": [args.x, args.y, args.z],
        "window": [args.t0, args.t0 + args.dt * max(args.nsteps - 1, 0), args.dt],
    }

    # Summary (folded style >- ; single line for each sentence)
    # Escape any single quotes in embedded strings by doubling (YAML single-quoted)
    ds_label = f"{args.slug}"
    safe_hint = hint.replace("'", "''")
    # Put meta compactly
    meta_str = (
        f"{{'dataset': '{args.flow}', 'var': 'u', "
        f"'xyz': [{args.x}, {args.y}, {args.z}], "
        f"'window': [{args.t0}, {args.t0 + args.dt * max(args.nsteps - 1, 0)}, {args.dt}]}}"
    ).replace("'", "''")

    # Build YAML
    outdir = Path("pulse/auto")
    outdir.mkdir(parents=True, exist_ok=True)
    batch = _next_batch(outdir, args.slug)
    outfile = outdir / f"{date.today().isoformat()}_{args.slug}_batch{batch}.yml"

    yaml_lines = []
    yaml_lines.append(f"title: '{safe_title}'")
    yaml_lines.append("summary: >-")
    yaml_lines.append(
        f"  NT rhythm probe on '{ds_label}' — "
        f"analysis: '{analysis_abs}'. "
        f"Source: jhtdb. Probe: {meta_str}. "
        f"hint: {safe_hint}"
    )
    yaml_lines.append("tags:")
    yaml_lines.append("  - nt_rhythm")
    yaml_lines.append("  - turbulence")
    yaml_lines.append("  - navier_stokes")
    yaml_lines.append("  - rgp")
    yaml_lines.append("papers:")
    yaml_lines.append("  - https://doi.org/10.5281/zenodo.15830659")
    yaml_lines.append("podcasts:")
    yaml_lines.append("  - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a")
    yaml = "\n".join(yaml_lines) + "\n"

    with open(outfile, "w", encoding="utf-8") as fh:
        fh.write(yaml)

    print(f"wrote pulse: {outfile}")


if __name__ == "__main__":
    main()
