# pipeline/io_loaders.py
from __future__ import annotations
from typing import Dict, Tuple
from pathlib import Path
import json
import gzip
import io

import numpy as np

TimeSeriesMap = Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray]]]
# {probe_id: {var: (t, x)}}

def load_jhtdb_series_from_meta(meta_path: str) -> TimeSeriesMap:
    """
    Read time-series produced by tools/fd_connectors/jhtdb/jhtdb_loader.py.
    Returns a single-probe map with keys u,v,w,speed (if present).
    """
    meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    base = _stem_from_meta(meta)
    csv_gz = Path("data/jhtdb") / f"{base}.csv.gz"

    if not csv_gz.exists():
        raise FileNotFoundError(f"Expected JHTDB series file not found: {csv_gz}")

    # read gz csv quickly without pandas dependency in the pipeline
    with gzip.open(csv_gz.as_posix(), "rt", encoding="utf-8") as fh:
        header = fh.readline().strip().split(",")
        cols = list(map(str.strip, header))
        data = np.loadtxt(io.StringIO(fh.read()), delimiter=",")
        if data.ndim == 1 and data.size > 0:  # single row edge
            data = data[None, :]

    col_idx = {c: i for i, c in enumerate(cols)}
    t = data[:, col_idx["t"]] if "t" in col_idx else None

    series = {}
    for var in ("u", "v", "w", "speed", "Z"):
        if var in col_idx:
            series[var] = (t, data[:, col_idx[var]])

    probe_id = f"{meta['flow']}@({meta['point']['x']},{meta['point']['y']},{meta['point']['z']})"
    return {probe_id: series}

def _stem_from_meta(meta: dict) -> str:
    return f"{meta['flow']}__x{meta['point']['x']}_y{meta['point']['y']}_z{meta['point']['z']}__t{meta['t0']}_dt{meta['dt']}_n{meta['nsteps']}"
