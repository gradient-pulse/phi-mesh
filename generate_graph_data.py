import yaml
import json
import os
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
OUT_PATH = "docs/graph_data.js"

def load_tag_index(path):
    """
    Supports both shapes:
    A) dict-of-dicts (current):
       {
         "RGP": { "links": [...], "pulses": [...], ... },
         "NT":  { "links": [...], ... },
         ...
       }

    B) legacy list form (fallback):
       [
         {"tag": "RGP", "links": [...], "centrality": 0.2},
         "LooseStringTag",
         ...
       ]
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    tag_map = {}

    if isinstance(raw, dict):
        # Current canonical shape
        for tag, payload in raw.items():
            links = []
            if isinstance(payload, dict):
                links = payload.get("links", []) or []
            tag_map[tag] = {
                "links": [str(x) for x in links if isinstance(x, (str,))],
            }
    elif isinstance(raw, list):
        # Legacy list shape
        for entry in raw:
            if isinstance(entry, str):
                tag_map[entry] = {"links": []}
            elif isinstance(entry, dict):
                tag = entry.get("tag")
                if not tag:
                    continue
                links = entry.get("links", []) or []
                tag_map[tag] = {
                    "links": [str(x) for x in links if isinstance(x, (str,))],
                }
    else:
        raise ValueError("Unsupported tag_index.yml structure")

    return tag_map

def ensure_all_nodes(tag_map):
    """Ensure all linked tags exist as nodes, even if they weren't declared as keys."""
    all_tags = set(tag_map.keys())
    for tag, data in tag_map.items():
        for linked in data.get("links", []):
            if linked not in all_tags:
                all_tags.add(linked)
                tag_map[linked] = {"links": []}
    return tag_map

def to_undirected_adjacency(tag_map):
    """Build undirected adjacency so degree/centrality reflect mutual connectivity."""
    adj = defaultdict(set)
    for a, data in tag_map.items():
        for b in data.get("links", []):
            if a == b:
                continue
            adj[a].add(b)
            adj[b].add(a)  # add reverse link for robustness
    return adj

def compute_centrality(adj):
    """Simple degree centrality normalized to [0,1]."""
    degrees = {n: len(neigh) for n, neigh in adj.items()}
    # include isolated nodes
    for n in adj.keys():
        degrees.setdefault(n, 0)
    if not degrees:
        return { }
    max_deg = max(degrees.values()) or 1
    return {n: (degrees[n] / max_deg) for n in adj.keys()}

def build_graph(tag_map):
    # Make sure every linked tag exists as a node
    tag_map = ensure_all_nodes(tag_map)

    # Adjacency & centrality
    adj = to_undirected_adjacency(tag_map)
    # Include isolated nodes (no links) in adjacency
    for t in tag_map.keys():
        adj.setdefault(t, set())
    centrality = compute_centrality(adj)

    # Nodes: use string IDs (the tag names) for easier debugging
    nodes = []
    for tag in sorted(tag_map.keys()):
        nodes.append({
            "id": tag,            # string id == tag name
            "label": tag,         # what UI shows
            "centrality": round(float(centrality.get(tag, 0.0)), 6)
        })

    # Links: emit both directions for visual stability, dedup to avoid doubles
    seen = set()
    links = []
    for a, neigh in adj.items():
        for b in neigh:
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            # store as directed pair A->B and B->A so forces are well distributed
            links.append({"source": a, "target": b})
            links.append({"source": b, "target": a})

    return {"nodes": nodes, "links": links}

def write_graph_js(graph, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(graph, ensure_ascii=False, indent=2))
        f.write(";\n")
    print(f"✅ Graph data written to {out_path} "
          f"({len(graph['nodes'])} nodes, {len(graph['links'])} links)")

def main():
    tag_map = load_tag_index(TAG_INDEX_PATH)
    graph = build_graph(tag_map)
    write_graph_js(graph, OUT_PATH)

if __name__ == "__main__":
    main()
