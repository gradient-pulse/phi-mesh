#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Tag Map data (window.PHI_DATA) from pulses + tag index.

Outputs docs/data.js with:
  - nodes: [{id, degree, centrality}]
  - links: [{source, target}]           # co-tag edges
  - tagResources: {tag: {papers:[], podcasts:[]}}  # URL-backed only
  - tagFirstSeen: {tag: "YYYY-MM-DD"}   # earliest seen date per tag
  - tagDescriptions: {tag: "…"}         # from meta/tag_index.yml if present
  - pulseIndex: {pulse_id: {date,title,summary,tags,papers,podcasts}}
  - tagPulseIndex: {tag: [pulse_id,...]}  # newest-first

Notes
-----
- Skips pulses under pulse/archive/ and pulse/telemetry/.
- Alias canonicalization is case/spacing/punctuation tolerant.
- Safe against malformed YAML: warns and continues.
"""

from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Iterable, Optional
from datetime import datetime

import yaml

# ------------------------------ utils --------------------------------- #

RE_SEP = re.compile(r"[\s_\-]+", flags=re.UNICODE)

def norm_key(s: str) -> str:
    """Lenient normalization for alias keys (casefold, strip (), spaces, -, _)."""
    if s is None:
        return ""
    s = str(s)
    s = s.replace("(", "").replace(")", "")
    s = RE_SEP.sub("", s)
    return s.casefold().strip()

def load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARN] YAML load failed: {path} :: {e}")
        return None

def looks_like_tag_index(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("tags"), dict)

def safe_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, (dict, list)):
        try:
            return json.dumps(x, ensure_ascii=False)
        except Exception:
            return str(x)
    return str(x)

def parse_iso_date(s: str) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    # Try common forms
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # Try prefix “YYYY-MM-DD” inside string
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d")
        except Exception:
            pass
    # Try compact yyyymmdd
    m2 = re.search(r"\b(\d{8})\b", s)
    if m2:
        try:
            return datetime.strptime(m2.group(1), "%Y%m%d")
        except Exception:
            pass
    return None

def first_non_none(dts: Iterable[Optional[datetime]]) -> Optional[datetime]:
    return min([dt for dt in dts if dt is not None], default=None)

def unique_preserve(seq: Iterable[Any]) -> List[Any]:
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# -------------------------- alias handling ---------------------------- #

def load_aliases(path: str) -> Dict[str, List[str]]:
    p = Path(path)
    if not p.exists():
        return {}
    obj = load_yaml(p) or {}
    return obj.get("aliases") or {}

def build_alias_index(spec: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Build inverse lookup: normalized alias -> canonical.
    Includes identity mapping for canonicals themselves.
    """
    idx: Dict[str, str] = {}
    for canonical, aliases in (spec or {}).items():
        kcanon = norm_key(canonical)
        if kcanon:
            idx[kcanon] = canonical
        for a in (aliases or []):
            ka = norm_key(a)
            if ka and ka not in idx:
                idx[ka] = canonical
    return idx

def canon(tag: str, alias_idx: Dict[str, str]) -> str:
    k = norm_key(tag)
    return alias_idx.get(k, tag.strip())

# ------------------------- pulse scanning ----------------------------- #

def normalize_resource_item(item: Any) -> Optional[Dict[str, str]]:
    """
    Accepts string URL or dict with url/title; returns dict {url, title?}.
    Drops entries without a URL (URL-backed only).
    """
    if item is None:
        return None
    if isinstance(item, str):
        u = item.strip()
        if not u:
            return None
        return {"url": u}
    if isinstance(item, dict):
        url = safe_str(item.get("url")).strip()
        if not url:
            return None
        out = {"url": url}
        title = item.get("title")
        if title:
            out["title"] = safe_str(title).strip()
        return out
    return None

