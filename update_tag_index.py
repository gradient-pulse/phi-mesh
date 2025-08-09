#!/usr/bin/env python3
import os, re, sys
from collections import defaultdict

PULSES_DIR = "phi-mesh/pulse"
OUT_PATH = "meta/tag_index.yml"
ALIASES_PATH = "meta/aliases.yml"

def load_aliases():
    import yaml
    if not os.path.exists(ALIASES_PATH):
        return {}
    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    # build lookup: alias_lower -> canonical
    lut = {}
    for canonical, variants in raw.items():
        canon = canonical.strip()
        if not canon: continue
        lut[canon.lower()] = canon  # allow canonical itself to match
        for v in (variants or []):
            key = (v or "").strip().lower()
            if not key: continue
            if key in lut and lut[key] != canon:
                # soft conflict warning; last write wins but print notice
                print(f"[aliases] warning: alias '{v}' claimed by '{lut[key]}' and '{canon}'. Using '{canon}'.")
            lut[key] = canon
    return lut

_ALIAS_LUT = None

def norm_tag(t: str) -> str:
    global _ALIAS_LUT
    t = (t or "").strip()
    if not t: return ""
    # basic cleanup first
    t = re.sub(r"\s+", " ", t)
    t = t.replace("-", "_")
    t = re.sub(r"__+", "_", t).strip(" _")

    # alias map (lazy-load once)
    if _ALIAS_LUT is None:
        _ALIAS_LUT = load_aliases()

    # 1) exact alias match (case-insensitive)
    key = t.lower()
    if key in _ALIAS_LUT:
        return _ALIAS_LUT[key]

    # 2) default auto-normalization (title-ize underscore words)
    if re.fullmatch(r"[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*", t):
        parts = t.split("_")
        parts = [p if p.isupper() or p.istitle() else (p[:1].upper()+p[1:]) for p in parts]
        t = "_".join(parts)
    return t

def gather():
    import yaml, glob
    tag_links = defaultdict(lambda: {"links": set(), "pulses": set()})

    files = glob.glob(os.path.join(PULSES_DIR, "*.yml")) + glob.glob(os.path.join(PULSES_DIR, "*.yaml"))
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        tags = [norm_tag(x) for x in (doc.get("tags") or []) if x]
        pulse_ref = f"pulse/{os.path.basename(path)}"
        for t in tags:
            if not t: continue
            tag_links[t]["pulses"].add(pulse_ref)
        for i in range(len(tags)):
            for j in range(i+1, len(tags)):
                a, b = tags[i], tags[j]
                if not a or not b or a == b: continue
                tag_links[a]["links"].add(b)
                tag_links[b]["links"].add(a)

    clean = {}
    for t, blob in tag_links.items():
        if not t: continue
        links = sorted(x for x in blob["links"] if x and x != t)
        pulses = sorted(blob["pulses"])
        clean[t] = {"links": links, "pulses": pulses}
    return clean

def main():
    idx = gather()
    import yaml
    payload = {k: {"links": v["links"], "pulses": v["pulses"]} for k, v in sorted(idx.items())}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=True)
    print(f"tag-index: wrote {len(payload)} tags")

if __name__ == "__main__":
    sys.exit(main())
