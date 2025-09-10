# tools/fd_connectors/nasa.py
from __future__ import annotations

import csv
import io
import os
import zipfile
import urllib.request
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Timeseries:
    t: List[float]
    v: List[float]


# ---------- internals ----------

def _is_url(spec: str) -> bool:
    return spec.startswith(("http://", "https://"))


def _resolve_path_or_url(spec: str) -> str:
    """
    Resolve a user spec into a concrete path/URL.
    Priority:
      1) absolute path or URL → use as-is
      2) repo-relative path that exists → use
      3) short filename -> 'data/nasa/<filename>' if exists
      4) otherwise return original (which will error in the reader)
    """
    spec = (spec or "").strip()
    if not spec:
        raise FileNotFoundError("Empty NASA dataset spec")

    # URL or absolute path
    if _is_url(spec) or os.path.isabs(spec):
        return spec

    # Try as given (repo-relative)
    if os.path.exists(spec):
        return spec

    # Try under data/nasa/
    candidate = os.path.join("data", "nasa", spec)
    if os.path.exists(candidate):
        return candidate

    # Last resort: return original (will be handled by reader)
    return spec


def _read_bytes(path_or_url: str) -> bytes:
    """Read bytes from local path or HTTP(S) URL."""
    if _is_url(path_or_url):
        with urllib.request.urlopen(path_or_url) as resp:  # nosec - trusted by maintainer input
            return resp.read()

    if not os.path.exists(path_or_url):
        raise FileNotFoundError(path_or_url)

    with open(path_or_url, "rb") as f:
        return f.read()


def _maybe_unzip_csv(payload: bytes) -> Optional[str]:
    """
    If 'payload' is a ZIP archive, extract and return text of the FIRST .csv found.
    Otherwise return None.
    """
    # ZIP magic: PK\x03\x04
    if len(payload) >= 4 and payload[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            # prefer first *.csv; if none, fall back to first file
            names = zf.namelist()
            csv_names = [n for n in names if n.lower().endswith(".csv")]
            pick = (csv_names[0] if csv_names else (names[0] if names else None))
            if not pick:
                raise ValueError("ZIP file appears empty.")
            with zf.open(pick, "r") as f:
                data = f.read()
            # decode as utf-8 with fallback
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("latin-1")
    return None


def _bytes_to_text(payload: bytes) -> str:
    """Decode bytes to text with sensible fallback."""
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1")


def _parse_csv(text: str) -> Timeseries:
    """
    Parse a minimal CSV.
    Accepts:
      - header row containing 't' and 'v' (any case)
      - OR plain two-column numeric rows.
    Ignores blank/invalid lines.
    """
    if not text.strip():
        return Timeseries(t=[], v=[])

    # Use csv module for robustness (commas; simple files).
    T: List[float] = []
    V: List[float] = []

    # Normalize newlines; allow stray BOM
    text_norm = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text_norm))

    rows = list(reader)
    if not rows:
        return Timeseries(t=[], v=[])

    # Detect header
    header = [h.strip().lower() for h in rows[0]] if rows else []
    has_header = ("t" in header and "v" in header)

    # Column indices
    if has_header:
        i_t = header.index("t")
        i_v = header.index("v")
        data_rows = rows[1:]
    else:
        # Assume two columns t,v
        i_t, i_v = 0, 1
        data_rows = rows

    for parts in data_rows:
        if len(parts) <= max(i_t, i_v):
            continue
        try:
            t_val = float(parts[i_t].strip())
            v_val = float(parts[i_v].strip())
        except Exception:
            # skip non-numeric rows
            continue
        T.append(t_val)
        V.append(v_val)

    return Timeseries(t=T, v=V)


def _filter_window(ts: Timeseries, t0: float, t1: float) -> Timeseries:
    """Return subset where t0 <= t <= t1 (if t0 < t1 and times look compatible)."""
    if not ts.t or t1 <= t0:
        return ts
    T: List[float] = []
    V: List[float] = []
    for tt, vv in zip(ts.t, ts.v):
        if t0 <= tt <= t1:
            T.append(tt)
            V.append(vv)
    # If the filter removed everything (e.g., units mismatch), return original
    return Timeseries(t=T, v=V) if T else ts


# ---------- public API ----------

def read_csv_timeseries(path_or_url: str) -> Timeseries:
    """
    Read a CSV/URL/ZIP (or short name) and return a Timeseries.
    Accepts:
      - '/abs/path/file.csv'
      - 'https://.../file.csv'
      - 'https://.../archive.zip' (first CSV inside is parsed)
      - 'data/nasa/file.csv'
      - 'file.csv'   (resolved to 'data/nasa/file.csv' if present)
    """
    target = _resolve_path_or_url(path_or_url)
    payload = _read_bytes(target)

    # ZIP?
    as_csv_text = _maybe_unzip_csv(payload)
    if as_csv_text is None:
        as_csv_text = _bytes_to_text(payload)

    ts = _parse_csv(as_csv_text)
    if not ts.t or not ts.v:
        raise ValueError(f"Parsed empty time series from: {target!r}")
    return ts


def fetch_timeseries(dataset: str, var: str, x: float, y: float, z: float,
                     t0: float, t1: float, dt: float) -> Timeseries:
    """
    For now, 'dataset' may be:
      - path or URL to a CSV
      - path or URL to a ZIP containing at least one CSV
      - short name resolved under data/nasa/

    The xyz/var args are accepted for interface symmetry; not used yet.
    We lightly window to [t0, t1] if time units align.
    """
    ts = read_csv_timeseries(dataset)
    # Light, best-effort windowing — if units are comparable, this reduces noise.
    ts_w = _filter_window(ts, t0, t1)
    # Do not resample to dt here; rhythm code only needs timestamps.
    # Return as-is (sorted helps downstream monotonic checks).
    if ts_w.t and ts_w.t != sorted(ts_w.t):
        # keep stable order but prepare downstream; do not reorder v against t incorrectly
        # because most CSVs are already ordered; if out of order, sort by t with paired v.
        pairs = sorted(zip(ts_w.t, ts_w.v), key=lambda p: p[0])
        t_sorted, v_sorted = zip(*pairs)
        return Timeseries(t=list(t_sorted), v=list(v_sorted))
    return ts_w
