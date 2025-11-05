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

OUT_YAML = META_DIR / "tag_taxonomy.yml"
OUT_MD = META_DIR / "tag_taxonomy.md"


PhaseKey = str  # "delta" | "gc" | "cf" | "unknown"


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_tag_descriptions() -> Dict[str, str]:
    raw = _load_yaml(TAG_DESCRIPTIONS)
    if not isinstance(raw, dict):
        raise ValueError(f"{TAG_DESCRIPTIONS} must be a mapping of tag -> description")
    return {str(k): ("" if v is None else str(v)).strip() for k, v in raw.items()}


def load_pulse_tag_counts() -> Dict[str, List[str]]:
    """
    Scan pulse/*.yml (and pulse/**/ if present) and build:
        tag -> [pulse_slug, ...]
    where pulse_slug is filename without extension.
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
                tag = str(t).strip()
                if not tag:
                    continue
                tag_to_pulses.setdefault(tag, []).append(slug)

    return tag_to_pulses


def load_phase_overrides() -> Dict[str, PhaseKey]:
    """
    Optional manual override file:
        delta: [tag1, tag2, ...]
        gc:    [...]
        cf:    [...]
        unknown: [...]
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


# --- Heuristic classification -------------------------------------------------


# A small curated core mapping so key concepts are always placed sensibly.
CORE_PHASE_MAP: Dict[str, PhaseKey] = {
    # Δ — Emergence
    "gradient": "delta",
    "delta_resonance": "delta",
    "emergence": "delta",
    "origin_condition": "delta",
    "genesis": "delta",
    "proto_pulse": "delta",
    "memetic_seed": "delta",

    # GC — Resonance
    "coherence": "gc",
    "coherence_rhythm": "gc",
    "coherence_emergence": "gc",
    "gradient_choreography": "gc",
    "resonance": "gc",
    "nt_rhythm": "gc",
    "phi_harmonics": "gc",
    "triad_of_resonance": "gc",
    "inter_model_alignment": "gc",
    "inter_model_coherence": "gc",

    # CF — Integration / Closure
    "contextual_filter": "cf",
    "coherence_closure": "cf",
    "unity_disunity_cycle": "cf",
    "ud": "cf",
    "phase_alignment": "cf",
    "societal_coherence": "cf",
    "cf_bank": "cf",
    "selective_permeability": "cf",
}


DELTA_KEYWORDS = {
    "emerge", "emergence", "seed", "proto", "origin", "initial", "first",
    "difference", "delta", "asymmetry", "spark", "birth", "genesis",
}

GC_KEYWORDS = {
    "resonance", "resonate", "alignment", "align", "rhythm", "harmonic",
    "choreography", "wave", "field", "propagation", "synchron", "coherence",
    "phase-lock", "heartbeat", "ladder",
}

CF_KEYWORDS = {
    "context", "filter", "closure", "integrat", "attractor", "stability",
    "stable", "governance", "societ", "economy", "architecture",
    "bank", "library", "memory", "invariant", "cycle", "unity", "disunity",
}


def classify_tag_heuristic(tag: str, desc: str) -> PhaseKey:
    """
    Best-effort automatic phase classifier based on:
      - small curated core mapping
      - keyword hits in (tag + description)
    Returns: "delta" | "gc" | "cf" | "unknown"
    """

    tag_l = tag.lower()
    desc_l = desc.lower()

    # 1. Core mapping first (hard override)
    if tag in CORE_PHASE_MAP:
        return CORE_PHASE_MAP[tag]
    if tag_l in CORE_PHASE_MAP:
        return CORE_PHASE_MAP[tag_l]

    # 2. Keyword scoring
    text = f"{tag_l} {desc_l}"

    def count_hits(keywords: set[str]) -> int:
        return sum(1 for kw in keywords if kw in text)

    delta_score = count_hits(DELTA_KEYWORDS)
    gc_score = count_hits(GC_KEYWORDS)
    cf_score = count_hits(CF_KEYWORDS)

    scores = {
        "delta": delta_score,
        "gc": gc_score,
        "cf": cf_score,
    }

    best_phase = max(scores, key=scores.get)
    best_score = scores[best_phase]

    # If no signal at all, or ambiguous tie, treat as unknown.
    if best_score <= 0:
        return "unknown"

    # Avoid classifying when everything is equally weak.
    non_zero = [p for p, s in scores.items() if s == best_score and s > 0]
    if len(non_zero) != 1:
        return "unknown"

    return best_phase


