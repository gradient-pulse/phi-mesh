#!/usr/bin/env python3
# generate_graph_data.py (canonical tooltips + alias-aware)
# - Reads pulses (YAML) from a glob (archive excluded by workflow)
# - Canonicalizes tags (lowercase, underscores) + applies aliases
# - Canonicalizes *tag description keys* to the same ids
# - Builds nodes/links, pulsesByTag, tagResources, tagFirstSeen

import argparse, glob, json, os, re, sys
from collections import defaultdict, OrderedDict
from datetime import datetime, date
from pathlib import Path
import yaml

# ----------------------- helpers -----------------------

def warn(msg): print(f"[WARN] {msg}", file=sys.stderr)
def info(msg): print(f"[INFO] {msg}", file=sys.stderr)

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

def is_url(s): return isinstance(s, str) and bool(re.match(r"^https?://", s, re.I))

def to_iso_date(val, fallback=""):
    if val is None: return fallback
    if isinstance(val, datetime): return val.date().isoformat()
    if isinstance(val, date): return val.isoformat()
    s = str(val).strip()
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[T\s]\d{2}:\d{2}:\d{2}", s)
    if m: return m.group(1)
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s): return s
    m = re.match(r"^(\d{4})[/.](\d{2})[/.](\d{2})$", s)
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return s or fallback

def date_from_filename(path):
    base = os.path.basename(path)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", base)
    if m: return m.group(1)
    m = re.search(r"(\d{8})", base)  # YYYYMMDD
    if m:
        s = m.group(1)
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return ""

def norm_summary(val):
    if val is None: return ""
    if isinstance(val, list): s = " ".join(str(x) for x in val)
    elif isinstance(val, dict): s = " ".join(f"{k}: {v}" for k, v in val.items())
    else: s = str(val)
    return s.strip().strip("`").strip()

def norm_links(val):
    out, seen = [], set()
    if not val: return out
    items = val if isinstance(val, list) else [val]
    for item in items:
        u = (item.get("url") or item.get("href") or "").strip() if isinstance(item, dict) else str(item or "").strip()
        if is_url(u) and u not in seen:
            out.append(u); seen.add(u)
    return out

def canon_tag(s: str) -> str:
    """Lowercase, replace non-alphanum with '_', collapse repeats, trim '_'."""
    s = (s or "").strip()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")

def apply_aliases(tag, alias_map):
    """Return canonical tag after alias mapping."""
    # alias_map: { canon_id: [alias1, alias2, ...] }  (keys already lower/underscore in your file)
    if tag in alias_map:  # already a canonical key
        return tag
    for canon, aliases in alias_map.items():
        if tag == canon: return canon
        for a in aliases or []:
            if tag == canon_tag(a):  # compare canonicalized alias
                return canon
    return tag

def load_alias_map(path):
    data = load_yaml(path) or {}
    pool = data.get("aliases") or {}
    alias_map = {}
    for canon, aliases in pool.items():
        c = canon_tag(str(canon))
        vals = aliases if isinstance(aliases, list) else [aliases]
        alias_map[c] = [str(x) for x in vals if x is not None]
    return alias_map

def load_tag_descriptions(path, alias_map):
    """
    Load tag descriptions and canonicalize their keys with canon_tag + aliases,
    so tooltips line up with node ids.
    """
    data = load_yaml(path) or {}
    # Accept {tags:{...}}, {descriptions:{...}}, or flat {k:v}
    if isinstance(data.get("tags"), dict):
        pool = data["tags"]
    elif isinstance(data.get("descriptions"), dict):
        pool = data["descriptions"]
    else:
        pool = {k: v for k, v in data.items() if isinstance(v, str)}

    out = {}
    for k, v in pool.items():
        # Canonicalize key then alias-map it
        ck = apply_aliases(canon_tag(str(k)), alias_map)
        out[ck] = str(v or "")
    return out

def _is_archived(path_str: str) -> bool:
    parts = list(Path(path_str).parts)
    return len(parts) >= 2 and parts[0] == "pulse" and parts[1] == "archive"

# ----------------------- pulse collection -----------------------

