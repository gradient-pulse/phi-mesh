import os
import yaml
from pathlib import Path
from collections import defaultdict

# Paths
pulse_dir = Path("pulse")
meta_path = Path("meta/tag_index.yml")

# Load canonical tag mappings
if meta_path.exists():
    tag_index = yaml.safe_load(meta_path.read_text())
    canonical_tags = tag_index.get("canonical_tags", {})
else:
    tag_index = {}
    canonical_tags = {}

# Helper: normalize tag to canonical form
def normalize_tag(tag):
    for canonical, variants in canonical_tags.items():
        if tag in variants or tag == canonical:
            return canonical
    return tag.replace(" ", "_").replace("-", "_")

# Build tag index
tag_map = defaultdict(lambda: {"linked_pulses": [], "related_concepts": [], "description": ""})

for pulse_file in pulse_dir.glob("*.yml"):
    with pulse_file.open() as f:
        try:
            pulse_data = yaml.safe_load(f)
            tags = pulse_data.get("tags", [])
            if isinstance(tags, str):  # handle single string case
                tags = [tags]
            for tag in tags:
                if not tag:
                    continue
                canonical = normalize_tag(tag.strip())
                tag_map[canonical]["linked_pulses"].append(pulse_file.name)
        except Exception as e:
            print(f"Error parsing {pulse_file.name}: {e}")

# Combine with canonical_tags
final_output = dict(tag_map)
final_output["canonical_tags"] = canonical_tags

# Write output
Path("meta").mkdir(exist_ok=True)
with open(meta_path, "w") as f:
    yaml.dump(final_output, f, sort_keys=False)

print(f"✅ Tag index updated: {meta_path}")
