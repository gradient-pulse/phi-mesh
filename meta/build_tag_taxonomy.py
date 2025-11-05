from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict, List, Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
PULSE_DIR = ROOT / "pulse"

TAG_DESCRIPTIONS = META_DIR / "tag_descriptions.yml"
TAG_PHASE_OVERRIDES = META_DIR / "tag_phase_overrides.yml"
ALIASES_YAML = META_DIR / "aliases.yml"

OUT_YAML = META_DIR / "tag_taxonomy.yml"
OUT_MD = META_DIR / "tag_taxonomy.md"


PhaseKey = str  # "delta" | "gc" | "cf" | "unknown"


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_tag_descriptions() -> Dict[str, str]:
    """Canonical tag descriptions from meta/tag_descriptions.yml."""
    raw = _load_yaml(TAG_DESCRIPTIONS)
    if not isinstance(raw, dict):
        raise ValueError(f"{TAG_DESCRIPTIONS} must be a mapping of tag -> description")
    return {str(k): ("" if v is None else str(v)).strip() for k, v in raw.items()}


def load_aliases(known_tags) -> Dict[str, str]:
    """
    Load alias → canonical mapping from meta/aliases.yml.

    The file might be either:
      - { alias: canonical, ... }  or
      - { aliases: { alias: canonical, ... } }

    We try to map "weird" or legacy forms onto canonical tags in tag_descriptions.
    """
    raw = _load_yaml(ALIASES_YAML)
    if not raw or not isinstance(raw, dict):
        return {}

    mapping = raw.get("aliases", raw)
    if not isinstance(mapping, dict):
        return {}

    aliases: Dict[str, str] = {}
    for a, b in mapping.items():
        ak = str(a).strip()
        bv = str(b).strip()
        if not ak or not bv:
            continue

        # Prefer mapping from non-canonical → canonical when possible
        if bv in known_tags and ak not in known_tags:
            aliases[ak] = bv
        elif ak in known_tags and bv not in known_tags:
            aliases[bv] = ak
        else:
            # Fallback: try lower-case versions against canonical tags
            if bv.lower() in known_tags:
                aliases[ak] = bv.lower()
            elif ak.lower() in known_tags:
                aliases[ak] = ak.lower()
            else:
                # Last resort: just map as-is
                aliases[ak] = bv
    return aliases


def load_pulse_tag_counts(
    aliases: Dict[str, str],
    known_tags,
) -> Dict[str, List[str]]:
    """
    Scan pulse/*.yml (and pulse/*/*.yml) and build:

        canonical_tag -> [pulse_slug, ...]

    Canonicalization uses:
      1) aliases.yml  (if present)
      2) lower-casing to match tag_descriptions.yml keys
    """
    tag_to_pulses: Dict[str, List[str]] = {}

    if not PULSE_DIR.exists():
        return tag_to_pulses

    patterns = ["*.yml", "*/*.yml"]
    for pattern in patterns:
        for path in PULSE_DIR.glob(pattern):
            if path.name.startswith("README"):
                continue
            try:
                data = _load_yaml(path)
            except Exception:
                continue

            if not isinstance(data, dict):
                continue

            tags = data.get("tags") or []
            if not isinstance(tags, list):
                continue

            slug = path.stem
            for t in tags:
                raw_tag = str(t).strip()
                if not raw_tag:
                    continue

                # 1) alias resolution
                tag = aliases.get(raw_tag, raw_tag)

                # 2) case-normalization toward canonical tags
                tag_lower = tag.lower()
                if tag_lower in known_tags:
                    tag = tag_lower

                tag_to_pulses.setdefault(tag, []).append(slug)

    return tag_to_pulses


