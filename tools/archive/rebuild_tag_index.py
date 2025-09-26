#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild meta/tag_index.yml from pulses (alias-aware, archive-safe).

- Scans pulse/**/*.yml, skipping pulse/archive/ and pulse/telemetry/.
- Loads meta/aliases.yml (if present) and canonicalizes tags.
- Aggregates per-tag:
    papers:   unique by URL
    podcasts: unique by URL
    pulses:   stable pulse IDs (filename stem)
    summary:  left blank (can be curated later)
- Sorts tags and lists for stable diffs.

Writes meta/tag_index.yml with the structure:
  tags:
    <CanonicalTag>:
      papers:   - {url: ...}  (title kept if present)
      podcasts: - {url: ...}
      pulses:   - <pulse_id>
      summary:  ""

This is intentionally minimal and safe for CI runners.
"""

from __future__ import annotations
import os, re, glob
from pathlib import Path
from typing import Any, Dict, List
import yaml

ROOT = Path(__file__).resolve().parents[1]
PULSE_GLOB = str(ROOT / "pulse" / "**" / "*.yml")
ALIAS_PATH = ROOT / "meta" / "aliases.yml"
OUT_PATH   = ROOT / "meta" / "tag_index.yml"

SKIP_DIRS = ("/pulse/archive/", "/pulse/telemetry/")

def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARN: failed to parse YAML: {path}: {e}")
        return {}

def _norm_key(s: str) -> str:
    # normalized lookup key (case/space/hyphen insensitive)
    return re.sub(r"[\s_\-]+", "_", (s or "").strip()).casefold()

def _build_alias_index(spec: Dict[str, List[str]]) -> Dict[str, str]:
    """
    spec is the 'aliases:' mapping from meta/aliases.yml.
    Returns dict mapping every alias (and its normalized key) to its canonical.
    """
    idx: Dict[str, str] = {}
    for canonical, aliases in (spec or {}).items():
        if not canonical:
            continue
        c = str(canonical)
        idx[c] = c
        idx[_norm_key(c)] = c
        for a in (aliases or []):
            if not a:
                continue
            a = str(a)
            idx[a] = c
            idx[_norm_key(a)] = c
    return idx

def _canon(tag: str, alias_idx: Dict[str, str]) -> str:
    if not isinstance(tag, str):
        return tag
    if tag in alias_idx:
        return alias_idx[tag]
    return alias_idx.get(_norm_key(tag), tag)

def _is_skipped(path: Path) -> bool:
    p = path.as_posix()
    return any(s in p for s in SKIP_DIRS)

def _norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    # unify DOI domain
    u = re.sub(r"^https?://(dx\.)?doi\.org/", "https://doi.org/", u, flags=re.I)
    return u

def _collect_items(raw) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not raw:
        return out
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, str):
                url = _norm_url(x)
                if url:
                    out.append({"url": url})
            elif isinstance(x, dict):
                url = _norm_url(str(x.get("url") or ""))
                ttl = x.get("title")
                if url:
                    item = {"url": url}
                    if ttl:
                        item["title"] = str(ttl)
                    out.append(item)
    return out

def main():
    aliases_doc = _load_yaml(ALIAS_PATH)
    alias_spec = (aliases_doc or {}).get("aliases") or {}
    alias_idx = _build_alias_index(alias_spec)

    tag_map: Dict[str, Dict[str, Any]] = {}

    files = sorted(glob.glob(PULSE_GLOB, recursive=True))
    for fp in files:
        p = Path(fp)
        if _is_skipped(p) or not p.suffix.lower().endswith("yml"):
            continue
        data = _load_yaml(p)
        if not isinstance(data, dict):
            continue

        # tags
        tags = data.get("tags") or data.get("Tags") or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [t for t in (tags or []) if isinstance(t, str) and t.strip()]
        if not tags:
            continue

        tags = [_canon(t, alias_idx) for t in tags]

        # resources
        papers   = _collect_items(data.get("papers"))
        podcasts = _collect_items(data.get("podcasts"))

        # pulse ID = filename stem (stable)
        pulse_id = p.stem

        # aggregate per tag
        for t in tags:
            slot = tag_map.setdefault(t, {"papers": [], "podcasts": [], "pulses": [], "summary": ""})

            # de-dupe by URL while preserving first title seen
            def _merge(lst: List[Dict[str,str]], incoming: List[Dict[str,str]]):
                seen = {it.get("url"): i for i, it in enumerate(lst) if it.get("url")}
                for it in incoming:
                    u = it.get("url")
                    if not u:
                        continue
                    if u in seen:
                        # keep existing; fill title if missing
                        i = seen[u]
                        if it.get("title") and not lst[i].get("title"):
                            lst[i]["title"] = it["title"]
                    else:
                        lst.append({"url": u, **({"title": it["title"]} if it.get("title") else {})})

            _merge(slot["papers"], papers)
            _merge(slot["podcasts"], podcasts)

            if pulse_id not in slot["pulses"]:
                slot["pulses"].append(pulse_id)

    # sort for stability
    sorted_tags = dict(sorted(tag_map.items(), key=lambda kv: kv[0].casefold()))
    for t, info in sorted_tags.items():
        info["papers"]   = sorted(info["papers"],   key=lambda d: d.get("url",""))
        info["podcasts"] = sorted(info["podcasts"], key=lambda d: d.get("url",""))
        info["pulses"]   = sorted(info["pulses"])

    out_doc = {"tags": sorted_tags}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(out_doc, f, sort_keys=False, allow_unicode=True)

    print(f"OK: rebuilt {OUT_PATH.relative_to(ROOT)} with {len(sorted_tags)} tags.")

if __name__ == "__main__":
    main()
