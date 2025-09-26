#!/usr/bin/env python3
"""
Princeton subset → standardized CSV.gz + meta.json

Reads a local subset provided by Princeton (CSV or HDF5), selects a probe
(if multiple), and writes a canonical pair:

  data/princeton/<STEM>.csv.gz
  data/princeton/<STEM>.meta.json

STEM format:
  princeton__<subset-stem>__probe<PROBE>

Columns in CSV:
  t, and any of [u, v, w, Z] that were present in the subset.

Meta JSON includes: subset path, probe id, dt estimate, row count, columns, slug, and stem.
"""

from __future__ import annotations
from pathlib import Path
import argparse, json
import pandas as pd

from pipeline.io_loaders import load_series
from pipeline.utils import ensure_dir

OUTDIR = Path("data/princeton")

def safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in str(s))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", required=True, help="Path to Princeton subset (.csv, .h5, .hdf5)")
    ap.add_argument("--probe", default=None, help="Probe id if multiple present (e.g., Q1)")
    ap.add_argument("--slug",  default="princeton", help="Short label used elsewhere")
    args = ap.parse_args()

    D = load_series("princeton", {"subset_path": args.subset, "probe": args.probe})
    subset_p = Path(args.subset)
    probe_id = D["meta"]["probe"]
    stem = f"princeton__{safe(subset_p.stem)}__probe{safe(probe_id)}"

    # Build a tidy DataFrame (t + available channels)
    cols = ["t"] + [k for k in ("u","v","w","Z","z","speed") if k in D["series"]]
    df = pd.DataFrame({"t": D["t"]})
    for k in cols[1:]:
        df[k] = D["series"][k]

    ensure_dir(OUTDIR)
    csv_path  = OUTDIR / f"{stem}.csv.gz"
    meta_path = OUTDIR / f"{stem}.meta.json"

    df.to_csv(csv_path, index=False, compression="gzip")

    meta = {
        "source":     "princeton",
        "subset":     str(subset_p),
        "probe":      probe_id,
        "slug":       args.slug,
        "dt":         float(D["dt"]),
        "rows":       int(df.shape[0]),
        "columns":    list(map(str, df.columns)),
        "stem":       stem,
        "path_data":  csv_path.as_posix(),
        "path_meta":  meta_path.as_posix(),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("✅ Saved:")
    print("  ", csv_path)
    print("  ", meta_path)

if __name__ == "__main__":
    main()
