# pipeline/io_loaders.py
"""
Unified loaders for Φ-Mesh GOLD PATH.

Exposed entry points
--------------------
- load_series(source, params)  -> dict
    source ∈ {"jhtdb", "princeton"}

Returned dict shape
-------------------
{
  "label": str,                 # pretty identifier
  "t": np.ndarray,              # time array (sorted, float)
  "series": {                   # available components
      "u": np.ndarray,          # optional keys: "v","w","Z",...
      "v": ...,
      "w": ...,
      "Z": ...,
  },
  "dt": float,                  # median Δt (seconds)
  "meta": dict                  # extra provenance
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Iterable, Optional

import json
import numpy as np
import pandas as pd


# ---------- helpers -----------------------------------------------------------

def _median_dt(t: np.ndarray) -> float:
    if t.size < 2:
        return float("nan")
    return float(np.median(np.diff(np.asarray(t, dtype=float))))


def _series_from_df(df: pd.DataFrame, cols: Iterable[str]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for c in cols:
        if c in df.columns:
            out[c] = df[c].to_numpy(dtype=float)
    return out


def _coerce_time(df: pd.DataFrame, t_col: str = "t") -> pd.DataFrame:
    if t_col not in df.columns:
        raise KeyError(f"Missing time column '{t_col}' in data frame (have: {list(df.columns)})")
    dfx = df.copy()
    dfx[t_col] = pd.to_numeric(dfx[t_col], errors="coerce")
    dfx = dfx.dropna(subset=[t_col]).sort_values(t_col, kind="mergesort")
    return dfx


# ---------- JHTDB loader ------------------------------------------------------

def load_jhtdb_from_meta(meta_path: str | Path) -> Dict[str, Any]:
    """
    Load a single JHTDB probe time series produced by tools/fd_connectors/jhtdb/jhtdb_loader.py

    Expects sibling files:
      <stem>.meta.json   (this path)
      <stem>.csv.gz  or  <stem>.csv  (written by the loader)

    CSV must have columns at least: t, u, v, w  (extra columns are ignored).
    """
    meta_p = Path(meta_path)
    if not meta_p.name.endswith(".meta.json"):
        raise ValueError("Expected a '.meta.json' path produced by the JHTDB loader")

    meta = json.loads(meta_p.read_text(encoding="utf-8"))

    stem = meta_p.as_posix().removesuffix(".meta.json")
    candidates = [stem + ".csv.gz", stem + ".csv", stem + ".parquet"]
    data_p = None
    for c in candidates:
        cp = Path(c)
        if cp.exists():
            data_p = cp
            break
    if data_p is None:
        raise FileNotFoundError(f"No data file found next to meta: tried {candidates}")

    # Load frame
    if data_p.suffix == ".parquet":
        df = pd.read_parquet(data_p)
    else:
        # works for .csv and .csv.gz
        df = pd.read_csv(data_p)

    df = _coerce_time(df, "t")
    series = _series_from_df(df, ["u", "v", "w", "Z"])  # Z may not exist; that's fine
    t = df["t"].to_numpy(dtype=float)
    dt = _median_dt(t)

    label = (
        f"jhtdb:{meta.get('flow','?')} "
        f"x={meta.get('point',{}).get('x')},"
        f"y={meta.get('point',{}).get('y')},"
        f"z={meta.get('point',{}).get('z')}"
    )

    return {
        "label": label,
        "t": t,
        "series": series,
        "dt": dt,
        "meta": {
            "path_meta": str(meta_p),
            "path_data": str(data_p),
            **meta,
        },
    }


# ---------- Princeton loader --------------------------------------------------

def load_princeton_subset(
    subset_path: str | Path,
    probe: Optional[str] = None,
    t_col: str = "t",
    value_cols: Iterable[str] = ("u", "v", "w", "Z"),
) -> Dict[str, Any]:
    """
    Load a Princeton subset file (CSV/CSV.GZ or HDF5) and select a single probe stream.

    Expected shapes (flexible):
      - CSV(.gz): columns like [t, u, v, w, Z] optionally with a 'probe' column
      - HDF5/HDF: a table with similar columns or a key 'data'

    If a 'probe' column exists and probe is None, the first probe id is chosen.
    """
    p = Path(subset_path)
    if not p.exists():
        raise FileNotFoundError(f"Princeton subset not found: {p}")

    # Read frame
    if p.suffix in {".csv", ".gz"} or p.name.endswith(".csv.gz"):
        df = pd.read_csv(p)
    elif p.suffix in {".h5", ".hdf", ".hdf5"}:
        # pandas.read_hdf requires pytables (tables); if missing, guide the user.
        try:
            df = pd.read_hdf(p)  # tries default key; adjust if needed
        except Exception as e:
            raise RuntimeError(
                f"Unable to read HDF5 file '{p}'. "
                f"Install PyTables (`pip install tables`) or export a CSV. Root cause: {e}"
            )
    else:
        raise ValueError(f"Unsupported subset format for Princeton: {p.suffix}")

    # Optional multi-probe selection
    if "probe" in df.columns:
        probes = list(map(str, sorted(df["probe"].unique())))
        chosen = probe if probe is not None else probes[0]
        df = df[df["probe"].astype(str) == str(chosen)].copy()
        chosen_probe = str(chosen)
    else:
        chosen_probe = probe or p.stem  # best-effort label

    df = _coerce_time(df, t_col)
    t = df[t_col].to_numpy(dtype=float)
    series = _series_from_df(df, value_cols)
    dt = _median_dt(t)

    return {
        "label": f"princeton:{chosen_probe}",
        "t": t,
        "series": series,
        "dt": dt,
        "meta": {
            "path_data": str(p),
            "probe": chosen_probe,
            "columns": list(df.columns),
        },
    }


# ---------- unified front door ------------------------------------------------

def load_series(source: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified loader used by GOLD PATH analyzers.

    Examples:
        load_series("jhtdb", {"meta_path": "data/jhtdb/isotropic__x...meta.json"})
        load_series("princeton", {"subset_path": "data/princeton/subset.csv", "probe": "Q1"})
    """
    src = (source or "").strip().lower()
    if src == "jhtdb":
        meta_path = params.get("meta_path") or params.get("meta")  # allow both keys
        if not meta_path:
            raise KeyError("JHTDB loader expects 'meta_path' (path to *.meta.json)")
        return load_jhtdb_from_meta(meta_path)

    if src == "princeton":
        subset_path = params.get("subset_path")
        if not subset_path:
            raise KeyError("Princeton loader expects 'subset_path' (CSV/CSV.GZ/HDF5)")
        return load_princeton_subset(
            subset_path=subset_path,
            probe=params.get("probe"),
            t_col=params.get("t_col", "t"),
            value_cols=params.get("value_cols", ("u", "v", "w", "Z")),
        )

    raise ValueError(f"Unknown source '{source}'. Use 'jhtdb' or 'princeton'.")


__all__ = [
    "load_series",
    "load_jhtdb_from_meta",
    "load_princeton_subset",
]
# -----------------------------------------------------------------------------
# Self-test (manual sanity checks)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    print("Φ-Mesh GOLD PATH loader self-test")

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python pipeline/io_loaders.py jhtdb <meta.json>")
        print("  python pipeline/io_loaders.py princeton <subset.csv> [probe_id]")
        sys.exit(0)

    source = sys.argv[1].lower()
    path = sys.argv[2]
    extra = sys.argv[3] if len(sys.argv) > 3 else None

    if source == "jhtdb":
        d = load_series("jhtdb", {"meta_path": path})
    elif source == "princeton":
        d = load_series("princeton", {"subset_path": path, "probe": extra})
    else:
        raise ValueError(f"Unknown source '{source}' (use jhtdb|princeton)")

    print(f"Loaded {d['label']}")
    print(f"  timesteps: {len(d['t'])}, dt ≈ {d['dt']:.4g}")
    print(f"  components: {list(d['series'].keys())}")
