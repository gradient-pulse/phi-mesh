#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a canonical tag index from pulse/*.yml files.

Output schema (YAML):
{
  <tag>: {
    links: [<other tag>, ...],    # co-occurring tags across pulses (sorted, unique)
    pulses: ["pulse/....yml", ...]# files that contain the tag (sorted, unique)
  },
  ...
}

Design goals:
- Never emit non-serializable types (NO OrderedDict, sets, custom classes).
- Be resilient to weird input (missing fields, non-list tags, mixed types).
- Keep diffs stable (sorted lists, sorted keys).
- Allow optional aliasing via meta/tag_aliases.yml (if present).

Exit codes:
 0 success
 1 usage / config errors
 2 parsing errors (but tries to continue & report)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Dict, List, Set, Tuple

try:
    import yaml  # PyYAML
except Exception as e:
    print(f"[fatal] PyYAML not available: {e}", file=sys.stderr)
    sys.exit(1)


# ----------------------------- helpers --------------------------------- #

def _read_yaml_file(path: str) -> Tuple[dict, List[str]]:
    """Safe-load a YAML file. Returns (data or {}, warnings)."""
    warns: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            warns.append(f"{path}: top-level YAML is not a mapping (got {type(data).__name__}); treating as empty.")
            return {}, warns
        return data, warns
    except FileNotFoundError:
        warns.append(f"{path}: not found.")
        return {}, warns
    except yaml.YAMLError as e:
        warns.append(f"{path}: YAML parse error: {e}")
        return {}, warns
    except Exception as e:
        warns.append(f"{path}: unreadable: {e}")
        return {}, warns


def _load_aliases(alias_path: str) -> Dict[str, str]:
    """
    Optional aliases file format:
      old_tag: Canonical_Tag
      Another old: Canonical_Tag
    """
    data, warns = _read_yaml_file(alias_path)
    for w in warns:
        print(f"[warn] {w}", file=sys.stderr)
    if not isinstance(data, dict):
        return {}
    aliases: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str) and k.strip():
            aliases[k.strip()] = v.strip()
    return aliases


def _canon(tag: str) -> str:
    """Minimal normalization to keep keys stable without being destructive."""
    # trim whitespace and collapse internal spaces to single spaces
    t = " ".join(str(tag).strip().split())
    return t


def _apply_alias(tag: str, aliases: Dict[str, str]) -> str:
    """Map tag via aliases if present; otherwise return as-is."""
    return aliases.get(tag, tag)


def _ensure_str_list(value, where: str) -> List[str]:
    """
    Coerce an arbitrary YAML field into a list[str].
    - None => []
    - str  => [str]
    - list => [str(x) for x in value if x is not None]
    - anything else => []
    """
    out: List[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        for i, x in enumerate(value):
            if x is None:
                continue
            try:
                out.append(str(x))
            except Exception:
                print(f"[warn] {where}: list item {i} not string-coercible; dropped.", file=sys.stderr)
        return out
    # best effort: try to stringify scalars
    try:
        return [str(value)]
    except Exception:
        print(f"[warn] {where}: unexpected type {type(value).__name__}; dropped.", file=sys.stderr)
        return []


# ----------------------------- core build -------------------------------- #

def build_index(
    pulse_dir: str,
    aliases_path: str | None = None,
) -> Tuple[Dict[str, Dict[str, List[str]]], List[str]]:
    """
    Scan pulse YAMLs and build the tag index.
    Returns (index, warnings)
    """
    warns: List[str] = []

    # Load aliases if present
    aliases: Dict[str, str] = {}
    if aliases_path and os.path.exists(aliases_path):
        aliases = _load_aliases(aliases_path)

    # Collect mapping
    pulses_by_tag: Dict[str, Set[str]] = {}
    links_by_tag: Dict[str, Set[str]] = {}

    # Accept both pulse/*.yml and pulse/**/*.yml
    patterns = [
        os.path.join(pulse_dir, "*.yml"),
        os.path.join(pulse_dir, "*.yaml"),
        os.path.join(pulse_dir, "**/*.yml"),
        os.path.join(pulse_dir, "**/*.yaml"),
    ]

    # de-dupe file list
    files: List[str] = []
    seen: Set[str] = set()
    for pat in patterns:
        for p in glob.glob(pat, recursive=True):
            if p not in seen and os.path.isfile(p):
                files.append(p)
                seen.add(p)

    if not files:
        warns.append(f"No pulse files found under '{pulse_dir}'.")
        return {}, warns

    for path in sorted(files):
        data, w = _read_yaml_file(path)
        warns.extend(w)
        if not data:
            continue

        # tags can be under 'tags', sometimes other variants creep in — stick to 'tags'
        raw_tags = data.get("tags", [])
        tag_list = _ensure_str_list(raw_tags, f"{path}:tags")

        # normalize + alias
        canon_tags: List[str] = []
        for t in tag_list:
            c = _canon(t)
            c = _apply_alias(c, aliases)
            if c:
                canon_tags.append(c)

        # co-occurrence links are all other tags in the same file
        tag_set = set(canon_tags)
        if not tag_set:
            continue

        # record pulses per tag
        rel_path = path.replace("\\", "/")  # normalize for cross-platform diffs
        for t in tag_set:
            pulses_by_tag.setdefault(t, set()).add(rel_path)

        # record co-occurrence links
        for t in tag_set:
            others = tag_set - {t}
            if not others:
                continue
            links_by_tag.setdefault(t, set()).update(others)

    # Assemble final index (plain dicts/lists only, sorted for stability)
    index: Dict[str, Dict[str, List[str]]] = {}
    for tag in sorted(set(pulses_by_tag.keys()) | set(links_by_tag.keys())):
        pulses = sorted(pulses_by_tag.get(tag, set()))
        links = sorted(links_by_tag.get(tag, set()))
        index[tag] = {
            "links": links,
            "pulses": pulses,
        }

    # Defensive: JSON round-trip to guarantee plain types only
    index = json.loads(json.dumps(index, ensure_ascii=False))

    return index, warns


# ----------------------------- CLI -------------------------------------- #

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Regenerate meta/tag_index.yml from pulse/*.yml files."
    )
    p.add_argument(
        "--pulse-dir",
        default="pulse",
        help="Directory containing pulse YAMLs (default: %(default)s)",
    )
    p.add_argument(
        "--aliases",
        default="meta/tag_aliases.yml",
        help="Optional YAML mapping of tag aliases to canonical names (default: %(default)s)",
    )
    p.add_argument(
        "--out",
        default="meta/tag_index.yml",
        help="Output YAML path (default: %(default)s)",
    )
    p.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Exit nonzero if any warnings occurred.",
    )
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    index, warns = build_index(ns.pulse_dir, ns.aliases if ns.aliases else None)

    for w in warns:
        print(f"[warn] {w}", file=sys.stderr)

    # Write output (sorted keys for stable diffs; unicode on)
    os.makedirs(os.path.dirname(ns.out), exist_ok=True)
    try:
        with open(ns.out, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                index,
                f,
                sort_keys=True,           # stable order for diffs
                allow_unicode=True,
                width=120,
                default_flow_style=False,
            )
    except Exception as e:
        print(f"[fatal] failed to write {ns.out}: {e}", file=sys.stderr)
        return 1

    if ns.fail_on_warn and warns:
        return 2

    print(f"[ok] wrote {ns.out} with {len(index)} tags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
