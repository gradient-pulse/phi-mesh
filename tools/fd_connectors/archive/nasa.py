# tools/fd_connectors/nasa.py
"""
NASA DNS Connector for RGP-NS agent.

Supports:
- Local/remote CSV files (t,v or t,u/v/w/p with header)
- ZIP archives containing CSV(s)
- NetCDF DNS files (x,y,z,t,u/v/w/...)

For NetCDF, extracts a time series at a probe point (x,y,z) over time.
"""

from __future__ import annotations

import csv
import io
import os
import zipfile
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

try:
    import xarray as xr
except ImportError:
    xr = None


@dataclass
class Timeseries:
    t: List[float]
    v: List[float]


# ---------- internals ----------

def _is_url(spec: str) -> bool:
    return spec.startswith(("http://", "https://"))


def _resolve_path_or_url(spec: str) -> str:
    """Resolve spec into a concrete path or URL."""
    spec = (spec or "").strip()
    if not spec:
        raise FileNotFoundError("Empty NASA dataset spec")

    if _is_url(spec) or os.path.isabs(spec):
        return spec
    if os.path.exists(spec):
        return spec

    candidate = os.path.join("data", "nasa", spec)
    if os.path.exists(candidate):
        return candidate

    return spec


def _read_bytes(path_or_url: str) -> bytes:
    """Read bytes from local path or HTTP(S) URL."""
    if _is_url(path_or_url):
        with urllib.request.urlopen(path_or_url) as resp:  # nosec - maintainer-provided inputs
            return resp.read()
    if not os.path.exists(path_or_url):
        raise FileNotFoundError(path_or_url)
    with open(path_or_url, "rb") as f:
        return f.read()


def _maybe_unzip_csv(payload: bytes) -> Optional[str]:
    """If payload is a ZIP, extract and return first CSV as text."""
    if len(payload) >= 4 and payload[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            names = zf.namelist()
            csv_names = [n for n in names if n.lower().endswith(".csv")]
            pick = csv_names[0] if csv_names else (names[0] if names else None)
            if not pick:
                raise ValueError("ZIP file appears empty.")
            with zf.open(pick, "r") as f:
                data = f.read()
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("latin-1")
    return None


def _bytes_to_text(payload: bytes) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1")


def _parse_csv(text: str, var: Optional[str] = None) -> Timeseries:
    """
    Parse CSV text into Timeseries.
    Accepts:
      - header with 't' and u/v/w/p columns, using var if provided
      - or plain two-column rows (t,v)
    """
    if not text.strip():
        return Timeseries(t=[], v=[])

    text_norm = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text_norm))
    rows = list(reader)
    if not rows:
        return Timeseries(t=[], v=[])

    header = [h.strip().lower() for h in rows[0]]
    has_header = "t" in header

    value_idx: Optional[int] = None
    if has_header:
        i_t = header.index("t")
        if var and var.lower() in header:
            value_idx = header.index(var.lower())
        else:
            for k in ["v", "u", "w", "p"]:
                if k in header:
                    value_idx = header.index(k)
                    break
        if value_idx is None and len(header) > 1:
            value_idx = 1
        data_rows = rows[1:]
    else:
        i_t, value_idx = 0, 1
        data_rows = rows

    if value_idx is None:
        return Timeseries(t=[], v=[])

    T: List[float] = []
    V: List[float] = []
    for parts in data_rows:
        if len(parts) <= max(i_t, value_idx):
            continue
        try:
            tt = float(parts[i_t].strip())
            vv = float(parts[value_idx].strip())
        except Exception:
            continue
        T.append(tt)
        V.append(vv)

    return Timeseries(t=T, v=V)


def _filter_window(ts: Timeseries, t0: float, t1: float) -> Timeseries:
    if not ts.t or t1 <= t0:
        return ts
    T: List[float] = []
    V: List[float] = []
    for tt, vv in zip(ts.t, ts.v):
        if t0 <= tt <= t1:
            T.append(tt)
            V.append(vv)
    return Timeseries(t=T, v=V) if T else ts


# ---------- NetCDF probe ----------

