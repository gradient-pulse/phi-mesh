# tools/fd_connectors/nasa.py
from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass
from typing import List


@dataclass
class Timeseries:
    t: List[float]
    v: List[float]


# ---------- internals ----------

def _read_text(path_or_url: str) -> str:
    """Read text from local path or HTTP(S) URL."""
    print(f"[NASA] Attempting to read: {path_or_url}")  # DEBUG
    # URL?
    if path_or_url.startswith(("http://", "https://")):
        with urllib.request.urlopen(path_or_url) as resp:  # nosec: trusted by user input
            text = resp.read().decode("utf-8")
            print(f"[NASA] Successfully fetched {len(text)} chars from URL")  # DEBUG
            return text

    # Local file (absolute or relative to repo root)
    if not os.path.exists(path_or_url):
        print(f"[NASA] File not found: {path_or_url}")  # DEBUG
        raise FileNotFoundError(path_or_url)
    with open(path_or_url, "r", encoding="utf-8") as f:
        text = f.read()
        print(f"[NASA] Successfully read {len(text)} chars from local file")  # DEBUG
        return text


def _resolve_path_or_url(spec: str) -> str:
    """
    Resolve a user spec into a concrete path/URL.
    Priority:
      1) absolute path or URL → use as-is
      2) repo-relative path that exists → use
      3) short filename -> 'data/nasa/<filename>' if exists
    """
    spec = (spec or "").strip()

    # NEW: tolerate surrounding quotes from shells/launchers/CI
    if (len(spec) >= 2) and ((spec[0] == spec[-1]) and spec[0] in ("'", '"')):
        spec = spec[1:-1]

    print(f"[NASA] Resolving spec: {spec}")  # DEBUG

    # URL or absolute path
    if spec.startswith(("http://", "https://")) or os.path.isabs(spec):
        print(f"[NASA] Using as direct path/URL: {spec}")  # DEBUG
        return spec

    # Try as given (repo-relative)
    if os.path.exists(spec):
        print(f"[NASA] Found repo-relative file: {spec}")  # DEBUG
        return spec

    # Try under data/nasa/
    candidate = os.path.join("data", "nasa", spec)
    if os.path.exists(candidate):
        print(f"[NASA] Found under data/nasa/: {candidate}")  # DEBUG
        return candidate

    # Last resort: report the original (will be raised by _read_text)
    print(f"[NASA] No match found; returning spec: {spec}")  # DEBUG
    return spec


def _parse_csv(text: str) -> Timeseries:
    """
    Parse minimal CSV with headers 't','v'. Ignores blank/invalid lines.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    print(f"[NASA] Parsing CSV: {len(lines)} lines")  # DEBUG
    if not lines:
        return Timeseries(t=[], v=[])

    # Very small, defensive parser
    header = [h.strip().lower() for h in lines[0].split(",")]
    try:
        i_t = header.index("t")
        i_v = header.index("v")
        print(f"[NASA] Detected headers: t={i_t}, v={i_v}")  # DEBUG
    except ValueError:
        # Not our format; attempt naive two-column parse
        i_t, i_v = 0, 1
        print(f"[NASA] No headers found, assuming columns 0 and 1")  # DEBUG

    T: List[float] = []
    V: List[float] = []
    for row in lines[1:]:
        parts = [p.strip() for p in row.split(",")]
        if len(parts) <= max(i_t, i_v):
            continue
        try:
            T.append(float(parts[i_t]))
            V.append(float(parts[i_v]))
        except Exception:
            continue

    print(f"[NASA] Parsed {len(T)} rows of data")  # DEBUG
    return Timeseries(t=T, v=V)


# ---------- public API ----------

def read_csv_timeseries(path_or_url: str) -> Timeseries:
    """
    Read a CSV/URL (or short name) and return a Timeseries.
    Accepts:
      - '/abs/path/file.csv'
      - 'https://.../file.csv'
      - 'data/nasa/file.csv'
      - 'file.csv'   (resolved to 'data/nasa/file.csv' if present)
    """
    target = _resolve_path_or_url(path_or_url)
    text = _read_text(target)
    ts = _parse_csv(text)

    if not ts.t or not ts.v:
        raise ValueError(f"Parsed empty time series from: {target!r}")
    return ts


def fetch_timeseries(dataset: str, var: str, x: float, y: float, z: float,
                     t0: float, t1: float, dt: float) -> Timeseries:
    """
    For now, 'dataset' may be a path/URL/short-name to a CSV.
    This mirrors the shape of the JHTDB API so callers are symmetric.
    """
    print(f"[NASA] Fetching timeseries for dataset={dataset}, var={var}, "
          f"xyz=({x},{y},{z}), t0={t0}, t1={t1}, dt={dt}")  # DEBUG
    return read_csv_timeseries(dataset)
