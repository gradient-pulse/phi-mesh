#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_graph_data.py
Builds a tag graph JS payload (nodes + links) from meta/tag_index.yml.

Hardening:
- Alias-aware: normalizes every tag via meta/aliases.yml (same logic as update_tag_index.py)
- Robust to old/new tag_index shapes
- Deduplicates nodes/edges
- Computes simple degree-based centrality
- Converts to plain dicts before dumping
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, Any, Tuple

import yaml


# ------------------------------- Alias + Dump utils ---------------------------

def load_alias_map(path: str | Path) -> dict:
    """Load meta/aliases.yml → return {'canonical': [aliases...], ...} or {}."""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return (data.get("aliases") or {}) if isinstance(data, dict) else {}


def build_alias_index(alias_spec: dict) -> Dict[str, str]:
    """
    Build alias → canonical index.
    - Exact alias strings map to canonical.
    - Also add a lowercase+separator-normalized lookup for resilience.
    """
    idx: Dict[str, str] = {}

    def norm(s: str) -> str:
        return re.sub(r"[\s_\-]+", " ", s).strip().casefold()

    for canonical, aliases in alias_spec.items():
        # defensive: allow strings/None in source
        if isinstance(aliases, (str, bytes)) or aliases is None:
            aliases = [aliases] if aliases else []
        # canonical maps to itself
        idx[canonical] = canonical
        idx[norm(canonical)] = canonical
        for a in aliases:
            if not a:
                continue
            idx[a] = canonical
            idx[norm(a)] = canonical
    return idx


def normalize_tag(tag: str, alias_index: Dict[str, str]) -> str:
    """Normalize a tag via alias_index; fall back to a loose normalized key; else original."""
    if not isinstance(tag, str):
        return tag
    if tag in alias_index:
        return alias_index[tag]
    key = re.sub(r"[\s_\-]+", " ", tag).strip().casefold()
    return alias_index.get(key, tag)


def to_plain_dict(obj: Any) -> Any:
    """Recursively coerce mappings to plain dicts so dumps are always safe."""
    from collections.abc import Mapping
    if isinstance(obj, Mapping):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_plain_dict(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_plain_dict(v) for v in obj]
    return obj


# ------------------------------- Tag index loaders ----------------------------

def load_tag_index(path: str | Path) -> dict:
    """
    Load tag_index.yml.

    Supports:
    - New shape: { <Tag>: {links: [...], pulses: [...]}, ... }
    - Old shape: {'tags': {<Tag>: {...}}, ...}  (we’ll unwrap to the same dict)
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Tag index not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # If it looks like the “new” flat mapping (keys are tags with dict values)
    if isinstance(data, dict) and all(
        isinstance(v, dict) or isinstance(v, list) for v in data.values()
    ) and ("tags" not in data):
        return data

    # If it looks like the older wrapped shape
    if isinstance(data, dict) and "tags" in data and isinstance(data["tags"], dict):
        return data["tags"]

    # Fall back: return as-is; downstream is defensive
    return data


# ------------------------------- Graph builder --------------------------------

def build_graph(
    tag_index: dict,
    alias_index: Dict[str, str]
) -> Tuple[list[dict], list[dict]]:
    """
    Returns (nodes, links) for JS.
    - nodes: [{id, degree, centrality}]
    - links: [{source, target}]
    """
    # Collect adjacency and canonical tag set
    adjacency: Dict[str, set[str]] = {}
    all_tags: set[str] = set()

    # tag_index is expected as {tag: {links: [...], pulses: [...]}}
    if not isinstance(tag_index, dict):
        tag_index = {}

    for raw_tag, payload in tag_index.items():
        tag = normalize_tag(raw_tag, alias_index)
        all_tags.add(tag)

        links = []
        if isinstance(payload, dict):
            links = payload.get("links", []) or payload.get("related_concepts", []) or []
        elif isinstance(payload, list):
            # very defensive: treat a list value as “links”
            links = payload

        # Normalize each linked tag
        norm_links = [normalize_tag(l, alias_index) for l in links if isinstance(l, str) and l]

        # Initialize adjacency
        adjacency.setdefault(tag, set())

        for l in norm_links:
            if not l:
                continue
            all_tags.add(l)
            if l == tag:
                continue  # skip self-loop
            # Undirected edge
            adjacency.setdefault(l, set())
            adjacency[tag].add(l)
            adjacency[l].add(tag)

    # Compute degrees & basic centrality (degree / max_degree)
    degrees = {t: len(adjacency.get(t, set())) for t in all_tags}
    max_deg = max(degrees.values()) if degrees else 1

    nodes = []
    for t in sorted(all_tags):
        deg = degrees.get(t, 0)
        centrality = (deg / max_deg) if max_deg else 0.0
        nodes.append({"id": t, "degree": deg, "centrality": round(centrality, 6)})

    # Deduplicate links with a normalized tuple key (min, max)
    seen = set()
    links = []
    for a, nbrs in adjacency.items():
        for b in nbrs:
            edge = tuple(sorted((a, b)))
            if edge in seen:
                continue
            seen.add(edge)
            links.append({"source": edge[0], "target": edge[1]})

    return nodes, links


# ------------------------------- Writer ---------------------------------------

def write_js(nodes: list[dict], links: list[dict], out_path: str | Path) -> None:
    """
    Writes a minimal JS module for the D3 front-end:
      const nodes = [...];
      const links = [...];
      export { nodes, links };
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "nodes": to_plain_dict(nodes),
        "links": to_plain_dict(links),
    }

    # Pretty JSON embed for readability in VCS diffs
    js = (
        "const nodes = "
        + json.dumps(payload["nodes"], ensure_ascii=False, indent=2)
        + ";\n"
        "const links = "
        + json.dumps(payload["links"], ensure_ascii=False, indent=2)
        + ";\n"
        "export { nodes, links };\n"
    )

    out.write_text(js, encoding="utf-8")
    print(f"[graph] wrote {out}  (nodes={len(nodes)}, links={len(links)})")


# ------------------------------- CLI ------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Generate graph_data.js from tag_index.yml")
    ap.add_argument(
        "--tag-index",
        default="meta/tag_index.yml",
        help="Path to tag index YAML (default: meta/tag_index.yml)",
    )
    ap.add_argument(
        "--alias-file",
        default="meta/aliases.yml",
        help="Path to alias spec (default: meta/aliases.yml)",
    )
    ap.add_argument(
        "--out",
        default="docs/graph_data.js",
        help="Output JS path (default: docs/graph_data.js)",
    )
    args = ap.parse_args()

    alias_spec = load_alias_map(args.alias_file)
    alias_index = build_alias_index(alias_spec)
    print(f"[graph] Aliases loaded: {len(alias_spec)} canonical, {len(alias_index)} total keys")

    tags = load_tag_index(args.tag_index)
    nodes, links = build_graph(tags, alias_index)
    write_js(nodes, links, args.out)


if __name__ == "__main__":
    main()
