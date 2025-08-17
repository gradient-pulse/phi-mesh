#!/usr/bin/env python3
"""
Clean Phi-Mesh pulses down to minimal schema.

Keeps only:
  - title
  - date
  - summary
  - tags
  - papers (urls or {title,url})
  - podcasts (urls)
"""

import sys, glob, os, argparse, datetime
from typing import Any, Dict, List, Tuple
import yaml

# ----------------------------------------------------------------------
# helpers

def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def dump_yaml(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )

def _flatten(seq):
    for el in seq:
        if isinstance(el, (list, tuple)):
            yield from _flatten(el)
        else:
            yield el

def _as_list(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(_flatten(x))
    return [x]

def _norm_date(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, datetime.date):
        return val.isoformat()
    return str(val)

def _norm_str(val: Any) -> str:
    return (val or "").strip()

def _norm_url_item(it: Any) -> str:
    if it is None:
        return ""
    if isinstance(it, str):
        return it.strip()
    if isinstance(it, dict):
        # if dict with url key
        u = it.get("url")
        if isinstance(u, str):
            return u.strip()
    return str(it)

def _norm_paper_item(it: Any) -> Any:
    if it is None:
        return None
    if isinstance(it, str):
        return it.strip()
    if isinstance(it, dict):
        t = _norm_str(it.get("title"))
        u = _norm_str(it.get("url"))
        if u:
            if t:
                return {"title": t, "url": u}
            return u
    return None

def norm_papers(x: Any) -> List[Any]:
    out: List[Any] = []
    for it in _as_list(x):
        v = _norm_paper_item(it)
        if v is not None:
            out.append(v)
    return out

def norm_podcasts(x: Any) -> List[str]:
    out: List[str] = []
    for it in _as_list(x):
        u = _norm_url_item(it)
        if u:
            out.append(u)
    return out

# ----------------------------------------------------------------------
# core

def to_minimal(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": _norm_str(data.get("title")),
        "date": _norm_date(data.get("date")),
        "summary": _norm_str(data.get("summary")),
        "tags": list(_as_list(data.get("tags"))),
        "papers": norm_papers(data.get("papers")),
        "podcasts": norm_podcasts(data.get("podcasts")),
    }

def process_file(path: str, write: bool, verbose: bool) -> Tuple[bool, str]:
    try:
        data = load_yaml(path)
        if not isinstance(data, dict):
            return False, "not a dict"
        minimal = to_minimal(path, data)
        changed = minimal != data
        if write and changed:
            dump_yaml(path, minimal)
        return changed, "cleaned" if changed else "ok"
    except Exception as e:
        return False, f"error: {e}"

def collect_pulse_paths() -> List[str]:
    patterns = ["pulse/**/*.yml", "pulse/**/*.yaml"]
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(pat, recursive=True))
    seen = set()
    out = []
    for p in sorted(paths):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

# ----------------------------------------------------------------------
# main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write cleaned files")
    ap.add_argument("--verbose", action="store_true", help="print details")
    args = ap.parse_args()

    paths = collect_pulse_paths()
    print(f"[info] found {len(paths)} pulse files")

    any_change = False
    for path in paths:
        changed, status = process_file(path, args.write, args.verbose)
        if changed:
            any_change = True
        if args.verbose:
            print(f"[{status:9}] {path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
