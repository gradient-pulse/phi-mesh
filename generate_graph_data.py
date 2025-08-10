#!/usr/bin/env python3
"""
Builds docs/data.js for the Phi-Mesh tag browser & graph map.

Priority order:
1) If meta/tag_index.yml exists and is non-empty → use it.
2) Otherwise, scan pulse/*.yml (skipping pulse/archive and pulse/telemetry).

Outputs docs/data.js with:
  window.PHI_DATA = {
    nodes: [{id, centrality}],
    links: [{source, target}],
    tagResources: { [tag]: {papers: [{title?, url}], podcasts: [{title?, url}] } },
    tagFirstSeen: { [tag]: {pulse, callout} }
  }
"""

import argparse
import glob
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml


# ------------------------------- utils --------------------------------- #

def safe_load_yaml(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: Failed to parse YAML {path}: {e}")
        return {}

def looks_like_tag_index(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    # Accept two common shapes:
    # A) { tag: { pulses:[...], links:[...], ... }, ... }
    # B) { tags: { tag: {...} } }
    return bool(obj) and (True in [
        all(isinstance(k, str) and isinstance(v, dict) for k, v in obj.items()),
        ("tags" in obj and isinstance(obj["tags"], dict))
    ])

def normalize_tag_map(tag_index_obj: Any) -> Dict[str, Dict]:
    """Return a unified map: { tag: { pulses:[...], links:[...], ... } }"""
    if "tags" in tag_index_obj and isinstance(tag_index_obj["tags"], dict):
        return tag_index_obj["tags"]
    return tag_index_obj


def add_edge(a: str, b: str, edge_set: set):
    if a == b:
        return
    edge_set.add(tuple(sorted((a, b))))


def is_skipped_pulse_path(path: str) -> bool:
    p = Path(path).as_posix()
    # skip archive & telemetry folders
    if "/pulse/archive/" in p or p.endswith("/pulse/archive") or "/pulse/telemetry/" in p or p.endswith("/pulse/telemetry"):
        return True
    return False


# --------------------------- pulse scanning ---------------------------- #

def scan_pulses_for_tags(glob_pattern: str) -> Tuple[
    Dict[str, List[str]],  # tag -> [pulse_paths]
    Dict[str, List[str]],  # pulse -> [tags]
    Dict[str, Dict[str, List[dict]]],  # pulse_resources
    Dict[str, Dict[str, str]],  # pulse_meta (title, callout)
    List[Tuple[str, str]]  # tag co-occurrence edges
]:
    tag_to_pulses: Dict[str, List[str]] = {}
    pulse_to_tags: Dict[str, List[str]] = {}
    pulse_resources: Dict[str, Dict[str, List[dict]]] = {}
    pulse_meta: Dict[str, Dict[str, str]] = {}
    edges_set = set()

    candidates = sorted(glob.glob(glob_pattern))
    for fp in candidates:
        if not fp.endswith((".yml", ".yaml")):
            continue
        if is_skipped_pulse_path(fp):
            continue

        data = safe_load_yaml(fp)
        if not isinstance(data, dict):
            continue

        tags = data.get("tags") or data.get("Tags") or []
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list) or not tags:
            continue

        # minimal normalization
        tags = [str(t).strip() for t in tags if str(t).strip()]
        if not tags:
            continue

        pulse_key = Path(fp).as_posix()
        title = str(data.get("title") or Path(fp).stem)
        callout = str(data.get("callout") or data.get("summary") or "").strip()
        pulse_meta[pulse_key] = {"title": title, "callout": callout}

        pulse_to_tags[pulse_key] = tags
        for t in tags:
            tag_to_pulses.setdefault(t, []).append(pulse_key)

        # collect resources (accept strings or {title,url})
        def norm_items(raw):
            out = []
            if not raw:
                return out
            if isinstance(raw, list):
                for x in raw:
                    if isinstance(x, str):
                        out.append({"url": x})
                    elif isinstance(x, dict):
                        url = x.get("url") or ""
                        ttl = x.get("title")
                        if url or ttl:
                            item = {}
                            if ttl: item["title"] = str(ttl)
                            if url: item["url"] = str(url)
                            out.append(item)
            return out

        papers = norm_items(data.get("papers"))
        podcasts = norm_items(data.get("podcasts"))
        pulse_resources[pulse_key] = {"papers": papers, "podcasts": podcasts}

        # co-occurrence edges inside this pulse
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                add_edge(tags[i], tags[j], edges_set)

    edges = [(a, b) for (a, b) in sorted(edges_set)]
    return tag_to_pulses, pulse_to_tags, pulse_resources, pulse_meta, edges


# ----------------------------- node stats ------------------------------ #

def build_nodes_from_tag_map(tag_map: Dict[str, Dict]) -> List[Dict]:
    """Build nodes with a simple centrality proxy (normalized degree)."""
    tags = list(tag_map.keys())
    deg = {t: 0 for t in tags}
    # infer degree from 'links' if present; else from pulses count
    for t, info in tag_map.items():
        links = info.get("links") or []
        if isinstance(links, list):
            deg[t] += len(links)
        pulses = info.get("pulses") or []
        if isinstance(pulses, list):
            # small bonus for appearing in many pulses
            deg[t] += len(pulses) * 0.25

    maxd = max(deg.values()) if deg else 1.0
    nodes = [{"id": t, "centrality": (deg[t] / maxd) if maxd else 0.0} for t in tags]
    return nodes


def build_nodes_edges_from_scan(tag_to_pulses: Dict[str, List[str]],
                                edges: List[Tuple[str, str]]) -> Tuple[List[Dict], List[Dict]]:
    tags = sorted(tag_to_pulses.keys())
    deg = {t: 0 for t in tags}
    for (a, b) in edges:
        deg[a] += 1
        deg[b] += 1
    # small bonus for multi-pulse presence
    for t, ps in tag_to_pulses.items():
        deg[t] += len(ps) * 0.25

    maxd = max(deg.values()) if deg else 1.0
    nodes = [{"id": t, "centrality": (deg[t] / maxd) if maxd else 0.0} for t in tags]
    link_objs = [{"source": a, "target": b} for (a, b) in edges]
    return nodes, link_objs


# ----------------------- resources & first-seen ------------------------ #

def aggregate_tag_resources(tag_to_pulses: Dict[str, List[str]],
                            pulse_resources: Dict[str, Dict[str, List[dict]]]) -> Dict[str, Dict[str, List[dict]]]:
    out: Dict[str, Dict[str, List[dict]]] = {}
    for tag, pulses in tag_to_pulses.items():
        papers, pods = [], []
        seen = set()
        for p in sorted(pulses):
            res = pulse_resources.get(p, {})
            for item in res.get("papers", []):
                key = (item.get("title"), item.get("url"))
                if key not in seen:
                    seen.add(key); papers.append(item)
            for item in res.get("podcasts", []):
                key = (item.get("title"), item.get("url"))
                if key not in seen:
                    seen.add(key); pods.append(item)
        out[tag] = {"papers": papers, "podcasts": pods}
    return out


def compute_first_seen(tag_to_pulses: Dict[str, List[str]],
                       pulse_meta: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    tag_first = {}
    for tag, pulses in tag_to_pulses.items():
        first = sorted(pulses)[0]
        meta = pulse_meta.get(first, {})
        tag_first[tag] = {
            "pulse": Path(first).stem,
            "callout": meta.get("callout", "") or ""
        }
    return tag_first


# -------------------------------- main --------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--pulse-glob", default="pulse/*.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    args = ap.parse_args()

    # 0) Try tag_index.yml
    tag_index_obj = {}
    if os.path.exists(args.tag_index):
        tag_index_obj = safe_load_yaml(args.tag_index)

    if looks_like_tag_index(tag_index_obj):
        # normalize and build from index
        tag_map = normalize_tag_map(tag_index_obj)

        # nodes
        nodes = build_nodes_from_tag_map(tag_map)

        # edges: from explicit links if present
        edges = []
        for t, info in tag_map.items():
            for other in (info.get("links") or []):
                edges.append(tuple(sorted((t, str(other)))))
        edges = sorted(set(edges))
        link_objs = [{"source": a, "target": b} for (a, b) in edges]

        # tag_to_pulses (for resources & first-seen); tolerate either field name
        tag_to_pulses = {t: list(set((info.get("pulses") or []) + (info.get("pulse") or [])))
                         for t, info in tag_map.items()}

        # pulse resources / meta must be derived by scanning pulses (non-fatal if missing)
        _, _, pulse_resources, pulse_meta, _ = scan_pulses_for_tags(args.pulse_glob)

        tag_resources = aggregate_tag_resources(tag_to_pulses, pulse_resources)
        tag_first = compute_first_seen(tag_to_pulses, pulse_meta)

    else:
        print("INFO: tag_index.yml empty or unsupported → scanning pulses …")
        tag_to_pulses, pulse_to_tags, pulse_resources, pulse_meta, edges = scan_pulses_for_tags(args.pulse_glob)
        nodes, link_objs = build_nodes_edges_from_scan(tag_to_pulses, edges)
        tag_resources = aggregate_tag_resources(tag_to_pulses, pulse_resources)
        tag_first = compute_first_seen(tag_to_pulses, pulse_meta)

    # payload
    payload = {
        "nodes": nodes,
        "links": link_objs,
        "tagResources": tag_resources,
        "tagFirstSeen": tag_first,
    }

    os.makedirs(Path(args.out_js).parent, exist_ok=True)
    with open(args.out_js, "w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = " + json.dumps(payload) + ";")

    # basic sanity
    if not nodes:
        print("WARN: No tags detected; window.PHI_DATA has empty nodes/links.")

    print(f"OK: wrote {args.out_js} ({Path(args.out_js).stat().st_size} bytes)")
    print(f"INFO: tag count = {len(nodes)}")


if __name__ == "__main__":
    main()
