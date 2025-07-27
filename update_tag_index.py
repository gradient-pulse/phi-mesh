import os
import yaml
from collections import defaultdict, Counter
from tag_index_utils import build_tag_browser

# === Configuration ===
pulse_dir = "pulse"
tag_index_path = "meta/tag_index.yml"

# === Load Existing Index (if any) ===
if os.path.exists(tag_index_path):
    with open(tag_index_path, "r") as f:
        existing_data = yaml.safe_load(f) or {}
else:
    existing_data = {}

# === Initialize structures ===
merged_tags = defaultdict(lambda: {
    "description": "TODO: Add description",
    "linked_pulses": [],
    "related_concepts": [],
    "rank": 0,
    "count": 0
})
tag_cooccurrence = defaultdict(Counter)

# === Load existing tag data ===
for tag, info in existing_data.get("tags", {}).items():
    merged_tags[tag]["description"] = info.get("description", "TODO: Add description")
    merged_tags[tag]["linked_pulses"] = list(set(info.get("linked_pulses", [])))
    merged_tags[tag]["related_concepts"] = list(set(info.get("related_concepts", [])))

# === Parse pulse files ===
for filename in os.listdir(pulse_dir):
    if filename.endswith((".yml", ".yaml")):
        file_path = os.path.join(pulse_dir, filename)
        try:
            with open(file_path, "r") as f:
                pulse_data = yaml.safe_load(f) or {}
                tags = pulse_data.get("tags", [])
                for tag in tags:
                    merged_tags[tag]["linked_pulses"].append(filename)
                    merged_tags[tag]["count"] += 1
                for i, tag1 in enumerate(tags):
                    for j, tag2 in enumerate(tags):
                        if i != j:
                            tag_cooccurrence[tag1][tag2] += 1
        except Exception:
            continue

# === Normalize and deduplicate lists ===
for tag in merged_tags:
    merged_tags[tag]["linked_pulses"] = sorted(set(merged_tags[tag]["linked_pulses"]))
    merged_tags[tag]["related_concepts"] = sorted(set(tag_cooccurrence[tag].keys()))

# === Assign rank based on frequency (lower = more frequent) ===
sorted_by_usage = sorted(merged_tags.items(), key=lambda x: -x[1]["count"])
for i, (tag, _) in enumerate(sorted_by_usage, start=1):
    merged_tags[tag]["rank"] = i

# === Final structure, tags sorted alphabetically ===
final_index = {
    "tags": dict(sorted(merged_tags.items(), key=lambda x: x[0].lower()))
}

# === Save to YAML ===
with open(tag_index_path, "w") as f:
    yaml.dump(final_index, f, sort_keys=False)

# === Regenerate the HTML tag browser ===
build_tag_browser()
