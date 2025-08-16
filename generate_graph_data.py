#!/usr/bin/env python3
"""
generate_graph_data.py

Builds docs/data.js (window.PHI_DATA) used by the interactive tag map.

Emits:
  {
    nodes: [{ id, degree, centrality }],
    links: [{ source, target }],
    tagDescriptions: { [tag]: "..." },
    tagResources: { [tag]: { papers: [url], podcasts: [url] } },
    pulsesByTag: { [tag]: [ { id,title,date,ageDays,summary,papers[],podcasts[],tags[] } ] },
    tagToPulses: { [tag]: [pulseId,...] },
    meta: { generated_at, pulse_count, tag_count }
  }

Args:
  --pulse-glob "pulse/**/*.yml"
  --alias-map meta/aliases.yml
  --tag-descriptions meta/tag_descriptions.yml
  --out-js docs/data.js
"""

import argparse
import datetime as dt
import glob
import json
import os
import sys
from collections import defaultdict, Counter

import yaml
import networkx as nx


def load_yaml(path, default=None):
    if not path or not os.path.exists(path):
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or (default if default is not None else {})


def norm_tag(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip()
    # unify separators and whitespace
    s = s.replace(" ", "_")
    # strip duplicates of underscore
    while "__" in s:
        s = s.replace("__", "_")
    return s


def apply_alias(tag: str, alias_map: dict) -> str:
    # alias_map is { alias: canonical, ... }
    if not tag:
        return tag
    return alias_map.get(tag, tag)


def listify(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def scrub_url_list(v):
    """Return a list of string URLs; flatten objects with 'url' fields."""
    out = []
    for x in listify(v):
        if not x:
            continue
        if isinstance(x, str):
            out.append(x.strip())
        elif isinstance(x, dict) and x.get("url"):
            out.append(str(x["url"]).strip())
    # de-dup keep order
    seen = set()
    out2 = []
    for u in out:
        if u and u not in seen:
            seen.add(u)
            out2.append(u)
    return out2


def parse_pulse_yaml(path: str):
    data = load_yaml(path, default={})
    # YAMLs may be front-matter like {title,date,summary,tags,papers,podcasts}
    title = data.get("title") or os.path.basename(path)
    date = data.get("date") or data.get("created") or ""
    # flatten multi-line folded summary if needed
    summary = data.get("summary") or ""
    tags = data.get("tags") or []
    papers = []
    podcasts = []

    # papers may be list of {title,url} or raw urls
    for p in listify(data.get("papers")):
        if isinstance(p, dict) and p.get("url"):
            papers.append(str(p["url"]).strip())
        elif isinstance(p, str):
            papers.append(p.strip())

    # podcasts list of urls or {url}
    podcasts = scrub_url_list(data.get("podcasts"))

    return {
        "title": str(title),
        "date": str(date),
        "summary": str(summary),
        "tags": tags,
        "papers": papers,
        "podcasts": podcasts,
    }


def days_since(date_str: str) -> int | None:
    if not date_str:
        return None
    # try a few common formats
    fmts = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in fmts:
        try:
            d = dt.datetime.strptime(date_str, fmt)
            break
        except Exception:
            d = None
    if d is None:
        return None
    return (dt.datetime.utcnow() - d.replace(tzinfo=None)).days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--tag-descriptions", default="meta/tag_descriptions.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    args = ap.parse_args()

    # Load alias map as { alias: canonical }
    aliases = load_yaml(args.alias_map, default={})
    # Support both shapes:
    # - { alias: canonical }
    # - { aliases: { alias: canonical } }
    if "aliases" in aliases and isinstance(aliases["aliases"], dict):
        aliases = aliases["aliases"]

    # Load tag descriptions file
    tag_desc_raw = load_yaml(args.tag_descriptions, default={})
    # Support shape:
    #   { tags: { TagName: "desc", ... }, ... }
    # or flat { TagName: "desc", ... }
    if "tags" in tag_desc_raw and isinstance(tag_desc_raw["tags"], dict):
        tag_descriptions = {norm_tag(k): str(v) for k, v in tag_desc_raw["tags"].items()}
    else:
        tag_descriptions = {norm_tag(k): str(v) for k, v in tag_desc_raw.items()}

    # Parse pulses
    pulse_files = sorted(glob.glob(args.pulse_glob, recursive=True))
    pulses = []
    for p in pulse_files:
        try:
            meta = parse_pulse_yaml(p)
        except Exception as e:
            # keep going; skip bad file
            continue

        # normalize and alias tags
        tags = [apply_alias(norm_tag(t), aliases) for t in listify(meta.get("tags"))]
        tags = [t for t in tags if t]  # drop empties
        tags = list(dict.fromkeys(tags))  # de-dup preserve order

        pl = {
            "id": os.path.splitext(os.path.basename(p))[0],
            "title": meta["title"],
            "date": meta["date"],
            "ageDays": days_since(meta["date"]),
            "summary": meta["summary"],
            "papers": scrub_url_list(meta["papers"]),
            "podcasts": scrub_url_list(meta["podcasts"]),
            "tags": tags,
        }
        pulses.append(pl)

    # Build graph from tag co-occurrence across pulses
    G = nx.Graph()
    # Collect resources per tag
    tag_resources = defaultdict(lambda: {"papers": [], "podcasts": []})
    # Tag→pulses
    tag_to_pulses = defaultdict(list)
    # Pulses by tag (full objects)
    pulses_by_tag = defaultdict(list)

    for pl in pulses:
        tags = pl["tags"]
        # add tag nodes
        for t in tags:
            if not G.has_node(t):
                G.add_node(t)
        # add co-occurrence edges
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted((tags[i], tags[j]))
                if G.has_edge(a, b):
                    G[a][b]["w"] += 1
                else:
                    G.add_edge(a, b, w=1)

        # accumulate resources to each tag the pulse touches
        for t in tags:
            tag_to_pulses[t].append(pl["id"])
            pulses_by_tag[t].append(pl)
            if pl["papers"]:
                tag_resources[t]["papers"].extend(pl["papers"])
            if pl["podcasts"]:
                tag_resources[t]["podcasts"].extend(pl["podcasts"])

    # de-dup resources per tag + keep order
    for t, r in tag_resources.items():
        for key in ("papers", "podcasts"):
            seen = set()
            uniq = []
            for u in r[key]:
                if u and u not in seen:
                    seen.add(u)
                    uniq.append(u)
            r[key] = uniq

    # Compute degree + a simple centrality proxy (normalized degree)
    degrees = dict(G.degree())
    if degrees:
        max_deg = max(degrees.values()) or 1
    else:
        max_deg = 1
    nodes = []
    for n in G.nodes():
        deg = int(degrees.get(n, 0))
        nodes.append({
            "id": n,
            "degree": deg,
            "centrality": round(deg / max_deg, 4)
        })

    links = [{"source": u, "target": v} for (u, v) in G.edges()]

    out = {
        "nodes": nodes,
        "links": links,
        "tagDescriptions": tag_descriptions,    # <— tooltips use this
        "tagResources": tag_resources,
        "pulses": pulses,                        # handy for debugging
        "pulsesByTag": pulses_by_tag,            # <— satellites use this
        "tagToPulses": tag_to_pulses,
        "meta": {
            "generated_at": dt.datetime.utcnow().isoformat() + "Z",
            "pulse_count": len(pulses),
            "tag_count": len(nodes),
        }
    }

    os.makedirs(os.path.dirname(args.out_js), exist_ok=True)
    with open(args.out_js, "w", encoding="utf-8") as f:
        f.write("window.PHI_DATA = ")
        json.dump(out, f, ensure_ascii=False)
        f.write(";\n")

    print(f"Wrote {args.out_js} with {len(nodes)} tags, {len(links)} links, "
          f"{len(pulses)} pulses; "
          f"tagDescriptions={len(tag_descriptions)}, pulsesByTag={len(pulses_by_tag)}")


if __name__ == "__main__":
    sys.exit(main())
