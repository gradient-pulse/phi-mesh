#!/usr/bin/env python3
"""
Generate docs/data.js for the interactive tag browser.

Robust to:
- meta/tag_index.yml being empty ({}) or missing.
- Multiple historical schemas of tag_index.yml.
- Optional alias map (meta/aliases.yml) with flexible shapes.

If tag_index is empty, we fall back to scanning pulse/*.yml files to
reconstruct tags, edges, and basic resources.

Output format (JS):
  window.GRAPH_DATA = { nodes, links, tagResources, stats };
  window.TAG_GRAPH  = window.GRAPH_DATA;
"""

from __future__ import annotations
import argparse
import glob
import json
import math
import os
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Set, Tuple, Any

import yaml


# ----------------------------- IO helpers ---------------------------------- #

def load_yaml(path: str) -> Any:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
    return data


# ----------------------------- Aliases ------------------------------------- #

def build_alias_maps(alias_raw: Any) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Returns:
      alias_to_canonical: maps any alias -> canonical
      canonical_to_aliases: maps canonical -> [aliases]
    Accepts flexible schemas, e.g.:
      1) { canonical: [aliases...] }
      2) { canonical: { aliases: [..] } }
      3) { aliases: { alias1: canonical, alias2: canonical2 } }
      4) list of {canonical: "...", aliases: [...]} dicts
    """
    alias_to_canonical: Dict[str, str] = {}
    canonical_to_aliases: Dict[str, List[str]] = defaultdict(list)

    if not alias_raw:
        return alias_to_canonical, canonical_to_aliases

    def add_pair(canon: str, alias: str):
        c = (canon or "").strip()
        a = (alias or "").strip()
        if not c or not a:
            return
        alias_to_canonical[a] = c
        if a != c:
            canonical_to_aliases[c].append(a)

    if isinstance(alias_raw, dict):
        # case 3: nested "aliases" maps alias->canonical
        if "aliases" in alias_raw and isinstance(alias_raw["aliases"], dict):
            for a, c in alias_raw["aliases"].items():
                add_pair(str(c), str(a))
        # case 1 & 2: canonical -> list or {aliases:[...]}
        for k, v in alias_raw.items():
            if k == "aliases":
                continue
            canon = str(k)
            if isinstance(v, list):
                for a in v:
                    add_pair(canon, str(a))
            elif isinstance(v, dict) and "aliases" in v and isinstance(v["aliases"], list):
                for a in v["aliases"]:
                    add_pair(canon, str(a))
    elif isinstance(alias_raw, list):
        # case 4
        for item in alias_raw:
            if not isinstance(item, dict):
                continue
            canon = str(item.get("canonical", "")).strip()
            for a in item.get("aliases", []) or []:
                add_pair(canon, str(a))
    return alias_to_canonical, canonical_to_aliases


def canonicalize(tag: str, alias_to_canonical: Dict[str, str]) -> str:
    t = (tag or "").strip()
    return alias_to_canonical.get(t, t)


# ----------------------------- Tag index parsing --------------------------- #

def extract_tag_mapping_from_index(idx: Any) -> Dict[str, List[str]]:
    """
    Normalize any historical tag_index.yml schema into:
      { tag_name: [pulse_paths...] }
    Supports shapes seen in the repo history:
      A) { <tag>: { pulses: [...] } }
      B) { <tag>: [ "pulse/..." ] }
      C) { <tag>: { linked_pulses: [...] } }
      D) { tags: { <tag>: { pulses: [...] } } }
      E) { tags: { <tag>: { linked_pulses: [...] } } }
    """
    if not idx or not isinstance(idx, dict):
        return {}

    if "tags" in idx and isinstance(idx["tags"], dict):
        idx = idx["tags"]

    out: Dict[str, List[str]] = {}
    for tag, val in idx.items():
        if isinstance(val, dict):
            if "pulses" in val and isinstance(val["pulses"], list):
                out[tag] = [str(x) for x in val["pulses"]]
            elif "linked_pulses" in val and isinstance(val["linked_pulses"], list):
                out[tag] = [str(x) for x in val["linked_pulses"]]
        elif isinstance(val, list):
            out[tag] = [str(x) for x in val]
        # else: ignore unknown shapes quietly
    return out


# ----------------------------- Pulse scan fallback ------------------------- #

def scan_pulses_for_tags(pulse_glob: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Scan pulse/**/*.yml and build:
      tag_to_pulses: { tag: [pulse_path,...] }
      pulse_to_tags: { pulse_path: [tag,...] }
    Also collect 'papers' and 'podcasts' per pulse to later aggregate per tag.
    """
    tag_to_pulses: Dict[str, List[str]] = defaultdict(list)
    pulse_to_tags: Dict[str, List[str]] = {}
    pulse_resources: Dict[str, Dict[str, List[str]]] = {}

    for path in glob.glob(pulse_glob, recursive=True):
        try:
            data = load_yaml(path) or {}
        except Exception:
            data = {}
        tags = data.get("tags") or data.get("Tags") or []
        tags = [str(t) for t in tags if isinstance(t, (str, int))]
        pulse_to_tags[path] = tags

        papers = data.get("papers") or []
        podcasts = data.get("podcasts") or []
        pulse_resources[path] = {
            "papers": [str(u) for u in papers if isinstance(u, str)],
            "podcasts": [str(u) for u in podcasts if isinstance(u, str)],
        }

        for t in tags:
            tag_to_pulses[t].append(path)

    return dict(tag_to_pulses), pulse_to_tags, pulse_resources


# ----------------------------- Edge building -------------------------------- #

