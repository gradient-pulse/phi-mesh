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
    "related_concepts": []
})

# Preserve existing tag metadata
for tag, info in existing_data.get("tags", {}).items():
    merged_tags[tag]["description"] = info.get("description", "TODO: Add description")
    merged_tags[tag]["linked_pulses"] = list(set(info.get("linked_pulses", [])))
    merged_tags[tag]["related_concepts"] = list(set(info.get("related_concepts", [])))

# Collect tags from pulse files
for filename in os.listdir(pulse_dir):
    if filename.endswith(('.yml', '.yaml')):
        file_path = os.path.join(pulse_dir, filename)
        try:
            with open(file_path, 'r') as f:
                pulse_data = yaml.safe_load(f) or {}
                tags = pulse_data.get('tags', [])
                for tag in tags:
                    if tag not in merged_tags:
                        merged_tags[tag] = {
                            "description": "TODO: Add description",
                            "linked_pulses": [],
                            "related_concepts": []
                        }
                    if filename not in merged_tags[tag]["linked_pulses"]:
                        merged_tags[tag]["linked_pulses"].append(filename)

                    # Auto-add co-tags as related_concepts
                    for other_tag in tags:
                        if other_tag != tag and other_tag not in merged_tags[tag]["related_concepts"]:
                            merged_tags[tag]["related_concepts"].append(other_tag)
        except Exception:
            continue

# Sort tags, pulses, related_concepts
final_index = {
    "tags": {
        tag: {
            "description": info["description"],
            "linked_pulses": sorted(info["linked_pulses"]),
            "related_concepts": sorted(set(info.get("related_concepts", [])))
        }
        for tag, info in sorted(merged_tags.items())
    }
}

# Save tag index
with open(tag_index_path, "w") as f:
    yaml.dump(final_index, f, sort_keys=False)

# Rebuild browser
from tag_index_utils import build_tag_browser
build_tag_browser(alphabetize_tags=True)
