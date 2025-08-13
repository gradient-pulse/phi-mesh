#!/usr/bin/env python3
"""
RGP–NS agent loop
- Loads config.yml
- Iterates over datasets
- Runs NT rhythm detection + statistical test
- Writes results + optional pulse if significant
"""

import os
import sys
import json
import pathlib
import datetime
import yaml

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def now_utc():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _has_jhtdb_token() -> bool:
    return bool(os.environ.get("JHTDB_TOKEN"))

# ---------------------------------------------------------------------
# Core agent logic (stub implementation here)
# ---------------------------------------------------------------------

def detect_nt_rhythm(dataset_id, source, config):
    """
    Stub: run NT rhythm detection & test.
    Replace with real logic that loads dataset, detects NTs, runs stats.
    """
    print(f"[RGP-NS] Processing dataset: {dataset_id} (source={source})")
    # Simulated result for demonstration:
    return {
        "dataset": dataset_id,
        "variant": "demo",
        "nt_test": {
            "p": 0.0042,
            "effect_size": 0.37,
            "significant": True
        }
    }

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    base_dir = pathlib.Path(__file__).resolve().parent
    repo_root = base_dir.parents[1]
    cfg_path = base_dir / "config.yml"
    config = load_yaml(cfg_path)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    results_dir = repo_root / "results" / "rgp_ns" / timestamp

    alpha = config.get("rhythm_test", {}).get("alpha", 0.01)
    effect_min = config.get("rhythm_test", {}).get("effect_size_min", 0.2)

    for ds_meta in config.get("datasets", []):
        ds_id = ds_meta.get("id", "unknown")
        source = ds_meta.get("source", "unknown")

        if source == "jhtdb" and not _has_jhtdb_token():
            print(f"[RGP-NS] SKIP {ds_id} — no JHTDB_TOKEN in environment")
            continue

        res = detect_nt_rhythm(ds_id, source, config)
        out_dir = results_dir / ds_id
        save_json(out_dir / "summary.json", res)

        nt_test = res.get("nt_test", {})
        pval = nt_test.get("p", 1.0)
        effsize = nt_test.get("effect_size", 0.0)
        sig = pval < alpha and effsize >= effect_min

        if sig and config.get("publishing", {}).get("make_pulse", False):
            pulse_dir = repo_root / "pulse" / "auto"
            pulse_dir.mkdir(parents=True, exist_ok=True)
            pulse_file = pulse_dir / f"{timestamp}_{ds_id}.yml"
            pulse = {
                "title": f"RGP–NS Agent Run ({ds_id})",
                "date": now_utc(),
                "tags": ["RGP", "Navier_Stokes", "NT_rhythm"],
                "summary": f"Automated NT rhythm analysis for dataset {ds_id}. Significant result (p={pval:.4f}, effect_size={effsize:.2f}).",
                "papers": [],
                "podcasts": []
            }
            with open(pulse_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(pulse, f, sort_keys=False)
            print(f"[RGP-NS] Pulse written: {pulse_file}")
        else:
            print(f"[RGP-NS] No pulse created for {ds_id} (p={pval:.4f}, effect_size={effsize:.2f}).")

    print(f"[RGP-NS] All datasets processed. Results in {results_dir}")

    # Show latest summary.json
    summaries = sorted(results_dir.glob("*/*/summary.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if summaries:
        latest = summaries[0]
        print("\n===== Latest Summary =====")
        print(latest)
        print(latest.read_text())
        print("==========================\n")
    else:
        print("[RGP-NS] No summary.json files found to display.")

if __name__ == "__main__":
    sys.exit(main())
