#!/usr/bin/env python3
"""
Clean pulses to a minimal schema.

We KEEP only:
  - title (str)
  - date  (str; inferred from filename if missing: 2025-08-12_example.yml -> "2025-08-12")
  - summary (str)
  - tags (list[str])
  - papers (list[str] or list[{title,url}])
  - podcasts (list[str])

We DROP everything else.

The script prints *every* file it considers and says exactly what it did.

Exit codes:
  --check : exit 1 if any file would change, else 0
  default : exit 0

"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import yaml

KEEP = ("title", "date", "summary", "tags", "papers", "podcasts")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


# ---------------- YAML IO ----------------

def load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARN] cannot read YAML: {path} -> {e}", file=sys.stderr)
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


# --------------- helpers -----------------

def as_str(x: Any) -> str:
    return "" if x is None else str(x).strip()


def ensure_list(x: Any) -> List[Any]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def flatten_once(seq: List[Any]) -> List[Any]:
    out: List[Any] = []
    for el in seq:
        if isinstance(el, list):
            out.extend(el)
        else:
            out.append(el)
    return out


def infer_date_from_filename(path: Path) -> str:
    m = DATE_RE.search(path.name)
    return m.group(1) if m else ""


def try_parse_stringified_dict(s: str) -> Union[Dict[str, Any], None]:
    s = s.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    # try JSON
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    # try single-quote dict as JSON
    try:
        s2 = s.replace("'", '"')
        obj = json.loads(s2)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def norm_paper_item(item: Any) -> Union[str, Dict[str, str], None]:
    if item is None:
        return None
    if isinstance(item, str):
        s = item.strip()
        if s.startswith("{") and s.endswith("}"):
            parsed = try_parse_stringified_dict(s)
            if parsed is not None:
                return norm_paper_item(parsed)
        return s
    if isinstance(item, dict):
        title = as_str(item.get("title"))
        url = as_str(item.get("url") or item.get("doi") or item.get("link"))
        if url and title:
            return {"title": title, "url": url}
        if url:
            return url
        return None
    # fallback: stringify
    s = as_str(item)
    return s if s else None


def norm_links(x: Any, *, papers: bool) -> List[Union[str, Dict[str, str]]]:
    items = ensure_list(x)
    if len(items) == 1 and isinstance(items[0], list):
        items = flatten_once(items)

    out: List[Union[str, Dict[str, str]]] = []
    for el in items:
        if isinstance(el, list):
            for sub in el:
                v = norm_paper_item(sub) if papers else as_str(sub)
                if v:
                    out.append(v)
        else:
            v = norm_paper_item(el) if papers else as_str(el)
            if v:
                out.append(v)

    # dedup while preserving order
    seen = set()
    dedup: List[Union[str, Dict[str, str]]] = []
    for v in out:
        key = json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, dict) else str(v)
        if key in seen:
            continue
        seen.add(key)
        dedup.append(v)
    return dedup


def norm_tags(x: Any) -> List[str]:
    items = ensure_list(x)
    out: List[str] = []
    for el in items:
        if isinstance(el, list):
            for sub in el:
                s = as_str(sub)
                if s:
                    out.append(s)
        elif isinstance(el, dict):
            for val in el.values():
                s = as_str(val)
                if s:
                    out.append(s)
        else:
            s = as_str(el)
            if s:
                out.append(s)
    # dedup preserve order
    seen = set()
    ret: List[str] = []
    for s in out:
        if s not in seen:
            seen.add(s)
            ret.append(s)
    return ret


def coerce_mapping(root: Any) -> Dict[str, Any]:
    if isinstance(root, dict):
        return root
    if isinstance(root, list):
        for el in root:
            if isinstance(el, dict):
                return el
        return {}
    return {}


def jsonish(x: Any) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def build_minimal(mapping: Dict[str, Any], path: Path) -> Dict[str, Any]:
    minimal: Dict[str, Any] = {}

    title = as_str(mapping.get("title"))
    if title:
        minimal["title"] = title

    date = as_str(mapping.get("date"))
    if not date:
        date = infer_date_from_filename(path)
    if date:
        minimal["date"] = date

    summary = as_str(mapping.get("summary"))
    if summary:
        minimal["summary"] = summary

    tags = norm_tags(mapping.get("tags"))
    if tags:
        minimal["tags"] = tags

    papers = norm_links(mapping.get("papers"), papers=True)
    if papers:
        minimal["papers"] = papers

    podcasts = norm_links(mapping.get("podcasts"), papers=False)
    if podcasts:
        minimal["podcasts"] = podcasts

    return minimal


def normalize_current_subset(mapping: Dict[str, Any], path: Path) -> Dict[str, Any]:
    subset = {k: mapping.get(k) for k in KEEP if k in mapping}
    return build_minimal(subset, path)


# --------------- sweep -------------------

def sweep(root: Path, write: bool) -> Tuple[int, int]:
    files = list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))
    files.sort()
    total = 0
    changed = 0

    print(f"[scan] found {len(files)} files under {root}/")

    for path in files:
        if not path.is_file():
            continue

        total += 1
        data = load_yaml(path)
        if data is None:
            print(f"[skip] {path} (unreadable)")
            continue

        mapping = coerce_mapping(data)
        minimal = build_minimal(mapping, path)
        current_kept = normalize_current_subset(mapping, path)

        extras = sorted(set(mapping.keys()) - set(KEEP))

        needs_trim = bool(extras)
        needs_update = (jsonish(minimal) != jsonish(current_kept))

        if write:
            if needs_trim or needs_update:
                dump_yaml(path, minimal)
                changed += 1
                what = []
                if needs_trim:
                    what.append(f"trim(-{', '.join(extras)})")
                if needs_update and not needs_trim:
                    what.append("update")
                print(f"[fixed] {path} :: {', '.join(what)}")
            else:
                print(f"[ok]   {path}")
        else:
            if needs_trim or needs_update:
                what = []
                if needs_trim:
                    what.append(f"trim(-{', '.join(extras)})")
                if needs_update and not needs_trim:
                    what.append("update")
                print(f"[would] {path} :: {', '.join(what)}")
            else:
                print(f"[ok]    {path}")

    return total, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes")
    ap.add_argument("--check", action="store_true", help="exit 1 if any file would change")
    args = ap.parse_args()

    pulse_root = Path("pulse")
    total, changed = sweep(pulse_root, write=args.write)
    print(f"\nScanned {total} files; {'changed' if args.write else 'would change'} {changed}.")

    if args.check:
        return 1 if changed > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
