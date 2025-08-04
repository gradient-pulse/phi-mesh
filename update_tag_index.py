import os
import yaml
from collections import defaultdict

# Correct relative path now that the script runs from repo root
PULSE_DIR = "pulse"
TAG_INDEX_PATH = "meta/tag_index.yml"

def load_pulses():
    pulses = {}
    for file in os.listdir(PULSE_DIR):
        if file.endswith(".yml") and not file.startswith("."):
            path = os.path.join(PULSE_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    if data and 'tags' in data:
                        canonical_tags = [str(tag).strip().replace("-", "_") for tag in data['tags']]
                        pulses[path] = canonical_tags
                except yaml.YAMLError:
                    print(f"Skipping invalid YAML: {path}")
    return pulses

def build_tag_index(pulses):
    tag_index = defaultdict(list)
    for pulse_path, tags in pulses.items():
        for tag in tags:
            if pulse_path not in tag_index[tag]:
                tag_index[tag].append(pulse_path)
    return dict(sorted(tag_index.items()))  # alphabetize tags

def write_tag_index(tag_index):
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)

if __name__ == "__main__":
    pulses = load_pulses()
    tag_index = build_tag_index(pulses)
    write_tag_index(tag_index)
    print(f"✅ tag_index.yml regenerated with {len(tag_index)} tags.")
