# pipeline/utils.py
from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import csv, json, hashlib, time

def pack_row(probe_id: str, var: str, det, cfg: Dict) -> Dict:
    return {
        "probe": probe_id,
        "var": var,
        "f_base_hz": det.f_base,
        "f2_over_f1": det.f2_over_f1,
        "f3_over_f1": det.f3_over_f1,
        "snr_base_db": det.snr_base_db,
        "snr_2f_db": det.snr_2f_db,
        "snr_3f_db": det.snr_3f_db,
        "window": cfg.get("preprocess", {}).get("window", "hann"),
        "detrend": cfg.get("preprocess", {}).get("detrend", "mean"),
        "passed": det.passed,
    }

def write_table(rows: List[Dict], path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "probe","var","f_base_hz","f2_over_f1","f3_over_f1",
        "snr_base_db","snr_2f_db","snr_3f_db","window","detrend","passed"
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_log(cfg: Dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cfg_hash": cfg_hash(cfg),
        "cfg": cfg,
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

def cfg_hash(cfg: Dict) -> str:
    return hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
