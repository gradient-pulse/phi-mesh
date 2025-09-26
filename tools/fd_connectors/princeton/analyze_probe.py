  #!/usr/bin/env python3
"""
Analyze a Princeton probe (from its meta.json) using the shared pipeline.

Input:
  --meta  data/princeton/<STEM>.meta.json
  --out   results/fd_probe/<STEM>.analysis.json
  --component (u|v|w|Z|speed) [default: u]

Writes:
  results/fd_probe/<STEM>.analysis.json
  (figures are optional; leave to analysis runners if desired)
"""

from __future__ import annotations
from pathlib import Path
import argparse, json
import pandas as pd

from pipeline.io_loaders import load_series
from pipeline.preprocess import prep_1d
from pipeline.spectrum import rfft_spectrum, dominant_peak
from pipeline.ladder import ladder_1_2_3
from pipeline.utils import ensure_dir, save_json

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, help="data/princeton/<STEM>.meta.json")
    ap.add_argument("--out",  required=True, help="results/fd_probe/<STEM>.analysis.json")
    ap.add_argument("--component", default="u", help="series to analyze (u|v|w|Z|speed)")
    args = ap.parse_args()

    meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    subset_path = meta.get("subset") or meta.get("path_data")  # prefer raw subset if present
    probe_id = meta.get("probe")

    # Load the original subset again to keep a single source of truth
    D = load_series("princeton", {"subset_path": subset_path, "probe": probe_id})
    x = D["series"].get(args.component)
    if x is None:
        raise SystemExit(f"Component '{args.component}' not available; have {list(D['series'].keys())}")

    # Pipeline: prep → spectrum → dominant → ladder
    P  = prep_1d(D["t"], x)
    SP = rfft_spectrum(P["t"], P["x"], P["w"])
    dom = dominant_peak(SP["freq"], SP["power"], fmin=0.0)
    f0  = dom["freq"] if dom else None
    lad = ladder_1_2_3(SP["freq"], SP["power"], f0) if f0 else None

    out_p = Path(args.out)
    ensure_dir(out_p.parent)
    summary = {
        "label":     D["label"],
        "component": args.component,
        "n":         int(len(P["t"])),
        "dt":        float(D["dt"]),
        "duration_s": float((len(P["t"])-1)*D["dt"] if len(P["t"])>1 else 0.0),
        "dominant":  dom,
        "ladder":    lad,
        "note":      "no fundamental detected" if not f0 else "",
        "meta": {
            "subset":   subset_path,
            "probe":    probe_id,
            "stem":     meta.get("stem"),
            "path_csv": meta.get("path_data"),
            "path_meta": meta.get("path_meta"),
        }
    }
    save_json(out_p, summary)
    print("✅ Wrote analysis:", out_p.as_posix())

if __name__ == "__main__":
    main()
