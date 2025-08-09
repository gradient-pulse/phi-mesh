#!/usr/bin/env python3
# Build docs/graph_data.js from meta/tag_index.yml
# - Handles multiple historical schemas
# - Falls back to co-occurrence on pulses to create links when 'links:' is absent
# - Emits weight on links; de-dups undirected edges

import yaml, json, os
from collections import defaultdict
from itertools import combinations

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_JS_PATH = "docs/graph_data.js"

def load_raw(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def normalize_entries(raw):
    """
    Return a list of entries with unified keys:
      {"tag": str, "links": [str], "pulses": [str], "centrality": float}
    Accepts:
      A) dict-of-tags -> {TAG: {links:[], pulses:[], centrality:0.0}, ...}
      B) list of similar dicts or strings
      C) simple dict -> {TAG: [pulses...]}  (no links)
    """
    out = []

    if isinstance(raw, dict):
        # Detect simple dict (values are lists of pulses OR dicts)
        for tag, val in raw.items():
            if isinstance(val, dict):
                out.append({
                    "tag": tag,
                    "links": list(val.get("links", []) or []),
                    "pulses": list(val.get("pulses", []) or []),
                    "centrality": float(val.get("centrality", 0.0)),
                })
            elif isinstance(val, list):
                # simple format: tag -> [pulse paths]
                out.append({
                    "tag": tag,
                    "links": [],
                    "pulses": list(val),
                    "centrality": 0.0,
                })
            else:
                out.append({"tag": tag, "links": [], "pulses": [], "centrality": 0.0})
        return out

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                out.append({"tag": item, "links": [], "pulses": [], "centrality": 0.0})
            elif isinstance(item, dict):
                tag = item.get("tag")
                if not tag and len(item.keys()) == 1:
                    # shape like [{"RGP": {...}}]
                    tag = next(iter(item.keys()))
                    payload = item[tag] or {}
                    out.append({
                        "tag": tag,
                        "links": list(payload.get("links", []) or []),
                        "pulses": list(payload.get("pulses", []) or []),
                        "centrality": float(payload.get("centrality", 0.0)),
                    })
                elif tag:
                    out.append({
                        "tag": tag,
                        "links": list(item.get("links", []) or []),
                        "pulses": list(item.get("pulses", []) or []),
                        "centrality": float(item.get("centrality", 0.0)),
                    })
        return out

    raise ValueError(f"Unsupported tag_index format: {type(raw)}")

def build_graph(entries):
    # Collect tags, centralities, direct links, and pulses
    all_tags = set()
    centrality = {}
    direct_links = defaultdict(set)      # tag -> set(other_tag)
    tag_to_pulses = defaultdict(set)     # tag -> set(pulse_ids)

    for e in entries:
        tag = e.get("tag")
        if not tag:
            continue
        all_tags.add(tag)
        centrality[tag] = float(e.get("centrality", 0.0))

        for t in (e.get("links") or []):
            if isinstance(t, str) and t:
                direct_links[tag].add(t)
                all_tags.add(t)

        for p in (e.get("pulses") or []):
            if isinstance(p, str) and p:
                tag_to_pulses[tag].add(p)

    # If there are no direct links, derive by co-occurrence on pulses
    derived_edges = defaultdict(int)  # (a,b) sorted tuple -> weight
    has_any_direct = any(len(v) for v in direct_links.values())

    if not has_any_direct:
        # Build pulse -> set(tags) inverse
        pulse_to_tags = defaultdict(set)
        for t, ps in tag_to_pulses.items():
            for p in ps:
                pulse_to_tags[p].add(t)

        for tags in pulse_to_tags.values():
            for a, b in combinations(sorted(tags), 2):
                derived_edges[(a, b)] += 1

    # Build nodes
    tags_sorted = sorted(all_tags)
    tag_id = {t: i for i, t in enumerate(tags_sorted)}
    nodes = [{"id": tag_id[t], "label": t, "centrality": centrality.get(t, 0.0)} for t in tags_sorted]

    # Build links (direct or derived)
    links = []
    if has_any_direct:
        seen = set()
        for a, outs in direct_links.items():
            for b in outs:
                if a == b or a not in tag_id or b not in tag_id:
                    continue
                key = tuple(sorted((a, b)))
                if key in seen:
                    continue
                seen.add(key)
                links.append({"source": tag_id[a], "target": tag_id[b], "weight": 1})
    else:
        for (a, b), w in derived_edges.items():
            if a in tag_id and b in tag_id and a != b:
                links.append({"source": tag_id[a], "target": tag_id[b], "weight": int(w)})

    return {"nodes": nodes, "links": links}

def write_js(graph, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(graph, indent=2))
        f.write(";\n")

if __name__ == "__main__":
    print(f"📥 Reading {TAG_INDEX_PATH} …")
    raw = load_raw(TAG_INDEX_PATH)
    entries = normalize_entries(raw)
    graph = build_graph(entries)
    write_js(graph, OUTPUT_JS_PATH)
    print(f"✅ Wrote {OUTPUT_JS_PATH}")
    print(f"   Nodes: {len(graph['nodes'])}  Links: {len(graph['links'])}")
    if len(graph["links"]) == 0:
        print("⚠️  No links generated. Check that 'pulses:' are listed per tag or 'links:' exist.")
    else:
        preview = graph["links"][:5]
        print(f"   Sample: {preview}")
