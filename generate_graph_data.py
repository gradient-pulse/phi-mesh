#!/usr/bin/env python3
"""
Robust tag graph builder for Phi-Mesh.

Supports multiple tag_index.yml shapes:
A) {"tags": {tag: {linked_pulses:[...], related_concepts:[...], ...}}}
B) {tag: ["pulse/…yml", ...]}   # flat
C) {tag: {pulses:[...], links:[...], ...}}  # rich (links = related tags)

Also applies aliases from meta/aliases.yml when provided:
aliases.yml example:
  canonical_tag:
    - alias1
    - alias2
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_alias_resolver(alias_map: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Returns a mapping alias->canonical. Canonicals map to themselves.
    """
    resolver: Dict[str, str] = {}
    if not alias_map:
        return resolver
    for canonical, aliases in alias_map.items():
        # map canonical to itself
        resolver[canonical] = canonical
        if not aliases:
            continue
        for a in aliases:
            if not a:
                continue
            resolver[str(a)] = canonical
    return resolver


def resolve_tag(name: str, resolver: Dict[str, str]) -> str:
    if not resolver:
        return name
    return resolver.get(name, name)


def normalize_tags(tags: Set[str], resolver: Dict[str, str]) -> Set[str]:
    return {resolve_tag(t, resolver) for t in tags if t}


