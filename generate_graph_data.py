#!/usr/bin/env python3
"""
Builds docs/data.js for the Phi-Mesh tag browser & graph map.

Behavior:
- If meta/tag_index.yml exists → use it for the node list/degree proxy.
- Regardless, ALWAYS scan pulse/*.yml to derive:
    • edges via tag co-occurrence,
    • resources (papers/podcasts) with URL-only policy + dedupe,
    • first-seen pulse info.

Outputs docs/data.js with:
  window.PHI_DATA = {
    nodes: [{id, centrality}],
    links: [{source, target}],
    tagResources: { [tag]: {papers:[{title?,url}], podcasts:[{title?,url}] } },
    tagFirstSeen: { [tag]: {pulse, callout} }
  }
"""

import argparse, glob, json, os, re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import yaml

# --- Aliases ---------------------------------------------------------------

def load_aliases(path: str) -> dict:
    p = Path(path)
    if not p.exists(): 
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # expect: {aliases: { Canonical: [alias1, alias2, ...], ... }}
    return (data.get("aliases") or {}) if isinstance(data, dict) else {}

def build_alias_index(spec: dict) -> dict:
    """
    Return dict mapping every alias (plus a normalized key) to its canonical.
    """
    idx = {}
    def norm(s: str) -> str:
        return re.sub(r"[\s_\-]+", "_", s).strip().casefold()
    for canonical, aliases in (spec or {}).items():
        if not canonical:
            continue
        c = str(canonical)
        idx[c] = c
        idx[norm(c)] = c
        for a in (aliases or []):
            if not a:
                continue
            a = str(a)
            idx[a] = c
            idx[norm(a)] = c
    return idx

def normalize_tag(tag: str, idx: dict) -> str:
    if not isinstance(tag, str):
        return tag
    if tag in idx:
        return idx[tag]
    key = re.sub(r"[\s_\-]+", "_", tag).strip().casefold()
    return idx.get(key, tag)

# ------------------------------- helpers -------------------------------- #

