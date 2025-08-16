#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_graph_data.py

Builds the Phi-Mesh data bundle used by the interactive Tag Map.

Outputs a single JS file:
  window.PHI_DATA = {
    nodes: [{ id, centrality }...],
    links: [{ source, target, weight }...],
    tagResources: { <tag>: { papers:[], podcasts:[] }, ... },
    tagDescriptions: { <tag>: "…", ... },
    pulses: {
      <pulse_id>: {
        id, date_iso, date_epoch, tags:[], summary:"", papers:[], podcasts:[]
      }, ...
    },
    tagToPulses: { <tag>: [<pulse_id>, ...], ... }
  };

Notes
- We NEVER drop nodes/links if a description is missing. Descriptions are optional.
- Alias normalization is applied everywhere tags appear.
- Robust to minor YAML issues; bad files are skipped with a warning.
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

try:
    import yaml
except Exception as e:
    print("[FATAL] pyyaml is required. pip install pyyaml", file=sys.stderr)
    raise

# -----------------------------
# Helpers
# -----------------------------

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

def _read_yaml(path: str) -> Any:
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[WARN] YAML load failed: {path} — {e}", file=sys.stderr)
        return None

def _normalize_tag(tag: str) -> str:
    # Preserve punctuation (parentheses/underscores/hyphens) as-is.
    # Just trim and collapse spaces.
    if tag is None:
        return ""
    return str(tag).strip()

def _build_alias_map(path: str) -> Dict[str, str]:
    """
    aliases.yml format:
      aliases:
        CanonicalA:
          - alias1
          - alias2
        CanonicalB:
          - alias3
    Produces: { "alias1":"CanonicalA", "alias2":"CanonicalA", "CanonicalA":"CanonicalA", ... }
    """
    m: Dict[str, str] = {}
    if not path or not os.path.exists(path):
        return m
    data = _read_yaml(path)
    if not data:
        return m
    aliases = data.get("aliases", {})
    for canonical, alias_list in aliases.items():
        c = _normalize_tag(canonical)
        if not c:
            continue
        # canonical maps to itself
        m[c] = c
        for a in (alias_list or []):
            a_norm = _normalize_tag(a)
            if a_norm:
                m[a_norm] = c
    return m

def _apply_alias(tag: str, alias_map: Dict[str, str]) -> str:
    t = _normalize_tag(tag)
    return alias_map.get(t, t)

def _ensure_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    # Single item -> list
    return [v]

def _flatten_urls(items: List[Any]) -> List[str]:
    """
    Accepts a list like:
        - "https://foo"
        - { url: "https://bar" }
        - { title: "...", url: "https://baz" }
    Returns list of URL strings.
    """
    out: List[str] = []
    for it in items:
        if isinstance(it, str):
            if it.strip():
                out.append(it.strip())
        elif isinstance(it, dict):
            u = it.get("url") or it.get("link") or ""
            if isinstance(u, str) and u.strip():
                out.append(u.strip())
    # De-dup while preserving order
    seen = set()
    dedup: List[str] = []
    for u in out:
        if u not in seen:
            seen.add(u)
            dedup.append(u)
    return dedup

def _parse_date_to_epoch(d: Any) -> Tuple[str, int]:
    """
    Accepts:
      - 'YYYY-MM-DD'
      - full ISO like '2025-08-13T15:01:57Z'
      - arbitrary string (best-effort)
    Returns (date_iso, epoch_seconds)
    """
    if not d:
        return ("", 0)
    s = str(d).strip().replace("’", "'")
    # common ISO-8601
    try:
        # If date only
        if ISO_DATE_RE.match(s):
            dt = datetime.fromisoformat(s)
            return (dt.date().isoformat(), int(dt.timestamp()))
        # Try generic
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (dt.isoformat(), int(dt.timestamp()))
    except Exception:
        pass
    # best-effort fallback using time.strptime variants
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            tm = time.strptime(s, fmt)
            epoch = int(time.mktime(tm))
            if fmt == "%Y-%m-%d":
                return (time.strftime("%Y-%m-%d", tm), epoch)
            return (s, epoch)
        except Exception:
            continue
    return (s, 0)

# -----------------------------
# Data builders
# -----------------------------

def load_tag_descriptions(path: str) -> Dict[str, str]:
    """
    meta/tag_descriptions.yml format:
      version: 1
      generated: "2025-08-14"
      descriptions:
        Tag_A: "…"
        "NT (Narrative_Tick)": "…"
    """
    if not path or not os.path.exists(path):
        return {}
    data = _read_yaml(path)
    if not data:
        return {}
    desc = data.get("descriptions", {})
    out: Dict[str, str] = {}
    for k, v in (desc or {}).items():
        k_norm = _normalize_tag(k)
        if k_norm:
            out[k_norm] = (v or "").strip()
    return out

