#!/usr/bin/env python3
"""
Clean pulses to a minimal schema AND prune auto-pulses:

Minimal schema (live pulses):
- title, summary, tags, papers, podcasts, links
  * 'date' is intentionally dropped (validator derives date from filename)
  * 'links' may contain URLs OR repo-relative paths (kept as strings)

Prune auto-pulses:
- Keep only the latest N auto pulses (default 3); move older ones to pulse/archive/auto/
"""

from __future__ import annotations
import sys, os, shutil, re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
PULSE_DIR = ROOT / "pulse"
AUTO_DIR = PULSE_DIR / "auto"
ARCHIVE_AUTO_DIR = PULSE_DIR / "archive" / "auto"

KEEP_AUTO = int(os.environ.get("KEEP_AUTO_PULSES", "3"))

# --------- helpers ---------
def load_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def dump_yaml(p: Path, data: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def to_list(x: Any) -> List[Any]:
    if x is None: return []
    if isinstance(x, list): return x
    return [x]

_URL = re.compile(r"^(https?://|https://doi.org/|doi:)", re.I)
_REL = re.compile(r"""^(
    (\.\./|\./|/)?                # optional relative/absolute prefix
    [A-Za-z0-9._\-/]+             # path body
    (\.[A-Za-z0-9]{1,8})?         # optional short extension
)$""", re.X)

def _norm_url_list(lst: Any) -> List[str]:
    """
    Convert papers/podcasts to list[str] of URLs only.
    - string → kept if URL
    - dict   → keep dict['url'] if URL
    - others → dropped
    """
    out: List[str] = []
    for item in to_list(lst):
        if isinstance(item, str):
            s = item.strip()
            if s and _URL.match(s):
                out.append(s)
        elif isinstance(item, dict):
            s = str(item.get("url") or "").strip()
            if s and _URL.match(s):
                out.append(s)
    return out

def _norm_links_list(lst: Any) -> List[str]:
    """
    Convert links to list[str] allowing URL or repo-relative path.
    - string → keep if URL or REL
    - dict   → try url/href/path, keep if URL or REL
    """
    out: List[str] = []
    seen = set()
    for item in to_list(lst):
        s = ""
        if isinstance(item, str):
            s = item.strip()
        elif isinstance(item, dict):
            s = (item.get("url") or item.get("href") or item.get("path") or "").strip()
        if not s:
            continue
        if not (_URL.match(s) or _REL.match(s)):
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out

# --------- 1) minimal cleanup ---------
def clean_minimal() -> None:
    changed = False
    for p in PULSE_DIR.rglob("*.yml"):
        try:
            data = load_yaml(p)
        except Exception as e:
            print(f"[warn] skip unreadable {p}: {e}")
            continue

        # Build minimal dict
        out: Dict[str, Any] = {}

        # Required
        if "title" in data:   out["title"]   = data["title"]
        if "summary" in data: out["summary"] = data["summary"]
        if "tags" in data:    out["tags"]    = [str(t).strip() for t in to_list(data.get("tags")) if str(t).strip()]

        # Resources
        out["papers"]   = _norm_url_list(data.get("papers"))
        out["podcasts"] = _norm_url_list(data.get("podcasts"))
        # Optional generic links (URLs or repo-relative)
        if "links" in data:
            out["links"] = _norm_links_list(data.get("links"))

        # Explicitly drop 'date' (validator forbids it in live pulses)

        # Only rewrite if changes
        if out != data:
            dump_yaml(p, out)
            changed = True
            print(f"[fix] minimalized {p.relative_to(ROOT)}")
    if not changed:
        print("[ok] no minimal-schema changes")

# --------- 2) prune older auto-pulses ---------
def parse_ts_from_name(name: str) -> datetime | None:
    """
    Try to parse timestamps from names like:
    20250813_170555_jhtdb_iso_1024.yml  or  jhtdb_iso_1024_2025-08-12_15-21-06Z.yml
    """
    m = re.match(r"^(\d{8})_(\d{6})_", name)
    if m:
        try:
            return datetime.strptime(m.group(1)+m.group(2), "%Y%m%d%H%M%S")
        except Exception:
            pass
    m = re.search(r"(\d{4}-\d{2}-\d{2})[_T](\d{2}-\d{2}-\d{2})(?:Z)?", name)
    if m:
        try:
            return datetime.strptime(m.group(1)+" "+m.group(2), "%Y-%m-%d %H-%M-%S")
        except Exception:
            pass
    return None

def prune_auto_keep_latest_n(n: int = KEEP_AUTO) -> None:
    if not AUTO_DIR.exists():
        print("[ok] no pulse/auto directory")
        return
    ARCHIVE_AUTO_DIR.mkdir(parents=True, exist_ok=True)

    files = [p for p in AUTO_DIR.glob("*.yml") if p.is_file()]
    if len(files) <= n:
        print(f"[ok] auto-pulses <= {n}; nothing to prune")
        return

    def sort_key(p: Path):
        ts = parse_ts_from_name(p.name)
        return ts or datetime.fromtimestamp(p.stat().st_mtime)

    files_sorted = sorted(files, key=sort_key, reverse=True)
    keep = files_sorted[:n]
    drop = files_sorted[n:]

    for p in drop:
        dest = ARCHIVE_AUTO_DIR / p.name
        i = 1
        while dest.exists():
            dest = ARCHIVE_AUTO_DIR / f"{p.stem}__dup{i}{p.suffix}"
            i += 1
        shutil.move(str(p), str(dest))
        print(f"[archive] {p.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")

    print(f"[ok] kept {len(keep)} newest auto-pulses, archived {len(drop)} older ones")

def main():
    clean_minimal()
    prune_auto_keep_latest_n()

if __name__ == "__main__":
    main()
