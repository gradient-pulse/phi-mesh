import yaml
import json
import os
import re
from collections import defaultdict

META_PATH = "meta/tag_index.yml"
OUT_PRIMARY = "docs/graph_data.js"
OUT_SECONDARY = "docs/graph_data.generated.js"

def norm(s: str) -> str:
    """
    Normalize a tag key for internal matching.
    Lowercase, trim, replace non [a-z0-9]+ with underscores, collapse repeats.
    """
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def load_tag_index(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def coerce_to_entries(raw):
    """
    Coerce various tag_index.yml shapes into a list of standardized entries:
    [
      {
        "tag": "<display label>",
        "key": "<normalized key>",
        "links": [ "<display label>", ... ],
        "link_keys": [ "<normalized key>", ... ],
        "centrality": float | int | None
      },
      ...
    ]
    """
    entries = []

    # Case A: mapping { tag_name: {links: [...], pulses: [...], ...} }
    if isinstance(raw, dict):
        for label, payload in raw.items():
            if not isinstance(payload, dict):
                # Bare mapping: treat as empty payload
                payload = {}
            links = payload.get("links") or []
            # some old variants used "related_concepts" or similar
            links = list(links) + list(payload.get("related_concepts", []))

            cen = payload.get("centrality", None)
            entry = {
                "tag": label,
                "key": norm(label),
                "links": [],
                "link_keys": [],
                "centrality": cen,
            }
            for l in links:
                if not isinstance(l, str):
                    continue
                entry["links"].append(l)
                entry["link_keys"].append(norm(l))
            entries.append(entry)
        return entries

    # Case B: list-of-dicts or list-of-strings
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                entries.append({
                    "tag": item,
                    "key": norm(item),
                    "links": [],
                    "link_keys": [],
                    "centrality": None,
                })
            elif isinstance(item, dict):
                # Accept either already in our shape, or {tag:..., links:..., centrality:...}
                tag = item.get("tag") or item.get("label") or "unknown"
                links = item.get("links", [])
                cen = item.get("centrality", None)
                e = {
                    "tag": tag,
                    "key": norm(tag),
                    "links": [],
                    "link_keys": [],
                    "centrality": cen,
                }
                for l in links:
                    if isinstance(l, str):
                        e["links"].append(l)
                        e["link_keys"].append(norm(l))
                entries.append(e)
        return entries

    # Fallback: nothing usable
    return entries

def build_graph_data(entries):
    # Build lookup of normalized key -> index
    # If duplicates of the same normalized key appear, keep the first
    key_to_index = {}
    unique_entries = []
    for e in entries:
        k = e["key"]
        if k and k not in key_to_index:
            key_to_index[k] = len(unique_entries)
            unique_entries.append(e)

    # Compute default centrality (out-degree) if missing
    out_degree = defaultdict(int)
    for e in unique_entries:
        # count only links that point to existing tags
        unique_targets = set(lk for lk in e["link_keys"] if lk in key_to_index and lk != e["key"])
        out_degree[e["key"]] += len(unique_targets)

    nodes = []
    for idx, e in enumerate(unique_entries):
        cen = e["centrality"]
        if cen is None:
            cen = float(out_degree[e["key"]])
        nodes.append({
            "id": idx,
            "label": e["tag"],
            "centrality": cen,
        })

    # Build links (dedup, no self-loops, only between existing tags)
    seen = set()
    links = []
    for e in unique_entries:
        src_idx = key_to_index[e["key"]]
        for lk in e["link_keys"]:
            if lk not in key_to_index:
                continue
            tgt_idx = key_to_index[lk]
            if tgt_idx == src_idx:
                continue
            tup = (src_idx, tgt_idx)
            if tup in seen:
                continue
            seen.add(tup)
            links.append({"source": src_idx, "target": tgt_idx})

    # Optional: stable sort nodes by label for nicer layout ID order
    # Need to remap links if we reindex
    remap = list(range(len(nodes)))
    # sort returns new order indices
    sorted_pairs = sorted(enumerate(nodes), key=lambda p: p[1]["label"].lower())
    old_to_new = {old_i: new_i for new_i, (old_i, _) in enumerate(sorted_pairs)}
    nodes_sorted = [p[1] for p in sorted_pairs]
    # fix IDs to be 0..n-1
    for new_i, n in enumerate(nodes_sorted):
        n["id"] = new_i
    links_sorted = [{"source": old_to_new[l["source"]], "target": old_to_new[l["target"]]} for l in links]

    return {"nodes": nodes_sorted, "links": links_sorted}

def write_js(graph, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(graph, ensure_ascii=False))
        f.write(";")

def main():
    raw = load_tag_index(META_PATH)
    entries = coerce_to_entries(raw)
    graph = build_graph_data(entries)

    # Write both files (primary for the app; secondary for diff/debug)
    write_js(graph, OUT_PRIMARY)

    # A more readable pretty version if you want to inspect diffs
    os.makedirs(os.path.dirname(OUT_SECONDARY), exist_ok=True)
    with open(OUT_SECONDARY, "w", encoding="utf-8") as f:
        f.write("window.graph = ")
        f.write(json.dumps(graph, indent=2, ensure_ascii=False))
        f.write(";")

    print(f"✅ Graph data written to {OUT_PRIMARY} and {OUT_SECONDARY}")
    print(f"   Nodes: {len(graph['nodes'])}, Links: {len(graph['links'])}")

if __name__ == "__main__":
    main()
