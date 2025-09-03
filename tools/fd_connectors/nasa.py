# tools/fd_connectors/nasa.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import csv
import io
import os
import urllib.request
import math

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def _is_url(path: str) -> bool:
    return path.startswith("http://") or path.startswith("https://")

def _read_text(path_or_url: str) -> str:
    if _is_url(path_or_url):
        with urllib.request.urlopen(path_or_url) as r:
            return r.read().decode("utf-8")
    with open(path_or_url, "r", encoding="utf-8") as f:
        return f.read()

def read_csv_timeseries(path_or_url: str) -> Timeseries:
    """
    Read a simple CSV with two columns 't','v' (header required).
    Returns Timeseries with floats.
    """
    text = _read_text(path_or_url)
    t, v = [], []
    reader = csv.DictReader(io.StringIO(text))
    if "t" not in reader.fieldnames or "v" not in reader.fieldnames:
        raise ValueError("NASA CSV must have headers: t,v")
    for row in reader:
        t.append(float(row["t"]))
        v.append(float(row["v"]))
    return Timeseries(t=t, v=v)

def fetch_timeseries(
    dataset: str,
    var: str,
    x: float, y: float, z: float,
    t0: float, t1: float, dt: float,
) -> Timeseries:
    """
    Wrapper used by run_fd_probe.py.

    Resolution order to find the CSV:
      1) If `dataset` looks like a path (contains '/' or endswith .csv), use it.
      2) Else if NASA_CSV secret is set, use that.
      3) Else try repo path: data/nasa/{dataset}.csv
      4) Else fallback demo: data/nasa/demo_timeseries.csv

    NOTE: var / (x,y,z) are accepted for symmetry but not used by the CSV reader.
    time window (t0,t1,dt) is currently advisory; we return the whole series.
    """
    # 1) explicit path-like in the dataset field
    if "/" in dataset or dataset.lower().endswith(".csv"):
        target = dataset
    else:
        # 2) repo secret (can be URL or path)
        target = os.getenv("NASA_CSV", "").strip()
        if not target:
            # 3) repo path using dataset name
            candidate = os.path.join("data", "nasa", f"{dataset}.csv")
            if os.path.exists(candidate):
                target = candidate
            else:
                # 4) final fallback to demo file
                target = os.path.join("data", "nasa", "demo_timeseries.csv")

    if not target:
        raise FileNotFoundError("Unable to resolve a NASA CSV path/URL.")

    ts = read_csv_timeseries(target)

    # (Optional) windowing: if you want to crop to [t0, t1], do it here.
    # Keeping it simple: return as-is for now.
    return ts
