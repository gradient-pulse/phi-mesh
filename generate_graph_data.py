#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate docs/data.js (alias-aware) for the Tag Browser.

- If meta/tag_index.yml exists and has content, use it as the source of truth.
- Otherwise, scan pulse/**/*.yml to build tag→pulses and resources.
- Optionally apply alias map from meta/aliases.yml (or any provided path).
- Writes a single JS file that assigns to window.tagData for non-module pages.

CLI:
  python generate_graph_data.py \
      --tag-index meta/tag_index.yml \
      --alias-map meta/aliases.yml \
      --pulse-glob "pulse/**/*.yml" \
      --out-js docs/data.js
"""
from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path
from glob import glob
from typing import Dict, List, Tuple, Any, Set

try:
    import yaml
except Exception as e:
    print(f"ERROR: pyyaml not available: {e}", file=sys.stderr)
    sys.exit(2)


# ---------------------------- IO helpers --------------------------------- #

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(read_text(path))
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"WARN: Failed to parse YAML {path}: {e}", file=sys.stderr)
        return None


# ---------------------------- Aliases ------------------------------------ #

def load_alias_map(alias_path: Path | None) -> Dict[str, str]:
    """
    alias map format (YAML):
      canonical_tag:
        - alias_one
        - alias-two
      Another Canonical:
        - another_alias

    Returns dict mapping normalized_alias -> canonical_tag.
    """
    if not alias_path or not alias_path.exists():
        return {}

    raw = load_yaml(alias_path)
    if not isinstance(raw, dict):
        return {}

    norm = lambda s: str(s).strip()

    mapping: Dict[str, str] = {}
    for canonical, aliases in raw.items():
        can = norm(canonical)
        if not isinstance(aliases, list):
            continue
        for a in aliases:
            alias = norm(a)
            if alias and alias not in mapping:
                mapping[alias] = can
    return mapping


def canonicalize(tag: str, alias_map: Dict[str, str]) -> str:
    if not tag:
        return tag
    t = tag.strip()
    # direct match
    if t in alias_map:
        return alias_map[t]
    # case-insensitive match
    lower_map = _LOWER_ALIAS_CACHE.get(id(alias_map))
    if lower_map is None:
        lm = {k.lower(): v for k, v in alias_map.items()}
        _LOWER_ALIAS_CACHE[id(alias_map)] = lm
        lower_map = lm
    return lower_map.get(t.lower(), t)


_LOWER_ALIAS_CACHE: Dict[int, Dict[str, str]] = {}


# ----------------------- Tag index loading -------------------------------- #

def load_tag_index(path: Path | None) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    data = load_yaml(path)
    if not isinstance(data, dict):
        return {}
    # Support both “flat” and “rich” formats used in the repo history.
    # We normalize into: { tag: { "links": [...], "pulses": [...], "summary": "" } }
    # If already in that shape, keep as-is.
    normalized: Dict[str, Any] = {}

    # new structured shape?
    # e.g. { AI_alignment: {links:[...], pulses:[...], summary:""} }
    all_values_are_dicts = all(isinstance(v, dict) for v in data.values()) if data else False
    if all_values_are_dicts:
        for tag, entry in data.items():
            e = dict(entry) if isinstance(entry, dict) else {}
            links = e.get("links") if isinstance(e.get("links"), list) else []
            pulses = e.get("pulses") if isinstance(e.get("pulses"), list) else []
            summary = e.get("summary") if isinstance(e.get("summary"), str) else ""
            normalized[tag] = {"links": links, "pulses": pulses, "summary": summary}
        return normalized

    # older flat shape? e.g. { AI_alignment: ["pulse/a.yml", "pulse/b.yml"], ... }
    all_values_are_lists = all(isinstance(v, list) for v in data.values()) if data else False
    if all_values_are_lists:
        for tag, files in data.items():
            pulses = []
            for f in files:
                # allow either full path strings or filenames
                pulses.append(str(f))
            normalized[tag] = {"links": [], "pulses": pulses, "summary": ""}
        return normalized

    # unknown / empty
    return {}


# ----------------------- Pulse directory scan ----------------------------- #

def merge_tag_sets(dst: Dict[str, Set[str]], tag: str, pulse_rel: str) -> None:
    if tag not in dst:
        dst[tag] = set()
    dst[tag].add(pulse_rel)


def coerce_tags_from_yaml(y: Any) -> List[str]:
    """
    Accepts a variety of shapes:
      - dict with 'tags': list[str]
      - list of dicts where each may contain 'tags'
      - list[str] directly
    Returns a flat list[str].
    """
    out: List[str] = []
    if y is None:
        return out
    if isinstance(y, dict):
        t = y.get("tags") or y.get("Tags") or []
        if isinstance(t, list):
            out.extend([str(x) for x in t])
        return out
    if isinstance(y, list):
        # could be a plain list of tags, or a list of blocks that include tags
        if all(isinstance(x, (str, int, float)) for x in y):
            return [str(x) for x in y]
        for item in y:
            if isinstance(item, dict):
                t = item.get("tags") or item.get("Tags") or []
                if isinstance(t, list):
                    out.extend([str(x) for x in t])
        return out
    return out


def extract_resources(y: Any) -> Dict[str, List[str]]:
    res = {"papers": [], "podcasts": [], "links": []}
    if not isinstance(y, dict):
        return res
    for key in ("papers", "podcasts", "links"):
        v = y.get(key)
        if isinstance(v, list):
            res[key] = [str(x) for x in v]
    return res


def scan_pulses_for_tags(pattern: str) -> Tuple[Dict[str, List[str]],
                                                Dict[str, List[str]],
                                                Dict[str, Dict[str, List[str]]]]:
    """
    Returns:
      tag_to_pulses: tag -> [rel pulse paths]
      pulse_to_tags: pulse -> [tags]
      pulse_resources: pulse -> {papers:[], podcasts:[], links:[]}
    """
    tag_to_sets: Dict[str, Set[str]] = {}
    pulse_to_tags: Dict[str, List[str]] = {}
    pulse_resources: Dict[str, Dict[str, List[str]]] = {}

    root = Path(".").resolve()
    paths = sorted(Path(p).resolve() for p in glob(pattern, recursive=True))
    for p in paths:
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        y = load_yaml(p)
        if y is None:
            continue
        tags = coerce_tags_from_yaml(y)
        if not tags and isinstance(y, dict):
            # Sometimes tags are under 'tags:' but empty; still record resources.
            pass
        pulse_resources[rel] = extract_resources(y)

        unique_tags = []
        seen = set()
        for t in tags:
            if not t:
                continue
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)

        for t in unique_tags:
            merge_tag_sets(tag_to_sets, t, rel)
        pulse_to_tags[rel] = unique_tags

    tag_to_list = {k: sorted(list(v)) for k, v in tag_to_sets.items()}
    return tag_to_list, pulse_to_tags, pulse_resources


# ----------------------- Build browser payload ---------------------------- #

def apply_aliases_to_tag_index(tag_index: Dict[str, Any],
                               alias_map: Dict[str, str]) -> Dict[str, Any]:
    if not alias_map or not tag_index:
        return tag_index

    merged: Dict[str, Any] = {}
    for tag, entry in tag_index.items():
        canon = canonicalize(tag, alias_map)
        # merge
        dst = merged.setdefault(canon, {"links": [], "pulses": [], "summary": ""})
        # unify lists
        links = entry.get("links", [])
        pulses = entry.get("pulses", [])
        if isinstance(links, list):
            dst["links"].extend(links)
        if isinstance(pulses, list):
            dst["pulses"].extend(pulses)
        # keep first non-empty summary
        if not dst.get("summary") and isinstance(entry.get("summary"), str):
            dst["summary"] = entry["summary"]

    # de-dup + sort
    for v in merged.values():
        v["links"] = sorted(set(v.get("links", [])))
        v["pulses"] = sorted(set(v.get("pulses", [])))
    return merged


def apply_aliases_to_scan(tag_to_pulses: Dict[str, List[str]],
                          alias_map: Dict[str, str]) -> Dict[str, List[str]]:
    if not alias_map:
        return tag_to_pulses
    out: Dict[str, Set[str]] = {}
    for tag, plist in tag_to_pulses.items():
        canon = canonicalize(tag, alias_map)
        out.setdefault(canon, set()).update(plist)
    return {k: sorted(list(v)) for k, v in out.items()}


def build_payload_from_index(tag_index: Dict[str, Any]) -> Dict[str, Any]:
    tags = []
    for tag, entry in sorted(tag_index.items(), key=lambda kv: kv[0].lower()):
        pulses = entry.get("pulses", [])
        links = entry.get("links", [])
        summary = entry.get("summary", "")
        tags.append({
            "id": tag,
            "count": len(pulses),
            "pulses": pulses,
            "links": links,
            "summary": summary or ""
        })
    return {"tags": tags}


def build_payload_from_scan(tag_to_pulses: Dict[str, List[str]],
                            pulse_resources: Dict[str, Dict[str, List[str]]]
                            ) -> Dict[str, Any]:
    tags = []
    for tag, pulses in sorted(tag_to_pulses.items(), key=lambda kv: kv[0].lower()):
        # optional: aggregate resources per tag (simple union)
        agg_links: Set[str] = set()
        for p in pulses:
            r = pulse_resources.get(p, {})
            for key in ("papers", "podcasts", "links"):
                for u in r.get(key, []):
                    agg_links.add(u)
        tags.append({
            "id": tag,
            "count": len(pulses),
            "pulses": pulses,
            "links": sorted(agg_links),
            "summary": ""
        })
    return {"tags": tags}


# ---------------------------- Writer -------------------------------------- #

def write_js(out_js: Path, payload: Dict[str, Any]) -> None:
    # IMPORTANT: expose on window so non-module pages can access it.
    js = "window.tagData=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";"
    write_text(out_js, js)
    size = out_js.stat().st_size
    print(f"OK: wrote {out_js} ({size} bytes)")


# ---------------------------- Main ---------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="Generate alias-aware graph payload (docs/data.js).")
    ap.add_argument("--tag-index", default="meta/tag_index.yml", help="Path to tag index YAML.")
    ap.add_argument("--alias-map", default=None, help="Path to aliases YAML (optional).")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml", help="Glob to scan pulses when index is empty.")
    ap.add_argument("--out-js", default="docs/data.js", help="Output JS file path.")
    args = ap.parse_args()

    tag_index_path = Path(args.tag_index)
    alias_path = Path(args.alias_map) if args.alias_map else None
    out_js = Path(args.out_js)

    alias_map = load_alias_map(alias_path)
    if alias_map:
        print(f"INFO: loaded {len(alias_map)} aliases from {alias_path}")

    tag_index = load_tag_index(tag_index_path)

    if tag_index:
        print("INFO: using tag_index.yml as source of truth")
        if alias_map:
            tag_index = apply_aliases_to_tag_index(tag_index, alias_map)
        payload = build_payload_from_index(tag_index)
    else:
        print("INFO: tag_index.yml empty or unsupported → scanning pulses …")
        tag_to_pulses, pulse_to_tags, pulse_resources = scan_pulses_for_tags(args.pulse_glob)
        if alias_map:
            tag_to_pulses = apply_aliases_to_scan(tag_to_pulses, alias_map)
        if not tag_to_pulses:
            print("ERROR: No tags parsed from pulses. Aborting.", file=sys.stderr)
            sys.exit(3)
        payload = build_payload_from_scan(tag_to_pulses, pulse_resources)

    # Write JS
    write_js(out_js, payload)

    # Sanity echo (kept short)
    try:
        print(f"INFO: tag count = {len(payload.get('tags', []))}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