def coerce_pulse_dict(path, obj):
    if isinstance(obj, dict): return obj
    if isinstance(obj, list):
        if len(obj) == 1 and isinstance(obj[0], dict): return obj[0]
        warn(f"Skipping multi-item or non-dict list top-level in {path}")
        return None
    warn(f"Skipping pulse (top-level {type(obj).__name__}) in {path}")
    return None

def normalize_pulse(path, data, alias_map):
    if data is None: return None
    title = (data.get("title") or "").strip()
    if not title:
        stem = os.path.splitext(os.path.basename(path))[0]
        title = stem.replace("_", " ").replace("-", " ").strip()

    raw_date = data.get("date")
    date_str = to_iso_date(raw_date, date_from_filename(path))

    # Canonicalize & alias-map tags
    raw_tags = data.get("tags")
    tags0 = []
    if isinstance(raw_tags, list):
        tags0 = [t for t in raw_tags if t is not None]
    elif isinstance(raw_tags, str):
        tags0 = re.split(r"[,\n]+", raw_tags)
    tags = [apply_aliases(canon_tag(str(t)), alias_map) for t in tags0 if str(t).strip()]

    papers = norm_links(data.get("papers"))
    podcasts = norm_links(data.get("podcasts"))
    summary = norm_summary(data.get("summary"))

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
    pulses, tag_to_pulses = [], defaultdict(list)
    files = sorted(glob.glob(pulse_glob, recursive=True))
    files = [p for p in files if not _is_archived(p)]
    for path in files:
        obj = load_yaml(path)
        if obj is None: continue
        data = coerce_pulse_dict(path, obj)
        if data is None: continue
        p = normalize_pulse(path, data, alias_map)
        if p is None: continue
        pulses.append(p)
        for t in p["tags"]:
            tag_to_pulses[t].append(p)
    return pulses, tag_to_pulses

# ----------------------- graph building -----------------------

def build_graph_from_pulses(tag_to_pulses):
    tags = sorted(tag_to_pulses.keys())
    nodes = [{"id": t} for t in tags]

    pair_weight = defaultdict(int)
    for t, plist in tag_to_pulses.items():
        for p in plist:
            co_tags = [x for x in p["tags"] if x != t]
            for other in co_tags:
                a, b = sorted([t, other])
                pair_weight[(a, b)] += 1

    links = [{"source": a, "target": b, "weight": w}
             for (a, b), w in pair_weight.items() if a != b]

    deg = defaultdict(int)
    for l in links:
        deg[l["source"]] += 1
        deg[l["target"]] += 1

    maxd = max(deg.values()) if deg else 1
    for n in nodes:
        d = deg.get(n["id"], 0)
        n["degree"] = d
        n["centrality"] = (d / maxd) if maxd else 0.0

    return nodes, links

def build_resources_and_first_seen(tag_to_pulses, tag_descriptions):
    tagResources, tagFirstSeen = {}, {}
    for tag, plist in tag_to_pulses.items():
        papers, seen_p = [], set()
        podcasts, seen_c = [], set()
        first_date = None
        for p in sorted(plist, key=lambda x: x["date"] or "9999-99-99"):
            for u in p["papers"]:
                if u not in seen_p: papers.append(u); seen_p.add(u)
            for u in p["podcasts"]:
                if u not in seen_c: podcasts.append(u); seen_c.add(u)
            if p["date"] and (first_date is None or p["date"] < first_date):
                first_date = p["date"]
        tagResources[tag] = {"papers": papers, "podcasts": podcasts}
        callout = (tag_descriptions.get(tag) or "").strip()
        tagFirstSeen[tag] = {"date": first_date, "callout": callout}
    return tagResources, tagFirstSeen

# ----------------------- main -----------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml")
    ap.add_argument("--alias-map", default="meta/aliases.yml")
    ap.add_argument("--tag-descriptions", default="meta/tag_descriptions.yml")
    ap.add_argument("--out-js", default="docs/data.js")
    args = ap.parse_args()

    alias_map = load_alias_map(args.alias_map)
    tag_desc = load_tag_descriptions(args.tag_descriptions, alias_map)

    pulses, tag_to_pulses = collect_pulses(args.pulse_glob, alias_map)
    info(f"Collected pulses: {len(pulses)}")

    nodes, links = build_graph_from_pulses(tag_to_pulses)
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
