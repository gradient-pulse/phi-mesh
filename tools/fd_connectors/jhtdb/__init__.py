# tools/fd_connectors/jhtdb/__init__.py
from __future__ import annotations
import os, json, gzip, csv
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def _stem(dataset: str, x: float, y: float, z: float, t0: float, dt: float, n: int) -> str:
    # Match the naming scheme we've been using in data/jhtdb/
    return f"{dataset}__x{round(x,3)}_y{round(y,3)}_z{round(z,3)}__t{round(t0,3)}_dt{dt}_n{n}"

def _find_cached_csv(stem: str) -> Optional[str]:
    base = os.path.join("data", "jhtdb", stem)
    for ext in (".csv.gz", ".csv"):
        p = base + ext
        if os.path.isfile(p):
            return p
    return None

def _read_csv(path: str):
    t, v = [], []
    # accept both gz and plain csv
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        r = csv.DictReader(f)
        # tolerate column names like t,u,v,w; if u not present, try first value col
        cols = [c.strip().lower() for c in r.fieldnames or []]
        has_t = "t" in cols
        # prefer u; otherwise take the first non-t column
        value_col = "u" if "u" in cols else next((c for c in cols if c != "t"), None)
        for row in r:
            if has_t:
                t.append(float(row["t"]))
            else:
                # synthesize t if absent (monotone index)
                t.append(float(len(t)))
            if value_col is None:
                raise RuntimeError(f"Could not identify a value column in {path}")
            v.append(float(row[value_col]))
    return Timeseries(t=t, v=v)

def fetch_timeseries(*, dataset: str, var: str, x: float, y: float, z: float,
                     t0: float, t1: float, dt: float) -> Timeseries:
    """
    Minimal adapter for the FD grid agent.
    - Tries to load a cached CSV produced earlier (fast path).
    - Otherwise, raises with a helpful message explaining how to re-enable live JHTDB fetch.
    """
    # infer n from window and dt (same convention as the loader)
    n = max(1, int(round((t1 - t0) / max(dt, 1e-12))))
    stem = _stem(dataset, x, y, z, t0, dt, n)

    cached = _find_cached_csv(stem)
    if cached:
        return _read_csv(cached)

    # No cached file → explain how to proceed.
    msg = (
        "JHTDB live connector not enabled: no cached CSV found at "
        f"data/jhtdb/{stem}.csv(.gz) and SOAP fetcher is not installed here.\n\n"
        "Options:\n"
        "  1) Restore the working SOAP loader (previous jhtdb_loader) and have this connector call it.\n"
        "  2) Run the grid with source=synthetic to validate the rest of the pipeline quickly.\n"
        "  3) Pre-seed data/jhtdb/ with CSVs named like the stem above to use the cache.\n"
    )
    raise RuntimeError(msg)
