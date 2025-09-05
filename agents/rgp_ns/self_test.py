#!/usr/bin/env python3
"""
agents/rgp_ns/self_test.py

Run the RGP–NS agent on a tiny synthetic config and assert:
- results dir created
- metrics.json exists & is readable
- (best-effort) n_events >= min_events, ratio_CV <= max_ratio_cv when present
No repo writes/commits; this is a CI health check.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]  # repo root
AGENT_DIR = ROOT / "agents" / "rgp_ns"
CONFIG = AGENT_DIR / "self_test.yml"
RUNNER = AGENT_DIR / "run_agent.py"
RESULTS = ROOT / "results" / "rgp_ns"

def newest_stamp_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if not dirs:
        return None
    # prefer YYYYMMDD_HHMMSS-like names; otherwise fallback to mtime
    date_like = [p for p in dirs if re.search(r"\d{8}", p.name)]
    target = max(date_like or dirs, key=lambda p: p.stat().st_mtime)
    return target

def main() -> int:
    if not RUNNER.exists():
        print(f"ERROR: runner not found: {RUNNER}", file=sys.stderr)
        return 2
    if not CONFIG.exists():
        print(f"ERROR: config not found: {CONFIG}", file=sys.stderr)
        return 2

    # Load thresholds
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    min_events = int(cfg.get("criteria", {}).get("min_events", 8))
    max_ratio_cv = float(cfg.get("criteria", {}).get("max_ratio_cv", 0.5))

    # Run agent
    print("→ Running RGP–NS agent (synthetic smoke)…")
    cmd = [sys.executable, str(RUNNER), "--config", str(CONFIG)]
    print("  ", " ".join(cmd))
    try:
        subprocess.run(cmd, cwd=str(ROOT), check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: agent run failed with code {e.returncode}", file=sys.stderr)
        return 3

    # Allow filesystem to settle on CI
    time.sleep(0.5)

    # Locate newest results/<stamp>/batch1/
    stamp_dir = newest_stamp_dir(RESULTS)
    if stamp_dir is None:
        print(f"ERROR: no results created under {RESULTS}", file=sys.stderr)
        return 4
    batch1 = stamp_dir / "batch1"
    if not batch1.exists():
        # Some agents might number differently; scan for a batch* subdir
        batches = [p for p in stamp_dir.iterdir() if p.is_dir() and p.name.startswith("batch")]
        if batches:
            batch1 = sorted(batches)[0]
        else:
            print(f"ERROR: no batch* dir in {stamp_dir}", file=sys.stderr)
            return 4

    metrics_path = batch1 / "metrics.json"
    if not metrics_path.exists():
        print(f"ERROR: missing metrics.json at {metrics_path}", file=sys.stderr)
        return 5

    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: cannot read metrics.json: {e}", file=sys.stderr)
        return 5

    # Best-effort checks: tolerate key name variations
    n_events = (metrics.get("n_events") or
                metrics.get("n") or
                metrics.get("event_count"))
    ratio_cv = (metrics.get("ratio_CV") or
                metrics.get("ratio_cv") or
                metrics.get("cv_ratio"))

    ok = True
    if isinstance(n_events, (int, float)):
        if n_events < min_events:
            print(f"ERROR: n_events={n_events} < min_events={min_events}", file=sys.stderr)
            ok = False
        else:
            print(f"✓ events: {n_events} ≥ {min_events}")
    else:
        print("! n_events not present; skipping count gate")

    if isinstance(ratio_cv, (int, float)):
        if ratio_cv > max_ratio_cv:
            print(f"ERROR: ratio_CV={ratio_cv} > max_ratio_cv={max_ratio_cv}", file=sys.stderr)
            ok = False
        else:
            print(f"✓ ratio_CV: {ratio_cv} ≤ {max_ratio_cv}")
    else:
        print("! ratio_CV not present; skipping CV gate")

    if ok:
        print(f"SMOKE TEST PASS → {metrics_path}")
        return 0
    else:
        return 6

if __name__ == "__main__":
    sys.exit(main())
