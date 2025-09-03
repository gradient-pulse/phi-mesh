# tools/fd_connectors/nasa.py
from dataclasses import dataclass
from typing import List, Tuple
import os, io, csv

try:
    import requests  # only used if NASA_CSV is a URL
except Exception:
    requests = None

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def _read_csv_from_path(path: str) -> Timeseries:
    ts, vs = [], []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ts.append(float(row["t"]))
            vs.append(float(row["v"]))
    return Timeseries(t=ts, v=vs)

def _read_csv_from_url(url: str) -> Timeseries:
    if requests is None:
        raise RuntimeError("requests not available to fetch NASA_CSV URL")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    ts, vs = [], []
    r = csv.DictReader(io.StringIO(resp.text))
    for row in r:
        ts.append(float(row["t"]))
        vs.append(float(row["v"]))
    return Timeseries(t=ts, v=vs)

def read_csv_timeseries() -> Timeseries:
    """
    Fallback loader for NASA mode:
    - If env NASA_CSV is set and looks like a URL -> fetch via HTTP(S)
    - If NASA_CSV is set and is a path -> read from disk
    - Else -> default to repo file: data/nasa/demo_timeseries.csv
    """
    target = os.getenv("NASA_CSV", "").strip()
    if not target:
        target = "data/nasa/demo_timeseries.csv"   # default fallback

    if target.startswith("http://") or target.startswith("https://"):
        return _read_csv_from_url(target)
    else:
        # allow workspace-relative paths
        if not os.path.exists(target):
            # try joining repo root if GitHub workspace is present
            root = os.getenv("GITHUB_WORKSPACE", "")
            candidate = os.path.join(root, target) if root else target
            if os.path.exists(candidate):
                target = candidate
        return _read_csv_from_path(target)
