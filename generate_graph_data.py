import yaml
import json
import os
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
OUT_PRIMARY = "docs/graph_data.js"
OUT_SECONDARY = "docs/graph_data.generated.js"  # optional mirror for debugging

def load_tag_index(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

def normalize_to_tag_map(raw):
    """
    Accepts either:
      A) dict[tag] -> {links: [...], pulses: [...], ...}
      B) list of dicts like [{"tag": "...", "links": [...]}]
      C) simple list of tag strings
    Returns dict[tag] -> {"links": set(), "pulses": set(), "centrality": float?}
    """
    tag_map = {}

    if isinstance(raw, dict):
        # Newer format: { tag: {links:[], pulses:[], ...}, ... }
        for tag, payload in raw.items():
            if not isinstance(payload, dict):
                payload = {}
            links = set(payload.get("links", []) or [])
            pulses = set(payload.get("pulses", []) or [])
            cent = payload.get("centrality", None)
            tag_map[tag] = {"links": links, "pulses": pulses, "centrality": cent}

    elif isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, str):
                tag_map.setdefault(entry, {"links": set(), "pulses": set(), "centrality": None})
            elif isinstance(entry, dict):
                # expect {"tag": "...", "links": [...], ...}
                tag = entry.get("tag")
                if not tag:
                    # if it’s a single-key dict like {"RGP": {...}}
                    if len(entry) == 1:
                        tag, payload = next(iter(entry.items()))
                        if isinstance(payload, dict):
                            links = set(payload.get("links", []) or [])
                            pulses = set(payload.get("pulses", []) or [])
                            cent = payload.get("centrality", None)
                            tag_map[tag] = {"links": links, "pulses": pulses, "centrality": cent}
                            continue
                    # skip malformed
                    continue
                links = set(entry.get("links", []) or [])
                pulses = set(entry.get("pulses", []) or [])
                cent = entry.get("centrality", None)
                tag_map[tag] = {"links": links, "pulses": pulses, "centrality": cent}
    else:
        # unknown format → empty graph (fail safe)
        pass

    # Ensure all linked tags exist as nodes, even if they had no own entry
    all_links = set()
    for v in tag_map.values():
        all_links |= set(v["links"])
    for l in all_links:
        tag_map.setdefault(l, {"links": set(), "pulses": set(), "centrality": None})

    return tag_map

def compute_centrality(tag_map):
    """
    Compute a simple degree centrality (in+out) normalized to [0,1].
    Uses undirected degree from links for now.
    """
    degree = defaultdict(int)
    for tag, payload in tag_map.items():
        for nbr in payload["links"]:
            degree[tag] += 1
            degree[nbr] += 1

    max_deg = max(degree.values()) if degree else 0
    for tag, payload in tag_map.items():
        if payload["centrality"] is None:
            if max_deg == 0:
                payload["centrality"] = 0.0
            else:
                payload["centrality"] = round(degree[tag] / max_deg, 4)

def build_graph(tag_map):
    tag_to_id = {tag: i for i, tag in enumerate(sorted(tag_map.keys()))}

    nodes = []
    for tag, payload in sorted(tag_map.items()):
        nodes.append({
            "id": tag_to_id[tag],
            "label": tag,
            "centrality": payload.get("centrality", 0.0)
        })

    links = []
    for tag, payload in tag_map.items():
        src = tag_to_id[tag]
        for tgt_tag in payload["links"]:
            if tgt_tag in tag_to_id:
                links.append({"source": src, "target": tag_to_id[tgt_tag]})

    return {"nodes": nodes, "links": links}

def write_js(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(obj, indent=2))
        f.write(";")

def main():
    try:
        raw = load_tag_index(TAG_INDEX_PATH)
    except FileNotFoundError:
        print(f"❌ {TAG_INDEX_PATH} not found. Writing empty graph.")
        write_js({"nodes": [], "links": []}, OUT_PRIMARY)
        write_js({"nodes": [], "links": []}, OUT_SECONDARY)
        return

    tag_map = normalize_to_tag_map(raw)
    compute_centrality(tag_map)
    graph = build_graph(tag_map)

    write_js(graph, OUT_PRIMARY)
    write_js(graph, OUT_SECONDARY)

    print(f"✅ Graph has {len(graph['nodes'])} nodes and {len(graph['links'])} links.")
    print(f"✅ Wrote {OUT_PRIMARY} and {OUT_SECONDARY}")

if __name__ == "__main__":
    main()
