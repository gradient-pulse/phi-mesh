# pipeline/io_loaders.py
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import numpy as np

__all__ = ["load_series"]

# -------------------------- helpers -------------------------- #

def _read_any(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext in {".csv", ".gz"}:
        # pandas handles .csv and .csv.gz transparently
        return pd.read_csv(path)
    if ext in {".parquet"}:
        return pd.read_parquet(path)
    if ext in {".h5", ".hdf5"}:
        return pd.read_hdf(path)
    raise ValueError(f"Unsupported subset file extension: {ext} (path={path})")

def _ensure_sorted_t(df: pd.DataFrame) -> pd.DataFrame:
    if "t" not in df.columns:
        raise ValueError("Subset must contain a 't' column for time.")
    return df.sort_values("t").reset_index(drop=True)

def _maybe_speed(series: dict[str, np.ndarray]) -> None:
    if all(k in series for k in ("u","v","w")):
        series["speed"] = np.sqrt(series["u"]**2 + series["v"]**2 + series["w"]**2)

# -------------------------- loaders (sources) -------------------------- #

def _load_jhtdb_from_meta(meta_path: str | Path) -> dict:
    """
    Read the meta.json written by the JHTDB loader and load the associated CSV.gz.
    Returns {label, t, dt, series{u,v,w,[speed]}, meta}.
    """
    meta_path = Path(meta_path)
    meta = json.loads(meta_path.read_text())
    base = (
        f"{meta['flow']}__x{meta['point']['x']}_y{meta['point']['y']}_z{meta['point']['z']}"
        f"__t{meta['t0']}_dt{meta['dt']}_n{meta['nsteps']}"
    )
    csv_path = meta_path.with_name(base + ".csv.gz")
    if not csv_path.exists():
        raise FileNotFoundError(f"JHTDB CSV not found: {csv_path}")

    df = _ensure_sorted_t(pd.read_csv(csv_path))
    t = df["t"].to_numpy(float)
    series: dict[str, np.ndarray] = {}
    for k in ("u", "v", "w", "speed"):
        if k in df.columns:
            series[k] = df[k].to_numpy(float)
    _maybe_speed(series)

    dt = float(meta.get("dt")) if "dt" in meta else (float(np.median(np.diff(t))) if t.size > 1 else np.nan)

    return {
        "label": f"JHTDB:{meta['flow']}@({meta['point']['x']},{meta['point']['y']},{meta['point']['z']})",
        "t": t,
        "dt": dt,
        "series": series,
        "meta": meta,
    }

def _load_princeton_subset(subset_path: str | Path, probe: str | None = None) -> dict:
    """
    Minimal, flexible reader for Princeton-provided subsets.

    Accepted shapes:
      A) Long form  : columns include [probe, t, u, v, w, (optional Z)]
      B) Wide form  : columns like [t, u_Q1, v_Q1, w_Q1, u_Q2, ...] (suffix is probe id)
      C) Simple form: columns like [t, u, v, w, (optional Z)] — single probe, no suffix

    Use `probe` to choose which probe (e.g., "Q1"). If None and only one exists, it is chosen.
    Returns {label, t, dt, series{u,v,w,[Z|speed]}, meta{subset_path,probe}}.
    """
    subset_path = Path(subset_path)
    if not subset_path.exists():
        raise FileNotFoundError(f"Subset file not found: {subset_path}")

    df = _read_any(subset_path)

    # Normalize column keys for detection (but preserve original case for data access)
    cols_lower = {c.lower() for c in df.columns}

    # ---- Detect shape A: Long form with explicit 'probe' column
    is_long = {"probe", "t", "u", "v", "w"}.issubset(cols_lower)

    if is_long:
        # Map to original-case columns
        colmap = {c.lower(): c for c in df.columns}
        df = _ensure_sorted_t(df)
        probe_col = colmap["probe"]
        t_col = colmap["t"]
        u_col = colmap.get("u")
        v_col = colmap.get("v")
        w_col = colmap.get("w")
        Z_col = colmap.get("z") or colmap.get("Z") if ("z" in colmap or "Z" in colmap) else None

        probe_vals = sorted(map(str, df[probe_col].unique()))
        chosen = probe or (probe_vals[0] if len(probe_vals) == 1 else None)
        if chosen is None:
            raise ValueError(f"Multiple probes present {probe_vals}; please pass probe id")

        dff = df[df[probe_col].astype(str) == str(chosen)].sort_values(t_col)
        t = dff[t_col].to_numpy(float)
        series: dict[str, np.ndarray] = {}
        if u_col in dff: series["u"] = dff[u_col].to_numpy(float)
        if v_col in dff: series["v"] = dff[v_col].to_numpy(float)
        if w_col in dff: series["w"] = dff[w_col].to_numpy(float)
        if Z_col and Z_col in dff: series["z"] = dff[Z_col].to_numpy(float)

    else:
        # ---- Detect shape B: Wide with suffixes (u_Q1, v_Q1, ...)
        heads = {"u", "v", "w", "z", "Z"}
        # Collect suffixes from any column of form head_suffix
        suffixes = sorted(
            {
                c.split("_", 1)[1]
                for c in df.columns
                if "_" in c and c.split("_", 1)[0] in heads
            }
        )

        if suffixes:
            chosen = probe or (suffixes[0] if len(suffixes) == 1 else None)
            if chosen is None:
                raise ValueError(f"Multiple probe suffixes present {suffixes}; please pass probe id (e.g., probe='Q1')")
            df = _ensure_sorted_t(df)
            t = df["t"].to_numpy(float)
            series = {}
            for head in ("u", "v", "w", "Z", "z"):
                col = f"{head}_{chosen}"
                if col in df.columns:
                    series[head.lower()] = df[col].to_numpy(float)

        else:
            # ---- Shape C: Simple single-probe: t, u, v, w, [Z]
            minimal = {"t", "u", "v", "w"}.issubset(cols_lower)
            if not minimal:
                raise ValueError(
                    "Unrecognized subset shape. Expect one of:\n"
                    "  A) long form: [probe, t, u, v, w, (Z)]\n"
                    "  B) wide form: t + u_<ID>, v_<ID>, w_<ID>...\n"
                    "  C) simple   : [t, u, v, w, (Z)]"
                )
            # Map back to original columns
            colmap = {c.lower(): c for c in df.columns}
            df = _ensure_sorted_t(df)
            t = df[colmap["t"]].to_numpy(float)
            series = {}
            for k in ("u", "v", "w"):
                series[k] = df[colmap[k]].to_numpy(float)
            # Optional Z/z
            if "z" in colmap:
                series["z"] = df[colmap["z"]].to_numpy(float)
            # Tag as a single implicit probe
            chosen = probe or "Q0"

    # estimate dt from t
    if t.size < 2:
        raise ValueError("Time vector too short to estimate dt.")
    dt = float(np.median(np.diff(t)))

    # convenience: speed if possible
    _maybe_speed(series)

    return {
        "label": f"Princeton:{subset_path.name}:{chosen}",
        "t": t,
        "dt": dt,
        "series": series,
        "meta": {"subset_path": subset_path.as_posix(), "probe": chosen},
    }

# ------------------------------ facade ------------------------------ #

def load_series(source: str, params: dict) -> dict:
    """
    Return dict: {label, t, dt, series{u,v,w,[speed|z]}, meta}.
    `source` in {"jhtdb","princeton"}.

    JHTDB expects:
        params = {"meta_path": ".../file.meta.json"}

    Princeton expects (any one of the supported shapes):
        params = {"subset_path": ".../subset.csv|parquet|h5", "probe": "Q1"|None}
    """
    s = (source or "").lower()
    if s == "jhtdb":
        return _load_jhtdb_from_meta(params["meta_path"])
    if s == "princeton":
        return _load_princeton_subset(params["subset_path"], params.get("probe"))
    raise ValueError(f"Unknown source: {source!r}")

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import sys
    print("Φ-Mesh GOLD PATH loader self-test")
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python pipeline/io_loaders.py jhtdb <meta.json>")
        print("  python pipeline/io_loaders.py princeton <subset.csv|parquet|h5> [probe_id]")
        sys.exit(0)

    source = sys.argv[1].lower()
    path = sys.argv[2]
    arg_probe = sys.argv[3] if len(sys.argv) > 3 else None

    if source == "jhtdb":
        d = load_series("jhtdb", {"meta_path": path})
    elif source == "princeton":
        d = load_series("princeton", {"subset_path": path, "probe": arg_probe})
    else:
        raise SystemExit("source must be jhtdb|princeton")

    print(f"Loaded {d['label']}")
    print(f"  n={len(d['t'])}  dt≈{d['dt']:.6g}  channels={list(d['series'].keys())}")
