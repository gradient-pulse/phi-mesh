from __future__ import annotations

from pathlib import Path
import datetime
import yaml

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
PULSE_DIR = ROOT / "pulse"

TAG_DESC_PATH = META_DIR / "tag_descriptions.yml"
PHASE_OVERRIDES_PATH = META_DIR / "tag_phase_overrides.yml"
OUT_PATH = META_DIR / "tag_taxonomy.yml"


def load_yaml(path: Path):
    """Safe YAML loader."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_tag_index() -> dict[str, list[str]]:
    """
    Walk pulse/*.yml (and subfolders), collect tags -> list of pulse ids.

    - Skips non-YAML files.
    - Skips obvious non-pulse files (e.g. README).
    - Treats either of these shapes as valid:

        tags: [a, b, c]

      or:

        pulse:
          tags: [a, b, c]
    """
    tag_index: dict[str, list[str]] = {}

    if not PULSE_DIR.exists():
        return tag_index

    for path in PULSE_DIR.rglob("*.yml"):
        # Ignore README or other non-pulse helpers
        if path.name.lower().startswith("readme"):
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            # Don't let one bad file kill the taxonomy build
            continue

        tags = []
        if isinstance(data, dict):
            if "tags" in data and isinstance(data["tags"], list):
                tags = data["tags"]
            elif "pulse" in data and isinstance(data["pulse"], dict):
                inner = data["pulse"]
                if "tags" in inner and isinstance(inner["tags"], list):
                    tags = inner["tags"]

        if not tags:
            continue

        # Use a compact id like "2025-11-04_what_is_life" or "archive/2024-…"
        pulse_id = path.relative_to(PULSE_DIR).with_suffix("").as_posix()

        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag = tag.strip()
            if not tag:
                continue
            tag_index.setdefault(tag, [])
            if pulse_id not in tag_index[tag]:
                tag_index[tag].append(pulse_id)

    # Sort pulse ids for determinism
    for tag, ids in tag_index.items():
        tag_index[tag] = sorted(ids)

    return tag_index


def build_tag_taxonomy():
    """Build complete tag taxonomy from descriptions, pulses, and phase overrides."""
    tag_data = load_yaml(TAG_DESC_PATH)
    phase_overrides = load_yaml(PHASE_OVERRIDES_PATH)
    tag_index = collect_tag_index()

    # Four phase buckets
    phases: dict[str, list[dict]] = {"delta": [], "gc": [], "cf": [], "unknown": []}

    # Iterate through all known tags from descriptions
    for tag, desc in tag_data.items():
        pulses = tag_index.get(tag, [])
        count = len(pulses)
        phase = "unknown"

        # Assign phase by override lists (if present)
        for key in ("delta", "gc", "cf"):
            if tag in phase_overrides.get(key, []):
                phase = key
                break

        phases[phase].append(
            {
                "tag": tag,
                "description": desc,
                "count": count,
                "pulses": pulses,
            }
        )

    # Sort tags alphabetically in each phase for easier scanning
    for key in phases:
        phases[key] = sorted(phases[key], key=lambda x: x.get("tag", ""))

    out = {
        "meta": {
            "generated_at": datetime.datetime.utcnow().isoformat(),
        },
        "phases": phases,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)

    print(f"✅ Written taxonomy YAML: {OUT_PATH}")


if __name__ == "__main__":
    build_tag_taxonomy()
