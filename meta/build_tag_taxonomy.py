from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
PULSE_DIR = ROOT / "pulse"

TAXONOMY_YAML = META_DIR / "tag_taxonomy.yml"


# ----------------------------
# Load helpers
# ----------------------------

def load_yaml(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data is not None else default


def load_tag_descriptions() -> Dict[str, str]:
    """
    Canonical tags + descriptions from meta/tag_descriptions.yml
    """
    raw = load_yaml(META_DIR / "tag_descriptions.yml", {})
    out: Dict[str, str] = {}
    for tag, desc in raw.items():
        if tag is None:
            continue
        tag_str = str(tag).strip()
        if not tag_str:
            continue
        out[tag_str] = (desc or "").strip()
    return out


def load_aliases() -> Dict[str, str]:
    """
    Optional alias mapping from meta/aliases.yml
    (alias_tag -> canonical_tag)
    """
    raw = load_yaml(META_DIR / "aliases.yml", {})
    aliases: Dict[str, str] = {}
    for alias, canonical in raw.items():
        if alias is None or canonical is None:
            continue
        alias_str = str(alias).strip()
        canon_str = str(canonical).strip()
        if not alias_str or not canon_str:
            continue
        aliases[alias_str] = canon_str
    return aliases


def iter_pulse_tags() -> List[Tuple[str, List[str]]]:
    """
    Yield (pulse_slug, [tags...]) for all top-level pulse/*.yml
    (ignores pulse/archive/).
    """
    results: List[Tuple[str, List[str]]] = []

    for path in sorted(PULSE_DIR.glob("*.yml")):
        slug = path.stem
        data = load_yaml(path, {})
        tags = data.get("tags") or []
        norm: List[str] = []
        for t in tags:
            if t is None:
                continue
            t_str = str(t).strip()
            if t_str:
                norm.append(t_str)
        results.append((slug, norm))

    return results


def load_phase_overrides() -> Dict[str, str]:
    """
    Optional explicit phase mapping from meta/tag_phase_overrides.yml.

    Expected (but not required) format:

      tag_name:
        phase: delta|gc|cf|unknown

    If the file is not a dict (e.g. it's a list or something else),
    we simply ignore it and return {} so it never breaks the build.
    """
    raw = load_yaml(META_DIR / "tag_phase_overrides.yml", {})

    # Safety guard: if it's not a mapping, ignore overrides entirely.
    if not isinstance(raw, dict):
        return {}

    out: Dict[str, str] = {}
    for tag, info in raw.items():
        if tag is None or info is None:
            continue
        if not isinstance(info, dict):
            continue
        phase = info.get("phase")
        if not phase:
            continue
        phase_str = str(phase).strip().lower()
        if phase_str not in {"delta", "gc", "cf", "unknown"}:
            continue
        out[str(tag).strip()] = phase_str
    return out


# ----------------------------
# Phase classification
# ----------------------------

def infer_phase(tag: str, desc: str, overrides: Dict[str, str]) -> str:
    """
    Decide which RGPx phase a tag belongs to.
    Priority:
      1) explicit override in tag_phase_overrides.yml
      2) keyword heuristic on description + tag name
      3) fallback to 'unknown'
    """
    if tag in overrides:
        return overrides[tag]

    text = f"{tag} {desc}".lower()

    # Δ — emergence
    if any(k in text for k in [
        "emergence", "genesis", "origin", "seed",
        "delta_", "difference", "triadic", "proto", "big_bang",
    ]):
        return "delta"

    # GC — resonance
    if any(k in text for k in [
        "alignment", "resonance", "rhythm", "gradient",
        "choreography", "translation", "flux", "propagation",
        "coherence_rhythm", "nt_rhythm",
    ]):
        return "gc"

    # CF — integration / closure
    if any(k in text for k in [
        "context", "filter", "closure", "economy", "governance",
        "infrastructure", "stability", "attractor", "integration",
        "ud", "unity_disunity", "taxonomy", "map",
    ]):
        return "cf"

    return "unknown"


# ----------------------------
# Main taxonomy builder
# ----------------------------

def build_taxonomy():
    tag_desc = load_tag_descriptions()
    aliases = load_aliases()
    overrides = load_phase_overrides()

    # Collect pulse counts per canonical tag
    stats: Dict[str, Dict[str, object]] = {}

    for slug, tags in iter_pulse_tags():
        for raw_tag in tags:
            # Respect aliases
            canonical = aliases.get(raw_tag, raw_tag)

            # Skip tags with uppercase letters; these are almost always
            # legacy variants we don't want to surface in the taxonomy.
            if any(ch.isupper() for ch in canonical):
                continue

            canonical = canonical.strip()
            if not canonical:
                continue

            if canonical not in stats:
                stats[canonical] = {"count": 0, "pulses": []}

            entry = stats[canonical]
            entry["count"] = int(entry["count"]) + 1  # type: ignore[arg-type]

            # Keep up to 3 example pulses per tag
            pulses: List[str] = entry["pulses"]  # type: ignore[assignment]
            if len(pulses) < 3:
                pulses.append(slug)

    # Union of all known tags:
    #  - canonical descriptions
    #  - anything that actually appears in pulses
    all_tags = set(tag_desc.keys()) | set(stats.keys())

    phases = {
        "delta": [],
        "gc": [],
        "cf": [],
        "unknown": [],
    }

    for tag in sorted(all_tags):
        desc = tag_desc.get(tag, "").strip()
        s = stats.get(tag, {"count": 0, "pulses": []})
        count = int(s.get("count", 0))  # type: ignore[arg-type]
        pulses = list(s.get("pulses", []))  # type: ignore[arg-type]

        phase = infer_phase(tag, desc, overrides)

        phases[phase].append(
            {
                "tag": tag,
                "description": desc,
                "count": count,
                "pulses": pulses,
            }
        )

    taxonomy = {
        "meta": {
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        "phases": phases,
    }

    TAXONOMY_YAML.write_text(
        yaml.safe_dump(
            taxonomy,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        ),
        encoding="utf-8",
    )
    print(f"Wrote taxonomy: {TAXONOMY_YAML}")


if __name__ == "__main__":
    build_taxonomy()
