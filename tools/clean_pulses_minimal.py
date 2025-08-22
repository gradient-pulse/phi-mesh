#!/usr/bin/env python3
"""
Clean pulses to a minimal schema AND prune auto-pulses:
- Minimal schema fields: title, date, summary, tags, papers, podcasts
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

ALLOWED_KEYS = {"title", "date", "summary", "tags", "papers", "podcasts"}

# ---------- helpers ----------
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

def coerce_minimal(d: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in ("title", "date", "summary", "tags", "papers", "podcasts"):
        if k in d:
            out[k] = d[k]
    # types
    out["tags"] = [str(t) for t in to_list(out.get("tags"))]
    out["papers"] = [str(u) if not isinstance(u, dict) else u for u in to_list(out.get("papers"))]
    out["podcasts"] = [str(u) if not isinstance(u, dict) else u for u in to_list(out.get("podcasts"))]
    return out

def parse_ts_from_name(name: str) -> datetime | None:
    """
    Try to parse timestamps from names like:
    20250813_170555_jhtdb_iso_1024.yml  or  jhtdb_iso_1024_2025-08-12_15-21-06Z.yml
    """
    # style A: 20250813_170555_...
    m = re.match(r"^(\d{8})_(\d{6})_", name)
    if m:
        try:
            return datetime.strptime(m.group(1)+m.group(2), "%Y%m%d%H%M%S")
        except Exception:
            pass
    # style B: ..._YYYY-MM-DD_HH-MM-SSZ.yml
    m = re.search(r"(\d{4}-\d{2}-\d{2})[_T](\d{2}-\d{2}-\d{2})(?:Z)?", name)
    if m:
        try:
            return datetime.strptime(m.group(1)+" "+m.group(2), "%Y-%m-%d %H-%M-%S")
        except Exception:
            pass
    return None

# ---------- 1) minimal cleanup ----------
def clean_minimal() -> None:
    changed = False
    for p in PULSE_DIR.rglob("*.yml"):
        # never rewrite inside archive
        if "/archive/" in str(p.as_posix()):
            continue
        try:
            data = load_yaml(p)
        except Exception as e:
            print(f"[warn] skip unreadable {p}: {e}")
            continue
        minimal = coerce_minimal(data)
        if minimal != data:
            dump_yaml(p, minimal)
            changed = True
            print(f"[fix] minimalized {p.relative_to(ROOT)}")
    if not changed:
        print("[ok] no minimal-schema changes")

# ---------- 2) prune older auto-pulses ----------
def prune_auto_keep_latest_n(n: int = KEEP_AUTO) -> None:
    if not AUTO_DIR.exists():
        print("[ok] no pulse/auto directory")
        return
    ARCHIVE_AUTO_DIR.mkdir(parents=True, exist_ok=True)

    files = [p for p in AUTO_DIR.glob("*.yml") if p.is_file()]
    if len(files) <= n:
        print(f"[ok] auto-pulses <= {n}; nothing to prune")
        return

    # sort newest first (filename timestamp if possible, else mtime)
    def sort_key(p: Path):
        ts = parse_ts_from_name(p.name)
        return ts or datetime.fromtimestamp(p.stat().st_mtime)

    files_sorted = sorted(files, key=sort_key, reverse=True)
    keep = files_sorted[:n]
    drop = files_sorted[n:]

    for p in drop:
        dest = ARCHIVE_AUTO_DIR / p.name
        # if name collision in archive, append suffix
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
