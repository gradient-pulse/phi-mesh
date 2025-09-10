# tools/fd_connectors/nasa.py
from __future__ import annotations

import os
import urllib.request
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Timeseries:
    t: List[float]
    v: List[float]


# ---------- internals ----------

def _read_text(path_or_url: str) -> str:
    """Read text from local path or HTTP(S) URL, with debug + rich errors."""
    print(f"[NASA] Attempting to read: {path_or_url}")
    try:
        # URL?
        if path_or_url.startswith(("http://", "https://")):
            with urllib.request.urlopen(path_or_url) as resp:  # nosec
                text = resp.read().decode("utf-8", errors="replace")
                print(f"[NASA] OK: fetched {len(text)} chars from URL")
                return text

        # Local file (absolute or relative)
        if not os.path.exists(path_or_url):
            msg = f"[NASA] ERROR: file not found: {path_or_url}"
            print(msg)
            raise FileNotFoundError(msg)
        with open(path_or_url, "r", encoding="utf-8") as f:
            text = f.read()
            print(f"[NASA] OK: read {len(text)} chars from local file")
            return text

    except Exception as e:
        print(f"[NASA] READ FAILURE for {path_or_url}: {type(e).__name__}: {e}")
        raise


def _resolve_path_or_url(spec: str) -> str:
    """
    Resolve a user spec into a concrete path/URL.
    Priority:
      1) absolute path or URL → use as-is
      2) repo-relative path that exists → use
      3) short filename -> 'data/nasa/<filename>' if exists
      4) otherwise return original (will fail in _read_text)
    """
    raw = (spec or "").strip()
    # Strip accidental quotes
    if len(raw) >= 2 and (raw[0] == raw[-1]) and raw[0] in ("'", '"'):
        raw = raw[1:-1]
    print(f"[NASA] Resolving spec: {raw}")

    # URL or absolute
    if raw.startswith(("http://", "https://")) or os.path.isabs(raw):
        print(f"[NASA] Using as direct path/URL: {raw}")
        return raw

    # Repo-relative?
    if os.path.exists(raw):
        print(f"[NASA] Found repo-relative file: {raw}")
        return raw

    # data/nasa/<raw> ?
    candidate = os.path.join("data", "nasa", raw)
    if os.path.exists(candidate):
        print(f"[NASA] Found under data/nasa/: {candidate}")
        return candidate

    print(f"[NASA] No local match; will try as-is: {raw}")
    return raw


def _parse_csv(text: str) -> Timeseries:
    """Parse minimal CSV (headers 't','v' or first two columns)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    print(f"[NASA] Parsing CSV: {len(lines)} non-empty lines")
    if not lines:
        return Timeseries(t=[], v=[])

    header = [h.strip().lower() for h in lines[0].split(",")]
    try:
        i_t = header.index("t")
        i_v = header.index("v")
        print(f"[NASA] Header detected: t at col {i_t}, v at col {i_v}")
        data_rows = lines[1:]
    except ValueError:
        print("[NASA] No 't','v' headers; assuming columns 0 and 1")
        i_t, i_v = 0, 1
        data_rows = lines  # treat first row as data

    T: List[float] = []
    V: List[float] = []
    bad = 0
    for row in data_rows:
        parts = [p.strip() for p in row.split(",")]
        if len(parts) <= max(i_t, i_v):
            bad += 1
            continue
        try:
            T.append(float(parts[i_t]))
            V.append(float(parts[i_v]))
        except Exception:
            bad += 1
            continue

    print(f"[NASA] Parsed {len(T)} rows; skipped {bad} rows")
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
    try:
        target = _resolve_path_or_url(path_or_url)
        text = _read_text(target)
        ts = _parse_csv(text)

        if not ts.t or not ts.v:
            msg = f"[NASA] ERROR: parsed empty time series from {target!r}"
            print(msg)
            raise ValueError(msg)

        print(f"[NASA] OK: timeseries length = {len(ts.t)}")
        return ts

    except Exception as e:
        print(f"[NASA] read_csv_timeseries FAILED for {path_or_url!r}: {type(e).__name__}: {e}")
        raise


def fetch_timeseries(dataset: str, var: str, x: float, y: float, z: float,
                     t0: float, t1: float, dt: float) -> Timeseries:
    """
    For now, 'dataset' is a CSV path/URL/short-name.
    Shape mirrors the JHTDB connector for symmetry.
    """
    print(f"[NASA] Fetching: dataset={dataset!r}, var={var}, "
          f"xyz=({x},{y},{z}), twin=({t0},{t1},{dt})")
    return read_csv_timeseries(dataset)
