#!/usr/bin/env python3
"""
Clean pulses to a minimal schema:

kept keys only:
  - title (str)
  - date (str; ISO-like if present)
  - summary (str)
  - tags (list[str])
  - papers (list[str or {title,url}])
  - podcasts (list[str])

Everything else is dropped.
Also fixes common issues:
  - nested lists under papers/podcasts (e.g., "- - https://…")
  - stringified dicts in papers (e.g., "{'title': '…', 'url': '…'}")
  - non-dict YAML roots (coerces first mapping if YAML is a list)
"""

from __future__ import annotations
import argparse, glob, json, sys, re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

import yaml

KEEP = ("title", "date", "summary", "tags", "papers", "podcasts")

# ---------- YAML utilities ----------

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

# ---------- normalizers ----------

def _ensure_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]

def _flatten_once(seq: List[Any]) -> List[Any]:
    """If a single nested list like [ [item, item] ] or [ [item], [item] ] → flatten."""
    out = []
    for el in seq:
        if isinstance(el, list):
            out.extend(el)
        else:
            out.append(el)
    return out

def _as_iso_date(x: Any) -> str:
    if not x:
        return ""
    if isinstance(x, datetime):
        return x.date().isoformat()
    s = str(x).strip()
    # keep as-is if already looks like ISO date or datetime
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s
    return s  # don’t invent dates

def _as_string(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()

def _parse_stringified_dict(s: str) -> Union[Dict[str, Any], None]:
    s = s.strip()
    # try JSON first
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    # try very simple python-ish dict: {'key': 'val', "k": "v"}
    if s.startswith("{") and s.endswith("}"):
        try:
            # convert single quotes to double carefully
            s2 = re.sub(r"'", '"', s)
            obj = json.loads(s2)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None
    return None

def _norm_paper_item(item: Any) -> Union[str, Dict[str, str], None]:
    """
    Accept:
      - url string
      - {title,url}
      - stringified dict
    Return either url string, or {title,url}
    """
    if item is None:
        return None
    if isinstance(item, str):
        s = item.strip()
        if s.startswith("{") and s.endswith("}"):
            parsed = _parse_stringified_dict(s)
            if parsed:
                return _norm_paper_item(parsed)
        # plain URL-ish
        return s
    if isinstance(item, dict):
        title = _as_string(item.get("title", ""))
        url = _as_string(item.get("url", ""))
        # tolerate doi/doi_url, link
        if not url:
            url = _as_string(item.get("doi") or item.get("link") or "")
        if url and title:
            return {"title": title, "url": url}
        if url:
            return url
        # neither url nor title → skip
        return None
    # unexpected → stringify if looks like a url
    return _as_string(item)

def _norm_link_list(x: Any, *, as_papers: bool) -> List[Union[str, Dict[str, str]]]:
    items = _ensure_list(x)
    # fix common "- - url" accidental nesting
    if len(items) == 1 and isinstance(items[0], list):
        items = _flatten_once(items)
    out: List[Union[str, Dict[str, str]]] = []
    for el in items:
        if isinstance(el, list):  # additional accidental nesting
            for sub in el:
                v = _norm_paper_item(sub) if as_papers else _as_string(sub)
                if v:
                    out.append(v)
        else:
            v = _norm_paper_item(el) if as_papers else _as_string(el)
            if v:
                out.append(v)
    # de-dup while preserving order
    seen = set()
    deduped: List[Union[str, Dict[str, str]]] = []
    for v in out:
        key = json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, dict) else str(v)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(v)
    return deduped

def _norm_tags(x: Any) -> List[str]:
    tags = _ensure_list(x)
    out = []
    for t in tags:
        if isinstance(t, (list, dict)):
            out.extend(_ensure_list(t))
        else:
            s = _as_string(t)
            if s:
                out.append(s)
    # normalize quirky "quoted" tags like 'NT (Narrative_Tick)'
    # (we keep the literal as-is, just strip surrounding quotes)
    out = [s.strip() for s in out]
    # stable de-dup
    seen = set(); deduped=[]
    for s in out:
        if s not in seen:
            seen.add(s); deduped.append(s)
    return deduped

def build_minimal(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct minimal mapping; only include keys that exist and are non-empty after normalization.
    """
    minimal: Dict[str, Any] = {}

    title = _as_string(data.get("title"))
    if title:
        minimal["title"] = title

    date = _as_iso_date(data.get("date"))
    if date:
        minimal["date"] = date

    summary = _as_string(data.get("summary"))
    if summary:
        minimal["summary"] = summary

    tags = _norm_tags(data.get("tags"))
    if tags:
        minimal["tags"] = tags

    papers = _norm_link_list(data.get("papers"), as_papers=True)
    if papers:
        minimal["papers"] = papers

    podcasts = _norm_link_list(data.get("podcasts"), as_papers=False)
    if podcasts:
        minimal["podcasts"] = podcasts

    return minimal

def coerce_mapping(root: Any) -> Dict[str, Any]:
    """
    Ensure we’re working with a mapping.
    - dict → return
    - list → use first mapping item if present, else {}
    - None/other → {}
    """
    if isinstance(root, dict):
        return root
    if isinstance(root, list):
        for el in root:
            if isinstance(el, dict):
                return el
        return {}
    return {}

# ---------- main sweep ----------

def sweep(paths: List[Path], write: bool) -> Tuple[int, int]:
    total = 0
    changed = 0
    for path in paths:
        if not path.is_file():
            continue
        total += 1
        data = load_yaml(path)
        if data is None:
            print(f"[skip] {path} (unreadable YAML)")
            continue
        mapping = coerce_mapping(data)
        minimal = build_minimal(mapping)

        # Decide if we should write:
        # 1) always rewrite if mapping has keys outside KEEP (i.e., extra noise)
        # 2) or if minimal (what we keep) differs from current kept subset
        current_kept = {k: mapping.get(k) for k in KEEP if k in mapping}
        extras = sorted(set(mapping.keys()) - set(KEEP))

        must_write = bool(extras) or (_jsonish(minimal) != _jsonish(normalize_current(current_kept)))

        if not must_write:
            print(f"[ok     ] {path}")
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
                print(f"[would trim] {path}  (-{', '.join(extras)})")
            else:
                print(f"[would update] {path}")
    return total, changed

def normalize_current(d: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize the *current kept* view the same way we normalize minimal, to compare fairly."""
    # Re-run our normalizers so the comparison is apples-to-apples.
    return build_minimal(d)

def _jsonish(x: Any) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes")
    args = ap.parse_args()

    globs = ["pulse/**/*.yml", "pulse/**/*.yaml"]
    paths = [Path(p) for g in globs for p in glob.glob(g, recursive=True)]

    total, changed = sweep(paths, write=args.write)
    print(f"\nScanned {total} pulse files; {'changed' if args.write else 'would change'} {changed}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
