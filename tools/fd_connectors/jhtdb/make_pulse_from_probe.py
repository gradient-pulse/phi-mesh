#!/usr/bin/env python3
"""
make_pulse_from_probe.py — build a Φ-Mesh pulse from probe meta+analysis.

Inputs
------
--flow   JHTDB dataset name (for metadata only)
--x --y --z  Probe coordinates (for metadata only)
--t0 --dt --nsteps  Window info (for metadata only)
--slug  REQUIRED: short identifier; output pulse will be pulse/auto/<slug>.yml

What it does
------------
- Reads the most recent matching meta+analysis produced by the loader/analyzer
  (we re-locate them from the standard names that the loader/analyzer write).
- Writes pulse to pulse/auto/<slug>.yml using dominant frequency from analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

PULSE_DIR = Path("pulse/auto")
PULSE_DIR.mkdir(parents=True, exist_ok=True)

def load_analysis(slug: str) -> Dict[str, Any]:
    """
    The workflow already writes analysis to results/fd_probe/<slug>.analysis.json.
    Prefer that if present (authoritative). Fallback is harmless.
    """
    p = Path("results/fd_probe") / f"{slug}.analysis.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # last resort: look for any analysis (won't happen in the new workflow)
    cands = sorted(Path("results/fd_probe").glob("*.analysis.json"))
    if not cands:
        raise FileNotFoundError("No analysis JSON found in results/fd_probe/")
    return json.loads(cands[-1].read_text(encoding="utf-8"))

def build_pulse(slug: str, analysis: Dict[str, Any], meta: Dict[str, Any]) -> str:
    f0 = float(analysis.get("dominant_freq_hz") or 0.0)
    hint = f"fundamental_hz={f0:.6g}" if f0 > 0 else "no_dominant_frequency"

    pulse = {
        "title": "NT Rhythm — FD Probe",
        "dataset": slug,
        "tags": ["nt_rhythm", "turbulence", "navier_stokes", "rgp"],
        "hint": hint,
        "meta": {
            "flow": meta.get("flow"),
            "point": meta.get("point"),
            "t0": meta.get("t0"),
            "dt": meta.get("dt"),
            "nsteps": meta.get("nsteps"),
        },
        "analysis": {
            "n": analysis.get("n"),
            "dt": analysis.get("dt"),
            "dominant_freq_hz": analysis.get("dominant_freq_hz"),
            "components": analysis.get("components"),
        },
    }
    out_path = PULSE_DIR / f"{slug}.yml"
    # very small, readable YAML
    import yaml  # type: ignore
    out_path.write_text(yaml.safe_dump(pulse, sort_keys=False), encoding="utf-8")
    return out_path.as_posix()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--nsteps", type=int, required=True)
    ap.add_argument("--slug", required=True, help="Short identifier (also pulse filename)")
    args = ap.parse_args()

    # Assemble a tiny meta snapshot (we don’t depend on exact filenames)
    meta = {
        "flow": args.flow,
        "point": {"x": args.x, "y": args.y, "z": args.z},
        "t0": args.t0,
        "dt": args.dt,
        "nsteps": args.nsteps,
    }
    # Prefer the workflow-written analysis for the matching slug
    analysis = load_analysis(args.slug)
    out = build_pulse(args.slug, analysis, meta)
    print(f"Wrote pulse → {out}")

if __name__ == "__main__":
    main()
