#!/usr/bin/env python3
"""
generate_graph_data.py

Builds docs/data.js (window.PHI_DATA = {...}) from pulse YAML files, aliases,
and optional tag descriptions.

Resilient to:
- nested tag lists (e.g. tags: - [A,B])
- mixed resource formats (string URL OR {url,title})
- missing/odd fields

CLI:
  --pulse-glob "pulse/**/*.yml"
  --alias-map meta/aliases.yml
  --tag-descriptions meta/tag_descriptions.yml
  --out-js docs/data.js
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import io
import json
import os
import re
import sys
from collections import defaultdict
from itertools import combinations

try:
    import yaml
except Exception:
    print("Missing dependency: pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    import networkx as nx
except Exception:
    print("Missing dependency: networkx", file=sys.stderr)
    sys.exit(2)


# --------------------------- Helpers -----------------------------------------
def read_yaml(path: str) -> dict | list | None:
    if not path or not os.path.exists(path):
        return None
    with io.open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] YAML load failed for {path}: {e}", file=sys.stderr)
            return None


def listify(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]


_slug_re = re.compile(r"[^\w\-]+", re.UNICODE)


def norm_tag(tag: str) -> str:
    if tag is None:
        return ""
    # Coerce to str (flattened items might not be strings yet)
    tag = str(tag)
    # keep underscores already used; spaces -> underscore; strip extras
    tag = tag.strip()
    tag = tag.replace(" ", "_")
    tag = _slug_re.sub("_", tag)
    tag = re.sub(r"_+", "_", tag)
    return tag.strip("_")


def apply_alias(tag: str, aliases: dict[str, str]) -> str:
    if not tag:
        return tag
    return aliases.get(tag, tag)


def coerce_url_item(item):
    """
    Accepts:
      - "https://example.com/..."  (string)
      - { url: "...", title: "..." }
      - { title: "...", url: "..." }
    Returns { "url": "...", "title": "..." } or None if no url.
    """
    if not item:
        return None
    if isinstance(item, str):
        url = item.strip()
        return {"url": url, "title": ""}
    if isinstance(item, dict):
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        if not url:
            return None
        return {"url": url, "title": title}
    # Unknown type
    return None


def unique_preserve(seq, key=lambda x: x):
    seen = set()
    out = []
    for s in seq:
        k = key(s)
        if k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def parse_date(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(s, fmt)
        except Exception:
            pass
    # last try: fromisoformat (py3.11 handles Z poorly; strip it)
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


# --------------------------- Core build ---------------------------------------
def load_alias_map(path: str) -> dict[str, str]:
    data = read_yaml(path) or {}
    # Allow either flat mapping {alias: canonical} or under key "aliases"
    aliases = data.get("aliases") if isinstance(data, dict) else None
    if isinstance(aliases, dict):
        # normalize keys/values
        return {norm_tag(k): norm_tag(v) for k, v in aliases.items()}
    if isinstance(data, dict):
        # assume the file itself is {alias: canonical}
        return {norm_tag(k): norm_tag(v) for k, v in data.items()}
    return {}


def load_tag_descriptions(path: str) -> dict[str, str]:
    """
    Supports either:
      tags:
        TagA: "desc"
        TagB: "desc"
    or a flat mapping { TagA: "desc", ... }
    """
    data = read_yaml(path) or {}
    if isinstance(data, dict) and "tags" in data and isinstance(data["tags"], dict):
        raw = data["tags"]
    elif isinstance(data, dict):
        raw = data
    else:
        raw = {}

    out = {}
    for k, v in raw.items():
        key = norm_tag(k)
        if isinstance(v, str):
            out[key] = v.strip()
        else:
            # allow dicts later if we add structured descriptions
            out[key] = str(v)
    return out


def flatten_tags(raw_tags, aliases: dict[str, str]) -> list[str]:
    """
    Robust tag flattening:
      - handles ["A", "B"]
      - handles [["A", "B"], "C"]
      - coerces all items to strings, normalizes + aliasing
      - de-dups preserving order
    """
    # First pass: flatten one level if nested lists exist
    flat = []
    for t in listify(raw_tags):
        if isinstance(t, (list, tuple)):
            flat.extend(t)
        else:
            flat.append(t)

    # Normalize + alias + filter empties
    normed = []
    for t in flat:
        tag = apply_alias(norm_tag(t), aliases)
        if tag:
            normed.append(tag)

    # De-dup
    return list(dict.fromkeys(normed))


def collect_pulses(pulse_glob: str, aliases: dict[str, str]) -> tuple[list[dict], dict[str, list[dict]]]:
    """
    Read all pulses, return:
      pulses: list of normalized pulse dicts
      tag_to_pulses: map tag -> list of pulse dicts (same obj refs as in pulses)
    """
    paths = sorted(glob.glob(pulse_glob, recursive=True))
    now = dt.datetime.utcnow()
    pulses = []
    tag_to_pulses = defaultdict(list)

    for path in paths:
        data = read_yaml(path) or {}
        # Basic fields
        title = (data.get("title") or "").strip()
        date_raw = data.get("date")
        date_dt = parse_date(date_raw)
        age_days = None
        if date_dt:
            age_days = max(0, int((now - date_dt).total_seconds() // 86400))

        # Tags (robust flatten)
        tags = flatten_tags(data.get("tags"), aliases)

        # Resources
        papers = []
        for itm in listify(data.get("papers")):
            if isinstance(itm, dict) and "url" not in itm and "title" in itm and "link" in itm:
                # rare weird shapes; try to coerce
                itm = {"url": itm.get("link", ""), "title": itm.get("title", "")}
            obj = coerce_url_item(itm)
            if obj:
                papers.append(obj)
        papers = unique_preserve(papers, key=lambda x: x["url"])

        podcasts = []
        for itm in listify(data.get("podcasts")):
            obj = coerce_url_item(itm)
            if obj:
                podcasts.append(obj)
        podcasts = unique_preserve(podcasts, key=lambda x: x["url"])

        summary = (data.get("summary") or "").strip()

        # Create a stable-ish id from filename (without dirs) or date+title
        base = os.path.splitext(os.path.basename(path))[0]
        pid = base

        pulse = {
            "id": pid,
            "path": path,
            "title": title or base,
            "date": date_dt.isoformat().replace("+00:00", "Z") if date_dt else "",
            "ageDays": age_days,
            "summary": summary,
            "papers": papers,
            "podcasts": podcasts,
            "tags": tags,
        }
        pulses.append(pulse)
        for t in tags:
            tag_to_pulses[t].append(pulse)

    return pulses, tag_to_pulses


def build_graph(tag_to_pulses: dict[str, list[dict]]) -> tuple[list[dict], list[dict], dict[str, float]]:
    """
    Build a co-occurrence graph of tags.
    Returns:
      nodes: [{id, centrality}]
      links: [{source, target, weight}]
      centrality: map tag -> centrality
    """
    G = nx.Graph()

    # Add nodes upfront (ensures isolated tags appear)
    for tag in tag_to_pulses.keys():
        G.add_node(tag)

    # For each pulse, connect every pair of its tags
    for tags in tag_to_pulses.values():
        # 'tags' here is a list of pulse dicts; we need the tag list from each pulse
        # Build set of unique tags from this tag's pulses? No: we need per pulse pairs
        # The simple way: we already iterate later per pulse to add edges. Instead:
        pass

    # Better: re-create pairs by iterating all pulses and using their tag sets
    # We need all pulses… easiest is: collect unique tag sets per pulse from the reverse index.
    # Instead, we’ll rebuild an index pulse_id -> tag list from the reverse map.
    pulse_to_tags = defaultdict(set)
    for tag, pulse_list in tag_to_pulses.items():
        for p in pulse_list:
            pulse_to_tags[p["id"]].add(tag)

    for tagset in pulse_to_tags.values():
        tlist = sorted(tagset)
        for a, b in combinations(tlist, 2):
            if not G.has_edge(a, b):
                G.add_edge(a, b, weight=0)
            G[a][b]["weight"] += 1

    # Centrality (degree centrality scaled into [0..1])
    cent = nx.degree_centrality(G)
    nodes = [{"id": n, "centrality": float(cent.get(n, 0.0))} for n in G.nodes()]
    links = [{"source": u, "target": v, "weight": int(d.get("weight", 1))} for u, v, d in G.edges(data=True)]

    # Sort nodes by id for stable output
    nodes.sort(key=lambda x: x["id"])
    return nodes, links, cent


def build_tag_resources(tag_to_pulses: dict[str, list[dict]]) -> dict[str, dict]:
    """
    Aggregate paper/podcast URLs per tag (de-duplicated).
    Returns: { tag: { papers: [{url,title}], podcasts: [...] } }
    """
    tag_resources = {}
    for tag, plist in tag_to_pulses.items():
        papers = []
        podcasts = []
        for p in plist:
            papers.extend(p.get("papers", []))
            podcasts.extend(p.get("podcasts", []))
        papers = unique_preserve(papers, key=lambda x: x["url"])
        podcasts = unique_preserve(podcasts, key=lambda x: x["url"])
        tag_resources[tag] = {"papers": papers, "podcasts": podcasts}
    return tag_resources


def emit_js(data: dict, out_js: str):
    os.makedirs(os.path.dirname(out_js) or ".", exist_ok=True)
    # Compact but still readable
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with io.open(out_js, "w", encoding="utf-8") as f:
        f.write("window.PHI_DATA=" + payload + ";")
    print(f"[OK] wrote {out_js} ({len(payload):,} bytes)")


# --------------------------- main --------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--tag-descriptions", default="meta/tag_descriptions.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    args = ap.parse_args()

    aliases = load_alias_map(args.alias_map)
    tag_desc = load_tag_descriptions(args.tag_descriptions)

    pulses, tag_to_pulses = collect_pulses(args.pulse_glob, aliases)

    # Ensure every tag that ever appears becomes a key in the reverse index
    all_tags = sorted({t for p in pulses for t in p.get("tags", [])})
    for t in all_tags:
        tag_to_pulses.setdefault(t, [])

    nodes, links, centrality = build_graph(tag_to_pulses)
    tag_resources = build_tag_resources(tag_to_pulses)

    # pulsesByTag view (map of tag -> list of pulse objects (subset fields))
    pulses_by_tag = {}
    for t, plist in tag_to_pulses.items():
        # Slice down each pulse to the fields the front-end needs for satellites
        tmp = []
        for p in plist:
            tmp.append({
                "id": p["id"],
                "title": p["title"],
                "date": p["date"],
                "ageDays": p["ageDays"],
                "summary": p["summary"],
                "papers": p["papers"],
                "podcasts": p["podcasts"],
                "tags": p["tags"],
            })
        # Sort by recency (newest first)
        tmp.sort(key=lambda x: (x["ageDays"] is None, x["ageDays"]))
        pulses_by_tag[t] = tmp

    # Top-level data
    data = {
        "nodes": nodes,
        "links": links,
        "tagDescriptions": tag_desc,
        "tagResources": tag_resources,
        "pulses": pulses,               # full list (normalized)
        "tagToPulses": {t: [p["id"] for p in plist] for t, plist in tag_to_pulses.items()},
        "pulsesByTag": pulses_by_tag,   # convenient map for UI
        "meta": {
            "buildAt": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "numTags": len(all_tags),
            "numPulses": len(pulses),
            "numLinks": len(links),
        },
    }

    emit_js(data, args.out_js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