def collect_resources(seq: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if isinstance(seq, list):
        for it in seq:
            norm = normalize_resource_item(it)
            if norm:
                out.append(norm)
    return out

def pulse_id_from_path(p: Path) -> str:
    return p.stem  # keep spaces if present; matches historical IDs in index

def scan_pulses_for_tags(glob_pat: str,
                         alias_idx: Dict[str, str]) -> Tuple[
                            Dict[str, List[str]],
                            Dict[str, List[str]],
                            Dict[str, Dict[str, List[Dict[str, str]]]],
                            Dict[str, Dict[str, Any]],
                            List[Tuple[str, str]]
                         ]:
    """
    Returns:
      tag_to_pulses: {tag: [pulse_id,...]}
      tag_to_titles: {tag: [pulse_title,...]}  (present but unused by map; kept for future)
      pulse_resources: {pulse_id: {papers:[], podcasts:[]}}
      pulse_meta: {pulse_id: {date,title,summary,tags}}
      edges: [(tagA, tagB), ...] undirected co-tag pairs
    """
    roots = [Path(p) for p in glob_pat.split()]
    # Use pathlib.glob comprehensively
    files: List[Path] = []
    for root in roots:
        if str(root).endswith(".yml") or str(root).endswith(".yaml"):
            files.append(root)
        else:
            files.extend(Path().glob(str(root)))

    tag_to_pulses: Dict[str, List[str]] = {}
    tag_to_titles: Dict[str, List[str]] = {}
    pulse_resources: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    pulse_meta: Dict[str, Dict[str, Any]] = {}
    edges_set: set[Tuple[str, str]] = set()

    for fp in files:
        # Skip archive & telemetry
        parts = [p.casefold() for p in fp.parts]
        if "archive" in parts or "telemetry" in parts:
            continue
        if not fp.is_file():
            continue

        obj = load_yaml(fp)
        if not isinstance(obj, dict):
            continue

        pid = pulse_id_from_path(fp)
        # Collect / sanitize
        raw_tags = obj.get("tags") or []
        if not isinstance(raw_tags, list):
            raw_tags = []

        ctags = unique_preserve(canon(t, alias_idx) for t in raw_tags if t)
        # Drop obvious junk line-ins (sometimes corrupted pulses append tags under podcasts etc.)
        ctags = [t for t in ctags if isinstance(t, str) and t and not t.lower().startswith("http")]

        title = safe_str(obj.get("title")).strip()
        date = safe_str(obj.get("date")).strip()
        summary = safe_str(obj.get("summary")).strip()

        # Fallback date: try parse from filename
        dt_candidates = [parse_iso_date(date), parse_iso_date(pid)]
        dt = first_non_none(dt_candidates)
        pulse_meta[pid] = {
            "date": dt.strftime("%Y-%m-%d") if dt else "",
            "title": title,
            "summary": summary,
            "tags": ctags,
        }

        res_papers = collect_resources(obj.get("papers"))
        res_podcasts = collect_resources(obj.get("podcasts"))
        pulse_resources[pid] = {"papers": res_papers, "podcasts": res_podcasts}

        # Index per tag and build edges
        for t in ctags:
            tag_to_pulses.setdefault(t, []).append(pid)
            tag_to_titles.setdefault(t, []).append(title)

        # Edges from co-tagging in the same pulse
        for i in range(len(ctags)):
            for j in range(i + 1, len(ctags)):
                a, b = sorted((ctags[i], ctags[j]))
                if a != b:
                    edges_set.add((a, b))

    edges = sorted(edges_set)
    # Dedup pulse lists (just in case) and keep order stable
    for t, lst in tag_to_pulses.items():
        tag_to_pulses[t] = unique_preserve(lst)
    for t, lst in tag_to_titles.items():
        tag_to_titles[t] = unique_preserve(lst)

    return tag_to_pulses, tag_to_titles, pulse_resources, pulse_meta, edges

# -------------------------- tag index helpers ------------------------- #

def normalize_tag_map(tag_index_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reduce meta/tag_index.yml into {tag: {summary:str}} (descriptions).
    """
    tags = tag_index_obj.get("tags") or {}
    out: Dict[str, Any] = {}
    if isinstance(tags, dict):
        for k, v in tags.items():
            if isinstance(v, dict):
                out[k] = {"summary": safe_str(v.get("summary", "")).strip()}
            else:
                out[k] = {"summary": ""}
    return out

def build_nodes_from_tag_map(tag_map: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Degree/centrality assigned later (from edges)
    return [{"id": k, "degree": 0, "centrality": 0.0} for k in sorted(tag_map.keys())]

# -------------------------- projection helpers ------------------------ #

def build_nodes_edges_from_scan(tag_to_pulses: Dict[str, List[str]],
                                edges: List[Tuple[str, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    tags = sorted(tag_to_pulses.keys())
    degree_count: Dict[str, int] = {t: 0 for t in tags}
    for a, b in edges:
        degree_count[a] = degree_count.get(a, 0) + 1
        degree_count[b] = degree_count.get(b, 0) + 1
    max_deg = max(degree_count.values() or [1])
    nodes = [{"id": t, "degree": degree_count.get(t, 0), "centrality": (degree_count.get(t, 0) / max_deg) if max_deg else 0.0}
             for t in tags]
    link_objs = [{"source": a, "target": b} for (a, b) in edges]
    return nodes, link_objs

def update_degrees_from_edges(nodes: List[Dict[str, Any]],
                              edges: List[Tuple[str, str]]) -> None:
    idx = {n["id"]: n for n in nodes}
    degree_count: Dict[str, int] = {k: 0 for k in idx.keys()}
    for a, b in edges:
        if a in degree_count:
            degree_count[a] += 1
        if b in degree_count:
            degree_count[b] += 1
    max_deg = max(degree_count.values() or [1])
    for k, n in idx.items():
        d = degree_count.get(k, 0)
        n["degree"] = d
        n["centrality"] = (d / max_deg) if max_deg else 0.0

def aggregate_tag_resources(tag_to_pulses: Dict[str, List[str]],
                            pulse_resources: Dict[str, Dict[str, List[Dict[str, str]]]]
                            ) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    out: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    for tag, pids in tag_to_pulses.items():
        papers: List[Dict[str, str]] = []
        pods: List[Dict[str, str]] = []
        for pid in pids:
            res = pulse_resources.get(pid, {})
            papers.extend(res.get("papers") or [])
            pods.extend(res.get("podcasts") or [])
        # Dedup by URL, preserve first title seen
        def dedup(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
            seen = {}
            out_items: List[Dict[str, str]] = []
            for it in items:
                u = it.get("url", "")
                if not u:
                    continue
                if u in seen:
                    continue
                seen[u] = True
                out_items.append(it)
            return out_items
        out[tag] = {"papers": dedup(papers), "podcasts": dedup(pods)}
    return out

def compute_first_seen(tag_to_pulses: Dict[str, List[str]],
                       pulse_meta: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for tag, pids in tag_to_pulses.items():
        dates: List[datetime] = []
        for pid in pids:
            d = pulse_meta.get(pid, {}).get("date", "")
            dt = parse_iso_date(d) if isinstance(d, str) else None
            if dt:
                dates.append(dt)
        first = min(dates).strftime("%Y-%m-%d") if dates else ""
        out[tag] = first
    return out

def build_tag_pulse_index(tag_to_pulses: Dict[str, List[str]],
                          pulse_meta: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Map tag -> list of pulse_ids sorted by date (newest first). Un-dated go last.
    """
    out: Dict[str, List[str]] = {}
    for tag, pids in tag_to_pulses.items():
        def key(pid: str):
            d = pulse_meta.get(pid, {}).get("date") or ""
            dt = parse_iso_date(d) if isinstance(d, str) else None
            # Newest first -> reverse sort; None -> very old
            return (dt is None, dt if dt is not None else datetime.min)
        out[tag] = sorted(unique_preserve(pids), key=key, reverse=True)
    return out

# ------------------------------- main --------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    args = ap.parse_args()

    # Aliases
    alias_spec = load_aliases(args.alias_map)
    alias_idx = build_alias_index(alias_spec)

    # Tag index (descriptions)
    tag_index_obj = load_yaml(Path(args.tag_index)) if os.path.exists(args.tag_index) else {}
    tag_map = normalize_tag_map(tag_index_obj) if looks_like_tag_index(tag_index_obj) else {}
    nodes_from_index = build_nodes_from_tag_map(tag_map) if tag_map else None
    node_ids_from_index = {n["id"] for n in (nodes_from_index or [])}

    # Scan pulses ALWAYS (for edges/resources/pulse meta)
    tag_to_pulses, _tag_to_titles, pulse_resources, pulse_meta, edges = scan_pulses_for_tags(
        args.pulse_glob, alias_idx
    )

    # Build nodes/links
    if nodes_from_index is None:
        nodes, link_objs = build_nodes_edges_from_scan(tag_to_pulses, edges)
    else:
        # Keep node set from index; filter edges to known nodes; then compute degrees
        if node_ids_from_index:
            filt_edges = [(a, b) for (a, b) in edges if a in node_ids_from_index and b in node_ids_from_index]
        else:
            filt_edges = edges
        nodes = nodes_from_index
        update_degrees_from_edges(nodes, filt_edges)
        link_objs = [{"source": a, "target": b} for (a, b) in filt_edges]

    # Aggregate resources & dates
    tag_resources = aggregate_tag_resources(tag_to_pulses, pulse_resources)
    tag_first = compute_first_seen(tag_to_pulses, pulse_meta)

    # Tag descriptions map
    tag_descriptions = {k: (v.get("summary") or "") for k, v in tag_map.items()} if tag_map else {}

    # Pulse indices (for satellites and sidebar)
    pulse_index = {}
    for pid, meta in pulse_meta.items():
        pulse_index[pid] = {
            "date": meta.get("date", ""),
            "title": meta.get("title", ""),
            "summary": meta.get("summary", ""),
            "tags": meta.get("tags", []),
            "papers": pulse_resources.get(pid, {}).get("papers", []),
            "podcasts": pulse_resources.get(pid, {}).get("podcasts", []),
        }
    tag_pulse_index = build_tag_pulse_index(tag_to_pulses, pulse_meta)

    payload = {
        "nodes": nodes,
        "links": link_objs,
        "tagResources": tag_resources,
        "tagFirstSeen": tag_first,
        "tagDescriptions": tag_descriptions,
        "pulseIndex": pulse_index,
        "tagPulseIndex": tag_pulse_index,
    }

    out_path = Path(args.out_js)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = " + json.dumps(payload, ensure_ascii=False) + ";")

    if not nodes:
        print("WARN: No tags detected; window.PHI_DATA has empty nodes/links.")
    print(f"OK: wrote {args.out_js} ({out_path.stat().st_size} bytes)")
    print(f"INFO: tag count = {len(nodes)}, edge count = {len(link_objs)}")

if __name__ == "__main__":
    main()