def load_phase_overrides() -> Dict[str, PhaseKey]:
    """
    Optional: explicit tag -> phase assignments from meta/tag_phase_overrides.yml

    Expected shape (all keys optional):

      delta:
        - tag_a
        - tag_b
      gc:
        - ...
      cf:
        - ...
      unknown:
        - ...

    You never *have* to fill this; it's just for finer control later.
    """
    overrides_raw = _load_yaml(TAG_PHASE_OVERRIDES)
    if not overrides_raw:
        return {}

    overrides: Dict[str, PhaseKey] = {}
    for phase_key in ("delta", "gc", "cf", "unknown"):
        tags = overrides_raw.get(phase_key) or []
        if not isinstance(tags, list):
            continue
        for tag in tags:
            tag_str = str(tag).strip()
            if tag_str:
                overrides[tag_str] = phase_key
    return overrides


def classify_tag(tag: str, overrides: Dict[str, PhaseKey]) -> PhaseKey:
    """
    Heuristic phase classifier with optional explicit overrides.

    You can always refine this later via tag_phase_overrides.yml;
    for now it just keeps Δ / GC / CF roughly in the right territory.
    """
    if tag in overrides:
        return overrides[tag]

    name = tag.lower()
    if any(k in name for k in ("genesis", "origin", "emergence", "delta", "seed")):
        return "delta"
    if any(
        k in name
        for k in (
            "resonance",
            "rhythm",
            "alignment",
            "gradient",
            "flux",
            "turbulence",
            "cycle2",
            "cycle_2",
            "propagation",
        )
    ):
        return "gc"
    if any(
        k in name
        for k in (
            "context",
            "filter",
            "closure",
            "taxonomy",
            "governance",
            "economy",
            "integration",
            "ud",
            "unity",
            "disunity",
        )
    ):
        return "cf"

    return "unknown"


def build_taxonomy():
    # 1) Canonical tag descriptions
    tag_descriptions = load_tag_descriptions()
    known_tags = set(tag_descriptions.keys())

    # 2) Aliases and pulse usage
    aliases = load_aliases(known_tags)
    tag_to_pulses = load_pulse_tag_counts(aliases, known_tags)

    # 3) Optional explicit phase overrides
    overrides = load_phase_overrides()

    phases: Dict[PhaseKey, Dict[str, Dict[str, object]]] = {
        "delta": {},
        "gc": {},
        "cf": {},
        "unknown": {},
    }

    # We want every described tag *plus* any used-only-in-pulses tag
    all_tags = set(tag_descriptions.keys()) | set(tag_to_pulses.keys())

    for tag in sorted(all_tags):
        phase = classify_tag(tag, overrides)
        description = tag_descriptions.get(tag, "")
        pulses = sorted(set(tag_to_pulses.get(tag, [])))
        phases[phase][tag] = {
            "description": description,
            "count": len(pulses),
            "pulses": pulses,
        }

    meta = {
        "generated_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "note": "Auto-generated taxonomy of tags grouped by RGPx phase.",
    }

    taxonomy = {
        "meta": meta,
        "phases": phases,
    }

    # YAML for scripts / HTML
    OUT_YAML.write_text(
        yaml.safe_dump(taxonomy, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    # Lightweight Markdown version
    md_lines: List[str] = []
    md_lines.append("# Φ-Mesh Tag Taxonomy\n")
    md_lines.append(
        "Tags grouped by RGPx phase: Δ (emergence), GC (resonance), "
        "CF (integration / closure).\n"
    )
    md_lines.append(f"_Generated: {meta['generated_at']}_\n")

    phase_titles = {
        "delta": "Δ — Emergence (Cycle 1)",
        "gc": "GC — Resonance (Cycle 2)",
        "cf": "CF — Integration / Closure (Cycle 3)",
        "unknown": "Unclassified",
    }

    for phase_key in ("delta", "gc", "cf", "unknown"):
        tags_map = phases[phase_key]
        if not tags_map:
            continue
        md_lines.append(f"## {phase_titles[phase_key]}\n")
        for tag, info in sorted(tags_map.items()):
            desc = info["description"] or "_No description available._"
            count = info["count"]
            md_lines.append(f"- **`{tag}`** — {desc} _(pulses: {count})_")
        md_lines.append("")

    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")


if __name__ == "__main__":
    build_taxonomy()
