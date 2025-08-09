#!/usr/bin/env python3
"""
update_tag_index.py

Builds a canonical tag index from pulse YAML files.

- Scans:   ./pulse/**/*.yml|yaml and ./phi-mesh/pulse/**/*.yml|yaml
- Output:  ./meta/tag_index.yml

The output format is:
{
  "<tag>": {
    "links":  [list of related tags that co-occur with this tag],
    "pulses": [list of pulse file paths where this tag appears]
  },
  ...
}

Design goals:
- Deterministic (sorted lists, stable diffs)
- Defensive (skips bad files, logs warnings)
- YAML-safe (convert to plain built-ins before dumping)
"""

from __future__ import annotations

import os
import sys
import glob
import traceback
from typing import Dict, List, Set, Tuple
import yaml

# ----------------------------
# Config
# ----------------------------

PULSE_DIR_CANDIDATES = [
    "pulse",
    os.path.join("phi-mesh", "pulse"),
]

OUTPUT_PATH = os.path.join("meta", "tag_index.yml")

VALID_EXTS = (".yml", ".yaml")

# ----------------------------
# Utilities
# ----------------------------

def log(msg: str) -> None:
    print(f"[update_tag_index] {msg}")

def find_pulse_files() -> List[str]:
    files: List[str] = []
    for base in PULSE_DIR_CANDIDATES:
        if not os.path.isdir(base):
            continue
        # recursive glob for yml/yaml
        for pattern in ("**/*.yml", "**/*.yaml"):
            files.extend(glob.glob(os.path.join(base, pattern), recursive=True))
    # Deduplicate and sort for deterministic processing
    files = sorted(set(files))
    return files

def read_yaml(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            log(f"WARNING: {path}: YAML root is not a mapping; skipping.")
            return None
        return data
    except Exception as e:
        log(f"ERROR: failed to read {path}: {e}")
        traceback.print_exc()
        return None

def normalize_tag(tag: str) -> str:
    """
    Minimal normalization: strip whitespace.
    (We intentionally avoid heavy canonicalization to respect author intent.)
    """
    if not isinstance(tag, str):
        return str(tag)
    return tag.strip()

def pairs(items: List[str]) -> List[Tuple[str, str]]:
    """
    Return unique undirected pairs (a,b) with a < b for a stable representation.
    """
    items = sorted(set(items))
    out: List[Tuple[str, str]] = []
    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            out.append((items[i], items[j]))
    return out

def _to_builtin(obj):
    """
    Recursively convert all containers to YAML-safe Python builtins:
    - dict
    - list
    - str/int/float/bool/None
    Also converts sets/tuples to sorted lists for determinism.
    """
    if isinstance(obj, dict):
        # keep insertion order as Python 3.7+ preserves it,
        # but we build dicts in sorted key order below anyway.
        return {k: _to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        # sort where possible for stable output
        lst = list(obj)
        try:
            lst = sorted(lst)
        except Exception:
            # fallback: keep original order
            pass
        return [_to_builtin(v) for v in lst]
    return obj

# ----------------------------
# Core logic
# ----------------------------

def build_index(pulse_files: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Build a tag index with:
      tag_index[tag]["pulses"] -> sorted list of pulse paths
      tag_index[tag]["links"]  -> sorted list of related tags (co-occurrence)
    """
    # Working storage
    tag_to_pulses: Dict[str, Set[str]] = {}
    undirected_edges: Set[Tuple[str, str]] = set()

    for path in pulse_files:
        data = read_yaml(path)
        if data is None:
            continue

        tags = data.get("tags")
        if tags is None:
            # No tags field — skip quietly.
            continue

        if not isinstance(tags, list):
            log(f"WARNING: {path}: 'tags' is not a list; skipping.")
            continue

        # Normalize, drop empties
        clean_tags = [normalize_tag(t) for t in tags if normalize_tag(t)]
        if not clean_tags:
            continue

        # record pulse membership
        for t in clean_tags:
            tag_to_pulses.setdefault(t, set()).add(path)

        # record co-occurrences as undirected edges
        for a, b in pairs(clean_tags):
            undirected_edges.add((a, b))

    # Build adjacency from undirected edges
    adjacency: Dict[str, Set[str]] = {t: set() for t in tag_to_pulses.keys()}
    for a, b in undirected_edges:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    # Build final payload (deterministic: sorted keys, sorted lists)
    all_tags_sorted = sorted(tag_to_pulses.keys())

    result: Dict[str, Dict[str, List[str]]] = {}
    for tag in all_tags_sorted:
        pulses_sorted = sorted(tag_to_pulses[tag])
        links_sorted = sorted(adjacency.get(tag, set()))
        result[tag] = {
            "links": links_sorted,
            "pulses": pulses_sorted,
        }

    return result

def ensure_parent_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)

def write_yaml(path: str, payload: dict) -> None:
    ensure_parent_dir(path)
    payload_builtin = _to_builtin(payload)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            payload_builtin,
            f,
            sort_keys=True,          # stable diffs across runs
            allow_unicode=True,
            width=1000,
            default_flow_style=False
        )

# ----------------------------
# Entry point
# ----------------------------

def main() -> int:
    log("Scanning for pulse YAML files…")
    pulse_files = find_pulse_files()
    if not pulse_files:
        log("WARNING: no pulse files found in expected locations.")
    else:
        log(f"Found {len(pulse_files)} files.")

    log("Building tag index…")
    index = build_index(pulse_files)

    log(f"Writing YAML to {OUTPUT_PATH} …")
    write_yaml(OUTPUT_PATH, index)

    log("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