# --- Build taxonomy -----------------------------------------------------------


def build_tag_taxonomy() -> Dict[str, Any]:
    tag_descriptions = load_tag_descriptions()
    tag_to_pulses = load_pulse_tag_counts()
    overrides = load_phase_overrides()

    all_tags = sorted(set(tag_descriptions.keys()) | set(tag_to_pulses.keys()))

    phases: Dict[PhaseKey, List[Dict[str, Any]]] = {
        "delta": [],
        "gc": [],
        "cf": [],
        "unknown": [],
    }

    for tag in all_tags:
        desc = tag_descriptions.get(tag, "")
        pulses = sorted(tag_to_pulses.get(tag, []))
        count = len(pulses)

        # 1) explicit override wins
        if tag in overrides:
            phase: PhaseKey = overrides[tag]
        else:
            phase = classify_tag_heuristic(tag, desc)

        entry = {
            "tag": tag,
            "description": desc,
            "count": count,
            "pulses": pulses,
        }
        phases[phase].append(entry)

    # Sort tags within each phase by tag name
    for lst in phases.values():
        lst.sort(key=lambda e: e["tag"])

    taxonomy = {
        "meta": {
            "generated_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        "phases": phases,
    }
    return taxonomy


# --- Markdown rendering -------------------------------------------------------


PHASE_TITLES = {
    "delta": "Δ — Emergence (Cycle 1)",
    "gc": "GC — Resonance (Cycle 2)",
    "cf": "CF — Integration / Closure (Cycle 3)",
    "unknown": "Unclassified — Open",
}

PHASE_SUBTITLES = {
    "delta": "Difference, initiation, tension.",
    "gc": "Alignment, rhythm, propagation.",
    "cf": "Stability, context, attractors.",
    "unknown": "Tags whose phase is not yet determined.",
}


def to_markdown(taxonomy: Dict[str, Any]) -> str:
    phases: Dict[PhaseKey, List[Dict[str, Any]]] = taxonomy.get("phases", {})
    lines: List[str] = []

    lines.append("# Φ-Mesh Tag Taxonomy\n")
    lines.append(
        "Tags grouped by RGPx phase: Δ (emergence), GC (resonance), CF (integration / closure).\n"
    )

    generated_at = taxonomy.get("meta", {}).get("generated_at")
    if generated_at:
        lines.append(f"_Generated at: {generated_at}_\n")

    for phase_key in ("delta", "gc", "cf", "unknown"):
        items = phases.get(phase_key, []) or []
        if not items:
            continue

        lines.append("\n---\n")
        lines.append(f"## {PHASE_TITLES.get(phase_key, phase_key)}\n")
        lines.append(f"{PHASE_SUBTITLES.get(phase_key, '')}\n")

        for item in items:
            tag = item["tag"]
            desc = (item.get("description") or "").strip()
            count = item.get("count", 0)
            pulses = item.get("pulses") or []

            lines.append(f"- **`{tag}`**  \n")
            if desc:
                lines.append(f"  {desc}  \n")
            lines.append(f"  _pulses: {count}_")
            if pulses:
                example_str = ", ".join(pulses[:3])
                if len(pulses) > 3:
                    example_str += ", …"
                lines.append(f"  _(e.g. {example_str})_")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


# --- Entry point --------------------------------------------------------------


def main() -> None:
    taxonomy = build_tag_taxonomy()

    # YAML
    OUT_YAML.write_text(
        yaml.safe_dump(taxonomy, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_YAML}")

    # Markdown
    OUT_MD.write_text(to_markdown(taxonomy), encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
