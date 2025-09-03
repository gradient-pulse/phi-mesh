# tools/fd_connectors/nasa.py
from dataclasses import dataclass
from typing import List, Optional
import os
import io
import csv

try:
    # urllib is fine in GH Actions; we avoid requests to keep deps minimal
    from urllib.request import urlopen  # type: ignore
except Exception:
    urlopen = None  # offline or sandboxed

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def _looks_like_inline_csv(s: str) -> bool:
    # crude but effective: must contain a newline and a comma, usually a header "t,v"
    return ("\n" in s) and ("," in s) and not os.path.exists(s) and not s.lower().startswith(("http://", "https://"))

def _read_csv_text(text: str) -> Timeseries:
    f = io.StringIO(text)
    reader = csv.DictReader(f)
    t, v = [], []
    for row in reader:
        # tolerate different header casing/spaces
        tt = row.get("t") or row.get("T") or row.get(" time ") or row.get("time")
        vv = row.get("v") or row.get("V") or row.get("value")
        if tt is None or vv is None:
            continue
        try:
            t.append(float(tt))
            v.append(float(vv))
        except ValueError:
            # skip bad lines
            continue
    return Timeseries(t=t, v=v)

def read_csv_timeseries(path_or_url: Optional[str] = None) -> Timeseries:
    """
    Read a 2-column CSV (header 't,v') as a time series.
    - path_or_url: repo-relative path, absolute path, http(s) URL, or inline CSV string.
    - if None, uses env NASA_CSV (same semantics).
    """
    target = (path_or_url or "").strip() or os.getenv("NASA_CSV", "").strip()
    if not target:
        raise ValueError("NASA CSV not provided: set workflow input or NASA_CSV secret.")

    # Inline CSV content?
    if _looks_like_inline_csv(target):
        return _read_csv_text(target)

    # File path?
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            return _read_csv_text(f.read())

    # URL?
    if target.lower().startswith(("http://", "https://")):
        if urlopen is None:
            raise RuntimeError("urllib not available to fetch URL; provide a file path or inline CSV.")
        with urlopen(target) as resp:  # type: ignore[attr-defined]
            data = resp.read().decode("utf-8", errors="replace")
            return _read_csv_text(data)

    # Last attempt: treat as repo-relative path (useful if runner CWD differs)
    repo_path = os.path.join(os.getcwd(), target)
    if os.path.exists(repo_path):
        with open(repo_path, "r", encoding="utf-8") as f:
            return _read_csv_text(f.read())

    raise FileNotFoundError(f"NASA CSV not found or unreadable: {target!r}")

def list_datasets() -> List[str]:
    # Placeholder; you can expand with known NASA CFD dataset names later
    return ["cfd_demo"]
