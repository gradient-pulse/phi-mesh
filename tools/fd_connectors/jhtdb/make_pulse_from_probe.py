#!/usr/bin/env python3
"""
make_pulse_from_probe.py — emit a short Φ-Mesh pulse for a JHTDB probe run.

Inputs (same knobs you used to fetch/analyze), plus a *slug* that becomes the
human-stable stem for today’s pulse filename:

  pulse/auto/YYYY-MM-DD_<slug>_batchN.yml

This script:
  1) Locates the matching analysis JSON in results/fd_probe/ (pattern-based).
  2) Reads the dominant frequency + a few stats.
  3) Writes a compact pulse with a 'hint:' that surfaces the f0 clearly.
"""

from __future__ import annotations
import argparse, datetime as dt, json, pathlib, re
from typing import Optional

ROOT = pathlib.Path(".").resolve()
FD_RESULTS = ROOT / "results" / "fd_probe"
PULSE_DIR  = ROOT / "pulse" / "auto"
PULSE_DIR.mkdir(parents=True, exist_ok=True)

def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "isotropic"

def _today() -> str:
    return dt.date.today().isoformat()  # GH runners are UTC

def _next_batch(today: str, slug: str) -> int:
    patt = f"{today}_{slug}_batch"
    nums = []
    for p in sorted(PULSE_DIR.glob(f"{today}_{slug}_batch*.yml")):
        m = re.search(r"_batch(\d+)\.yml$", p.name)
        if m: nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

def _find_analysis(flow: str, x: float, y: float, z: float,
                   t0: float, dt: float, nsteps: int) -> Optional[pathlib.Path]:
    """
    We try the exact stem first (the analyze step used these literal values),
    then fall back to a wildcard on t0 to be tolerant to tiny formatting drifts.
    """
    # Exact stem first
    exact = FD_RESULTS / f"{flow}__x{x}_y{y}_z{z}__t{t0}_dt{dt}_n{nsteps}.analysis.json"
    if exact.exists():
        return exact

    # t0 can be formatted slightly differently depending on caller; try a wildcard
    patt = FD_RESULTS / f"{flow}__x{x}_y{y}_z{z}__t*_dt{dt}_n{nsteps}.analysis.json"
    matches = sorted(patt.parent.glob(patt.name))
    return matches[0] if matches else None

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow",   required=True)
    ap.add_argument("--x",      required=True, type=float)
    ap.add_argument("--y",      required=True, type=float)
    ap.add_argument("--z",      required=True, type=float)
    ap.add_argument("--t0",     required=True, type=float)
    ap.add_argument("--dt",     required=True, type=float)
    ap.add_argument("--nsteps", required=True, type=int)
    ap.add_argument("--slug",   required=False, default="isotropic")
    args = ap.parse_args()

    slug = slugify(args.slug)
    analysis = _find_analysis(args.flow, args.x, args.y, args.z, args.t0, args.dt, args.nsteps)
    if not analysis:
        raise SystemExit(f"[make_pulse] analysis JSON not found for "
                         f"{args.flow} @ ({args.x},{args.y},{args.z}) t0={args.t0} dt={args.dt} n={args.nsteps}")

    try:
        m = json.loads(analysis.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[make_pulse] failed to read analysis JSON {analysis}: {e}")

    # Pull a dominant frequency if present (we support both keys we’ve used)
    f0 = None
    if isinstance(m, dict):
        f0 = m.get("dominant_freq_hz")
        if f0 is None and isinstance(m.get("dominant"), dict):
            f0 = m["dominant"].get("freq_hz")
        try:
            if f0 is not None:
                f0 = float(f0)
        except Exception:
            f0 = None

    # Compose a tiny, readable pulse
    today = _today()
    batch = _next_batch(today, slug)
    pulse_path = PULSE_DIR / f"{today}_{slug}_batch{batch}.yml"

    hint = "no fundamental detected"
    if (f0 is not None) and (f0 > 0):
        hint = f"dominant≈{f0:.6g} Hz"

    pulse = {
        "title": "NT Rhythm — JHTDB Probe",
        "dataset": slug,
        "tags": ["nt_rhythm", "turbulence", "navier_stokes", "jhtdb"],
        "meta": {
            "flow": args.flow,
            "point": {"x": args.x, "y": args.y, "z": args.z},
            "t0": args.t0, "dt": args.dt, "nsteps": args.nsteps,
            "analysis_json": analysis.as_posix(),
        },
        "hint": hint,
    }

    pulse_yaml = (
        "title: " + pulse["title"] + "\n" +
        "dataset: " + pulse["dataset"] + "\n" +
        "tags:\n  - " + "\n  - ".join(pulse["tags"]) + "\n" +
        "meta:\n"
        f"  flow: {pulse['meta']['flow']}\n"
        f"  point: {{x: {args.x}, y: {args.y}, z: {args.z}}}\n"
        f"  t0: {args.t0}\n"
        f"  dt: {args.dt}\n"
        f"  nsteps: {args.nsteps}\n"
        f"  analysis_json: {analysis.as_posix()}\n"
        f"hint: {hint}\n"
    )

    pulse_path.write_text(pulse_yaml, encoding="utf-8")
    print(f"[make_pulse] wrote {pulse_path}  ← {analysis.name}  ({hint})")

if __name__ == "__main__":
    main()
