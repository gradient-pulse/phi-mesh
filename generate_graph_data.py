#!/usr/bin/env python3
"""
Generate docs/graph_data.js from meta/tag_index.yml.

- Accepts either:
    { tags: { <Tag>: {links:[], pulses:[]}, ... } }
  or a flat mapping:
    { <Tag>: {links:[], pulses:[]}, ... }

- Normalizes tag ids (lowercase + underscores), but preserves labels.
- De-duplicates nodes/links, merges weights, ignores self-links.
- Computes a simple centrality = weighted degree.
- Writes docs/graph_data.js (pretty) and docs/graph_data.generated.js (same).
"""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
META = ROOT / "meta" / "tag_index.yml"
OUT_JS = ROOT / "docs" / "graph_data.js"
OUT_GEN = ROOT / "docs" / "graph_data.generated.js"

def normalize_id(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    s = s.replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^\w_]+", "", s)  # keep letters, digits, underscore
    return s.lower()

def load_tags_dict():
    if not META.exists():
        raise FileNotFoundError(f"Missing {META}")

    with META.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # detect layout
    if "tags" in data and isinstance(data["tags"], dict):
        tags_dict = data["tags"]
    else:
        # flat mapping form: filter only entries that look like a tag node
        tags_dict = {k: v for k, v in data.items()
                     if isinstance(v, dict) and ("links" in v or "pulses" in v)}
    return tags_dict, data

def build_alias_map(data):
    """
    Optional alias support if present under a 'canonical_tags' section:
      canonical_tags:
        Some_Canon:
          - alias1
          - alias2
    Returns alias->canonical label mapping.
    """
    alias_map = {}
    ct = data.get("canonical_tags") or data.get("canonicalTags")
    if isinstance(ct, dict):
        for canon, aliases in ct.items():
            if isinstance(aliases, list):
                canon_id = normalize_id(canon)
                for a in aliases:
                    alias_map[normalize_id(a)] = canon_id
    return alias_map

def canonize(id_or_label, alias_map, known_ids):
    nid = normalize_id(id_or_label)
    nid = alias_map.get(nid, nid)
    # If alias points to a canonical that doesn't exist yet, keep nid;
    # caller will decide whether to create a node for it.
    return nid

def generate_graph(tags_dict, alias_map):
    # 1) collect known nodes (canonical ids + labels)
    id_to_label = {}
    for label in tags_dict.keys():
        cid = canonize(label, alias_map, known_ids=None)
        # Prefer most descriptive label: use the exact key (original)
        if cid not in id_to_label:
            id_to_label[cid] = str(label)

    # 2) links (undirected, weighted)
    edge_w = {}  # key = tuple(sorted(idA,idB)) -> weight
    for label, payload in tags_dict.items():
        src = canonize(label, alias_map, id_to_label.keys())
        links = (payload or {}).get("links", []) or []
        for L in links:
            dst = canonize(L, alias_map, id_to_label.keys())
            if not dst or dst == src:
                continue
            # ensure node exists (helps when link references a tag that has no own entry)
            id_to_label.setdefault(dst, L if isinstance(L, str) else str(L))
            a, b = sorted((src, dst))
            edge_w[(a, b)] = edge_w.get((a, b), 0) + 1

    # 3) nodes with centrality
    degree = {nid: 0 for nid in id_to_label.keys()}
    for (a, b), w in edge_w.items():
        degree[a] += w
        degree[b] += w

    nodes = [{
        "id": nid,
        "label": id_to_label[nid],
        "centrality": degree.get(nid, 0)
    } for nid in id_to_label.keys()]

    # stable sort (labels asc)
    nodes.sort(key=lambda n: (n["label"].lower(), n["id"]))

    links = [{
        "source": a,
        "target": b,
        "weight": w
    } for (a, b), w in sorted(edge_w.items(), key=lambda kv: (-kv[1], kv[0]))]

    return {"nodes": nodes, "links": links}

def write_js(graph, path):
    txt = "window.graph = " + json.dumps(graph, ensure_ascii=False, indent=2) + ";\n"
    path.write_text(txt, encoding="utf-8")

def main():
    tags_dict, raw = load_tags_dict()
    alias_map = build_alias_map(raw)

    graph = generate_graph(tags_dict, alias_map)

    # safety: empty link set warning still produces valid file
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    write_js(graph, OUT_JS)
    write_js(graph, OUT_GEN)
    print(f"Wrote {OUT_JS} and {OUT_GEN} ({len(graph['nodes'])} nodes, {len(graph['links'])} links)")

if __name__ == "__main__":
    main()
