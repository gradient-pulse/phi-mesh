#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate docs/data.js for the interactive tag graph.

Inputs:
- meta/tag_index.yml      (produced by update_tag_index.py)
- pulse/**/*.yml          (optional; mined for per-tag papers/podcasts)

Output:
- docs/data.js  (ES module-ish: `const nodes = ...; const links = ...; const tagResources = ...;`)

Design:
- Nodes: one per tag, with a derived "centrality" score in [0..1] based on degree and pulse count.
- Links: undirected edges from tag_index 'links'; de-duped (A,B) == (B,A).
- tagResources: aggregate unique 'papers' and 'podcasts' across pulses per tag (if present).

All outputs are plain JS literals for easy inclusion in a D3 page.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from typing import Dict, List, Set, Tuple

try:
    import yaml
except Exception as e:
    print(f"[fatal] PyYAML not available: {e}", file=sys.stderr)
    sys.exit(1)

# Optional helper, but we won't hard-require it.
def _try_load_tag_index_util(path: str = "meta/tag_index_utils.py"):
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("tag_index_utils", path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return getattr(mod, "load_tag_index", None)
    except Exception:
        pass
    return None


def _read_yaml_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def _ensure_list_str(x) -> List[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, list):
        out = []
        for v in x:
            if v is None:
                continue
            out.append(str(v))
        return out
    return [str(x)]


def load_index(index_path: str) -> Dict[str, dict]:
    # Prefer the helper if available (keeps a single source of truth),
    # but fall back to our own safe loader.
    loader = _try_load_tag_index_util()
    if loader:
        try:
            idx = loader(index_path)
            if isinstance(idx, dict):
                return idx
        except Exception as e:
            print(f"[warn] tag_index_utils.load_tag_index failed: {e}", file=sys.stderr)

    data = _read_yaml_file(index_path)
    if not isinstance(data, dict):
        raise ValueError(f"{index_path}: expected mapping at top level.")
    # JSON roundtrip to guarantee plain types
    return json.loads(json.dumps(data, ensure_ascii=False))


def mine_resources(pulse_dir: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Aggregate resources (papers, podcasts) per tag by scanning pulses.
    Returns: { tag: { papers: [...], podcasts: [...] } }
    """
    res: Dict[str, Dict[str, Set[str]]] = {}

    patterns = [
        os.path.join(pulse_dir, "*.yml"),
        os.path.join(pulse_dir, "*.yaml"),
        os.path.join(pulse_dir, "**/*.yml"),
        os.path.join(pulse_dir, "**/*.yaml"),
    ]
    files: List[str] = []
    seen: Set[str] = set()
    for pat in patterns:
        for p in glob.glob(pat, recursive=True):
            if p not in seen and os.path.isfile(p):
                files.append(p)
                seen.add(p)

    for path in files:
        try:
            data = _read_yaml_file(path)
        except Exception as e:
            print(f"[warn] {path}: skipped ({e})", file=sys.stderr)
            continue

        tags = _ensure_list_str(data.get("tags"))
        papers = _ensure_list_str(data.get("papers"))
        podcasts = _ensure_list_str(data.get("podcasts"))

        if not tags:
            continue

        for t in set(tags):
            slot = res.setdefault(t, {"papers": set(), "podcasts": set()})
            for u in papers:
                if u.strip():
                    slot["papers"].add(u.strip())
            for u in podcasts:
                if u.strip():
                    slot["podcasts"].add(u.strip())

    # Convert sets to lists + JSON-clean
    out: Dict[str, Dict[str, List[str]]] = {}
    for t, v in res.items():
        out[t] = {
            "papers": sorted(v["papers"]),
            "podcasts": sorted(v["podcasts"]),
        }
    return json.loads(json.dumps(out, ensure_ascii=False))


def compute_centrality(index: Dict[str, dict]) -> Dict[str, float]:
    """
    Very simple centrality: normalize by max(degree + 0.5*pulse_count).
    Produces values in (0,1], or 0 if empty.
    """
    scores: Dict[str, float] = {}
    for tag, entry in index.items():
        links = entry.get("links", []) or []
        pulses = entry.get("pulses", []) or []
        score = float(len(links)) + 0.5 * float(len(pulses))
        scores[tag] = score

    if not scores:
        return {}

    max_score = max(scores.values()) or 1.0
    return {k: (v / max_score) for k, v in scores.items()}


def build_graph(index: Dict[str, dict]) -> Tuple[List[dict], List[dict]]:
    """
    Build nodes and de-duped undirected links from the tag index.
    nodes: [{id, centrality}]
    links: [{source, target}]
    """
    centrality = compute_centrality(index)
    nodes = [{"id": t, "centrality": round(centrality.get(t, 0.0), 6)} for t in sorted(index.keys())]

    # undirected de-dupe using frozenset
    edge_set: Set[frozenset] = set()
    for t, entry in index.items():
        for u in entry.get("links", []) or []:
            if t == u:
                continue
            k = frozenset((t, u))
            edge_set.add(k)

    links = [{"source": a, "target": b} for a, b in sorted((tuple(e) for e in edge_set))]
    return nodes, links


def write_js(out_path: str, nodes: List[dict], links: List[dict], tag_resources: Dict[str, dict]) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    js = (
        "const nodes = "
        + json.dumps(nodes, ensure_ascii=False, indent=2)
        + ";\nconst links = "
        + json.dumps(links, ensure_ascii=False, indent=2)
        + ";\nconst tagResources = "
        + json.dumps(tag_resources, ensure_ascii=False, indent=2)
        + ";\nexport { nodes, links, tagResources };"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate docs/data.js for tag graph.")
    p.add_argument("--index", default="meta/tag_index.yml", help="Path to tag index YAML.")
    p.add_argument("--pulse-dir", default="pulse", help="Pulse directory to mine resources.")
    p.add_argument("--out", default="docs/data.js", help="Output JS file path.")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    index = load_index(ns.index)
    nodes, links = build_graph(index)
    resources = mine_resources(ns.pulse_dir)

    # Only keep resources for known tags (avoid clutter).
    filtered_resources = {t: resources.get(t, {"papers": [], "podcasts": []}) for t in index.keys()}

    write_js(ns.out, nodes, links, filtered_resources)
    print(f"[ok] wrote {ns.out}: {len(nodes)} nodes, {len(links)} links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
