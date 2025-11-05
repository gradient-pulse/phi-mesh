from __future__ import annotations
from pathlib import Path
import yaml
import datetime

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
PULSE_DIR = ROOT / "pulse"
TAG_INDEX_PATH = META_DIR / "tag_index.yml"
TAG_DESC_PATH = META_DIR / "tag_descriptions.yml"
PHASE_OVERRIDES_PATH = META_DIR / "tag_phase_overrides.yml"
OUT_PATH = META_DIR / "tag_taxonomy.yml"


def load_yaml(path: Path):
    """Safe YAML loader."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_tag_taxonomy():
    tag_index = load_yaml(TAG_INDEX_PATH)
    tag_data = load_yaml(TAG_DESC_PATH)
    phase_overrides = load_yaml(PHASE_OVERRIDES_PATH)

    phases = {"delta": [], "gc": [], "cf": [], "unknown": []}

    for tag, desc in tag_data.items():
        count = len(tag_index.get(tag, [])) if tag in tag_index else 0
        phase = "unknown"
        for key in ["delta", "gc", "cf"]:
            if tag in phase_overrides.get(key, []):
                phase = key
                break
        phases[phase].append({
            "tag": tag,
            "description": desc,
            "count": count,
            "pulses": tag_index.get(tag, [])
        })

    out = {
        "meta": {"generated_at": datetime.datetime.utcnow().isoformat()},
        "phases": phases,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)

    print(f"✅ Written taxonomy YAML: {OUT_PATH}")


if __name__ == "__main__":
    build_tag_taxonomy()
