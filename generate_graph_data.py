#!/usr/bin/env python3
"""
generate_graph_data.py — hardened + AUTO alias rollups

- Uses meta/tag_index.yml (+ optional meta/alias_map.yml)
- Always applies hard normalization (case/space/hyphen/underscore/Φ)
- NEW: auto-builds a *soft* alias map by grouping tags that only differ
       by case/underscore/hyphen/punct (and Φ↔Phi), then collapses them
       to a single winner (with most pulses; tie → lexicographic).
- Writes docs/graph_data.js and docs/data.js (unless --skip-sidebar)

CLI:
  python generate_graph_data.py \
    --tag-index meta/tag_index.yml \
    --alias-map meta/alias_map.yml \
    --out-js docs/graph_data.js \
    --sidebar-js docs/data.js
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict, OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    import yaml
except Exception:
    print("ERROR: pyyaml is required. pip install pyyaml", file=sys.stderr)
    raise

# ---------------------------
# Normalization / alias logic
# ---------------------------

_GREEK_PHI_VARIANTS = {
    "Φ": "Phi",
    "φ": "Phi",
    "RΦ": "R-phi",
    "Φ-harmonics": "Phi-harmonics",
}

_CANONICAL_FIXUPS = {
    "ai architecture": "ai_architecture",
    "ai architectures": "AI_architectures",
    "ai_architectures": "AI_architectures",
    "ai alignment": "AI_alignment",
    "contextual-filter": "contextual_filter",
    "contextualfilter": "contextual_filter",
    "contextual filter": "contextual_filter",
    "gradient syntax": "gradient_syntax",
    "gradient-syntax": "gradient_syntax",
    "navier stokes": "Navier_Stokes",
    "ns_solution": "NS_solution",
    "phi monitor": "Phi-monitor",
    "phi-monitor": "Phi-monitor",
    "rpg": "RPG",
    "rgp": "RGP",
    "pola": "PoLA",
    "nt": "NT",
    "nt_rhythm": "NT_rhythm",
    "narrative tick": "Narrative_Tick",
    "big bang": "Big_Bang",
    "big quiet": "Big_Quiet",
    "unity-disunity": "unity-disunity",
    "unity gradient": "unity_gradient",
    "triadic emergence": "triadic_emergence",
    "cinematic-drift": "cinematic_drift",
    "scene-drift": "scene_drift",
    "gradient-coherence": "gradient_coherence",
    "gradient-contrast": "gradient_contrast",
    "gradient-choreography": "gradient_choreography",
    "gradient cocoon theory": "gradient_cocoon_theory",
    # common typos seen before
    "contectual_filter": "contextual_filter",
    "gradient-driven_behavior": "gradient-driven_behavior",
}

_ws_regex = re.compile(r"\s+")
_nonword_regex = re.compile(r"[^A-Za-z0-9_\-]+")

def _basic_normalize(tag: str) -> str:
    s = tag.strip()
    if s in _GREEK_PHI_VARIANTS:
        s = _GREEK_PHI_VARIANTS[s]
    s = s.replace("Φ", "Phi").replace("φ", "Phi")
    s = _ws_regex.sub(" ", s)
    s = s.replace(" - ", "-").replace(" ", "_")
    s = _nonword_regex.sub("", s)
    return s

def _apply_canonical_fixups(norm: str) -> str:
    key = norm.lower()
    return _CANONICAL_FIXUPS.get(key, norm)

def _soft_key(tag: str) -> str:
    """Collapse differences in case/underscore/hyphen/punct for grouping."""
    n = _apply_canonical_fixups(_basic_normalize(tag))
    return n.lower().replace("_", "").replace("-", "")

def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)

def _load_alias_map(path: Optional[Path]) -> Dict[str, str]:
    alias_to_canonical: Dict[str, str] = {}
    if not path or not path.exists():
        return alias_to_canonical
    raw = _load_yaml(path) or {}
    if not isinstance(raw, dict):
        print(f"WARNING: alias map at {path} is not a dict; ignoring.", file=sys.stderr)
        return alias_to_canonical
    for k, v in raw.items():
        if isinstance(v, list):
            canonical = _apply_canonical_fixups(_basic_normalize(k))
            for alias in v:
                if not isinstance(alias, str):
                    continue
                alias_n = _apply_canonical_fixups(_basic_normalize(alias))
                alias_to_canonical[alias_n] = canonical
        elif isinstance(v, str):
            alias_n = _apply_canonical_fixups(_basic_normalize(k))
            canonical = _apply_canonical_fixups(_basic_normalize(v))
            alias_to_canonical[alias_n] = canonical
    return alias_to_canonical

def _canon(tag: str, alias_map: Dict[str, str]) -> str:
    n = _apply_canonical_fixups(_basic_normalize(tag))
    for _ in range(6):
        nxt = alias_map.get(n)
        if not nxt:
            return n
        n = nxt
    return n

# ---------------------------
# Graph extraction
# ---------------------------

def _extract_graph_from_tag_index(
    tag_index: Dict[str, Any],
    alias_map: Dict[str, str],
    keep_isolated_with_pulses: bool = True,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for raw_tag, payload in (tag_index or {}).items():
        if not isinstance(raw_tag, str) or not isinstance(payload, dict):
            continue
        ctag = _canon(raw_tag, alias_map)
        links = [str(x) for x in (payload.get("links", []) or []) if isinstance(x, (str, int, float))]
        pulses = [str(x) for x in (payload.get("pulses", []) or []) if isinstance(x, (str, int, float))]
        dst = merged.setdefault(ctag, {"links": set(), "pulses": set()})
        for l in links:
            dst["links"].add(_canon(l, alias_map))
        for p in pulses:
            dst["pulses"].add(p)

    # Remove self-loops
    for t, payload in merged.items():
        payload["links"].discard(t)

    # Degree
    degree: Dict[str, int] = defaultdict(int)
    for t, payload in merged.items():
        for l in payload["links"]:
            degree[t] += 1
            degree[l] += 1

    # Drop nodes with nothing at all
    merged = {
        t: payload
        for t, payload in merged.items()
        if len(payload["pulses"]) > 0 or degree.get(t, 0) > 0
    }

    # Sort nodes deterministically
    def node_key(item):
        t, payload = item
        return (-len(payload["pulses"]), -degree.get(t, 0), t.lower())
    sorted_items = sorted(merged.items(), key=node_key)

    nodes: List[Dict[str, Any]] = []
    tag_to_index: Dict[str, int] = {}
    for i, (t, payload) in enumerate(sorted_items):
        tag_to_index[t] = i
        nodes.append({
            "id": t,
            "degree": degree.get(t, 0),
            "pulseCount": len(payload["pulses"]),
            "weight": max(1, min(10, len(payload["pulses"]) + degree.get(t, 0) // 2)),
        })

    # Links once (undirected; canonical alphabetical pair)
    seen: Set[Tuple[str, str]] = set()
    for t, payload in sorted_items:
        for l in sorted(payload["links"]):
            if t not in tag_to_index or l not in tag_to_index or t == l:
                continue
            a, b = sorted([t, l])
            seen.add((a, b))
    links = [{"source": a, "target": b} for (a, b) in sorted(seen)]

    # Sidebar payload
    sidebar: Dict[str, Any] = OrderedDict()
    for t, payload in sorted_items:
        sidebar[t] = {"pulses": sorted(payload["pulses"]), "links": sorted(payload["links"])}

    return nodes, links, sidebar

# ---------------------------
# Auto aliasing (soft)
# ---------------------------

def _build_auto_soft_aliases(cooked: Dict[str, Dict[str, Any]], existing_aliases: Dict[str, str]) -> Dict[str, str]:
    """
    Group tags that only differ by case/_/-/punct/Φ, then map all but the chosen
    representative to that representative. Does NOT override explicit alias rules.
    """
    # Gather all candidate tags (top-level + links)
    seen_tags: Set[str] = set()
    pulse_count: Dict[str, int] = defaultdict(int)

    for k, v in cooked.items():
        nkey = _apply_canonical_fixups(_basic_normalize(k))
        seen_tags.add(nkey)
        pulse_count[nkey] += len([p for p in v.get("pulses", []) if isinstance(p, (str, int, float))])
        for l in v.get("links", []) or []:
            if isinstance(l, (str, int, float)):
                lnorm = _apply_canonical_fixups(_basic_normalize(str(l)))
                seen_tags.add(lnorm)

    groups: Dict[str, Set[str]] = defaultdict(set)
    for t in seen_tags:
        groups[_soft_key(t)].add(t)

    auto_map: Dict[str, str] = {}
    for _, variants in groups.items():
        if len(variants) <= 1:
            continue
        # choose winner: most pulses, tie → lexicographic
        winner = sorted(variants, key=lambda t: (-pulse_count.get(t, 0), t.lower()))[0]
        for other in variants:
            if other == winner:
                continue
            if other in existing_aliases:        # respect explicit config
                continue
            auto_map[other] = winner

    if auto_map:
        print(f"Auto-alias: collapsing {len(auto_map)} soft duplicates into {len(groups)} groups.", file=sys.stderr)
    return auto_map

# ---------------------------
# Main
# ---------------------------

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate D3 graph data for tag map.")
    ap.add_argument("--tag-index", type=Path, default=Path("meta/tag_index.yml"))
    ap.add_argument("--alias-map", type=Path, default=Path("meta/alias_map.yml"))
    ap.add_argument("--out-js", type=Path, default=Path("docs/graph_data.js"))
    ap.add_argument("--sidebar-js", type=Path, default=Path("docs/data.js"))
    ap.add_argument("--skip-sidebar", action="store_true", help="Do not write docs/data.js")
    ap.add_argument("--no-soft-alias", action="store_true", help="Disable automatic soft alias collapsing")
    args = ap.parse_args(argv)

    if not args.tag_index.exists():
        print(f"ERROR: {args.tag_index} does not exist.", file=sys.stderr)
        return 2

    raw = _load_yaml(args.tag_index)
    if not isinstance(raw, dict):
        print(f"ERROR: {args.tag_index} must be a YAML mapping.", file=sys.stderr)
        return 2

    # Coerce to expected structure (links/pulses lists)
    cooked: Dict[str, Dict[str, Any]] = {}
    for k, v in raw.items():
        if not isinstance(k, str) or not isinstance(v, dict):
            print(f"WARNING: skipping non-dict tag entry: {k!r}", file=sys.stderr)
            continue
        links = v.get("links", []) or []
        pulses = v.get("pulses", []) or []
        if not isinstance(links, list): links = list(links) if isinstance(links, (list, tuple, set)) else []
        if not isinstance(pulses, list): pulses = list(pulses) if isinstance(pulses, (list, tuple, set)) else []
        cooked[k] = {"links": links, "pulses": pulses}

    # Load explicit alias map (optional)
    alias_map = _load_alias_map(args.alias_map) if args.alias_map and args.alias_map.exists() else {}

    # Seed a few built-ins so zero-config is still sane
    if not alias_map:
        for k, v in {"Φ_harmonics": "Phi-harmonics", "Φ-harmonics": "Phi-harmonics", "RΦ": "R-phi"}.items():
            alias_map[_apply_canonical_fixups(_basic_normalize(k))] = _apply_canonical_fixups(_basic_normalize(v))

    # Build & apply *automatic* soft alias groups unless disabled
    if not args.no_soft_alias:
        auto_aliases = _build_auto_soft_aliases(cooked, alias_map)
        # don’t override explicit aliases
        for a, c in auto_aliases.items():
            alias_map.setdefault(a, c)

    nodes, links, sidebar = _extract_graph_from_tag_index(cooked, alias_map)

    graph_payload = {"nodes": nodes, "links": links}
    _save_text(args.out_js, "window.GRAPH_DATA = " + json.dumps(graph_payload, ensure_ascii=False) + ";\n")

    if not args.skip_sidebar:
        _save_text(args.sidebar_js, "window.TAG_SIDEBAR = " + json.dumps(sidebar, ensure_ascii=False) + ";\n")

    print(f"Wrote {args.out_js} ({len(nodes)} nodes, {len(links)} links)")
    if not args.skip_sidebar:
        print(f"Wrote {args.sidebar_js}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
