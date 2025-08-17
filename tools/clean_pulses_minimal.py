#!/usr/bin/env python3
"""
Clean pulses to a minimal schema:

kept keys only:
  - title (str)
  - date (str; inferred from filename if missing, e.g. 2025-08-12_foo.yml -> "2025-08-12")
  - summary (str)
  - tags (list[str])
  - papers (list[str or {title,url}])
  - podcasts (list[str])

Everything else is dropped.

Also fixes:
  - nested lists under papers/podcasts (e.g., "- - https://…")
  - stringified dicts in papers (e.g., "{'title':'…','url':'…'}")
  - non-dict YAML roots (uses first mapping if YAML is a list)
"""

from __future__ import annotations
import argparse, glob, json, re, sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
import yaml

KEEP = ("title", "date", "summary", "tags", "papers", "podcasts")

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

# ---------- YAML I/O ----------

def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] YAML load failed for {path}: {e}", file=sys.stderr)
            return None

def dump_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=88,
            default_flow_style=False,
        )

# ---------- helpers ----------

def _ensure_list(x: Any) -> List[Any]:
    if x is None: return []
    return x if isinstance(x, list) else [x]

def _flatten_once(seq: List[Any]) -> List[Any]:
    out = []
    for el in seq:
        if isinstance(el, list): out.extend(el)
        else: out.append(el)
    return out

def _as_string(x: Any) -> str:
    if x is None: return ""
    return str(x).strip()

def infer_date_from_filename(path: Path) -> str:
    m = DATE_RE.search(path.name)
    return m.group(1) if m else ""

def parse_stringified_dict(s: str) -> Union[Dict[str, Any], None]:
    s = s.strip()
    # Try JSON
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    # Try simple python-ish dict -> convert quotes and load as JSON
    if s.startswith("{") and s.endswith("}"):
        try:
            s2 = re.sub(r"'", '"', s)
            obj = json.loads(s2)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
    return None

def norm_paper_item(item: Any) -> Union[str, Dict[str, str], None]:
    if item is None: return None
    if isinstance(item, str):
        s = item.strip()
        if s.startswith("{") and s.endswith("}"):
            parsed = parse_stringified_dict(s)
            if parsed: return norm_paper_item(parsed)
        return s
    if isinstance(item, dict):
        title = _as_string(item.get("title"))
        url = _as_string(item.get("url") or item.get("doi") or item.get("link"))
        if url and title: return {"title": title, "url": url}
        if url: return url
        return None
    return _as_string(item)

def norm_link_list(x: Any, *, as_papers: bool) -> List[Union[str, Dict[str, str]]]:
    items = _ensure_list(x)
    if len(items) == 1 and isinstance(items[0], list):
        items = _flatten_once(items)
    out: List[Union[str, Dict[str, str]]] = []
    for el in items:
        if isinstance(el, list):
            for sub in el:
                v = norm_paper_item(sub) if as_papers else _as_string(sub)
                if v: out.append(v)
        else:
            v = norm_paper_item(el) if as_papers else _as_string(el)
            if v: out.append(v)
    # de-dup
    seen = set(); dedup=[]
    for v in out:
        key = json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, dict) else str(v)
        if key in seen: continue
        seen.add(key); dedup.append(v)
    return dedup

def norm_tags(x: Any) -> List[str]:
    tags = _ensure_list(x)
    out: List[str] = []
    for t in tags:
        if isinstance(t, (list, dict)):
            for s in _ensure_list(t):
                s2 = _as_string(s)
                if s2: out.append(s2)
        else:
            s = _as_string(t)
            if s: out.append(s)
    # de-dup stable
    seen=set(); dedup=[]
    for s in out:
        if s not in seen:
            seen.add(s); dedup.append(s)
    return dedup

def coerce_mapping(root: Any) -> Dict[str, Any]:
    if isinstance(root, dict): return root
    if isinstance(root, list):
        for el in root:
            if isinstance(el, dict): return el
        return {}
    return {}

def build_minimal(mapping: Dict[str, Any], path: Path) -> Dict[str, Any]:
    minimal: Dict[str, Any] = {}
    title = _as_string(mapping.get("title"))
    if title: minimal["title"] = title

    date = _as_string(mapping.get("date"))
    if not date:
        date = infer_date_from_filename(path)
    if date: minimal["date"] = date

    summary = _as_string(mapping.get("summary"))
    if summary: minimal["summary"] = summary

    tags = norm_tags(mapping.get("tags"))
    if tags: minimal["tags"] = tags

    papers = norm_link_list(mapping.get("papers"), as_papers=True)
    if papers: minimal["papers"] = papers

    podcasts = norm_link_list(mapping.get("podcasts"), as_papers=False)
    if podcasts: minimal["podcasts"] = podcasts

    return minimal

def normalize_current_subset(mapping: Dict[str, Any], path: Path) -> Dict[str, Any]:
    subset = {k: mapping.get(k) for k in KEEP if k in mapping}
    return build_minimal(subset, path)

def jsonish(x: Any) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False)

# ---------- sweep ----------

def sweep(paths: List[Path], write: bool) -> Tuple[int, int]:
    total = 0
    changed = 0
    for path in paths:
        if not path.is_file(): continue
        total += 1
        data = load_yaml(path)
        if data is None:
            print(f"[skip]    {path} (unreadable)")
            continue
        mapping = coerce_mapping(data)
        minimal = build_minimal(mapping, path)

        current_kept = normalize_current_subset(mapping, path)
        extras = sorted(set(mapping.keys()) - set(KEEP))
        must_write = bool(extras) or (jsonish(minimal) != jsonish(current_kept))

        if not must_write:
            print(f"[ok]      {path}")
            continue

        if write:
            dump_yaml(path, minimal)
            changed += 1
            if extras:
                print(f"[trimmed] {path}  (-{', '.join(extras)})")
            else:
                print(f"[updated] {path}")
        else:
            if extras:
                print(f"[would]   {path}  trim (-{', '.join(extras)})")
            else:
                print(f"[would]   {path}  update")
    return total, changed

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes")
    ap.add_argument("--check", action="store_true", help="exit 1 if changes would be made (no write)")
    args = ap.parse_args()

    globs = ["pulse/**/*.yml", "pulse/**/*.yaml"]
    paths = [Path(p) for g in globs for p in glob.glob(g, recursive=True)]

    total, changed = sweep(paths, write=args.write)
    print(f"\nScanned {total} pulse files; {'changed' if args.write else 'would change'} {changed}.")

    if args.check:
        return 1 if changed > 0 else 0
    return 0

if __name__ == "__main__":
    sys.exit(main())
