from __future__ import annotations

import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

import yaml


Phase = Literal["delta", "gc", "cf", "unknown"]


ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
PULSE_DIR = ROOT / "pulse"
TAG_DESC_PATH = META_DIR / "tag_descriptions.yml"
OVERRIDE_PATH = META_DIR / "tag_phase_overrides.yml"
OUT_YAML_PATH = META_DIR / "tag_taxonomy.yml"
OUT_MD_PATH = META_DIR / "tag_taxonomy.md"


def load_yaml(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_tag_usage() -> Dict[str, Dict[str, object]]:
    """
    Scan all pulses and collect:
    - usage count per tag
    - list of pulse filenames where each tag appears
    """
    usage: Dict[str, Dict[str, object]] = {}
    if not PULSE_DIR.exists():
        return usage

    for pulse_file in sorted(PULSE_DIR.glob("*.yml")):
        data = load_yaml(pulse_file)
        if not isinstance(data, dict):
            continue
        pulse = data.get("pulse") or {}
        tags = pulse.get("tags") or []
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if not isinstance(tag, str):
                continue
            info = usage.setdefault(tag, {"count": 0, "pulses": []})
            info["count"] = int(info["count"]) + 1
            info["pulses"].append(pulse_file.name)
    return usage


def classify_phase(
    tag: str,
    description: Optional[str],
    overrides: Dict[str, str],
) -> Phase:
    # Manual override always wins
    if tag in overrides:
        phase = overrides[tag].lower().strip()
        if phase in {"delta", "gc", "cf"}:
            return phase  # type: ignore[return-value]
        return "unknown"

    text = (tag + " " + (description or "")).lower()

    # Very simple heuristics – conservative, errs on "unknown"
    delta_keywords = [
        "emergence",
        "emergent",
        "birth",
        "origin",
        "asymmetry",
        "seed",
        "tension",
        "gradient",
        "synthetic_life",
        "spark",
    ]
    gc_keywords = [
        "resonance",
        "feedback",
        "alignment",
        "rhythm",
        "oscillation",
        "interaction",
        "propagation",
        "memetic",
        "gardening",
        "evolution",
    ]
    cf_keywords = [
        "closure",
        "filter",
        "integration",
        "stability",
        "stabilize",
        "attractor",
        "field",
        "cortex",
        "culture",
        "societal",
        "contextual",
    ]

    if any(k in text for k in delta_keywords):
        return "delta"
    if any(k in text for k in gc_keywords):
        return "gc"
    if any(k in text for k in cf_keywords):
        return "cf"
    return "unknown"


def build_taxonomy():
    tag_descriptions = load_yaml(TAG_DESC_PATH) or {}
    overrides = load_yaml(OVERRIDE_PATH) or {}
    usage = collect_tag_usage()

    taxonomy: Dict[Phase, List[Dict[str, object]]] = {
        "delta": [],
        "gc": [],
        "cf": [],
        "unknown": [],
    }

    for tag, desc in sorted(tag_descriptions.items()):
        if not isinstance(tag, str):
            continue
        if isinstance(desc, dict):
            # In case descriptions were structured later
            description_text = desc.get("description") or ""
        else:
            description_text = str(desc or "")

        phase = classify_phase(tag, description_text, overrides)
        info = usage.get(tag, {"count": 0, "pulses": []})

        taxonomy[phase].append(
            {
                "tag": tag,
                "description": description_text.strip(),
                "count": int(info.get("count", 0)),
                "pulses": sorted(info.get("pulses", [])),
            }
        )

    # Sort within each phase by tag name
    for phase in taxonomy:
        taxonomy[phase].sort(key=lambda x: x["tag"])  # type: ignore[index]

    meta = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "root": str(ROOT),
        "notes": (
            "Tags are grouped heuristically by RGPx phase. "
            "Edit meta/tag_phase_overrides.yml to pin specific tags to delta/gc/cf. "
            "This script does not modify any other files."
        ),
    }

    out = {
        "meta": meta,
        "phases": taxonomy,
    }

    OUT_YAML_PATH.write_text(
        yaml.safe_dump(out, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    # Also emit a human-readable Markdown view
    lines: List[str] = []
    lines.append("# Tag Taxonomy by RGPx Phase\n")
    lines.append(f"_Generated at: {meta['generated_at']}_\n")
    lines.append(
        "This file is derived from `meta/tag_descriptions.yml` and `pulse/*.yml`.\n"
        "Use `meta/tag_phase_overrides.yml` to correct or refine classifications.\n"
    )

    phase_titles = {
        "delta": "Δ — Emergence",
        "gc": "GC — Resonance",
        "cf": "CF — Integration / Closure",
        "unknown": "Unclassified",
    }

    for phase in ["delta", "gc", "cf", "unknown"]:
        items = taxonomy[phase]  # type: ignore[index]
        if not items:
            continue
        lines.append(f"\n## {phase_titles[phase]}\n")
        for entry in items:
            tag = entry["tag"]
            desc = entry["description"]
            count = entry["count"]
            pulses = entry["pulses"]
            lines.append(f"### `{tag}`\n")
            if desc:
                lines.append(f"{desc}\n")
            else:
                lines.append("_No description available._\n")
            lines.append(f"- Usage count: **{count}**\n")
            if pulses:
                preview = ", ".join(pulses[:10])
                if len(pulses) > 10:
                    preview += ", …"
                lines.append(f"- Pulses: {preview}\n")
            else:
                lines.append("- Pulses: _none found_\n")
            lines.append("")  # blank line

    OUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    build_taxonomy()
