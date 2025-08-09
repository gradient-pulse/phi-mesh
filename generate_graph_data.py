#!/usr/bin/env python3
"""
Generate docs/graph_data.js from meta/tag_index.yml.

Accepts either:
  - { tags: { <Tag>: {...} } }  OR a flat mapping { <Tag>: {...} }
Per-tag fields (any of the following pairs work):
  - links / pulses
  - related_concepts / linked_pulses    (legacy)

Outputs:
  - docs/graph_data.js
  - docs/graph_data.generated.js

Both define:  window.graph = { nodes:[{id,label,centrality}], links:[{source,target,weight}] };
"""

import json
import re
from pathlib import Path

import yaml

ROOT   = Path(__file__).resolve().parent
META   = ROOT / "meta" / "tag_index.yml"
OUT1   = ROOT / "docs" / "graph_data.js"
OUT2   = ROOT / "docs" / "graph_data.generated.js"

# ---------- helpers ----------

def norm_id(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^\w_]+", "", s)  # keep [A-Za-z0-9_]
    return s.lower()

def load_tag_block():
    if not META.exists():
        raise FileNotFoundError(f"Missing {META}")
    with META.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # nested or flat
    tags = data.get("tags")
    if isinstance(tags, dict):
        tag_map = tags
    else:
        # flat: keep only dict entries
        tag_map = {k: v for k, v in data.items()
                   if isinstance(v, dict) and any(k2 in v for k2 in
                      ("links","pulses","related_concepts","linked_pulses"))}
    return data, tag_map

def build_alias_map(data):
    # Optional alias support
    alias_map = {}
    ct = data.get("canonical_tags") or data.get("canonicalTags")
    if isinstance(ct, dict):
        for canonical, aliases in ct.items():
            if isinstance(aliases, list):
                cid = norm_id(canonical)
                for a in aliases:
                    alias_map[norm_id(a)] = cid
    return alias_map

def canonize(tag_label, alias_map):
    nid = norm_id(tag_label)
    return alias_map.get(nid, nid)

# ---------- core ----------

def generate_graph(tag_map, alias_map):
    id_to_label = {}

    # First pass: ensure nodes exist for all tags present as keys
    for label in tag_map.keys():
        cid = canonize(label, alias_map)
        id_to_label.setdefault(cid, str(label))

    # Second pass: collect links with multiple possible field names
    edge_w = {}  # (a,b)->weight
    for label, payload in tag_map.items():
        if not isinstance(payload, dict):
            continue

        src = canonize(label, alias_map)

        # tolerate old/new field names
        links  = payload.get("links")
        if links is None:
            links = payload.get("related_concepts")  # legacy

        if not isinstance(links, list):
            links = []

        for L in links:
            dst = canonize(L, alias_map)
            if not dst or dst == src:
                continue
            # ensure node label for dst
            id_to_label.setdefault(dst, str(L))
            a, b = sorted((src, dst))
            edge_w[(a, b)] = edge_w.get((a, b), 0) + 1

    # Degree-based centrality
    degree = {nid: 0 for nid in id_to_label.keys()}
    for (a, b), w in edge_w.items():
        degree[a] += w
        degree[b] += w

    nodes = [{
        "id": nid,
        "label": id_to_label[nid],
        "centrality": degree.get(nid, 0)
    } for nid in id_to_label.keys()]
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
    data, tag_map = load_tag_block()
    alias_map = build_alias_map(data)
    graph = generate_graph(tag_map, alias_map)

    OUT1.parent.mkdir(parents=True, exist_ok=True)
    write_js(graph, OUT1)
    write_js(graph, OUT2)
    print(f"[graph] nodes={len(graph['nodes'])} links={len(graph['links'])}")
    if not graph["links"]:
        print("[graph] WARNING: produced zero links. Check YAML fields (links/related_concepts).")

if __name__ == "__main__":
    main()
