#!/usr/bin/env python3
"""
Rebuild meta/tag_index.yml from pulses.

- Scans pulse/**/*.yml (recursively), skipping pulse/archive and pulse/telemetry
- Applies aliases from meta/aliases.yml (exact + loose/diacritic-insensitive)
- For each tag, records:
    - pulses:   list of pulse stems where it appears
    - papers:   [{title?, url}] (URL-required; deduped by URL)
    - podcasts: [{title?, url}] (URL-required; deduped by URL)
    - summary:  first non-empty callout/summary encountered

This is a human-friendly curated index you can inspect/edit.
We still let the graph builder compute EDGES from a full scan for richness.
"""

from __future__ import annotations
import os, glob, re, unicodedata, yaml
from pathlib import Path
from typing import Dict, Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
ALIAS_PATH = ROOT / "meta" / "aliases.yml"
OUT_PATH   = ROOT / "meta" / "tag_index.yml"
PULSE_GLOB = str(ROOT / "pulse" / "**" / "*.yml")

# ---------- helpers ----------
def norm_str(s: str) -> str:
    if not isinstance(s, str): s = str(s or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[\s_\-]+", " ", s).strip().casefold()
    return s

def load_yaml(fp: Path) -> Any:
    try:
        with fp.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: Failed to parse YAML {fp}: {e}")
        return {}

def load_alias_map(path: Path) -> Dict[str, list]:
    if not path.exists(): return {}
    data = load_yaml(path)
    return data.get("aliases") or {}

def build_alias_index(alias_spec: dict) -> Dict[str, str]:
    """Return mapping from alias/loose key → canonical tag."""
    idx: Dict[str,str] = {}
    if not isinstance(alias_spec, dict): return idx
    for canonical, aliases in alias_spec.items():
        if not isinstance(aliases, Iterable) or isinstance(aliases, (str, bytes)):
            continue
        # self
        idx[canonical] = canonical
        idx[norm_str(canonical)] = canonical
        # aliases
        for a in aliases:
            if not a: continue
            idx[a] = canonical
            idx[norm_str(a)] = canonical
    return idx

def map_tag(tag: str, alias_idx: Dict[str,str]) -> str:
    if not isinstance(tag, str): return tag
    if tag in alias_idx: return alias_idx[tag]
    key = norm_str(tag)
    return alias_idx.get(key, tag)

def to_item_list(raw) -> list[dict]:
    """Normalize a papers/podcasts array to [{title?, url}] (drop entries w/o url)."""
    out = []
    if not raw: return out
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, str):
                # strings are URLs if they look like one
                if re.match(r"^https?://|^doi\.org/", x):
                    out.append({"url": x})
            elif isinstance(x, dict):
                url = str(x.get("url") or "").strip()
                ttl = x.get("title")
                if url:
                    item = {"url": url}
                    if ttl: item["title"] = str(ttl)
                    out.append(item)
    return out

# ---------- build index ----------
def main():
    alias_spec = load_alias_map(ALIAS_PATH)
    alias_idx  = build_alias_index(alias_spec)

    tag_index: Dict[str, Dict[str, Any]] = {}  # canonical tag → {pulses, papers, podcasts, summary}

    for fp_str in sorted(glob.glob(PULSE_GLOB, recursive=True)):
        # skip folders we never index
        if "/pulse/archive/" in fp_str or "/pulse/telemetry/" in fp_str:
            continue
        fp = Path(fp_str)
        data = load_yaml(fp)
        if not isinstance(data, dict): continue

        # tags
        tags = data.get("tags") or data.get("Tags") or []
        if isinstance(tags, str): tags = [tags]
        if not isinstance(tags, list) or not tags: continue

        tags = [map_tag(str(t).strip(), alias_idx) for t in tags if str(t).strip()]
        if not tags: continue

        # pulse key + metadata
        pulse_stem = fp.stem  # nice short id
        callout = (data.get("callout") or data.get("summary") or "").strip()

        # resources (URL-only; dedupe by URL)
        papers   = to_item_list(data.get("papers"))
        podcasts = to_item_list(data.get("podcasts"))

        for t in tags:
            entry = tag_index.setdefault(t, {"pulses": [], "papers": [], "podcasts": [], "summary": ""})

            if pulse_stem not in entry["pulses"]:
                entry["pulses"].append(pulse_stem)

            if callout and not entry["summary"]:
                entry["summary"] = callout

            # dedupe by URL
            seenP = {it["url"] for it in entry["papers"] if "url" in it}
            for it in papers:
                u = it.get("url")
                if u and u not in seenP:
                    entry["papers"].append(it); seenP.add(u)

            seenC = {it["url"] for it in entry["podcasts"] if "url" in it}
            for it in podcasts:
                u = it.get("url")
                if u and u not in seenC:
                    entry["podcasts"].append(it); seenC.add(u)

    out = {"tags": tag_index}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=True, allow_unicode=True)

    print(f"OK: wrote {OUT_PATH} with {len(tag_index)} tags")

if __name__ == "__main__":
    main()