def _probe_timeseries_from_netcdf(path: str, var: str, xyz: tuple[float, float, float]) -> Timeseries:
    """
    Open NASA DNS NetCDF and interpolate var at spatial point (x,y,z) over time.
    Normalizes common dim/coord aliases to canonical names: t, x, y, z.
    Resolves var (u/v/w/p) case-insensitively (e.g., U,V,W).
    """
    if xr is None:
        raise ImportError("xarray is required for NetCDF probing")

    # Open file
    try:
        ds = xr.open_dataset(path, engine="netcdf4")
    except Exception:
        # Fallback to default engine if netcdf4 not available
        ds = xr.open_dataset(path)

    # 1) Normalize dims/coords -> t,x,y,z
    alias_map = {
        "t": ["t", "time", "timesteps", "Time", "TIME"],
        "x": ["x", "xcoord", "xc", "X", "Xcoord", "XC"],
        "y": ["y", "ycoord", "yc", "Y", "Ycoord", "YC"],
        "z": ["z", "zcoord", "zc", "Z", "Zcoord", "ZC"],
    }
    rename_map: dict[str, str] = {}

    def pick_rename(canon: str) -> None:
        if canon in ds.dims or canon in ds.coords:
            return
        for a in alias_map[canon]:
            if a in ds.dims or a in ds.coords:
                rename_map[a] = canon
                return

    for canon in ["t", "x", "y", "z"]:
        pick_rename(canon)

    if rename_map:
        ds = ds.rename(rename_map)

    missing = [k for k in ["t", "x", "y", "z"] if (k not in ds.dims and k not in ds.coords)]
    if missing:
        raise KeyError(
            f"Missing required coords/dims after normalization: {missing}. "
            f"Available dims={list(ds.dims)}, coords={list(ds.coords)}"
        )

    # 2) Resolve variable name case-insensitively
    var_candidates = [var, var.lower(), var.upper(), var.capitalize()]
    vname: Optional[str] = None
    for cand in var_candidates:
        if cand in ds.data_vars:
            vname = cand
            break
    if vname is None:
        low = var.lower()
        for k in ds.data_vars:
            if k.lower() == low:
                vname = k
                break
    if vname is None:
        raise KeyError(f"Variable {var!r} not found. Available: {list(ds.data_vars)}")

    v = ds[vname]

    # 3) Interpolate at point (x,y,z) across all times
    for ax in ["t", "x", "y", "z"]:
        if ax not in v.coords and ax in ds.coords:
            v = v.assign_coords({ax: ds[ax]})

    try:
        vt = v.interp(x=xyz[0], y=xyz[1], z=xyz[2], method="linear")
    except Exception as e:
        ds.close()
        raise RuntimeError(f"Interpolation failed at xyz={xyz}: {e}")

    t = ds["t"].values
    vals = vt.values
    ds.close()

    # 4) Sanity: coerce to 1-D time series and sort if needed
    t = np.asarray(t).reshape(-1)
    vals = np.asarray(vals).reshape(-1)

    if t.size > 1 and np.any(np.diff(t) < 0):
        idx = np.argsort(t)
        t = t[idx]
        vals = vals[idx]

    mask = np.isfinite(t) & np.isfinite(vals)
    if not np.any(mask):
        raise ValueError("All interpolated values are NaN/Inf — probe may be outside the domain.")
    t = t[mask]
    vals = vals[mask]

    return Timeseries(t=t.astype(float).tolist(), v=vals.astype(float).tolist())


# ---------- public API ----------

def read_csv_timeseries(path_or_url: str, var: Optional[str] = None) -> Timeseries:
    target = _resolve_path_or_url(path_or_url)
    payload = _read_bytes(target)
    as_csv_text = _maybe_unzip_csv(payload)
    if as_csv_text is None:
        as_csv_text = _bytes_to_text(payload)
    ts = _parse_csv(as_csv_text, var=var)
    if not ts.t or not ts.v:
        raise ValueError(f"Parsed empty time series from: {target!r}")
    return ts


def fetch_timeseries(
    dataset: str, var: str, x: float, y: float, z: float,
    t0: float, t1: float, dt: float
) -> Timeseries:
    """
    Unified entry point.
    dataset:
      - CSV/ZIP file (local or URL)
      - NetCDF file (local or URL)
    var: variable name ('u','v','w','p')
    xyz: probe point
    t0,t1: time window
    dt: nominal step (not used yet)
    """
    path = _resolve_path_or_url(dataset)

    if path.lower().endswith((".nc", ".nc4", ".cdf")):
        ts = _probe_timeseries_from_netcdf(path, var, (x, y, z))
    else:
        ts = read_csv_timeseries(path, var=var)

    ts_w = _filter_window(ts, t0, t1)

    if ts_w.t and ts_w.t != sorted(ts_w.t):
        pairs = sorted(zip(ts_w.t, ts_w.v), key=lambda p: p[0])
        t_sorted, v_sorted = zip(*pairs)
        return Timeseries(t=list(t_sorted), v=list(v_sorted))

    return ts_w