def scan_pulses(pulse_glob: str, alias_map: Dict[str, str]) -> Tuple[
    Dict[str, Dict[str, Any]],
    Dict[str, List[str]],
    Dict[str, Dict[str, List[str]]]
]:
    """
    Returns:
      pulses: {
        pulse_id: {
          id, date_iso, date_epoch, tags:[], summary, papers:[], podcasts:[]
        }
      }
      tag_to_pulses: { tag: [pulse_id, ...], ... }
      tag_resources: { tag: { papers:[], podcasts:[] }, ... }  # aggregated
    """
    pulses: Dict[str, Dict[str, Any]] = {}
    tag_to_pulses: Dict[str, List[str]] = defaultdict(list)
    tag_resources: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"papers": [], "podcasts": []})

    paths = sorted(glob.glob(pulse_glob, recursive=True))
    for path in paths:
        data = _read_yaml(path)
        if not data or not isinstance(data, dict):
            continue

        # Pulse id = path without dirs, no extension
        pulse_id = os.path.splitext(os.path.basename(path))[0]

        # Tags
        raw_tags = _ensure_list(data.get("tags", []))
        norm_tags: List[str] = []
        for t in raw_tags:
            t_norm = _apply_alias(str(t), alias_map)
            if t_norm:
                norm_tags.append(t_norm)
        # de-dup preserve order
        seen = set()
        norm_tags = [x for x in norm_tags if not (x in seen or seen.add(x))]

        # Summary
        summary = data.get("summary", "")
        if isinstance(summary, str):
            summary = summary.strip()
        else:
            summary = str(summary or "").strip()

        # Date
        date_iso, date_epoch = _parse_date_to_epoch(data.get("date"))

        # Papers & Podcasts (flatten to URLs)
        papers = _flatten_urls(_ensure_list(data.get("papers", [])))
        podcasts = _flatten_urls(_ensure_list(data.get("podcasts", [])))

        pulses[pulse_id] = {
            "id": pulse_id,
            "date_iso": date_iso,
            "date_epoch": date_epoch,
            "tags": norm_tags,
            "summary": summary,
            "papers": papers,
            "podcasts": podcasts,
        }

        # Index per tag and aggregate resources
        for tag in norm_tags:
            tag_to_pulses[tag].append(pulse_id)
            # Aggregate resources by tag (de-dup across pulses later)
            if papers:
                tag_resources[tag]["papers"].extend(papers)
            if podcasts:
                tag_resources[tag]["podcasts"].extend(podcasts)

    # De-dup aggregated resources, preserve order
    for tag, res in tag_resources.items():
        res["papers"] = _dedup_order(res["papers"])
        res["podcasts"] = _dedup_order(res["podcasts"])

    return pulses, tag_to_pulses, tag_resources

def _dedup_order(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out

def build_tag_graph(pulses: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Builds an undirected co-occurrence graph across all pulses.
    Node centrality is a very light proxy: normalized degree (0..1).
    """
    # Collect all tags and co-occur counts
    tag_counts: Dict[str, int] = defaultdict(int)
    edge_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for p in pulses.values():
        tags = p.get("tags", []) or []
        for t in tags:
            tag_counts[t] += 1
        # pairwise co-occur
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted((tags[i], tags[j]))
                if a == b:
                    continue
                edge_counts[(a, b)] += 1

    # Build nodes
    all_tags = sorted(tag_counts.keys())
    degrees: Dict[str, int] = defaultdict(int)
    for (a, b), w in edge_counts.items():
        degrees[a] += 1
        degrees[b] += 1
    max_deg = max(degrees.values()) if degrees else 1

    nodes = [{"id": t, "centrality": (degrees.get(t, 0) / max_deg if max_deg else 0.0)} for t in all_tags]

    # Build links
    links = [{"source": a, "target": b, "weight": w} for (a, b), w in edge_counts.items()]

    return nodes, links

# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Build Phi-Mesh data bundle for the Tag Map.")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml", help="Glob for pulse YAML files (recursive).")
    ap.add_argument("--alias-map", default="meta/aliases.yml", help="Path to aliases.yml (optional).")
    ap.add_argument("--tag-descriptions", default="meta/tag_descriptions.yml", help="Path to tag_descriptions.yml (optional).")
    ap.add_argument("--out-js", default="docs/data.js", help="Output JS file path.")
    args = ap.parse_args()

    alias_map = _build_alias_map(args.alias_map)
    tag_descriptions = load_tag_descriptions(args.tag_descriptions)

    pulses, tag_to_pulses, tag_resources = scan_pulses(args.pulse_glob, alias_map)
    nodes, links = build_tag_graph(pulses)

    # Assemble bundle
    bundle: Dict[str, Any] = {
        "nodes": nodes,
        "links": links,
        "tagResources": tag_resources,       # { tag: {papers:[], podcasts:[]} }
        "tagDescriptions": tag_descriptions, # { tag: "…"}
        "pulses": pulses,                    # { pulse_id: {…} }
        "tagToPulses": tag_to_pulses,        # { tag: [pulse_id, …] }
        "meta": {
            "generated": datetime.utcnow().isoformat() + "Z",
            "pulseCount": len(pulses),
            "tagCount": len(nodes),
            "linkCount": len(links),
            "aliasMapPresent": bool(alias_map),
            "descriptionsPresent": bool(tag_descriptions),
        },
    }

    # Write as window.PHI_DATA = ...
    out_path = args.out_js
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = ")
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print(f"[OK] Wrote {out_path} with {len(nodes)} tags, {len(links)} links, {len(pulses)} pulses.")

if __name__ == "__main__":
    main()
