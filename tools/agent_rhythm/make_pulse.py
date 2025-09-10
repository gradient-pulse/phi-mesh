#!/usr/bin/env python3
"""
make_pulse.py — turn a metrics JSON into a single Pulse YAML + update “recent” JSONL.

Usage:
  --metrics  path/to/*.metrics.json   (required)
  --title    "NT Rhythm — FD Probe"   (required)
  --dataset  slug-like dataset name   (required)
  --tags     "a b c" or "a, b, c"     (optional)
  --outdir   pulse/auto                (default)
  --recent   results/rgp_ns/YYYY-MM-DD_fundamentals.jsonl  (optional)
"""

from __future__ import annotations
import argparse, json, os, sys, datetime, re
from typing import Any, Dict, List, Tuple

def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def _as_list(s: str) -> List[str]:
    if not s:
        return []
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return [x.strip() for x in s.split() if x.strip()]

def compute_ladder_and_dominance(metrics: Dict[str, Any]) -> Tuple[int, float]:
    peaks = metrics.get("peaks") or []
    # peaks expected as [[f0,p0],[f1,p1],...]
    ladder = 0
    dom = 1.0
    if isinstance(peaks, list) and peaks:
        ladder = len(peaks)
        try:
            p0 = float(peaks[0][1])
            p1 = float(peaks[1][1]) if len(peaks) > 1 else 0.0
            dom = (p0 / p1) if p1 > 0 else float("inf") if p0 > 0 else 1.0
        except Exception:
            dom = 1.0
    return ladder, dom

def classify(ladder: int, dominance: float) -> str:
    if ladder >= 3 and dominance >= 1.5:
        return "Strong"
    if ladder >= 2 and dominance >= 1.1:
        return "Suggestive"
    return "Inconclusive"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--outdir", default="pulse/auto")
    ap.add_argument("--recent", default="")
    args = ap.parse_args()

    # Read metrics JSON
    m = _read_json(args.metrics)

    # Defensive pulls
    period = m.get("period")
    f0 = m.get("main_peak_freq")
    if f0 is None and isinstance(m.get("peaks"), list) and m["peaks"]:
        try:
            f0 = float(m["peaks"][0][0])
        except Exception:
            f0 = None

    ladder, dominance = compute_ladder_and_dominance(m)
    status = classify(ladder, dominance)

    # Build pulse YAML text (minimal, robust)
    today = datetime.date.today().isoformat()
    ds_slug = _slug(args.dataset)
    tags = _as_list(args.tags)
    # Always include core tags
    for core in ["nt_rhythm", "turbulence", "navier_stokes", "rgp"]:
        if core not in tags:
            tags.append(core)

    yaml_lines = []
    yaml_lines.append(f"title: \"{args.title}\"")
    yaml_lines.append("summary: >-")
    yaml_lines.append(f"  Metrics: period={period!r}, f0={f0!r}, ladder={ladder}, dominance={dominance:.3g}.")
    yaml_lines.append(f"  Status: {status}. Dataset: {args.dataset}.")
    yaml_lines.append("tags:")
    for t in tags:
        yaml_lines.append(f"  - {t}")
    yaml_lines.append("papers: []")
    yaml_lines.append("podcasts: []")
    yaml_lines.append("artifacts:")
    yaml_lines.append(f"  metrics_json: {args.metrics}")
    yaml_lines.append(f"  source: {m.get('source','unknown')}")
    if "details" in m:
        yaml_lines.append("details:")
        for k, v in m["details"].items():
            yaml_lines.append(f"  {k}: {v}")

    # Write pulse YAML
    _ensure_dir(args.outdir)
    out_name = f"{today}_{ds_slug}.yml"
    out_path = os.path.join(args.outdir, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")
    print(f"Wrote Pulse → {out_path}")

    # Append a fundamentals line (non-fatal)
    if args.recent:
        try:
            _ensure_dir(os.path.dirname(args.recent) or ".")
            line = {
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
                "dataset": args.dataset,
                "status": status,
                "ladder": ladder,
                "dominance": dominance,
                "period": period,
                "f0": f0,
                "metrics": args.metrics,
                "pulse": out_path,
            }
            with open(args.recent, "a", encoding="utf-8") as f:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
            print(f"Appended fundamentals → {args.recent}")
        except Exception as e:
            print(f"[make_pulse] WARN: could not append to recent: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
