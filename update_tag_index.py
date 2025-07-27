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

# Initialize tag structure
merged_tags = defaultdict(lambda: {
    "description": "TODO: Add description",
    "linked_pulses": [],
})

# Preserve existing tag metadata
for tag, info in existing_data.get("tags", {}).items():
    merged_tags[tag]["description"] = info.get("description", "TODO: Add description")
    merged_tags[tag]["linked_pulses"] = list(set(info.get("linked_pulses", [])))
    if "related_concepts" in info:
        merged_tags[tag]["related_concepts"] = info["related_concepts"]

# Collect tags from pulse files
for filename in os.listdir(pulse_dir):
    if filename.endswith((".yml", ".yaml")):
        file_path = os.path.join(pulse_dir, filename)
        try:
            with open(file_path, "r") as f:
                pulse_data = yaml.safe_load(f) or {}
                tags = pulse_data.get("tags", [])
                for tag in tags:
                    # Ensure tag exists
                    if tag not in merged_tags:
                        merged_tags[tag] = {
                            "description": "TODO: Add description",
                            "linked_pulses": [],
                        }
                    # Add pulse to linked list if not present
                    if filename not in merged_tags[tag]["linked_pulses"]:
                        merged_tags[tag]["linked_pulses"].append(filename)
        except Exception:
            continue

# Sort tags and linked pulses
final_index = {
    "tags": {
        tag: {
            **info,
            "linked_pulses": sorted(info["linked_pulses"]),
        }
        for tag, info in sorted(merged_tags.items())
    }
}

# Save tag index
with open(tag_index_path, "w") as f:
    yaml.dump(final_index, f, sort_keys=False)

# Rebuild browser
from tag_index_utils import build_tag_browser
build_tag_browser()
