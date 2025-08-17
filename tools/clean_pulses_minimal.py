#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean pulses to a minimal schema:
  title (str), date (YYYY-MM-DD), summary (str), tags ([str]),
  papers ([url str]), podcasts ([url str])

It also tolerates a variety of legacy shapes and stringified dicts.
"""

from __future__ import annotations
import argparse
import os
import re
import sys
import glob
import datetime as dt
from collections import OrderedDict
from typing import Any, Dict, List, Tuple
import yaml
import ast

YAML_OPTS = dict(allow_unicode=True, sort_keys=False, default_flow_style=False)

URL_RE = re.compile(r'^https?://', re.I)

def load_yaml(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def dump_yaml(path: str, data: Any) -> None:
    """Dump plain-Python data (no OrderedDicts)."""
    def to_plain(obj):
        if isinstance(obj, OrderedDict):
            return {k: to_plain(v) for k, v in obj.items()}
        if isinstance(obj, dict):
            return {k: to_plain(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_plain(x) for x in obj]
        return obj

    plain = to_plain(data)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(plain, f, **YAML_OPTS)

def as_str(x: Any) -> str:
    if x is None: return ""
    if isinstance(x, (int, float)): return str(x)
    if isinstance(x, (dt.date, dt.datetime)): return x.isoformat()
    return str(x)

def parse_date(x: Any) -> str:
    """Return YYYY-MM-DD if possible; otherwise raw string."""
    if isinstance(x, dt.datetime) or isinstance(x, dt.date):
        return x.strftime('%Y-%m-%d')
    s = as_str(x).strip()
    if not s:
        return s
    # accept YYYY-MM-DD or full ISO 8601
    try:
        return dt.datetime.fromisoformat(s.replace('Z','+00:00')).date().isoformat()
    except Exception:
        return s

def norm_tag(t: Any) -> str:
    s = as_str(t).strip()
    return s

def norm_tag_list(x: Any) -> List[str]:
    out: List[str] = []
    if isinstance(x, (list, tuple)):
        for t in x:
            s = norm_tag(t)
            if s:
                out.append(s)
    elif isinstance(x, str):
        # Split on commas if someone put "a, b, c"
        parts = [p.strip() for p in x.split(',')]
        out.extend([p for p in parts if p])
    return list(dict.fromkeys(out))  # dedup keep order

def _maybe_literal_eval(s: str) -> Any:
    try:
        return ast.literal_eval(s)
    except Exception:
        return s

def _extract_url(item: Any) -> str | None:
    """
    Accept:
      - string URL
      - dict with 'url'
      - stringified dict "{'title':..., 'url':...}"
    Return the URL or None.
    """
    if item is None:
        return None
    if isinstance(item, str):
        s = item.strip()
        if URL_RE.match(s):
            return s
        # stringified dict?
        val = _maybe_literal_eval(s)
        if isinstance(val, dict):
            u = val.get('url') or val.get('href')
            if isinstance(u, str) and URL_RE.match(u):
                return u
        return None
    if isinstance(item, dict) or isinstance(item, OrderedDict):
        u = item.get('url') or item.get('href')
        if isinstance(u, str) and URL_RE.match(u):
            return u
        # Sometimes dicts are notes only → ignore
        return None
    # Unknown type → ignore
    return None

def norm_url_list(x: Any) -> List[str]:
    out: List[str] = []
    if isinstance(x, (list, tuple)):
        for it in x:
            u = _extract_url(it)
            if u:
                out.append(u.strip())
    elif isinstance(x, str):
        # Could be a single URL or a stringified dict
        u = _extract_url(x)
        if u:
            out.append(u.strip())
    return list(dict.fromkeys(out))

def to_minimal(path: str, data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        # Give up and keep raw – but wrap into minimal shape
        return {
            "title": os.path.splitext(os.path.basename(path))[0].replace('_',' ').strip(),
            "date": "",
            "summary": as_str(data),
            "tags": [],
            "papers": [],
            "podcasts": [],
        }

    title   = as_str(data.get("title")).strip()
    date    = parse_date(data.get("date"))
    summary = as_str(data.get("summary")).strip()
    tags    = norm_tag_list(data.get("tags"))
    papers  = norm_url_list(data.get("papers"))
    pods    = norm_url_list(data.get("podcasts"))

    # If nothing in papers/podcasts but some URLs live under 'links' or 'resources'
    links = data.get("links") or data.get("resources")
    if (not papers) and links:
        papers = norm_url_list(links)

    # Minimal schema
    minimal = OrderedDict()
    minimal["title"] = title
    minimal["date"] = date
    minimal["summary"] = summary
    minimal["tags"] = tags
    minimal["papers"] = papers
    minimal["podcasts"] = pods
    return minimal

def process_file(path: str, write: bool) -> Tuple[bool, str]:
    try:
        data = load_yaml(path)
    except Exception as e:
        return False, f"[skip load ] {path}  ({e})"

    minimal = to_minimal(path, data)

    # Compare with on-disk if possible
    if write:
        dump_yaml(path, minimal)
        return True, f"[fixed     ] {path}"
    else:
        # Just report what would change
        return True, f"[would-fix ] {path}"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='apply changes')
    ap.add_argument('--check', action='store_true', help='just report')
    ap.add_argument('--glob', default='pulse/**/*.yml', help='glob for pulses')
    args = ap.parse_args()

    paths = sorted(glob.glob(args.glob, recursive=True))
    changed_any = False
    for path in paths:
        ch, msg = process_file(path, write=args.write)
        print(msg)
        changed_any = changed_any or (ch and args.write)

    return 0

if __name__ == "__main__":
    sys.exit(main())
