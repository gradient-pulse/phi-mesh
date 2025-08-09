#!/usr/bin/env python3
"""
generate_graph_data.py
Builds a tag graph (nodes + links) for the D3 map.

- Reads tag index from one of:
    meta/tag_index.yml
    tag_index.yml
    phi-mesh/meta/tag_index.yml

- Always emits a non-empty links list if adjacency exists in the tag index.
- Deduplicates nodes/links, keeps IDs as strings.
- Writes two files into docs/:
    1) graph_data.<hash>.js      # payload (window.graph = {...})
    2) graph_data.js             # tiny loader that injects the hashed file
"""

import json
import hashlib
import os
from pathlib import Path

try:
    import yaml
except Exception as e:
    raise SystemExit(
        "Missing dependency: pyyaml\nInstall with: pip install pyyaml"
    ) from e


# -----------------------------
# Config / Paths
# -----------------------------
CANDIDATES = [
    Path("meta/tag_index.yml"),
    Path("tag_index.yml"),
    Path("phi-mesh/meta/tag_index.yml"),
]
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------
def find_tag_index() -> Path:
    for p in CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Could not find tag_index.yml. Looked in: {', '.join(map(str, CANDIDATES))}"
    )


def load_tag_index(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Support both flattened and nested structures:
    # Expected modern shape:
    #   {
    #     TAG: { links: [...], pulses: [...], papers: [...], ... },
    #     ...
    #   }
    # Older shapes will still be processed best-effort.
    if not isinstance(data, dict):
        raise ValueError("tag_index.yml must parse to a dict at the top level.")
    return data


def sanitize_id(s) -> str:
    # Force IDs to strings; keep underscores etc. D3 doesn’t care.
    return str(s)


def unique_links_from_adjacency(index: dict) -> list[dict]:
    """
    Build an undirected simple graph from tag adjacency:
      edges between tag <-> each neighbor in 'links' (if present).
    Deduplicated by (min(tag, nbr), max(tag, nbr)).
    """
    edges = []
    seen = set()

    for tag, payload in index.items():
        tag_id = sanitize_id(tag)
        if not isinstance(payload, dict):
            continue
        nbrs = payload.get("links") or payload.get("link") or []
        if not isinstance(nbrs, (list, tuple)):
            continue
        for nb in nbrs:
            nb_id = sanitize_id(nb)
            if nb_id == tag_id:
                continue
            a, b = sorted((tag_id, nb_id))
            key = (a, b)
            if key in seen:
                continue
            seen.add(key)
            edges.append({"source": a, "target": b, "weight": 1})
    return edges


def collect_nodes(index: dict, links: list[dict]) -> list[dict]:
    """
    Union of:
      - all tag keys in index
      - all endpoints that appear in links
    """
    ids = set()

    for tag in index.keys():
        ids.add(sanitize_id(tag))

    for e in links:
        ids.add(sanitize_id(e["source"]))
        ids.add(sanitize_id(e["target"]))

    # Emit as array of {id}
    return [{"id": i} for i in sorted(ids)]


def write_hashed_payload(graph: dict) -> str:
    """
    Writes docs/graph_data.<hash>.js with `window.graph = {...};`
    Returns the basename (used by the loader).
    """
    payload = "window.graph=" + json.dumps(graph, separators=(",", ":"), ensure_ascii=False) + ";"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:8]
    basename = f"graph_data.{digest}.js"
    out_path = DOCS_DIR / basename
    with out_path.open("w", encoding="utf-8") as f:
        f.write(payload)
    return basename


def write_loader(basename: str) -> None:
    """
    Writes docs/graph_data.js which dynamically loads the hashed payload and
    exposes window.GRAPH_SRC for debug.
    """
    loader = f"""(function() {{
  var src = {json.dumps(basename)};
  window.GRAPH_SRC = src;
  var s = document.createElement('script');
  s.src = src;
  (document.currentScript && document.currentScript.parentNode
    ? document.currentScript.parentNode.insertBefore(s, document.currentScript.nextSibling)
    : document.body.appendChild(s));
  console.log("[tag_map] overlay graph loaded: –", src);
}})();
"""
    with (DOCS_DIR / "graph_data.js").open("w", encoding="utf-8") as f:
        f.write(loader)


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    idx_path = find_tag_index()
    print(f"[generate_graph_data] using tag index: {idx_path}")

    tag_index = load_tag_index(idx_path)

    # Build links from adjacency (most reliable). If nothing, leave empty.
    links = unique_links_from_adjacency(tag_index)

    # Build nodes (includes all tags and link endpoints).
    nodes = collect_nodes(tag_index, links)

    # Final sanity: if there are zero links AND zero/one node, we still emit
    # a valid (but boring) graph. The runtime layout can fall back too.
    graph = {"nodes": nodes, "links": links}

    hashed = write_hashed_payload(graph)
    write_loader(hashed)

    print(
        f"[generate_graph_data] wrote docs/{hashed} "
        f"({len(nodes)} nodes, {len(links)} links) and docs/graph_data.js"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Fail loudly in CI so the workflow shows the cause.
        raise
