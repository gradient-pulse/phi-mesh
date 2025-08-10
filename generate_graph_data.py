#!/usr/bin/env python3
# generate_graph_data.py
# Builds docs/data.js from meta/tag_index.yml or (if empty/missing) from pulse/**/*.yml.
# Usage:
#   python generate_graph_data.py \
#       --tag-index meta/tag_index.yml \
#       --alias-map meta/aliases.yml \
#       --pulse-glob "pulse/**/*.yml" \
#       --out-js docs/data.js \
#       [--debug]

import argparse, json, sys, pathlib, glob
from collections import defaultdict, Counter
from itertools import combinations

try:
    import yaml
except Exception as e:
    print("ERROR: pyyaml is required.", file=sys.stderr)
    sys.exit(2)

def read_text(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def load_yaml(p: pathlib.Path):
    if not p.exists():
        return None
    txt = read_text(p)
    if not txt.strip():
        return None
    try:
        return yaml.safe_load(txt)
    except Exception as e:
        print(f"WARNING: Failed to parse YAML {p}: {e}", file=sys.stderr)
        return None

def load_alias_map(alias_path: pathlib.Path):
    # aliases.yml can be {"canonical": ["alias1","alias2", ...], ...}
    # or {"aliases": {"canonical": [...]} }
    aliases_raw = load_yaml(alias_path)
    alias_to_canon = {}
    if not aliases_raw:
        return alias_to_canon

    if isinstance(aliases_raw, dict) and "aliases" in aliases_raw and isinstance(aliases_raw["aliases"], dict):
        items = aliases_raw["aliases"].items()
    elif isinstance(aliases_raw, dict):
        items = aliases_raw.items()
    else:
        items = []

    for canon, aliases in items:
        if not aliases: 
            continue
        for a in (aliases if isinstance(aliases, list) else [aliases]):
            if not a: 
                continue
            alias_to_canon[str(a).strip()] = str(canon).strip()
    return alias_to_canon

def normalize(tag: str) -> str:
    return str(tag).strip()

def apply_alias(tag: str, alias_to_canon: dict) -> str:
    t = normalize(tag)
    # match raw, and also case-insensitive
    if t in alias_to_canon:
        return normalize(alias_to_canon[t])
    # fallback case-insensitive
    lower_map = {k.lower(): v for k, v in alias_to_canon.items()}
    if t.lower() in lower_map:
        return normalize(lower_map[t.lower()])
    return t

def parse_tag_index_any_shape(obj):
    """
    Accepts several historical shapes and returns:
      tags -> set[pulses]
      related -> set[(tagA, tagB)]  (optional)
    """
    tag_to_pulses = defaultdict(set)
    related_edges = set()

    if not obj:
        return tag_to_pulses, related_edges

    # Shape A: {"tags": { "<tag>": {"linked_pulses":[...], "related_concepts":[...] }, ... } }
    if isinstance(obj, dict) and "tags" in obj and isinstance(obj["tags"], dict):
        for tag, info in obj["tags"].items():
            if isinstance(info, dict):
                for p in info.get("linked_pulses", []) or []:
                    tag_to_pulses[tag].add(str(p))
                for r in info.get("related_concepts", []) or []:
                    related_edges.add((tag, str(r)))
        return tag_to_pulses, related_edges

    # Shape B: flat dict mapping tag -> list of pulse paths
    # e.g. { "RGP":[ "pulse/2025-..yml", ... ], "NT":[ ... ] }
    if isinstance(obj, dict):
        for tag, val in obj.items():
            if isinstance(val, list):
                for p in val:
                    tag_to_pulses[tag].add(str(p))
        return tag_to_pulses, related_edges

    # Shape C: dict-of-dicts like { tag: { "pulses":[...], "links":[...] } }
    if isinstance(obj, dict):
        for tag, info in obj.items():
            if isinstance(info, dict):
                for p in info.get("pulses", []) or []:
                    tag_to_pulses[tag].add(str(p))
                for r in info.get("links", []) or []:
                    related_edges.add((tag, str(r)))
        return tag_to_pulses, related_edges

    # Shape D: list of dict entries with nested keys
    if isinstance(obj, list):
        for entry in obj:
            if isinstance(entry, dict):
                for tag, info in entry.items():
                    if isinstance(info, dict):
                        for p in info.get("pulses", []) or []:
                            tag_to_pulses[tag].add(str(p))
                        for r in info.get("links", []) or []:
                            related_edges.add((tag, str(r)))
                    elif isinstance(info, list):
                        for p in info:
                            tag_to_pulses[tag].add(str(p))
    return tag_to_pulses, related_edges

def derive_from_pulses(pulse_glob: str):
    """
    Scan pulse/**/*.yml and build:
      - tag_to_pulses: tag -> set[pulse_relpath]
      - co_occurrence edges: pairs of tags that appear together in a pulse
      - per-tag resources (papers, podcasts) aggregated across pulses
    """
    tag_to_pulses = defaultdict(set)
    edges = Counter()
    resources = defaultdict(lambda: {"papers": set(), "podcasts": set()})

    for path in glob.glob(pulse_glob, recursive=True):
        p = pathlib.Path(path)
        obj = load_yaml(p)
        if not isinstance(obj, dict):
            continue

        tags = obj.get("tags") or obj.get("tag") or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [normalize(t) for t in tags if t]

        if not tags:
            continue

        # record tag -> pulse
        for t in set(tags):
            tag_to_pulses[t].add(str(p.as_posix()))

        # co-occurrence edges between all tag pairs in this pulse
        for a, b in combinations(sorted(set(tags)), 2):
            edges[(a, b)] += 1

        # collect any per-pulse resources under each tag
        for lst_name, key in (("papers", "papers"), ("podcasts", "podcasts")):
            lst = obj.get(key) or []
            for t in set(tags):
                for it in lst:
                    resources[t][lst_name].add(str(it))

    # turn co-occurrence counts into edge list
    related_edges = set()
    for (a, b), cnt in edges.items():
        # store undirected edge
        related_edges.add((a, b))

    # materialize resources to lists
    res_final = {t: {"papers": sorted(list(v["papers"])),
                     "podcasts": sorted(list(v["podcasts"]))}
                 for t, v in resources.items()}

    return tag_to_pulses, related_edges, res_final

def build_graph(tag_to_pulses, related_edges, alias_to_canon):
    # apply aliases
    canon_map = {}
    for t in list(tag_to_pulses.keys()) + [x for e in related_edges for x in e]:
        canon_map[t] = apply_alias(t, alias_to_canon)

    # merge pulse sets under canonical names
    canon_tag_to_pulses = defaultdict(set)
    for t, pulses in tag_to_pulses.items():
        canon_tag_to_pulses[canon_map[t]].update(pulses)

    # rebuild related edges under canonical names (dedupe self-loops)
    canon_edges = set()
    for a, b in related_edges:
        ca, cb = canon_map[a], canon_map[b]
        if ca != cb:
            # normalize undirected
            e = tuple(sorted([ca, cb]))
            canon_edges.add(e)

    # degree / centrality (very simple: co-occur degree + pulse count weight)
    degree = Counter()
    for a, b in canon_edges:
        degree[a] += 1
        degree[b] += 1
    for t, pulses in canon_tag_to_pulses.items():
        degree[t] += min(len(pulses), 5)  # small bonus for usage

    # nodes
    nodes = []
    if degree:
        max_deg = max(degree.values()) or 1
    else:
        max_deg = 1
    for t in sorted(canon_tag_to_pulses.keys()):
        centrality = degree[t] / max_deg if max_deg else 0.0
        nodes.append({"id": t, "centrality": round(centrality, 4), "count": len(canon_tag_to_pulses[t])})

    # links
    links = [{"source": a, "target": b} for (a, b) in sorted(canon_edges)]

    return nodes, links, canon_tag_to_pulses

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    tag_index_path = pathlib.Path(args.tag_index)
    alias_path = pathlib.Path(args.alias_map)
    out_js = pathlib.Path(args.out_js)

    alias_to_canon = load_alias_map(alias_path)

    # 1) Try tag_index
    tag_index_obj = load_yaml(tag_index_path)
    tag_to_pulses, related_edges = parse_tag_index_any_shape(tag_index_obj)

    # If empty, 2) derive from pulses
    resources_by_tag = {}
    if not tag_to_pulses:
        print("INFO: tag_index was empty or unparseable; deriving tags from pulses.", file=sys.stderr)
        tag_to_pulses, related_edges, resources_by_tag = derive_from_pulses(args.pulse_glob)

    # If still empty, emit a minimal, valid JS so downstream doesn’t crash
    if not tag_to_pulses:
        print("WARNING: No tags discovered. Emitting empty graph.", file=sys.stderr)
        graph_obj = {
            "nodes": [],
            "links": [],
            "tagResources": {},
            "stats": {"tags": 0, "edges": 0}
        }
        out_js.parent.mkdir(parents=True, exist_ok=True)
        payload = (
            "window.GRAPH_DATA = " + json.dumps(graph_obj, ensure_ascii=False) + ";\n"
            "window.TAG_GRAPH = window.GRAPH_DATA;\n"
        )
        out_js.write_text(payload, encoding="utf-8")
        return

    # 3) Build graph with aliases
    nodes, links, canon_tag_to_pulses = build_graph(tag_to_pulses, related_edges, alias_to_canon)

    # 4) resources map (papers/podcasts) — if we didn’t derive earlier, make empty buckets
    tag_resources = {}
    for t in {n["id"] for n in nodes}:
        tag_resources[t] = resources_by_tag.get(t, {"papers": [], "podcasts": []})

    graph_obj = {
        "nodes": nodes,
        "links": links,
        "tagResources": tag_resources,
        "stats": {"tags": len(nodes), "edges": len(links)}
    }

    if args.debug:
        print("DEBUG: tags:", len(nodes), "edges:", len(links), file=sys.stderr)
        print("DEBUG sample nodes:", nodes[:5], file=sys.stderr)

    out_js.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        "window.GRAPH_DATA = " + json.dumps(graph_obj, ensure_ascii=False) + ";\n"
        "window.TAG_GRAPH = window.GRAPH_DATA;\n"
    )
    out_js.write_text(payload, encoding="utf-8")

if __name__ == "__main__":
    main()
