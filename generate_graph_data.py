import yaml
import json
import os
import re
from collections import defaultdict
from datetime import datetime

TAG_INDEX_PATH = "meta/tag_index.yml"
OUT_JS_MAIN = "docs/graph_data.js"
OUT_JS_CACHEBUSTER = "docs/graph_data.generated.js"


# --------------------------
# Helpers
# --------------------------
_slug_re = re.compile(r"[^a-z0-9]+")

def slugify(name: str) -> str:
    if not isinstance(name, str):
        name = str(name)
    name = name.strip().lower()
    name = name.replace("-", "_").replace(" ", "_")
    name = _slug_re.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def build_alias_map(canon_block) -> dict:
    """
    Build alias->canonical mapping from a 'canonical_tags' block like:
      canonical_tags:
        Navier_Stokes: [NS_solution, navier-stokes, turbulence]
        Gradient_Syntax: [gradient_syntax, GradientSyntax, gradient-syntax]
    We normalize both sides with slugify and return alias->canon_slug.
    """
    alias2canon = {}
    if not isinstance(canon_block, dict):
        return alias2canon

    for canon, aliases in canon_block.items():
        canon_slug = slugify(canon)
        alias2canon[slugify(canon)] = canon_slug  # allow canonical to map to itself
        if isinstance(aliases, list):
            for a in aliases:
                alias2canon[slugify(a)] = canon_slug
    return alias2canon


def to_canonical(name: str, alias2canon: dict) -> str:
    s = slugify(name)
    return alias2canon.get(s, s)


# --------------------------
# Load & normalize tag index
# --------------------------
def load_tag_index(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Pull canonical map if present
    canon_block = {}
    if isinstance(raw, dict) and "canonical_tags" in raw:
        canon_block = raw.get("canonical_tags") or {}
    alias2canon = build_alias_map(canon_block)

    # Accept either shape:
    # (A) dict of { tag: {links:[...], ...}, ... }
    # (B) list of entries: [{tag:"RGP", links:[...]}, "loose_tag", ...]
    # Also accept a top-level wrapper like {tags: {...}}.
    tags_raw = raw
    if isinstance(raw, dict) and "tags" in raw and isinstance(raw["tags"], dict):
        tags_raw = raw["tags"]

    # Accumulate into canonical buckets
    canon_nodes = defaultdict(lambda: {"links": set(), "labels": set(), "centrality": None})

    if isinstance(tags_raw, dict):
        for tag, payload in tags_raw.items():
            canon_tag = to_canonical(tag, alias2canon)
            canon_nodes[canon_tag]["labels"].add(tag)

            links = []
            cent = None
            if isinstance(payload, dict):
                links = payload.get("links", []) or []
                cent = payload.get("centrality", None)

            # prefer first non-None centrality
            if cent is not None and canon_nodes[canon_tag]["centrality"] is None:
                try:
                    canon_nodes[canon_tag]["centrality"] = float(cent)
                except Exception:
                    pass

            for lk in links:
                canon_nodes[canon_tag]["links"].add(to_canonical(lk, alias2canon))

    elif isinstance(tags_raw, list):
        for entry in tags_raw:
            if isinstance(entry, str):
                canon_tag = to_canonical(entry, alias2canon)
                canon_nodes[canon_tag]["labels"].add(entry)
            elif isinstance(entry, dict):
                tag = entry.get("tag")
                if not tag:
                    continue
                canon_tag = to_canonical(tag, alias2canon)
                canon_nodes[canon_tag]["labels"].add(tag)

                cent = entry.get("centrality", None)
                if cent is not None and canon_nodes[canon_tag]["centrality"] is None:
                    try:
                        canon_nodes[canon_tag]["centrality"] = float(cent)
                    except Exception:
                        pass

                for lk in entry.get("links", []) or []:
                    canon_nodes[canon_tag]["links"].add(to_canonical(lk, alias2canon))

    # materialize to plain dict lists
    result = {}
    for ctag, data in canon_nodes.items():
        # remove self-links after canonicalization
        links = {l for l in data["links"] if l and l != ctag}
        result[ctag] = {
            "links": sorted(links),
            "centrality": data["centrality"],
            # keep one display label (prefer the most common/longest original)
            "label": sorted(data["labels"], key=lambda s: (len(s), s))[-1] if data["labels"] else ctag,
        }
    return result


# --------------------------
# Graph building
# --------------------------
def compute_degree_centrality(tags: dict):
    degree = defaultdict(int)
    for t, payload in tags.items():
        for nbr in payload["links"]:
            degree[t] += 1
            degree[nbr] += 1
    if not degree:
        return {t: 0.0 for t in tags.keys()}
    max_deg = max(degree.values()) or 1
    return {t: degree.get(t, 0) / max_deg for t in tags.keys()}


def build_graph(tags: dict):
    # stable ordering
    tag_list = sorted(tags.keys())
    idx = {t: i for i, t in enumerate(tag_list)}

    comp_cent = compute_degree_centrality(tags)

    nodes = []
    edges = []

    for t in tag_list:
        display = tags[t].get("label", t)
        c = tags[t].get("centrality")
        if c is None:
            c = comp_cent.get(t, 0.0)

        nodes.append({
            "id": idx[t],
            "label": display,
            "centrality": float(round(c, 4)),
        })

        for nbr in tags[t]["links"]:
            if nbr in idx and nbr != t:
                edges.append({"source": idx[t], "target": idx[nbr]})

    # de-duplicate undirected edges
    seen = set()
    dedup = []
    for e in edges:
        a, b = e["source"], e["target"]
        k = (min(a, b), max(a, b))
        if k not in seen:
            seen.add(k)
            dedup.append(e)

    return {"nodes": nodes, "links": dedup}


def write_js(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(obj, indent=2))
        f.write(";\n")


def main():
    tags = load_tag_index(TAG_INDEX_PATH)
    graph = build_graph(tags)

    write_js(graph, OUT_JS_MAIN)
    write_js({"generated_at": datetime.utcnow().isoformat() + "Z", "graph": graph},
             OUT_JS_CACHEBUSTER)

    print(f"✅ Graph data written to {OUT_JS_MAIN} and {OUT_JS_CACHEBUSTER}")
    print(f"   Nodes: {len(graph['nodes'])}  Links: {len(graph['links'])}")


if __name__ == "__main__":
    main()
