from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import numpy as np

__all__ = ["load_series"]

# -------------------------- loaders (sources) -------------------------- #

def _load_jhtdb_from_meta(meta_path: str | Path) -> dict:
    """Read the meta.json written by the JHTDB loader and load the CSV.gz."""
    meta = json.loads(Path(meta_path).read_text())
    base = (
        f"{meta['flow']}__x{meta['point']['x']}_y{meta['point']['y']}_z{meta['point']['z']}"
        f"__t{meta['t0']}_dt{meta['dt']}_n{meta['nsteps']}"
    )
    csv_path = Path(meta_path).with_name(base + ".csv.gz")

    df = pd.read_csv(csv_path)
    t = df["t"].to_numpy(float)
    series = {}
    for k in ("u", "v", "w", "speed"):
        if k in df.columns:
            series[k] = df[k].to_numpy(float)

    return {
        "label": f"JHTDB:{meta['flow']} @ ({meta['point']['x']},{meta['point']['y']},{meta['point']['z']})",
        "t": t,
        "dt": float(meta["dt"]),
        "series": series,
        "meta": meta,
    }


def _load_princeton_subset(subset_path: str | Path, probe: str | None = None) -> dict:
    """
    Reader for Princeton-provided subsets.

    Accepted shapes:
      A) long form: columns [probe, t, u, v, w, (optional Z)]
      B) wide form: t, u_Q1, v_Q1, w_Q1, u_Q2, ...

    Use `probe` to choose which probe (e.g., "Q1").
    If None and only one probe exists, pick it automatically.
    """
    subset_path = Path(subset_path)
    if not subset_path.exists():
        raise FileNotFoundError(f"Subset file not found: {subset_path}")

    if subset_path.suffix.lower() == ".csv":
        df = pd.read_csv(subset_path)
    else:
        df = pd.read_hdf(subset_path)

    cols = set(df.columns.str.lower())
    long = {"probe", "t", "u", "v", "w"}.issubset(cols)

    if long:
        probe_vals = sorted(map(str, df["probe"].unique()))
        chosen = probe or (probe_vals[0] if len(probe_vals) == 1 else None)
        if chosen is None:
            raise ValueError(
                f"Multiple probes present {probe_vals}; please pass probe id "
                "(e.g. --probe Q1)"
            )
        dff = df[df["probe"].astype(str) == str(chosen)].sort_values("t")
        t = dff["t"].to_numpy(float)
        series = {}
        for k in ("u", "v", "w", "Z", "z"):
            if k in dff.columns:
                series[k.lower()] = dff[k].to_numpy(float)

    else:
        suffixes = sorted({
            c.split("_", 1)[1]
            for c in df.columns
            if "_" in c and c.split("_", 1)[0].lower() in {"u", "v", "w", "z"}
        })
        chosen = probe or (suffixes[0] if len(suffixes) == 1 else None)
        if chosen is None:
            raise ValueError(
                f"Multiple probe suffixes present {suffixes}; please pass probe id "
                "(e.g. --probe Q1)"
            )
        t = df["t"].to_numpy(float)
        series = {}
        for head in ("u", "v", "w", "Z", "z"):
            col = f"{head}_{chosen}"
            if col in df.columns:
                series[head.lower()] = df[col].to_numpy(float)

    if t.size < 2:
        raise ValueError("Time vector too short to estimate dt")
    dt = float(np.median(np.diff(t)))

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
    Return dict: {label, t, dt, series{u,v,w,[speed|Z]}, meta}.
    `source` in {"jhtdb","princeton"}.

    - JHTDB: params = {"meta_path": ".../file.meta.json"}
    - Princeton: params = {"subset_path": ".../subset.csv|h5", "probe": "Q1"|None}
    """
    s = source.lower()
    if s == "jhtdb":
        return _load_jhtdb_from_meta(params["meta_path"])
    if s == "princeton":
        return _load_princeton_subset(params["subset_path"], params.get("probe"))
    raise ValueError(f"Unknown source {source}")

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import sys
    print("Φ-Mesh GOLD PATH loader self-test")
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python pipeline/io_loaders.py jhtdb <meta.json>")
        print("  python pipeline/io_loaders.py princeton <subset.csv|h5> [probe_id]")
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
