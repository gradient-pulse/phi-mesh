#!/usr/bin/env python3
import argparse, json, sys, yaml
from collections import defaultdict

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def normalize_tag_map(raw):
    """
    Accepts either:
      - { 'tags': { tag: {links|related_concepts, pulses|linked_pulses} } }
      - { tag: {links|related_concepts, pulses|linked_pulses} }
    Returns a dict: { tag: { 'links': [...], 'pulses': [...] } }
    """
    obj = raw.get("tags") if isinstance(raw, dict) and "tags" in raw and isinstance(raw["tags"], dict) else raw
    if not isinstance(obj, dict):
        raise ValueError("tag_index.yml must be a mapping at top level (optionally under 'tags').")

    out = {}
    for tag, entry in obj.items():
        if not isinstance(entry, dict):
            continue
        # Accept both field names
        links  = entry.get("links", entry.get("related_concepts", [])) or []
        pulses = entry.get("pulses", entry.get("linked_pulses", [])) or []
        # Normalize to lists
        if not isinstance(links, list):  links  = []
        if not isinstance(pulses, list): pulses = []
        out[tag] = {"links": links, "pulses": pulses}
    return out

def apply_alias_map(tag_map, alias_map):
    """
    alias_map example:
      CanonicalTag:
        - alias1
        - alias2
    All aliases are merged into CanonicalTag. If alias had links/pulses, they get merged.
    """
    if not alias_map:
        return tag_map

    # Build reverse index: alias -> canonical
    alias_to_canon = {}
    for canon, aliases in alias_map.items():
        if not isinstance(aliases, list): 
            continue
        for a in aliases:
            alias_to_canon[a] = canon

    merged = dict(tag_map)
    for alias, canon in alias_to_canon.items():
        if alias == canon:
            continue
        if alias in merged:
            # Ensure canon exists
            if canon not in merged:
                merged[canon] = {"links": [], "pulses": []}
            # Merge
            merged[canon]["links"]  = sorted(set(merged[canon]["links"]  + merged[alias]["links"]))
            merged[canon]["pulses"] = sorted(set(merged[canon]["pulses"] + merged[alias]["pulses"]))
            # Redirect links pointing to alias → canon
            for t, data in merged.items():
                if t == alias:
                    continue
                if alias in data["links"]:
                    data["links"] = sorted({canon if x == alias else x for x in data["links"]})
            # Drop alias node
            del merged[alias]
    return merged

def build_graph(tag_map):
    """
    Build nodes/edges for data.js
    Node size is a simple function of degree + pulse count.
    """
    nodes = {}
    edges = set()

    # Create nodes first
    for tag, data in tag_map.items():
        degree = len(set(data.get("links", [])))
        pulse_count = len(set(data.get("pulses", [])))
        score = degree + 0.5 * pulse_count  # simple heuristic
        nodes[tag] = {
            "id": tag,
            "degree": degree,
            "pulses": pulse_count,
            "score": score,
        }

    # Edges from links
    for src, data in tag_map.items():
        for dst in data.get("links", []):
            if dst == src:
                continue
            if dst not in nodes:
                # If a link points to a non-existent tag, still include as a node with zero stats
                nodes[dst] = {"id": dst, "degree": 0, "pulses": 0, "score": 0}
            edge = tuple(sorted((src, dst)))
            edges.add(edge)

    # Recompute degrees (now that we ensured all link targets exist)
    deg = defaultdict(int)
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    for t, d in nodes.items():
        d["degree"] = deg[t]
        d["score"] = d["degree"] + 0.5 * d["pulses"]

    # Convert edges to list of {source,target}
    edge_list = [{"source": a, "target": b} for (a, b) in sorted(edges)]

    return {
        "nodes": [{"id": n["id"], "degree": n["degree"], "pulses": n["pulses"], "score": n["score"]} for n in nodes.values()],
        "links": edge_list,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", required=True)
    ap.add_argument("--alias-map", required=False)
    ap.add_argument("--out-js", required=True)
    args = ap.parse_args()

    tag_raw = load_yaml(args.tag_index)
    tag_map = normalize_tag_map(tag_raw)

    alias_map = None
    if args.alias_map:
        alias_map = load_yaml(args.alias_map) or {}

    tag_map = apply_alias_map(tag_map, alias_map)

    graph = build_graph(tag_map)

    # Write docs/data.js as a JS assignment
    out = "window.GRAPH_DATA = " + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(args.out_js, "w") as f:
        f.write(out)

    # Helpful stdout summary (shows up in Actions logs)
    print(f"[generate_graph_data] nodes={len(graph['nodes'])} links={len(graph['links'])}")

if __name__ == "__main__":
    main()