def safe_load_yaml(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: Failed to parse YAML {path}: {e}")
        return {}

def looks_like_tag_index(obj: Any) -> bool:
    if not isinstance(obj, dict): return False
    return bool(obj) and (True in [
        all(isinstance(k, str) and isinstance(v, dict) for k, v in obj.items()),
        ("tags" in obj and isinstance(obj["tags"], dict))
    ])

def normalize_tag_map(tag_index_obj: Any) -> Dict[str, Dict]:
    if "tags" in tag_index_obj and isinstance(tag_index_obj["tags"], dict):
        return tag_index_obj["tags"]
    return tag_index_obj

def add_edge(a: str, b: str, edge_set: set):
    if a != b:
        edge_set.add(tuple(sorted((a, b))))

def is_skipped_pulse_path(path: str) -> bool:
    p = Path(path).as_posix()
    return ("/pulse/archive/" in p or p.endswith("/pulse/archive")
            or "/pulse/telemetry/" in p or p.endswith("/pulse/telemetry"))

def _norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u: return ""
    u = re.sub(r"^https?://(dx\.)?doi\.org/", "https://doi.org/", u, flags=re.I)
    return u.lower()


# --------------------------- pulse scanning ---------------------------- #

def scan_pulses_for_tags(glob_pattern: str, alias_index: dict | None = None) -> Tuple[
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

    candidates = sorted(glob.glob(glob_pattern, recursive=True))
    for fp in candidates:
        if not fp.endswith((".yml", ".yaml")): continue
        if is_skipped_pulse_path(fp): continue

        data = safe_load_yaml(fp)
        if not isinstance(data, dict): continue

        tags = data.get("tags") or data.get("Tags") or []
        if isinstance(tags, str):
            tags = [tags]
        if not isinstance(tags, list) or not tags:
            continue

        # normalize + alias-map
        alias_index = alias_index or {}
        tags = [
            normalize_tag(str(t).strip(), alias_index)
            for t in tags
            if str(t).strip()
        ]
        if not tags:
            continue

        pulse_key = Path(fp).as_posix()
        title = str(data.get("title") or Path(fp).stem)
        callout = str(data.get("callout") or data.get("summary") or "").strip()
        pulse_meta[pulse_key] = {"title": title, "callout": callout}

        pulse_to_tags[pulse_key] = tags
        for t in tags:
            tag_to_pulses.setdefault(t, []).append(pulse_key)

        # collect resources; drop items without URL
        def norm_items(raw):
            out = []
            if not raw: return out
            if isinstance(raw, list):
                for x in raw:
                    if isinstance(x, str):
                        s = x.strip()
                        if s.startswith(("http://", "https://")):
                            nu = _norm_url(s)
                            if nu: out.append({"url": nu})
                        else:
                            print(f"WARN: dropping resource without URL in {fp}: {x!r}")
                    elif isinstance(x, dict):
                        url = _norm_url(x.get("url", ""))
                        ttl = x.get("title")
                        if url:
                            item = {"url": url}
                            if ttl: item["title"] = str(ttl)
                            out.append(item)
                        else:
                            if ttl:
                                print(f"WARN: dropping '{ttl}' (no URL) in {fp}")
            return out

        papers   = norm_items(data.get("papers"))
        podcasts = norm_items(data.get("podcasts"))
        pulse_resources[pulse_key] = {"papers": papers, "podcasts": podcasts}

        # co-occurrence edges
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                add_edge(tags[i], tags[j], edges_set)

    edges = [(a, b) for (a, b) in sorted(edges_set)]
    return tag_to_pulses, pulse_to_tags, pulse_resources, pulse_meta, edges


# ----------------------------- nodes/links ----------------------------- #

def build_nodes_from_tag_map(tag_map: Dict[str, Dict]) -> List[Dict]:
    """Nodes with a simple centrality proxy (normalized degree)."""
    tags = list(tag_map.keys())
    deg = {t: 0 for t in tags}
    for t, info in tag_map.items():
        links = info.get("links") or []
        if isinstance(links, list): deg[t] += len(links)
        pulses = info.get("pulses") or []
        if isinstance(pulses, list): deg[t] += len(pulses) * 0.25
    maxd = max(deg.values()) if deg else 1.0
    return [{"id": t, "centrality": (deg[t] / maxd) if maxd else 0.0} for t in tags]

def build_nodes_edges_from_scan(tag_to_pulses: Dict[str, List[str]],
                                edges: List[Tuple[str, str]]) -> Tuple[List[Dict], List[Dict]]:
    tags = sorted(tag_to_pulses.keys())
    deg = {t: 0 for t in tags}
    for (a, b) in edges:
        deg[a] += 1; deg[b] += 1
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
        seen_p, seen_q = set(), set()
        for p in sorted(pulses):
            res = pulse_resources.get(p, {})
            for item in res.get("papers", []):
                key = _norm_url(item.get("url", ""))
                if key and key not in seen_p:
                    seen_p.add(key)
                    papers.append({"title": item.get("title"), "url": item.get("url")})
            for item in res.get("podcasts", []):
                key = _norm_url(item.get("url", ""))
                if key and key not in seen_q:
                    seen_q.add(key)
                    pods.append({"title": item.get("title"), "url": item.get("url")})
        out[tag] = {"papers": papers, "podcasts": pods}
    return out

def compute_first_seen(tag_to_pulses: Dict[str, List[str]],
                       pulse_meta: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    tag_first = {}
    for tag, pulses in tag_to_pulses.items():
        first = sorted(pulses)[0]
        meta = pulse_meta.get(first, {})
        tag_first[tag] = {"pulse": Path(first).stem, "callout": meta.get("callout", "") or ""}
    return tag_first


# -------------------------------- main --------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")  # recursive scan
    ap.add_argument("--out-js", default="docs/data.js")
    # Back-compat: accept --alias-map and ignore it (we auto-load meta/aliases.yml)
    ap.add_argument("--alias-map", default=None, help="(ignored; back-compat)")
    args = ap.parse_args()

    # 0) Load aliases (optional)
    alias_spec = load_aliases("meta/aliases.yml")
    alias_index = build_alias_index(alias_spec) if alias_spec else {}

    # 1) Nodes: prefer tag_index if available
    tag_index_obj = safe_load_yaml(args.tag_index) if os.path.exists(args.tag_index) else {}
    if looks_like_tag_index(tag_index_obj):
        tag_map = normalize_tag_map(tag_index_obj)
        nodes_from_index = build_nodes_from_tag_map(tag_map)
        node_ids = {n["id"] for n in nodes_from_index}
    else:
        tag_map = {}
        nodes_from_index = None
        node_ids = set()

    # 2) ALWAYS scan pulses for edges/resources/first-seen (with aliases)
    try:
        tag_to_pulses, _, pulse_resources, pulse_meta, edges = scan_pulses_for_tags(
            args.pulse_glob, alias_index=alias_index
        )
    except Exception as e:
        print(f"WARN: pulse scan failed: {e}")
        tag_to_pulses, pulse_resources, pulse_meta, edges = {}, {}, {}, []

    # 3) Build nodes/links
    if nodes_from_index is None:
        # No curated index → derive nodes from scan
        nodes, link_objs = build_nodes_edges_from_scan(tag_to_pulses, edges or [])
    else:
        # Curated index for nodes; edges come from scan, filtered to known nodes
        filt_edges = [(a, b) for (a, b) in (edges or []) if a in node_ids and b in node_ids]
        nodes = nodes_from_index
        link_objs = [{"source": a, "target": b} for (a, b) in filt_edges]

    # 4) Resources & first seen
    tag_resources = aggregate_tag_resources(tag_to_pulses, pulse_resources)
    tag_first = compute_first_seen(tag_to_pulses, pulse_meta)

    # 5) Emit
    payload = {
        "nodes": nodes,
        "links": link_objs,
        "tagResources": tag_resources,
        "tagFirstSeen": tag_first,
    }

    Path(args.out_js).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_js, "w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = " + json.dumps(payload) + ";")

    if not nodes:
        print("WARN: No tags detected; window.PHI_DATA has empty nodes/links.")
    print(f"OK: wrote {args.out_js} ({Path(args.out_js).stat().st_size} bytes)")
    print(f"INFO: tag count = {len(nodes)}, edge count = {len(link_objs)}")


if __name__ == "__main__":
    main()
