#!/usr/bin/env python3
"""
Suggest likely tag aliases by bucketing near-duplicates.

Reads the built tag index (meta/tag_index.yml) and groups tags that only differ
by case, spaces, hyphens vs underscores, or trivial punctuation. Outputs a
human-readable report (default) or JSON for automation.

Usage:
  python tools/suggest_aliases.py \
    --index meta/tag_index.yml \
    --out meta/alias_suggestions.txt \
    --min-size 2 \
    --format text

You can then copy preferred groups into meta/aliases.yml like:

Canonical_Tag:
  - alias one
  - alias-two
  - alias_three
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception as e:
    print("ERROR: pyyaml is required. pip install pyyaml", file=sys.stderr)
    raise


def baseform(s: str) -> str:
    """
    Normalize a tag into a base form that collapses trivial differences:
    - lowercase
    - collapse spaces, hyphens to underscores
    - remove repeated underscores
    - strip leading/trailing underscores
    - drop trivial punctuation (./:,)
    """
    s = (s or "").lower().strip()
    s = re.sub(r"[ \t\-]+", "_", s)       # spaces & hyphens → underscores
    s = re.sub(r"[./:,]+", "", s)         # drop trivial punctuation
    s = re.sub(r"__+", "_", s)            # collapse multiple underscores
    s = s.strip("_")
    return s


def load_index(path: str) -> Dict[str, dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping.")
    return data


def bucket_tags(tags: List[str]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = {}
    for t in tags:
        b = baseform(t)
        buckets.setdefault(b, []).append(t)
    return buckets


def sort_group(group: List[str]) -> List[str]:
    # sort with canonical-ish looking names first (Title_Case over all-caps/all-lower)
    def weight(name: str) -> Tuple[int, str]:
        # Lower weight = earlier in sort
        if "_" in name and name == "_".join(p[:1].upper() + p[1:] for p in name.split("_")):
            return (0, name)  # Title_Cased snake
        if name.istitle():
            return (1, name)
        if name.isupper():
            return (2, name)
        return (3, name.lower())
    return sorted(group, key=weight)


def suggest_aliases(index_path: str, min_size: int = 2) -> List[List[str]]:
    idx = load_index(index_path)
    tags = list(idx.keys())
    buckets = bucket_tags(tags)

    groups = []
    for b, group in sorted(buckets.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(group) >= min_size:
            groups.append(sort_group(group))
    return groups


def main() -> int:
    ap = argparse.ArgumentParser(description="Suggest likely tag aliases.")
    ap.add_argument("--index", default="meta/tag_index.yml", help="Path to tag index YAML.")
    ap.add_argument("--out", default="", help="Optional path to write the report.")
    ap.add_argument("--min-size", type=int, default=2, help="Only show groups with at least this many variants.")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = ap.parse_args()

    groups = suggest_aliases(args.index, args.min_size)

    if args.format == "json":
        payload = {"groups": groups, "count": len(groups)}
        out_str = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        lines = ["Possible alias groups (copy into meta/aliases.yml):"]
        for g in groups:
            # Choose a provisional canonical suggestion (first by sort heuristic)
            canonical = g[0]
            lines.append(f"- Canonical? {canonical}")
            for alt in g[1:]:
                lines.append(f"  - {alt}")
        if not groups:
            lines.append("(no groups found)")
        out_str = "\n".join(lines)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"Wrote alias suggestions to {args.out}")
    else:
        print(out_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
