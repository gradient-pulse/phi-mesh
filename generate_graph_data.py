import yaml
import json
import os
from collections import defaultdict
from datetime import datetime

TAG_INDEX_PATH = "meta/tag_index.yml"
OUT_JS_MAIN = "docs/graph_data.js"
OUT_JS_CACHEBUSTER = "docs/graph_data.generated.js"

def load_tag_index(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Accept either of these shapes:
    # 1) { tag: {links:[...], pulses:[...], ...}, ... }
    # 2) [{tag:"RGP", links:[...], centrality:0.7}, "loose_string_tag", ...]
    tags = {}

    if isinstance(data, dict):
        # Newer canonical format
        for tag, payload in data.items():
            if isinstance(payload, dict):
                links = payload.get("links", []) or []
                centrality = payload.get("centrality", None)
            else:
                links, centrality = [], None
            tags[tag] = {
                "links": [str(x) for x in links],
                "centrality": centrality,
            }

    elif isinstance(data, list):
        # Legacy list format
        for entry in data:
            if isinstance(entry, str):
                tags[entry] = {"links": [], "centrality": None}
            elif isinstance(entry, dict):
                tag = entry.get("tag")
                if not tag:
                    # skip malformed
                    continue
                tags[tag] = {
                    "links": [str(x) for x in entry.get("links", [])],
                    "centrality": entry.get("centrality"),
                }
    else:
        # Anything else → empty set
        tags = {}

    return tags

def compute_degree_centrality(tags: dict):
    # Simple degree centrality normalized to [0,1]
    degree = defaultdict(int)
    for t, payload in tags.items():
        for nbr in payload["links"]:
            degree[t] += 1
            degree[nbr] += 1  # treat as undirected for sizing

    if not degree:
        return {t: 0.0 for t in tags.keys()}

    max_deg = max(degree.values()) or 1
    return {t: degree.get(t, 0) / max_deg for t in tags.keys()}

def build_graph(tags: dict):
    # Node ids are integers; 'label' is the tag string used by sidebar
    tag_list = sorted(tags.keys())
    index_of = {t: i for i, t in enumerate(tag_list)}

    # Prefer provided centrality; otherwise compute by degree
    computed_cent = compute_degree_centrality(tags)

    nodes = []
    links = []

    for t in tag_list:
        c = tags[t].get("centrality")
        if c is None:
            c = computed_cent.get(t, 0.0)

        nodes.append({
            "id": index_of[t],
            "label": t,
            "centrality": float(round(c, 4)),
        })

        for nbr in tags[t]["links"]:
            # Only create link if neighbor exists in the set
            if nbr in index_of:
                links.append({
                    "source": index_of[t],
                    "target": index_of[nbr],
                })

    # De-duplicate links (since we might have both A→B and B→A)
    seen = set()
    dedup_links = []
    for e in links:
        a, b = e["source"], e["target"]
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        dedup_links.append(e)

    return {"nodes": nodes, "links": dedup_links}

def write_js(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(obj, indent=2))
        f.write(";\n")

def main():
    tags = load_tag_index(TAG_INDEX_PATH)
    graph = build_graph(tags)

    # Main file used by the page
    write_js(graph, OUT_JS_MAIN)

    # Extra cache-busted artifact (optional; handy for debugging)
    write_js({
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "graph": graph
    }, OUT_JS_CACHEBUSTER)

    print(f"✅ Graph data written to {OUT_JS_MAIN} and {OUT_JS_CACHEBUSTER}")
    print(f"   Nodes: {len(graph['nodes'])}  Links: {len(graph['links'])}")

if __name__ == "__main__":
    main()