def build_edges_from_pulses(pulse_to_tags: Dict[str, List[str]]) -> Dict[Tuple[str, str], int]:
    """
    Build undirected edges between tags that co-occur in the same pulse.
    Returns weighted edge counts.
    """
    weights: Dict[Tuple[str, str], int] = defaultdict(int)
    for _, tags in pulse_to_tags.items():
        uniq = sorted(set(tags))
        for a, b in combinations(uniq, 2):
            edge = (a, b) if a < b else (b, a)
            weights[edge] += 1
    return dict(weights)


# ----------------------------- Centrality ---------------------------------- #

def compute_centrality(tag_to_pulses: Dict[str, List[str]],
                       edges: Dict[Tuple[str, str], int]) -> Dict[str, float]:
    """
    Simple degree-based centrality scaled to [0,1].
    """
    degree: Dict[str, int] = defaultdict(int)
    for (a, b), _w in edges.items():
        degree[a] += 1
        degree[b] += 1
    # include isolated tags
    for t in tag_to_pulses.keys():
        degree.setdefault(t, 0)

    if not degree:
        return {t: 0.0 for t in tag_to_pulses.keys()}

    max_deg = max(degree.values()) if degree else 1
    return {t: (degree[t] / max_deg if max_deg > 0 else 0.0) for t in degree}


# ----------------------------- Resources per tag --------------------------- #

def aggregate_resources_per_tag(tag_to_pulses: Dict[str, List[str]],
                                pulse_resources: Dict[str, Dict[str, List[str]]]
                                ) -> Dict[str, Dict[str, List[str]]]:
    """
    Combine pulse-level {papers,podcasts} into tag-level sets.
    """
    out: Dict[str, Dict[str, List[str]]] = {}
    for tag, pulses in tag_to_pulses.items():
        papers: Set[str] = set()
        podcasts: Set[str] = set()
        for p in pulses:
            res = pulse_resources.get(p, {})
            for u in res.get("papers", []) or []:
                papers.add(u)
            for u in res.get("podcasts", []) or []:
                podcasts.add(u)
        out[tag] = {
            "papers": sorted(papers),
            "podcasts": sorted(podcasts),
        }
    return out


# ----------------------------- Main build ---------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    args = ap.parse_args()

    # Load alias map (optional)
    alias_raw = load_yaml(args.alias_map)
    alias_to_canon, canon_to_aliases = build_alias_maps(alias_raw)

    # Try tag index
    idx = load_yaml(args.tag_index)
    tag_to_pulses = extract_tag_mapping_from_index(idx)

    # Fallback: scan pulses if index is empty
    if not tag_to_pulses:
        print("INFO: tag_index.yml empty or unsupported → scanning pulses …")
        tag_to_pulses, pulse_to_tags, pulse_resources = scan_pulses_for_tags(args.pulse_glob)
    else:
        # Build pulse_to_tags & resources from tag_to_pulses (reverse)
        pulse_to_tags: Dict[str, List[str]] = defaultdict(list)
        for t, plist in tag_to_pulses.items():
            for p in plist:
                pulse_to_tags[p].append(t)
        # Try to harvest resources by scanning pulses mentioned
        pulse_resources = {}
        for p in pulse_to_tags.keys():
            data = load_yaml(p) or {}
            papers = data.get("papers") or []
            podcasts = data.get("podcasts") or []
            pulse_resources[p] = {
                "papers": [str(u) for u in papers if isinstance(u, str)],
                "podcasts": [str(u) for u in podcasts if isinstance(u, str)],
            }

    # Apply aliases: collapse tags to canonical
    canonical_tag_to_pulses: Dict[str, Set[str]] = defaultdict(set)
    for tag, plist in tag_to_pulses.items():
        canon = canonicalize(tag, alias_to_canon)
        for p in plist:
            canonical_tag_to_pulses[canon].add(p)

    # Also canonicalize pulse_to_tags
    canonical_pulse_to_tags: Dict[str, List[str]] = {}
    for p, tags in pulse_to_tags.items():
        ctags = sorted(set(canonicalize(t, alias_to_canon) for t in tags))
        canonical_pulse_to_tags[p] = ctags

    # Rebuild edges using canonical tags
    edges_w = build_edges_from_pulses(canonical_pulse_to_tags)

    # Compute centrality
    canon_tag_to_pulses_list = {t: sorted(list(v)) for t, v in canonical_tag_to_pulses.items()}
    centrality = compute_centrality(canon_tag_to_pulses_list, edges_w)

    # Aggregate resources at tag-level
    tag_resources = aggregate_resources_per_tag(canon_tag_to_pulses_list, pulse_resources)

    # Build nodes/links
    nodes = []
    for t, plist in canon_tag_to_pulses_list.items():
        nodes.append({
            "id": t,
            "count": len(plist),
            "centrality": round(float(centrality.get(t, 0.0)), 6),
            "aliases": sorted(canon_to_aliases.get(t, [])),
        })
    # sort nodes by centrality desc, then name
    nodes.sort(key=lambda n: (-n["centrality"], n["id"].lower()))

    links = []
    for (a, b), w in sorted(edges_w.items()):
        links.append({"source": a, "target": b, "weight": int(w)})

    stats = {
        "tags": len(nodes),
        "edges": len(links),
        "pulses": len(canonical_pulse_to_tags),
        "alias_entries": sum(len(v) for v in canon_to_aliases.values())
    }

    graph = {
        "nodes": nodes,
        "links": links,
        "tagResources": tag_resources,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(args.out_js), exist_ok=True)
    with open(args.out_js, "w", encoding="utf-8") as f:
        f.write("window.GRAPH_DATA = ")
        json.dump(graph, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\nwindow.TAG_GRAPH = window.GRAPH_DATA;\n")

    print(f"Wrote {args.out_js} with {stats['tags']} tags, {stats['edges']} edges, {stats['pulses']} pulses.")


if __name__ == "__main__":
    main()