def parse_tag_index(obj: dict) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Returns:
        pulses_by_tag: {tag -> set(pulse_paths)}
        links_by_tag : {tag -> set(related_tag)}
    Handles schemas A, B, C described above.
    """
    pulses_by_tag: Dict[str, Set[str]] = {}
    links_by_tag: Dict[str, Set[str]] = {}

    def ensure(d: Dict[str, Set[str]], k: str) -> Set[str]:
        if k not in d:
            d[k] = set()
        return d[k]

    if not isinstance(obj, dict):
        return pulses_by_tag, links_by_tag

    # Schema A: top-level "tags"
    if "tags" in obj and isinstance(obj["tags"], dict):
        for tag, info in obj["tags"].items():
            if not isinstance(info, dict):
                # tolerate odd shapes
                continue
            # pulses might be under 'linked_pulses' or 'pulses'
            for key in ("linked_pulses", "pulses"):
                val = info.get(key)
                if isinstance(val, list):
                    ensure(pulses_by_tag, tag).update([str(x) for x in val])

            # related tags under 'related_concepts' or 'links'
            for key in ("related_concepts", "links"):
                val = info.get(key)
                if isinstance(val, list):
                    ensure(links_by_tag, tag).update([str(x) for x in val])

    else:
        # Could be schema B (flat) or C (rich per-tag)
        for tag, val in obj.items():
            # flat: list of pulses
            if isinstance(val, list):
                ensure(pulses_by_tag, tag).update([str(x) for x in val])

            # rich per-tag dict
            elif isinstance(val, dict):
                # pulses possibly under 'pulses' or 'linked_pulses'
                for key in ("pulses", "linked_pulses"):
                    v = val.get(key)
                    if isinstance(v, list):
                        ensure(pulses_by_tag, tag).update([str(x) for x in v])

                # related tags possibly under 'links' or 'related_concepts'
                for key in ("links", "related_concepts"):
                    v = val.get(key)
                    if isinstance(v, list):
                        ensure(links_by_tag, tag).update([str(x) for x in v])

            # else: ignore other forms

    return pulses_by_tag, links_by_tag


def apply_aliases_to_graph(
    pulses_by_tag: Dict[str, Set[str]],
    links_by_tag: Dict[str, Set[str]],
    resolver: Dict[str, str],
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    if not resolver:
        return pulses_by_tag, links_by_tag

    # remap pulses_by_tag keys
    new_pulses: Dict[str, Set[str]] = {}
    for tag, pulses in pulses_by_tag.items():
        t = resolve_tag(tag, resolver)
        new_pulses.setdefault(t, set()).update(pulses)

    # remap links_by_tag keys + targets
    new_links: Dict[str, Set[str]] = {}
    for src, targets in links_by_tag.items():
        s = resolve_tag(src, resolver)
        for tgt in targets:
            t = resolve_tag(tgt, resolver)
            if not t:
                continue
            if t == s:
                # skip self loops after alias merge
                continue
            new_links.setdefault(s, set()).add(t)

    return new_pulses, new_links


def compute_degree_centrality(links_by_tag: Dict[str, Set[str]]) -> Dict[str, float]:
    """
    Simple degree centrality normalized to [0,1].
    Degree = out + in.
    """
    all_tags: Set[str] = set(links_by_tag.keys())
    for targets in links_by_tag.values():
        all_tags.update(targets)

    degree: Dict[str, int] = {t: 0 for t in all_tags}
    for s, targets in links_by_tag.items():
        degree[s] += len(targets)  # out-degree
        for t in targets:
            degree[t] += 1         # in-degree

    if not degree:
        return {}

    max_deg = max(degree.values()) or 1
    return {t: (deg / max_deg) for t, deg in degree.items()}


def build_nodes_links(
    pulses_by_tag: Dict[str, Set[str]],
    links_by_tag: Dict[str, Set[str]],
) -> Tuple[List[dict], List[dict]]:
    # nodes: include every tag present in pulses or links
    all_tags: Set[str] = set(pulses_by_tag.keys()) | set(links_by_tag.keys())
    for targets in links_by_tag.values():
        all_tags.update(targets)

    centrality = compute_degree_centrality(links_by_tag)

    nodes = []
    for t in sorted(all_tags):
        nodes.append({
            "id": t,
            "centrality": round(float(centrality.get(t, 0.0)), 4),
            "pulseCount": len(pulses_by_tag.get(t, set())),
        })

    links = []
    for s, targets in links_by_tag.items():
        for t in targets:
            if s == t:
                continue
            links.append({"source": s, "target": t})

    return nodes, links


def write_js(out_path: Path, nodes: List[dict], links: List[dict], stats: dict):
    payload = {
        "nodes": nodes,
        "links": links,
        "stats": stats,
    }
    js = "window.PHI_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    out_path.write_text(js, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", required=True, help="Path to meta/tag_index.yml")
    ap.add_argument("--alias-map", default=None, help="Optional path to meta/aliases.yml")
    ap.add_argument("--out-js", required=True, help="Output JS file (docs/data.js)")
    args = ap.parse_args()

    tag_index_path = Path(args.tag_index)
    alias_map_path = Path(args.alias_map) if args.alias_map else None
    out_js_path = Path(args.out_js)

    if not tag_index_path.exists():
        print(f"ERROR: tag index not found at {tag_index_path}", file=sys.stderr)
        sys.exit(2)

    tag_obj = load_yaml(tag_index_path)

    alias_resolver: Dict[str, str] = {}
    if alias_map_path and alias_map_path.exists():
        raw_aliases = load_yaml(alias_map_path) or {}
        # Support both {canonical: [aliases]} and {aliases: {canonical:[…]}}
        if isinstance(raw_aliases, dict) and "aliases" in raw_aliases and isinstance(raw_aliases["aliases"], dict):
            alias_resolver = build_alias_resolver(raw_aliases["aliases"])
        else:
            alias_resolver = build_alias_resolver(raw_aliases)

    pulses_by_tag, links_by_tag = parse_tag_index(tag_obj)
    pulses_by_tag, links_by_tag = apply_aliases_to_graph(pulses_by_tag, links_by_tag, alias_resolver)

    nodes, links = build_nodes_links(pulses_by_tag, links_by_tag)

    stats = {
        "tagCount": len(nodes),
        "edgeCount": len(links),
        "hasAliases": bool(alias_resolver),
    }

    # If nothing parsed, fail loudly so CI catches it (your workflow sanity step also checks size)
    if stats["tagCount"] == 0:
        # Still write a tiny payload so the workflow can show the file, but exit non-zero
        write_js(out_js_path, [], [], stats)
        print("ERROR: No tags parsed from tag_index.yml (schema mismatch?).", file=sys.stderr)
        sys.exit(3)

    write_js(out_js_path, nodes, links, stats)
    print(f"Wrote {out_js_path} with {stats['tagCount']} tags and {stats['edgeCount']} edges.")


if __name__ == "__main__":
    main()
