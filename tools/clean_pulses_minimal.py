#!/usr/bin/env python3
"""
Clean all pulses to a minimal schema:

  title (str)
  date (str, ISO8601 preferred)
  summary (str; multiline is fine)
  tags (list[str])
  papers (list[str or {url,title}] )  # we preserve dict items if present
  podcasts (list[str or {url,title}])

Everything else is dropped.

Runs over pulse/**/*.yml while excluding pulse/archive/** and pulse/telemetry/**.

Usage:
  python tools/clean_pulses_minimal.py --write
  python tools/clean_pulses_minimal.py --check
  python tools/clean_pulses_minimal.py --dry-run
"""

import argparse
import glob
import io
import os
import sys
from typing import Any, Dict, List, Union

import yaml

YAML_PATHS = [
    "pulse/**/*.yml",
    "pulse/**/*.yaml",
]
EXCLUDE_DIR_TOKENS = ("/archive/", "/telemetry/")

KEEP_KEYS_ORDER = ["title", "date", "summary", "tags", "papers", "podcasts"]


def is_excluded(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(tok in p for tok in EXCLUDE_DIR_TOKENS)


def load_yaml(path: str):
    with io.open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] YAML load failed for {path}: {e}", file=sys.stderr)
            return None


def ensure_list(x) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def normalize_tags(v) -> List[str]:
    out: List[str] = []
    for item in ensure_list(v):
        if isinstance(item, list):
            # Very rare malformed case: nested list → flatten
            for sub in item:
                if isinstance(sub, str):
                    s = sub.strip()
                    if s and s not in out:
                        out.append(s)
        elif isinstance(item, str):
            s = item.strip()
            if s and s not in out:
                out.append(s)
        else:
            # ignore non-strings
            pass
    return out


def normalize_resources(v) -> List[Union[str, Dict[str, Any]]]:
    """
    Accept list of strings or dicts (e.g., {url, title}).
    - If dict has 'url', keep dict (and preserve title if present).
    - If string, keep as-is.
    - Drop empties/unknowns.
    """
    out: List[Union[str, Dict[str, Any]]] = []
    for item in ensure_list(v):
        if isinstance(item, str):
            s = item.strip()
            if s:
                out.append(s)
        elif isinstance(item, dict):
            url = str(item.get("url", "")).strip()
            title = item.get("title")
            if url:
                d = {"url": url}
                if isinstance(title, str) and title.strip():
                    d["title"] = title.strip()
                out.append(d)
        # ignore others
    return out


def as_minimal(doc: Dict[str, Any]) -> Dict[str, Any]:
    minimal: Dict[str, Any] = {}

    # title
    title = doc.get("title")
    if isinstance(title, (str, int, float)):
        minimal["title"] = str(title).strip()

    # date
    date = doc.get("date")
    if isinstance(date, (str, int, float)):
        minimal["date"] = str(date).strip()

    # summary
    summary = doc.get("summary")
    if isinstance(summary, str):
        minimal["summary"] = summary.rstrip()
    elif summary is not None:
        # keep something if it's not a string? safest to stringify
        minimal["summary"] = str(summary).rstrip()

    # tags
    minimal["tags"] = normalize_tags(doc.get("tags"))

    # papers
    minimal["papers"] = normalize_resources(doc.get("papers"))

    # podcasts
    minimal["podcasts"] = normalize_resources(doc.get("podcasts"))

    # Drop empty fields (but keep tags/papers/podcasts even if empty? up to you)
    for k in list(minimal.keys()):
        if minimal[k] in (None, ""):
            del minimal[k]

    # Reorder keys
    ordered: Dict[str, Any] = {}
    for k in KEEP_KEYS_ORDER:
        if k in minimal:
            ordered[k] = minimal[k]
    # If any other unexpected keys slipped in, ignore

    return ordered


def dump_yaml(doc: Dict[str, Any]) -> str:
    """
    Dump with:
    - '---' header
    - block style for long/multiline summary
    - stable key order (we already ordered)
    """
    class Dumper(yaml.SafeDumper):
        pass

    def str_presenter(dumper, data):
        if "\n" in data or len(data) > 120:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    Dumper.add_representer(str, str_presenter)

    # Do not sort keys; we already set the order
    s = yaml.dump(
        doc,
        Dumper=Dumper,
        sort_keys=False,
        allow_unicode=True,
        width=100000,
    )
    # Add header if desired
    return f"---\n{s}"


def cleanup_file(path: str, write: bool) -> bool:
    raw = load_yaml(path)
    if raw is None:
        return False

    if not isinstance(raw, dict):
        print(f"[WARN] {path}: top-level YAML must be a mapping; skipping", file=sys.stderr)
        return False

    minimal = as_minimal(raw)
    new_text = dump_yaml(minimal)

    with io.open(path, "r", encoding="utf-8") as f:
        old_text = f.read()

    if old_text.strip() == new_text.strip():
        return False  # no change

    if write:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        print(f"[FIX] {path}")
    else:
        print(f"[NEEDS FIX] {path}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Apply changes")
    ap.add_argument("--check", action="store_true", help="Exit 1 if changes are needed")
    ap.add_argument("--dry-run", action="store_true", help="Alias for --check")
    args = ap.parse_args()

    if args.dry_run:
        args.check = True

    changed = 0
    total = 0

    paths: List[str] = []
    for pat in YAML_PATHS:
        paths.extend(glob.glob(pat, recursive=True))
    paths = [p for p in paths if not is_excluded(p)]
    paths.sort()

    for p in paths:
        total += 1
        try:
            if cleanup_file(p, write=args.write):
                changed += 1
        except Exception as e:
            print(f"[ERROR] {p}: {e}", file=sys.stderr)

    print(f"Checked {total} files; changes: {changed}")
    if args.check and changed > 0:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
