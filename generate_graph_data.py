#!/usr/bin/env python3
import json, os, re, sys, hashlib
from collections import defaultdict

# -------- Config
PULSES_DIR = "phi-mesh/pulse"
TAG_INDEX_PATH = "meta/tag_index.yml"
DATA_JS = "docs/data.js"
GRAPH_DATA_JS = "docs/graph_data.js"
LINK_INDEX_JS = "docs/link_index.js"
SCHEMA_VERSION = "2"

# -------- Utilities
def load_yaml(path):
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def dump_js(path, varname, payload):
    text = f"/* schema:{SCHEMA_VERSION} */\nconst {varname} = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    # write only if changed
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read() == text:
                return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True

# Canonicalize tags: trim, collapse spaces/underscores/dashes, title-case certain patterns
def norm_tag(tag: str) -> str:
    t = (tag or "").strip()
    if not t: return ""
    t = re.sub(r"\s+", " ", t)
    t = t.replace("-", "_")
    t = re.sub(r"__+", "_", t)
    t = t.strip(" _")
    # Known canonical cases
    aliases = {
        "big quiet":"Big_Quiet", "big_quiet":"Big_Quiet",
        "big bang":"Big_Bang", "big_bang":"Big_Bang",
        "ai architectures":"AI_architectures", "ai_architectures":"AI_architectures",
        "ai architecture":"AI_architecture", "ai_architecture":"AI_architecture",
        "narrative tick":"Narrative_Tick", "narrative_tick":"Narrative_Tick",
        "phi monitor":"Phi-Monitor", "phi-monitor":"Phi-Monitor",
        "deepseek":"DeepSeek",
        "gpt5":"GPT5", "gpt4o":"GPT4o",
        "rφ":"RΦ", "rφ_":"RΦ",
    }
    key = t.lower()
    if key in aliases: return aliases[key]
    # Title-ish for some categories
    if re.fullmatch(r"[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*", t):
        # Keep internal underscores as word separators, title case words that start lower
        parts = t.split("_")
        parts = [p if p.isupper() or p.istitle() else (p[0:1].upper()+p[1:]) for p in parts]
        t = "_".join(parts)
    return t

def uniq(seq):
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

# -------- Build from tag_index.yml
def build():
    import yaml
    idx = load_yaml(TAG_INDEX_PATH) or {}
    # normalize into {tag: {links:[], pulses:[]}}
    tags = {}
    for raw_tag, blob in (idx or {}).items():
        tag = norm_tag(raw_tag)
        links = [norm_tag(x) for x in (blob.get("links") or []) if x]
        pulses = [p for p in (blob.get("pulses") or []) if p]
        tags[tag] = {
            "links": uniq([x for x in links if x and x != tag]),
            "pulses": uniq(pulses),
        }

    # create graph nodes/edges
    nodes = [{"id": t, "degree": 0} for t in sorted(tags.keys())]
    id_to_idx = {n["id"]: i for i, n in enumerate(nodes)}
    edges = []
    for t, blob in tags.items():
        for u in blob["links"]:
            if u == t: continue
            if u not in id_to_idx: continue
            i, j = id_to_idx[t], id_to_idx[u]
            a, b = min(i, j), max(i, j)
            edges.append((a, b))
    # dedupe edges
    edges = sorted(set(edges))
    links = [{"source": a, "target": b} for (a, b) in edges]

    # degree
    deg = defaultdict(int)
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
    for i, n in enumerate(nodes):
        n["degree"] = deg[i]

    # export payloads
    data_payload = {
        "schema": SCHEMA_VERSION,
        "tags": tags,  # normalized
    }
    graph_payload = {
        "schema": SCHEMA_VERSION,
        "nodes": nodes,
        "links": links,
        "meta": {
            "nodeCount": len(nodes),
            "linkCount": len(links),
        }
    }
    # link index for sidebar
    link_index = {}
    for t, blob in tags.items():
        link_index[t] = {
            "links": blob["links"],
            "pulses": blob["pulses"],
        }

    changed = False
    changed |= dump_js(DATA_JS, "DATA_INDEX", data_payload)
    changed |= dump_js(GRAPH_DATA_JS, "GRAPH_DATA", graph_payload)
    changed |= dump_js(LINK_INDEX_JS, "LINK_INDEX", link_index)
    return changed

if __name__ == "__main__":
    changed = build()
    print("graph-data: wrote files" if changed else "graph-data: no changes")
