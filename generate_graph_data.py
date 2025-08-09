#!/usr/bin/env python3
# generate_graph_data.py
# Build docs/graph_data.js from meta/tag_index.yml

import yaml
import json
import os
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_JS_PATH = "docs/graph_data.js"

def load_tag_index(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Accept both historical schemas:
    # 1) dict-of-tags: { "RGP": {"links":[...], "pulses":[...], ...}, ... }
    # 2) list-of-entries: [ {"tag":"RGP","links":[...],"centrality":0.5}, "or", ... ]
    if isinstance(data, dict):
        # new schema: top-level keys are tag names
        entries = []
        for tag, payload in data.items():
            if not isinstance(payload, dict):
                # tolerate odd values
                payload = {}
            entries.append({
                "tag": tag,
                "links": list(payload.get("links", []) or []),
                "centrality": float(payload.get("centrality", 0.0)),
            })
        return entries

    elif isinstance(data, list):
        # older schema already a list of entries or tag strings
        entries = []
        for item in data:
            if isinstance(item, str):
                entries.append({"tag": item, "links": [], "centrality": 0.0})
            elif isinstance(item, dict):
                tag = item.get("tag")
                if not tag:
                    # try to infer single-key dict like {"RGP": {...}}
                    if len(item.keys()) == 1:
                        tag = next(iter(item.keys()))
                        payload = item[tag] or {}
                        entries.append({
                            "tag": tag,
                            "links": list(payload.get("links", []) or []),
                            "centrality": float(payload.get("centrality", 0.0)),
                        })
                        continue
                    else:
                        continue
                entries.append({
                    "tag": tag,
                    "links": list(item.get("links", []) or []),
                    "centrality": float(item.get("centrality", 0.0)),
                })
        return entries

    else:
        raise ValueError(f"Unsupported tag_index format at {path}: {type(data)}")

def normalize_and_build(entries):
    # Collect all tags mentioned anywhere (nodes + link targets)
    all_tags = set()
    tag_to_links = defaultdict(list)
    tag_centrality = {}

    for e in entries:
        tag = e.get("tag")
        if not tag:
            continue
        all_tags.add(tag)
        tag_centrality[tag] = float(e.get("centrality", 0.0))

        links = e.get("links") or []
        # Ensure list of strings
        if isinstance(links, str):
            links = [links]
        for t in links:
            if not t or not isinstance(t, str):
                continue
            tag_to_links[tag].append(t)
            all_tags.add(t)

    # Build numeric IDs
    tags_sorted = sorted(all_tags)
    tag_to_id = {t: i for i, t in enumerate(tags_sorted)}

    # Nodes
    nodes = []
    for t in tags_sorted:
        nodes.append({
            "id": tag_to_id[t],
            "label": t,
            "centrality": float(tag_centrality.get(t, 0.0)),
        })

    # Links (de-duped, undirected by default)
    seen = set()
    links = []
    for src, outs in tag_to_links.items():
        for dst in outs:
            if src == dst:
                continue
            if dst not in tag_to_id or src not in tag_to_id:
                continue
            key = tuple(sorted((src, dst)))  # undirected de-dup
            if key in seen:
                continue
            seen.add(key)
            links.append({
                "source": tag_to_id[src],
                "target": tag_to_id[dst],
            })

    return {"nodes": nodes, "links": links}

def write_js(graph, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(graph, indent=2))
        f.write(";\n")

if __name__ == "__main__":
    print(f"📥 Reading {TAG_INDEX_PATH} …")
    entries = load_tag_index(TAG_INDEX_PATH)
    graph = normalize_and_build(entries)
    write_js(graph, OUTPUT_JS_PATH)
    print(f"✅ Graph data written to {OUTPUT_JS_PATH}")
    print(f"   Nodes: {len(graph['nodes'])}  Links: {len(graph['links'])}")
    if len(graph["links"]) == 0:
        print("⚠️  No links were generated. Check meta/tag_index.yml 'links:' lists for each tag.")
    else:
        # Show a few sample edges for sanity
        sample = graph["links"][:5]
        print(f"   Sample links (first {len(sample)}): {sample}")
