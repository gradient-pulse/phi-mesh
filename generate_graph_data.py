#!/usr/bin/env python3
"""
Robust tag graph builder for Phi-Mesh.

Supports tag_index.yml schemas:
A) {"tags": {tag: {linked_pulses:[...], related_concepts:[...]}}}
B) {tag: ["pulse/…yml", ...]}
C) {tag: {pulses:[...], links:[...]}}
D) [ {tag: <A|B|C-shape>}, {tag2: ...}, ... ]  # top-level list

Also applies aliases from meta/aliases.yml, accepting either:
  {canonical: [aliases]}  OR  {"aliases": {canonical: [aliases]}}
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_alias_resolver(alias_map: Dict[str, List[str]]) -> Dict[str, str]:
    resolver: Dict[str, str] = {}
    if not alias_map:
        return resolver
    for canonical, aliases in alias_map.items():
        if not canonical:
            continue
        resolver[canonical] = canonical
        if not aliases:
            continue
        for a in aliases:
            if a:
                resolver[str(a)] = canonical
    return resolver


def resolve_tag(name: str, resolver: Dict[str, str]) -> str:
    return resolver.get(name, name) if resolver else name


def parse_kv_block(
    tag: str, val: Any,
    pulses_by_tag: Dict[str, Set[str]],
    links_by_tag: Dict[str, Set[str]],
):
    """Handle a single tag entry in shapes B or C."""
    if isinstance(val, list):  # B: flat list of pulses
        pulses_by_tag.setdefault(tag, set()).update(str(x) for x in val)
    elif isinstance(val, dict):  # C: rich dict
        for key in ("pulses", "linked_pulses"):
            v = val.get(key)
            if isinstance(v, list):
                pulses_by_tag.setdefault(tag, set()).update(str(x) for x in v)
        for key in ("links", "related_concepts"):
            v = val.get(key)
            if isinstance(v, list):
                links_by_tag.setdefault(tag, set()).update(str(x) for x in v)


def parse_tag_index(obj: Any) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    pulses_by_tag: Dict[str, Set[str]] = {}
    links_by_tag: Dict[str, Set[str]] = {}

    # D) top-level list → merge items
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                # could be {tag: ...} OR {"tags": {...}}
                if "tags" in item and isinstance(item["tags"], dict):
                    for t, info in item["tags"].items():
                        parse_kv_block(str(t), info, pulses_by_tag, links_by_tag)
                else:
                    for t, info in item.items():
                        parse_kv_block(str(t), info, pulses_by_tag, links_by_tag)
        return pulses_by_tag, links_by_tag

    # A) has "tags" mapping
    if isinstance(obj, dict) and "tags" in obj and isinstance(obj["tags"], dict):
        for t, info in obj["tags"].items():
            parse_kv_block(str(t), info, pulses_by_tag, links_by_tag)
        return pulses_by_tag, links_by_tag

    # B/C) plain mapping of tags
    if isinstance(obj, dict):
        for t, val in obj.items():
            parse_kv_block(str(t), val, pulses_by_tag, links_by_tag)
        return pulses_by_tag, links_by_tag

    # Unknown
    return pulses_by_tag, links_by_tag


def apply_aliases(
    pulses_by_tag: Dict[str, Set[str]],
    links_by_tag: Dict[str, Set[str]],
    resolver: Dict[str, str],
) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    if not resolver:
        return pulses_by_tag, links_by_tag

    new_pulses: Dict[str, Set[str]] = {}
    for tag, pulses in pulses_by_tag.items():
        t = resolve_tag(tag, resolver)
        new_pulses.setdefault(t, set()).update(pulses)

    new_links: Dict[str, Set[str]] = {}
    for src, tgts in links_by_tag.items():
        s = resolve_tag(src, resolver)
        for tgt in tgts:
            t = resolve_tag(tgt, resolver)
            if t and t != s:
                new_links.setdefault(s, set()).add(t)

    return new_pulses, new_links


def compute_degree_centrality(links_by_tag: Dict[str, Set[str]]) -> Dict[str, float]:
    all_tags: Set[str] = set(links_by_tag.keys())
    for targets in links_by_tag.values():
        all_tags.update(targets)

    deg: Dict[str, int] = {t: 0 for t in all_tags}
    for s, targets in links_by_tag.items():
        deg[s] += len(targets)
        for t in targets:
            deg[t] += 1

    if not deg:
        return {}
    m = max(deg.values()) or 1
    return {t: (v / m) for t, v in deg.items()}


def build_nodes_links(
    pulses_by_tag: Dict[str, Set[str]],
    links_by_tag: Dict[str, Set[str]],
):
    all_tags: Set[str] = set(pulses_by_tag.keys()) | set(links_by_tag.keys())
    for tgts in links_by_tag.values():
        all_tags.update(tgts)

    centrality = compute_degree_centrality(links_by_tag)

    nodes = [{
        "id": t,
        "centrality": round(float(centrality.get(t, 0.0)), 4),
        "pulseCount": len(pulses_by_tag.get(t, set())),
    } for t in sorted(all_tags)]

    links = []
    for s, tgts in links_by_tag.items():
        for t in tgts:
            if s != t:
                links.append({"source": s, "target": t})

    return nodes, links


def write_js(out_path: Path, nodes, links, stats):
    payload = {"nodes": nodes, "links": links, "stats": stats}
    out_path.write_text("window.PHI_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", required=True)
    ap.add_argument("--alias-map")
    ap.add_argument("--out-js", required=True)
    args = ap.parse_args()

    tag_path = Path(args.tag_index)
    alias_path = Path(args.alias_map) if args.alias_map else None
    out_js = Path(args.out_js)

    if not tag_path.exists():
        print(f"ERROR: tag index not found at {tag_path}", file=sys.stderr)
        sys.exit(2)

    tag_obj = load_yaml(tag_path)

    # load aliases
    resolver = {}
    if alias_path and alias_path.exists():
        raw = load_yaml(alias_path) or {}
        if isinstance(raw, dict) and "aliases" in raw and isinstance(raw["aliases"], dict):
            resolver = build_alias_resolver(raw["aliases"])
        elif isinstance(raw, dict):
            resolver = build_alias_resolver(raw)
        # else ignore weird shapes

    pulses_by_tag, links_by_tag = parse_tag_index(tag_obj)
    pulses_by_tag, links_by_tag = apply_aliases(pulses_by_tag, links_by_tag, resolver)

    nodes, links = build_nodes_links(pulses_by_tag, links_by_tag)
    stats = {"tagCount": len(nodes), "edgeCount": len(links), "hasAliases": bool(resolver)}

    if stats["tagCount"] == 0:
        write_js(out_js, [], [], stats)
        print("ERROR: No tags parsed from tag_index.yml (schema mismatch?).", file=sys.stderr)
        # Exit non-zero so the workflow catches it
        sys.exit(3)

    write_js(out_js, nodes, links, stats)
    print(f"Wrote {out_js} with {stats['tagCount']} tags and {stats['edgeCount']} edges.")


if __name__ == "__main__":
    main()
