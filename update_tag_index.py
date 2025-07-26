
import os
import yaml
from collections import defaultdict

# Paths
pulse_dir = "pulse"
tag_index_path = "meta/tag_index.yml"

# Load existing tag index
if os.path.exists(tag_index_path):
    with open(tag_index_path, "r") as f:
        existing_data = yaml.safe_load(f) or {}
else:
    existing_data = {}

merged_tags = defaultdict(lambda: {"description": "TODO: Add description", "linked_pulses": []})

# Initialize with existing data
for tag, info in existing_data.get("tags", {}).items():
    merged_tags[tag]["description"] = info.get("description", "TODO: Add description")
    merged_tags[tag]["linked_pulses"] = list(set(info.get("linked_pulses", [])))
    if "related_concepts" in info:
        merged_tags[tag]["related_concepts"] = info["related_concepts"]

# Walk through pulse files and collect all tags
for filename in os.listdir(pulse_dir):
    if filename.endswith(".yml") or filename.endswith(".yaml"):
        file_path = os.path.join(pulse_dir, filename)
        try:
            with open(file_path, "r") as f:
                pulse_data = yaml.safe_load(f) or {}
                tags = pulse_data.get("tags", [])
                for tag in tags:
                    if filename not in merged_tags[tag]["linked_pulses"]:
                        merged_tags[tag]["linked_pulses"].append(filename)
        except Exception:
            continue

# Sort linked pulses for consistency
for tag in merged_tags:
    merged_tags[tag]["linked_pulses"] = sorted(merged_tags[tag]["linked_pulses"])

# Final structure
final_index = {"tags": dict(merged_tags)}

# Save merged tag index
with open(tag_index_path, "w") as f:
    yaml.dump(final_index, f, sort_keys=False)

from tag_index_utils import build_tag_browser
build_tag_browser()
