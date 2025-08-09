#!/usr/bin/env python3
import os, re, sys
from collections import defaultdict

PULSES_DIR = "phi-mesh/pulse"
OUT_PATH = "meta/tag_index.yml"

def norm_tag(t: str) -> str:
    import re
    t = (t or "").strip()
    if not t: return ""
    t = re.sub(r"\s+", " ", t)
    t = t.replace("-", "_")
    t = re.sub(r"__+", "_", t).strip(" _")
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
    if re.fullmatch(r"[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*", t):
        parts = t.split("_")
        parts = [p if p.isupper() or p.istitle() else (p[0:1].upper()+p[1:]) for p in parts]
        t = "_".join(parts)
    return t

def gather():
    import yaml, glob
    tag_links = defaultdict(lambda: {"links": set(), "pulses": set()})

    for path in glob.glob(os.path.join(PULSES_DIR, "*.yml")) + glob.glob(os.path.join(PULSES_DIR, "*.yaml")):
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        tags = [norm_tag(t) for t in (doc.get("tags") or []) if t]
        # add tag → pulse
        pulse_ref = f"pulse/{os.path.basename(path)}"
        for t in tags:
            if not t: continue
            tag_links[t]["pulses"].add(pulse_ref)
        # tag co-occurrence links (undirected)
        for i in range(len(tags)):
            for j in range(i+1, len(tags)):
                a, b = tags[i], tags[j]
                if not a or not b or a == b: continue
                tag_links[a]["links"].add(b)
                tag_links[b]["links"].add(a)

    # convert sets → sorted lists, plain dict (no OrderedDict)
    clean = {}
    for t, blob in tag_links.items():
        if not t: continue
        links = sorted(x for x in blob["links"] if x and x != t)
        pulses = sorted(blob["pulses"])
        clean[t] = {"links": links, "pulses": pulses}

    # push to YAML safely
    return clean

def main():
    idx = gather()
    import yaml
    # ensure plain dict; represent safely
    payload = {k: {"links": v["links"], "pulses": v["pulses"]} for k, v in sorted(idx.items())}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=True)
    print(f"tag-index: wrote {len(payload)} tags")

if __name__ == "__main__":
    sys.exit(main())
