#!/usr/bin/env python3
"""
Regenerate meta/tag_index.yml from pulse/*.yml files.

Features
- Robust YAML read with error guards.
- Tag normalization: trim, collapse whitespace, replace spaces with underscores.
- Optional canonical mapping:
    * meta/tag_canonical.yml (preferred if present)
    * or a "canonical_tags:" section inside an existing meta/tag_index.yml
- Bi-directional, de-duplicated links built from co-occurring tags per pulse.
- Deterministic, sorted output for clean diffs.

Output schema (meta/tag_index.yml):
  <tag>:
    links: [<related tag>...]
    pulses: [<relative pulse path>...]

You can safely extend later to include papers/podcasts if you want.
"""

import sys
import re
import json
from pathlib import Path
from collections import defaultdict, OrderedDict
from typing import Dict, List, Set, Tuple

try:
    import yaml
except Exception as e:
    print(f"[update_tag_index] ERROR: pyyaml not installed: {e}", file=sys.stderr)
    sys.exit(1)

# --- Config -------------------------------------------------------------------

PULSE_DIRS = [
    Path("pulse"),                  # primary
    Path("phi-mesh/pulse"),         # alt
]

TAG_INDEX_PATH = Path("meta/tag_index.yml")
CANONICAL_PATH = Path("meta/tag_canonical.yml")  # optional

# If True, we preserve case as written after canonicalization;
# keys in the file will appear exactly as the canonical key (case-sensitive).
PRESERVE_CASE = True

# --- Helpers ------------------------------------------------------------------

_ws_re = re.compile(r"\s+")

def norm_tag(tag: str) -> str:
    """Basic normalization: strip, collapse whitespace, use underscores."""
    if not isinstance(tag, str):
        return ""
    t = tag.strip()
    t = _ws_re.sub(" ", t)  # collapse internal spaces
    t = t.replace(" ", "_")
    # Do NOT lower() by default to keep display nicer; rely on canonical map for true merging.
    return t

def load_yaml(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[update_tag_index] WARN: failed to read {path}: {e}", file=sys.stderr)
        return None

def find_pulse_files() -> List[Path]:
    out: List[Path] = []
    for base in PULSE_DIRS:
        if base.exists():
            out.extend(sorted(base.glob("*.yml")))
            out.extend(sorted(base.glob("*.yaml")))
    return out

def build_canonical_map() -> Dict[str, str]:
    """
    Canonical map lets you merge variants, e.g.:
      Contextual_Filter: [contextual-filter, ContextualFilter, Contextual_Filter]
      Gradient_Syntax:   [gradient_syntax, GradientSyntax, gradient-syntax]
    Map format accepted from either:
      - meta/tag_canonical.yml
      - meta/tag_index.yml under key: canonical_tags
    """
    mapping: Dict[str, str] = {}

    # 1) A dedicated canonical file (preferred, simple format)
    #    YAML schema: { CanonicalKey: [alias1, alias2, ...], ... }
    data = load_yaml(CANONICAL_PATH)
    if isinstance(data, dict):
        for canon, aliases in data.items():
            ckey = norm_tag(canon)
            if not ckey:
                continue
            # Map canonical to itself
            mapping[ckey] = ckey
            if isinstance(aliases, list):
                for a in aliases:
                    akey = norm_tag(str(a))
                    if akey:
                        mapping[akey] = ckey

    # 2) Fallback: try to read canonical_tags from existing tag_index.yml
    idx = load_yaml(TAG_INDEX_PATH)
    if isinstance(idx, dict) and "canonical_tags" in idx:
        cats = idx["canonical_tags"]
        if isinstance(cats, dict):
            for canon, aliases in cats.items():
                ckey = norm_tag(canon)
                if not ckey:
                    continue
                mapping.setdefault(ckey, ckey)
                if isinstance(aliases, list):
                    for a in aliases:
                        akey = norm_tag(str(a))
                        if akey:
                            mapping[akey] = ckey

    return mapping

def canonicalize(tag: str, cmap: Dict[str, str]) -> str:
    t = norm_tag(tag)
    if not t:
        return ""
    return cmap.get(t, t)

# --- Core ---------------------------------------------------------------------

def main() -> int:
    pulses = find_pulse_files()
    if not pulses:
        print("[update_tag_index] WARN: no pulse/*.yml files found", file=sys.stderr)

    canonical_map = build_canonical_map()

    # Build: tag -> { 'links': set(), 'pulses': set() }
    links: Dict[str, Set[str]] = defaultdict(set)
    buckets: Dict[str, Set[str]] = defaultdict(set)  # tag -> set of pulse paths

    for p in pulses:
        data = load_yaml(p)
        if not isinstance(data, dict):
            continue

        raw_tags = data.get("tags", [])
        if not isinstance(raw_tags, list):
            continue

        # Canonicalize & normalize
        tags: List[str] = []
        for t in raw_tags:
            ct = canonicalize(str(t), canonical_map)
            if ct:
                tags.append(ct)

        # De-dupe within this pulse
        tags = sorted(set(tags))
        if not tags:
            continue

        # Register pulse file path (relative)
        rel = str(p.as_posix())

        # Build co-occurrence links for this pulse
        for i, a in enumerate(tags):
            buckets[a].add(rel)
            for j, b in enumerate(tags):
                if i == j:
                    continue
                links[a].add(b)
                links[b].add(a)  # ensure bi-directional

    # Convert to deterministic, sorted dict
    out: Dict[str, Dict[str, List[str]]] = OrderedDict()

    # Optional: include canonical_tags back into the file (handy for round-trips)
    canonical_tags_out: Dict[str, List[str]] = OrderedDict()
    # Only write this section if we actually had a dedicated canonical file
    if CANONICAL_PATH.exists():
        raw_can = load_yaml(CANONICAL_PATH) or {}
        if isinstance(raw_can, dict):
            for canon in sorted(raw_can.keys(), key=lambda s: s.lower()):
                ckey = canonicalize(canon, canonical_map)
                aliases = raw_can.get(canon) or []
                alias_norm = sorted({canonicalize(a, canonical_map) for a in aliases if canonicalize(a, canonical_map)})
                canonical_tags_out[ckey] = alias_norm

    # Harvest all tags we saw (union of buckets/links), sorted
    all_tags: Set[str] = set(buckets.keys()) | set(links.keys())
    for tag in sorted(all_tags, key=lambda s: s.lower()):
        tag_key = tag if PRESERVE_CASE else tag.lower()
        out[tag_key] = {
            "links": sorted(links.get(tag, set()), key=lambda s: s.lower()),
            "pulses": sorted(buckets.get(tag, set())),
        }

    # Final payload (optionally include canonical_tags)
    payload: Dict[str, object] = OrderedDict()
    if canonical_tags_out:
        payload["canonical_tags"] = canonical_tags_out
    payload.update(out)

    # Ensure meta/ exists
    TAG_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TAG_INDEX_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

    print(f"[update_tag_index] Wrote {TAG_INDEX_PATH} with {len(all_tags)} tags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
