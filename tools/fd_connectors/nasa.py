# tools/fd_connectors/nasa.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import csv
import io
import os
import urllib.request

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def list_datasets():
    # Placeholder set; expand as you wire real sources.
    return ["cfd_demo"]

def _load_text_from_url(url: str) -> str:
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8", errors="replace")

def read_csv_timeseries(src: str, t_col: str = "t", v_col: str = "v") -> Timeseries:
    """
    Read a simple CSV with header containing columns t and v.
    src can be:
      - http(s):// URL to a CSV
      - raw CSV text (if it contains a newline)
      - local file path
    """
    if "://" in src and src.startswith(("http://","https://")):
        text = _load_text_from_url(src)
    elif "\n" in src or "," in src and not os.path.exists(src):
        # Treat as inline CSV text if it looks like CSV and path doesn't exist
        text = src
    else:
        with open(src, "r", encoding="utf-8") as f:
            text = f.read()

    reader = csv.DictReader(io.StringIO(text))
    t, v = [], []
    for row in reader:
        if row.get(t_col) is None or row.get(v_col) is None:
            continue
        try:
            t.append(float(row[t_col]))
            v.append(float(row[v_col]))
        except Exception:
            # skip bad rows
            continue
    if len(t) < 3:
        raise ValueError("Not enough rows parsed from CSV (need >=3).")
    return Timeseries(t=t, v=v)

def fetch_timeseries(dataset: str, var: str, x: float, y: float, z: float,
                     t0: float, t1: float, dt: float) -> Timeseries:
    """
    Placeholder for a real NASA CFD source. For now, require a CSV via env:
      NASA_CSV=<url or path or inline CSV text>
    """
    src = os.getenv("NASA_CSV", "").strip()
    if not src:
        raise NotImplementedError("Set repository secret NASA_CSV to a CSV (url/path/inline).")
    return read_csv_timeseries(src)
