#!/usr/bin/env python3
# generate_graph_data.py
# Robust generator for docs/data.js (window.PHI_DATA).
# - Reads pulses (YAML) from a glob
# - Applies aliases
# - Reads tag descriptions
# - Builds nodes/links, pulsesByTag, tagResources, tagFirstSeen
# - Tolerates messy YAML: unwraps single-item lists, skips multi-item lists

import argparse
import glob
import io
import json
import os
import re
import sys
from collections import defaultdict, OrderedDict

import yaml
from datetime import datetime, date
from pathlib import Path

# ----------------------- helpers -----------------------

def warn(msg):
    print(f"[WARN] {msg}", file=sys.stderr)

def info(msg):
    print(f"[INFO] {msg}", file=sys.stderr)

def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        warn(f"YAML load failed for {path}: {e}")
        return None

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def is_url(s):
    return isinstance(s, str) and bool(re.match(r"^https?://", s, re.I))

def to_iso_date(val, fallback=""):
    """Return YYYY-MM-DD string if possible; else trimmed string; else fallback."""
    if val is None:
        return fallback
    if isinstance(val, datetime):
        return val.date().isoformat()
    if isinstance(val, date):
        return val.isoformat()
    s = str(val).strip()
    # Trim full ISO timestamp to date
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[T\s]\d{2}:\d{2}:\d{2}", s)
    if m:
        return m.group(1)
    # Already YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    # Try YYYY/MM/DD or YYYY.MM.DD
    m = re.match(r"^(\d{4})[/.](\d{2})[/.](\d{2})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return s or fallback

def date_from_filename(path):
    base = os.path.basename(path)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", base)
    if m:
        return m.group(1)
    m = re.search(r"(\d{8})", base)  # YYYYMMDD
    if m:
        s = m.group(1)
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return ""

def norm_summary(val):
    if val is None:
        return ""
    if isinstance(val, list):
        s = " ".join(str(x) for x in val)
    elif isinstance(val, dict):
        s = " ".join(f"{k}: {v}" for k, v in val.items())
    else:
        s = str(val)
    # strip errant backticks often left by earlier tools
    return s.strip().strip("`").strip()

def norm_links(val):
    """Return list of http(s) URLs, deduped, keep order."""
    out, seen = [], set()
    if not val:
        return out
    items = val if isinstance(val, list) else [val]
    for item in items:
        if isinstance(item, dict):
            u = (item.get("url") or item.get("href") or "").strip()
        else:
            u = str(item or "").strip()
        if is_url(u) and u not in seen:
            out.append(u); seen.add(u)
    return out

def norm_tags(val):
    out, seen = [], set()
    def push(tag):
        t = (tag or "").strip()
        if t and t not in seen:
            out.append(t); seen.add(t)
    if not val:
        return out
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                push(item)
            elif isinstance(item, dict):
                push(item.get("tag") or item.get("name") or "")
            else:
                push(str(item))
        return out
    if isinstance(val, str):
        for part in re.split(r"[,\n]+", val):
            push(part)
        return out
    push(str(val))
    return out

def apply_aliases(tag, alias_map):
    """Return canonical tag if tag matches an alias, else tag."""
    # alias_map: { canonical: [alias1, alias2, ...] }
    for canon, aliases in alias_map.items():
        if tag == canon:
            return canon
        for a in aliases or []:
            if tag == a:
                return canon
    return tag

def load_alias_map(path):
    data = load_yaml(path)
    alias_map = {}
    if not data or "aliases" not in data:
        return alias_map
    # normalize keys to strings; values to list[str]
    for canon, aliases in data["aliases"].items():
        canon_s = str(canon)
        if isinstance(aliases, list):
            alias_map[canon_s] = [str(x) for x in aliases]
        elif isinstance(aliases, str):
            alias_map[canon_s] = [aliases]
        else:
            alias_map[canon_s] = []
    return alias_map

def load_tag_descriptions(path):
    data = load_yaml(path)
    if not data:
        return {}
    # allow both {tag: desc} or {descriptions: {tag: desc}} or top-level "tags:"
    if "descriptions" in data and isinstance(data["descriptions"], dict):
        pool = data["descriptions"]
    elif "tags" in data and isinstance(data["tags"], dict):
        pool = data["tags"]
    else:
        pool = {k: v for k, v in data.items() if isinstance(v, str)}
    # stringify keys, ensure string values
    out = {}
    for k, v in pool.items():
        out[str(k)] = str(v or "")
    return out

def _is_archived(path_str: str) -> bool:
    """
    True for files under pulse/archive/** (we exclude these from the graph).
    """
    parts = list(Path(path_str).parts)
    # Require at least ["pulse", "archive", ...]
    return len(parts) >= 2 and parts[0] == "pulse" and parts[1] == "archive"

# ----------------------- pulse collection -----------------------

def coerce_pulse_dict(path, obj):
    """
    Ensure we return a mapping for a pulse YAML.
    - If dict: ok
    - If list with single dict: unwrap
    - If list with many items: skip (bad shape)
    - Otherwise skip
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list):
        if len(obj) == 1 and isinstance(obj[0], dict):
            return obj[0]
        warn(f"Skipping multi-item or non-dict list top-level in {path}")
        return None
    warn(f"Skipping pulse (top-level {type(obj).__name__}) in {path}")
    return None

def normalize_pulse(path, data, alias_map):
    """
    Produce a minimal pulse dict:
      id, title, date, summary, tags, papers, podcasts, ageDays
    """
    if data is None:
        return None
    title = (data.get("title") or "").strip()
    if not title:
        stem = os.path.splitext(os.path.basename(path))[0]
        title = stem.replace("_", " ").replace("-", " ").strip()

    # date
    raw_date = data.get("date")
    date_str = to_iso_date(raw_date, date_from_filename(path))

    # tags
    tags = [apply_aliases(t, alias_map) for t in norm_tags(data.get("tags"))]

    # resources
    papers = norm_links(data.get("papers"))
    podcasts = norm_links(data.get("podcasts"))

    summary = norm_summary(data.get("summary"))

    # compute ageDays if date parses
    age_days = None
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            age_days = (datetime.utcnow().date() - d).days
    except Exception:
        pass

    pid = os.path.relpath(path).replace("\\", "/")
    return {
        "id": pid,
        "title": title,
        "date": date_str,
        "summary": summary,
        "tags": tags,
        "papers": papers,
        "podcasts": podcasts,
        "ageDays": age_days,
    }

def collect_pulses(pulse_glob, alias_map):
    pulses = []
    tag_to_pulses = defaultdict(list)

    files = sorted(glob.glob(pulse_glob, recursive=True))
    files = [p for p in files if not _is_archived(p)]
    for path in files:
        obj = load_yaml(path)
        if obj is None:
            continue
        data = coerce_pulse_dict(path, obj)
        if data is None:
            continue
        p = normalize_pulse(path, data, alias_map)
        if p is None:
            continue
        pulses.append(p)
        for t in p["tags"]:
            tag_to_pulses[t].append(p)

    return pulses, tag_to_pulses

# ----------------------- graph building -----------------------

def build_graph_from_pulses(tag_to_pulses):
    """
    Nodes are unique tags. Links between tags that co-occur in a pulse.
    Degree = count of distinct neighbors.
    Centrality is a simple degree-based scaling for display.
    """
    # gather nodes
    tags = sorted(tag_to_pulses.keys())
    nodes = [{"id": t} for t in tags]

    # co-occurrence
    pair_weight = defaultdict(int)
    for t, plist in tag_to_pulses.items():
        for p in plist:
            co_tags = [x for x in p["tags"] if x != t]
            for other in co_tags:
                a, b = sorted([t, other])
                pair_weight[(a, b)] += 1

    # links
    links = [{"source": a, "target": b, "weight": w} for (a, b), w in pair_weight.items() if a != b]

    # degree
    deg = defaultdict(int)
    for l in links:
        deg[l["source"]] += 1
        deg[l["target"]] += 1

    # centrality proxy
    maxd = max(deg.values()) if deg else 1
    for n in nodes:
        d = deg.get(n["id"], 0)
        n["degree"] = d
        n["centrality"] = (d / maxd) if maxd else 0.0

    return nodes, links

def build_resources_and_first_seen(tag_to_pulses, tag_descriptions):
    tagResources = {}
    tagFirstSeen = {}
    for tag, plist in tag_to_pulses.items():
        # resources: union of papers/podcasts across pulses (keep order, dedupe)
        papers, seen_p = [], set()
        podcasts, seen_c = [], set()
        first_date = None
        for p in sorted(plist, key=lambda x: x["date"] or "9999-99-99"):
            for u in p["papers"]:
                if u not in seen_p:
                    papers.append(u); seen_p.add(u)
            for u in p["podcasts"]:
                if u not in seen_c:
                    podcasts.append(u); seen_c.add(u)
            # track earliest date
            if p["date"]:
                if first_date is None or p["date"] < first_date:
                    first_date = p["date"]
        tagResources[tag] = {"papers": papers, "podcasts": podcasts}
        callout = (tag_descriptions.get(tag) or "").strip()
        tagFirstSeen[tag] = {"date": first_date, "callout": callout}
    return tagResources, tagFirstSeen

# ----------------------- main -----------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml", help="Glob for pulses")
    ap.add_argument("--alias-map", default="meta/aliases.yml", help="YAML of aliases")
    ap.add_argument("--tag-descriptions", default="meta/tag_descriptions.yml", help="YAML of tag descriptions")
    ap.add_argument("--out-js", default="docs/data.js", help="Output JS path (window.PHI_DATA = ...)")
    args = ap.parse_args()

    alias_map = load_alias_map(args.alias_map)
    tag_desc = load_tag_descriptions(args.tag_descriptions)

    pulses, tag_to_pulses = collect_pulses(args.pulse_glob, alias_map)
    info(f"Collected pulses: {len(pulses)}")

    # Build graph
    nodes, links = build_graph_from_pulses(tag_to_pulses)

    # Resources + first-seen
    tagResources, tagFirstSeen = build_resources_and_first_seen(tag_to_pulses, tag_desc)

    payload = OrderedDict()
    payload["nodes"] = nodes
    payload["links"] = links
    payload["tagDescriptions"] = tag_desc
    payload["pulsesByTag"] = {k: v for k, v in sorted(tag_to_pulses.items())}
    payload["tagResources"] = tagResources
    payload["tagFirstSeen"] = tagFirstSeen

    js = "window.PHI_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    write_text(args.out_js, js)
    info(f"Wrote {args.out_js}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
