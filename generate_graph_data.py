#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_graph_data.py
Builds docs/data.js for the Tag Browser.

- Reads meta/tag_index.yml when present & well-formed.
- If tag_index.yml is empty/unsupported, scans pulse/**/*.yml (and **/*.yaml)
  to reconstruct tags, links, and resources.
- Skips noisy/legacy directories: pulse/archive/** and pulse/telemetry/**
- Applies alias normalization from meta/aliases.yml (and from the optional
  canonical_tags section inside tag_index.yml if available).
- Outputs a single JS file that defines:  window.PHI_DATA = { nodes, links, tagResources };

Usage:
  python generate_graph_data.py \
      --tag-index meta/tag_index.yml \
      --alias-map meta/aliases.yml \
      --pulse-glob "pulse/**/*.yml" \
      --out-js docs/data.js
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set

try:
    import yaml
except Exception as e:
    print(f"ERROR: pyyaml not installed: {e}", file=sys.stderr)
    sys.exit(1)


# ----------------------------- YAML helpers --------------------------------- #

def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)  # may return dict | list | None
    except Exception as e:
        print(f"WARN: Failed to parse YAML {path}: {e}", file=sys.stderr)
        return None


def write_js(out_path: Path, payload: Dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")


# --------------------------- Alias normalization ---------------------------- #

def build_alias_normalizer(
    alias_map_path: Path | None,
    tag_index_obj: Any,
) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Returns:
      to_canonical: map tag_variant -> canonical_tag
      canonical_to_aliases: canonical_tag -> [aliases]
    Accepts:
      - meta/aliases.yml structure like:
          aliases:
            canonical: [alias1, alias2, ...]
      - OR a flat mapping canonical -> [aliases]
      - AND/OR an optional `canonical_tags:` section inside tag_index.yml
    """
    canonical_to_aliases: Dict[str, List[str]] = {}

    # 1) From meta/aliases.yml
    if alias_map_path and alias_map_path.exists():
        data = load_yaml(alias_map_path) or {}
        if isinstance(data, dict):
            if "aliases" in data and isinstance(data["aliases"], dict):
                src = data["aliases"]
            else:
                # assume whole file is canonical -> [aliases]
                src = data
            for canon, arr in src.items():
                if not isinstance(arr, list):
                    continue
                canonical_to_aliases.setdefault(canon, [])
                for a in arr:
                    if isinstance(a, str) and a not in canonical_to_aliases[canon]:
                        canonical_to_aliases[canon].append(a)

    # 2) From tag_index.yml canonical_tags (if any)
    if isinstance(tag_index_obj, dict) and "canonical_tags" in tag_index_obj:
        ct = tag_index_obj.get("canonical_tags")
        if isinstance(ct, dict):
            for canon, arr in ct.items():
                if not isinstance(arr, list):
                    continue
                canonical_to_aliases.setdefault(canon, [])
                for a in arr:
                    if isinstance(a, str) and a not in canonical_to_aliases[canon]:
                        canonical_to_aliases[canon].append(a)

    # Build inverse map (variant -> canonical); include identity
    to_canonical: Dict[str, str] = {}
    for canon, aliases in canonical_to_aliases.items():
        to_canonical[canon] = canon
        for a in aliases:
            to_canonical[a] = canon

    # Identity mapping fallback for anything unseen
    return to_canonical, canonical_to_aliases


def normalize_tag(tag: str, to_canonical: Dict[str, str]) -> str:
    # Attempt exact match first
    if tag in to_canonical:
        return to_canonical[tag]

    # Try case-insensitive match
    lower_map = {k.lower(): v for k, v in to_canonical.items()}
    if tag.lower() in lower_map:
        return lower_map[tag.lower()]

    # Return original if no alias known
    return tag


# --------------------------- Pulse scanning path ---------------------------- #

def scan_pulses_for_tags(
    glob_patterns: List[str],
    to_canonical: Dict[str, str],
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, Dict[str, List[str]]]]:
    """
    Returns:
      tag_to_pulses: tag -> [pulse file basenames]
      pulse_to_tags: pulse_basename -> [tags]
      pulse_resources: tag -> {"papers": [...], "podcasts": [...]}
    Skips any file within directories named 'archive' or 'telemetry'.
    Accepts both .yml and .yaml files via multiple globs.
    """
    tag_to_pulses: Dict[str, List[str]] = defaultdict(list)
    pulse_to_tags: Dict[str, List[str]] = defaultdict(list)
    tag_resources: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"papers": [], "podcasts": []})

    # Collect files from all patterns
    files: Set[Path] = set()
    for pat in glob_patterns:
        for fp in Path().glob(pat):
            files.add(fp)

    for fp in sorted(files):
        # Skip noisy/legacy dirs
        parts = set(fp.parts)
        if {"archive", "telemetry"} & parts:
            continue

        if not fp.is_file():
            continue

        data = load_yaml(fp)
        if not isinstance(data, dict):
            # Some legacy files may be lists or malformed; skip those gracefully
            continue

        # Pull tags; pulses tend to store under 'tags' (lowercase) but we check variants
        raw_tags = data.get("tags") or data.get("Tags") or []
        if not isinstance(raw_tags, list):
            raw_tags = []
        tags = [normalize_tag(t, to_canonical) for t in raw_tags if isinstance(t, str) and t.strip()]
        if not tags:
            continue

        pulse_name = fp.name  # or fp.stem; using .name keeps unique filenames visible

        # Map pulse -> tags
        pulse_to_tags[pulse_name] = sorted(set(tags), key=str.lower)

        # Map tag -> pulses
        for t in pulse_to_tags[pulse_name]:
            if pulse_name not in tag_to_pulses[t]:
                tag_to_pulses[t].append(pulse_name)

        # Optional: collect resources from each pulse under the same tag
        papers = data.get("papers") or []
        podcasts = data.get("podcasts") or []
        if isinstance(papers, list) or isinstance(podcasts, list):
            for t in tags:
                if isinstance(papers, list):
                    for u in papers:
                        if isinstance(u, str) and u not in tag_resources[t]["papers"]:
                            tag_resources[t]["papers"].append(u)
                if isinstance(podcasts, list):
                    for u in podcasts:
                        if isinstance(u, str) and u not in tag_resources[t]["podcasts"]:
                            tag_resources[t]["podcasts"].append(u)

    # Sort lists for determinism
    for t in tag_to_pulses:
        tag_to_pulses[t].sort(key=str.lower)
    for t in tag_resources:
        tag_resources[t]["papers"].sort()
        tag_resources[t]["podcasts"].sort()

    return tag_to_pulses, pulse_to_tags, tag_resources


# -------------------------- tag_index.yml ingestion ------------------------- #

def parse_tag_index(
    tag_index_obj: Any,
    to_canonical: Dict[str, str]
) -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, List[str]]]]:
    """
    Supports two structures we’ve seen in the repo:

    A) New “rich” schema:
       {
         "AI_alignment": {
           "links": [...],
           "pulses": ["2025-07-22_CF_split.yml"]
         },
         "RGP": { ... },
         ...
       }

    B) Older “flat” schema:
       {
         "AI_alignment": ["pulse/...yml", "pulse/...yml"],
         "RGP": ["pulse/...yml"],
         ...
       }

    Returns:
      tag_to_pulses (canonicalized)
      tag_resources  (tag -> {"papers":[...], "podcasts":[...]})
    """
    tag_to_pulses: Dict[str, List[str]] = defaultdict(list)
    tag_resources: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"papers": [], "podcasts": []})

    if not isinstance(tag_index_obj, dict) or not tag_index_obj:
        return {}, {}

    for tag_name, entry in tag_index_obj.items():
        canon_tag = normalize_tag(tag_name, to_canonical)

        # New schema: expect dict entries
        if isinstance(entry, dict):
            pulses = entry.get("pulses") or entry.get("linked_pulses") or []
            if isinstance(pulses, list):
                for p in pulses:
                    if isinstance(p, str):
                        # Keep basenames consistent with scanner
                        pulse_name = Path(p).name
                        if pulse_name not in tag_to_pulses[canon_tag]:
                            tag_to_pulses[canon_tag].append(pulse_name)
            # If resources are ever stored centrally, wire them in
            # (for now tag_resources remains empty here)
        # Old flat schema: tag -> [pulse-paths]
        elif isinstance(entry, list):
            for p in entry:
                if isinstance(p, str):
                    pulse_name = Path(p).name
                    if pulse_name not in tag_to_pulses[canon_tag]:
                        tag_to_pulses[canon_tag].append(pulse_name)
        # else: ignore unknown types

    # Sort for determinism
    for t in tag_to_pulses:
        tag_to_pulses[t].sort(key=str.lower)

    return tag_to_pulses, tag_resources


# ------------------------------ Graph builder ------------------------------- #

def build_graph(
    tag_to_pulses: Dict[str, List[str]],
    pulse_to_tags: Dict[str, List[str]],
    tag_resources: Dict[str, Dict[str, List[str]]],
) -> Dict[str, Any]:
    """
    Build a lightweight undirected co-occurrence graph across tags.
    nodes: [{id, centrality}]
    links: [{source, target, weight}]
    """
    # Co-occurrence counts
    edge_weight: Dict[Tuple[str, str], int] = defaultdict(int)
    degree_count: Dict[str, int] = defaultdict(int)

    # For each pulse, connect all tag pairs
    for _pulse, tags in pulse_to_tags.items():
        tags = sorted(set(tags))
        for a, b in combinations(tags, 2):
            u, v = (a, b) if a < b else (b, a)
            edge_weight[(u, v)] += 1

    # Degree counting
    for (u, v), w in edge_weight.items():
        degree_count[u] += w
        degree_count[v] += w

    # Centrality proxy (normalize degrees)
    max_deg = max(degree_count.values()) if degree_count else 1
    nodes = []
    all_tags = sorted(set(tag_to_pulses.keys()) | set(degree_count.keys()), key=str.lower)
    for t in all_tags:
        deg = degree_count.get(t, 0)
        centrality = (deg / max_deg) if max_deg > 0 else 0.0
        nodes.append({"id": t, "centrality": round(float(centrality), 6)})

    links = [{"source": u, "target": v, "weight": w} for (u, v), w in sorted(edge_weight.items())]

    # Resources
    tag_resources = {t: tag_resources.get(t, {"papers": [], "podcasts": []}) for t in all_tags}

    return {"nodes": nodes, "links": links, "tagResources": tag_resources}


# ---------------------------------- main ------------------------------------ #

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml", help="Path to tag index YAML.")
    ap.add_argument("--alias-map", default="meta/aliases.yml", help="Path to alias map YAML.")
    ap.add_argument(
        "--pulse-glob",
        default=None,
        help='Glob(s) for pulse files. If omitted, defaults to ["pulse/**/*.yml","pulse/**/*.yaml"].'
    )
    ap.add_argument("--out-js", default="docs/data.js", help="Output JS file.")
    args = ap.parse_args()

    tag_index_path = Path(args.tag_index)
    alias_map_path = Path(args.alias_map) if args.alias_map else None
    out_js = Path(args.out_js)

    # Load tag_index & build alias normalizer (also reads canonical_tags if present)
    tag_index_obj = load_yaml(tag_index_path)
    to_canonical, canonical_to_aliases = build_alias_normalizer(alias_map_path, tag_index_obj)

    # First try the tag_index route
    tag_to_pulses: Dict[str, List[str]] = {}
    tag_resources: Dict[str, Dict[str, List[str]]] = {}
    if isinstance(tag_index_obj, dict) and tag_index_obj:
        tag_to_pulses, tag_resources = parse_tag_index(tag_index_obj, to_canonical)

    # If tag_index is empty or yielded nothing, scan pulses instead
    if not tag_to_pulses:
        print("INFO: tag_index.yml empty or unsupported → scanning pulses …")
        patterns = []
        if args.pulse_glob:
            # Allow comma-separated or space-separated user input
            for piece in str(args.pulse_glob).split(","):
                piece = piece.strip()
                if piece:
                    patterns.append(piece)
        else:
            patterns = ["pulse/**/*.yml", "pulse/**/*.yaml"]

        tag_to_pulses, pulse_to_tags, pulse_resources = scan_pulses_for_tags(patterns, to_canonical)

        # If scanning yielded nothing, hard error to catch schema issues early
        if not tag_to_pulses:
            print("ERROR: No tags parsed from pulses (check globs / YAML).", file=sys.stderr)
            sys.exit(3)

        # Build graph from scanned data
        payload = build_graph(tag_to_pulses, pulse_to_tags, pulse_resources)
    else:
        # When using tag_index, we still need pulse_to_tags to build cooccurrence.
        # Reconstruct a minimal pulse_to_tags from tag_to_pulses.
        pulse_to_tags: Dict[str, List[str]] = defaultdict(list)
        for t, plist in tag_to_pulses.items():
            for p in plist:
                if t not in pulse_to_tags[p]:
                    pulse_to_tags[p].append(t)
        for p in pulse_to_tags:
            pulse_to_tags[p].sort(key=str.lower)

        # Combine with any known resources (currently tag_resources may be empty if not in tag_index)
        payload = build_graph(tag_to_pulses, pulse_to_tags, tag_resources)

    # Emit canonical alias info (handy if the front-end wants it later)
    payload["aliasInfo"] = {
        "canonicalToAliases": canonical_to_aliases,
        # inverse map can be reconstructed client-side if needed
    }

    # Write JS as window.PHI_DATA = {...};
    write_js(out_js, payload)

    # Basic sanity check (so CI fails loudly if something regresses)
    text = out_js.read_text(encoding="utf-8")
    if "window.PHI_DATA" not in text:
        print("ERROR: docs/data.js missing window.PHI_DATA", file=sys.stderr)
        sys.exit(2)

    size = out_js.stat().st_size
    if size < 200:  # tiny files are usually a sign of an upstream parsing issue
        print(f"ERROR: docs/data.js is suspiciously small ({size} bytes).", file=sys.stderr)
        sys.exit(1)

    print(f"OK: wrote {out_js} ({size} bytes)")
    # Optional: basic counts
    nodes = payload.get("nodes", [])
    print(f"INFO: tag count = {len(nodes)}")


if __name__ == "__main__":
    main()
