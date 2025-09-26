#!/usr/bin/env python3
"""
Make a Φ-Mesh pulse from a Princeton probe analysis.

Inputs:
  --stem   princeton__<subset-stem>__probe<PROBE>      (used for file naming)
  --slug   short label for the batch/pulse name        (default: princeton)
  (expects results/fd_probe/<STEM>.analysis.json)

Outputs:
  pulse/auto/YYYY-MM-DD_<slug>_batchN.yml
  results/fd_probe/YYYY-MM-DD_<slug>_batchN.metrics.json  (copy of analysis)
"""

from __future__ import annotations
from pathlib import Path
import argparse, datetime as dt, json, shutil, re

def _next_batch(today: str, slug: str) -> int:
    root = Path("pulse/auto")
    root.mkdir(parents=True, exist_ok=True)
    rx = re.compile(rf"^{re.escape(today)}_{re.escape(slug)}_batch(\d+)\.yml$")
    nums = []
    for p in root.glob(f"{today}_{slug}_batch*.yml"):
        m = rx.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums)+1) if nums else 1

def _sq(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True, help="princeton__<subset-stem>__probe<PROBE>")
    ap.add_argument("--slug", default="princeton", help="short slug for pulse filename")
    args = ap.parse_args()

    analysis = Path(f"results/fd_probe/{args.stem}.analysis.json")
    if not analysis.exists():
        raise SystemExit(f"Analysis not found: {analysis}")

    try:
        a = json.loads(analysis.read_text(encoding="utf-8"))
    except Exception:
        a = {}

    comp = (a.get("dominant") or {}).get("component") or "u"
    f0   = float((a.get("dominant") or {}).get("freq") or (a.get("dominant") or {}).get("freq_hz") or 0.0)
    note = a.get("note") or ("no fundamental detected" if f0 <= 0 else "")

    hint_bits = []
    if f0 > 0:
        hint_bits.append(f"dominant={comp}@{f0:.4f}Hz")
    if note:
        hint_bits.append(note)
    hint = "; ".join(hint_bits) if hint_bits else "none"

    today = dt.date.today().isoformat()
    batch = _next_batch(today, args.slug)

    # Copy analysis to a dated "metrics" filename for easy linking
    metrics_dir = Path("results/fd_probe"); metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_name = f"{today}_{args.slug}_batch{batch}.metrics.json"
    metrics_path = metrics_dir / metrics_name
    try:
        shutil.copyfile(analysis.as_posix(), metrics_path.as_posix())
        print("copied analysis →", metrics_path)
    except Exception as e:
        print("[WARN] could not copy analysis to metrics name:", e)

    # Build the pulse YAML
    pulse_dir = Path("pulse/auto"); pulse_dir.mkdir(parents=True, exist_ok=True)
    pulse_name = f"{today}_{args.slug}_batch{batch}.yml"
    pulse_path = pulse_dir / pulse_name

    summary = (
        f"NT rhythm probe on '{args.slug}' — analysis: '{analysis.resolve().as_posix()}'. "
        f"Probe stem: {args.stem}. "
        f"hint: {hint}"
    )
    lines = []
    lines.append(f"title: {_sq('NT Rhythm — Princeton Probe')}")
    lines.append("summary: >-")
    lines.append(f"  {summary}")
    lines.append("tags:")
    lines.append("  - nt_rhythm")
    lines.append("  - turbulence")
    lines.append("  - navier_stokes")
    lines.append("  - rgp")
    lines.append("papers:")
    lines.append("  - https://doi.org/10.5281/zenodo.17183439   # Doom → Destiny & Departure (v1.1)")
    lines.append("  - https://doi.org/10.5281/zenodo.17185350   # RGP-Based LLMs (v1.0)")
    lines.append("podcasts:")
    lines.append("  - https://notebooklm.google.com/            # replace with specific artifact if available")
    pulse_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("✅ Wrote pulse:", pulse_path.as_posix())

if __name__ == "__main__":
    main()
