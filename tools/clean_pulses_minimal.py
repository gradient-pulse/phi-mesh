#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brutal pulse cleaner:
Keeps ONLY: title, date, summary, tags, papers, podcasts
• papers: list of URL strings or {title, url} dicts (normalized)
• podcasts: list of URL strings (normalized)
Everything else is discarded.
"""

from __future__ import annotations
import argparse, glob, os, re, sys, ast, datetime as dt
from typing import Any, Dict, List, Tuple
import yaml

ALLOW_KEYS = ("title", "date", "summary", "tags", "papers", "podcasts")
URL_RE = re.compile(r"^https?://", re.I)
YAML_OPTS = dict(allow_unicode=True, sort_keys=False, default_flow_style=False)

# ---------- IO ----------
def load_yaml(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def dump_yaml(path: str, data: Any, frontmatter: bool = True) -> None:
    with open(path, "w", encoding="utf-8") as f:
        if frontmatter:
            f.write("---\n")
        yaml.safe_dump(data, f, **YAML_OPTS)

# ---------- helpers ----------
def as_str(x: Any) -> str:
    if x is None: return ""
    if isinstance(x, (int, float)): return str(x)
    if isinstance(x, (dt.date, dt.datetime)): return x.isoformat()
    return str(x)

def parse_date(x: Any) -> str:
    if isinstance(x, (dt.date, dt.datetime)):
        return x.strftime("%Y-%m-%d")
    s = as_str(x).strip()
    if not s: return s
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        # leave as-is if not ISO parseable
        return s

def norm_tags(x: Any) -> List[str]:
    if isinstance(x, (list, tuple)):
        vals = [as_str(t).strip() for t in x if as_str(t).strip()]
    elif isinstance(x, str):
        vals = [p.strip() for p in x.split(",") if p.strip()]
    else:
        vals = []
    # dedup, preserve order
    seen, out = set(), []
    for t in vals:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def _literal_eval_if_dict_string(s: str) -> Any:
    try:
        v = ast.literal_eval(s)
        return v
    except Exception:
        return s

def _norm_paper_item(it: Any) -> Dict[str, Any] | str | None:
    """
    Accept:
      - URL string -> keep as string
      - dict with url (and optional title) -> {title?, url}
      - stringified dict -> parse and treat like dict
    """
    if it is None:
        return None
    if isinstance(it, str):
        s = it.strip()
        if URL_RE.match(s):
            return s
        val = _literal_eval_if_dict_string(s)
        if isinstance(val, dict):
            return _norm_paper_item(val)
        return None
    if isinstance(it, dict):
        url = it.get("url") or it.get("href")
        title = it.get("title")
        if isinstance(url, str) and URL_RE.match(url.strip()):
            url = url.strip()
            if isinstance(title, str) and title.strip():
                return {"title": title.strip(), "url": url}
            return url
        return None
    return None

def _norm_url_item(it: Any) -> str | None:
    if isinstance(it, str) and URL_RE.match(it.strip()):
        return it.strip()
    if isinstance(it, dict):
        # permissive: dict with url → take it
        u = it.get("url") or it.get("href")
        if isinstance(u, str) and URL_RE.match(u.strip()):
            return u.strip()
    if isinstance(it, str):
        # stringified dict?
        val = _literal_eval_if_dict_string(it)
        return _norm_url_item(val) if val is not it else None
    return None

def norm_papers(x: Any) -> List[Any]:
    out: List[Any] = []
    seq = x if isinstance(x, (list, tuple)) else [x]
    for it in seq:
        v = _norm_paper_item(it)
        if v is not None:
            out.append(v)
    # dedup (string URLs only; dicts dedup by (title,url))
    seen = set(); dedup: List[Any] = []
    for v in out:
        key = v if isinstance(v, str) else ("__obj__", v.get("title",""), v.get("url",""))
        if key not in seen:
            seen.add(key); dedup.append(v)
    return dedup

def norm_podcasts(x: Any) -> List[str]:
    out: List[str] = []
    seq = x if isinstance(x, (list, tuple)) else [x]
    for it in seq:
        u = _norm_url_item(it)
        if u: out.append(u)
    # dedup
    seen=set(); dedup=[]
    for u in out:
        if u not in seen:
            seen.add(u); dedup.append(u)
    return dedup

# ---------- core ----------
def to_minimal(path: str, data: Any, verbose: bool=False) -> Tuple[Dict[str, Any], List[str]]:
    removed: List[str] = []
    if not isinstance(data, dict):
        # fallback minimal shell
        minimal = {
            "title": os.path.splitext(os.path.basename(path))[0].replace("_", " "),
            "date": "",
            "summary": as_str(data),
            "tags": [],
            "papers": [],
            "podcasts": [],
        }
        return minimal, ["(non-mapping YAML → replaced entirely)"]

    # compute what we'll drop
    for k in list(data.keys()):
        if k not in ALLOW_KEYS:
            removed.append(k)

    # Build strictly minimal record
    minimal: Dict[str, Any] = {
        "title"   : as_str(data.get("title")).strip(),
        "date"    : parse_date(data.get("date")),
        "summary" : as_str(data.get("summary")).strip(),
        "tags"    : norm_tags(data.get("tags")),
        "papers"  : norm_papers(data.get("papers", [])),
        "podcasts": norm_podcasts(data.get("podcasts", [])),
    }

    # Guarantee keys appear in canonical order and nothing else remains
    minimal = {k: minimal[k] for k in ALLOW_KEYS}

    if verbose:
        # show a tiny diff overview
        if removed:
            print(f"  removed keys: {', '.join(sorted(removed))}")
        # show coercions
        if data.get("date") and minimal["date"] != as_str(data.get("date")).strip():
            print(f"  coerced date: {as_str(data.get('date'))!r} -> {minimal['date']!r}")
    return minimal, removed

def process_file(path: str, write: bool, verbose: bool) -> Tuple[bool, str]:
    try:
        data = load_yaml(path)
    except Exception as e:
        return False, f"[skip load ] {path}  ({e})"

    minimal, removed = to_minimal(path, data, verbose=verbose)

    # If write, always overwrite (to forcefully strip clutter)
    if write:
        dump_yaml(path, minimal, frontmatter=True)
        return True, f"[cleaned   ] {path}"
    else:
        # Dry-run: just say what would happen
        prefix = "[would clean]" if removed or True else "[ok        ]"
        return True, f"{prefix} {path}"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes")
    ap.add_argument("--glob", default="pulse/**/*.yml", help="glob for pulses")
    ap.add_argument("--verbose", action="store_true", help="print what changed")
    args = ap.parse_args()

    paths = sorted(glob.glob(args.glob, recursive=True))
    if not paths:
        print("No pulses found.")
        return 0

    changed_any = False
    for p in paths:
        ch, msg = process_file(p, write=args.write, verbose=args.verbose)
        print(msg)
        changed_any = changed_any or ch

    return 0

if __name__ == "__main__":
    sys.exit(main())
