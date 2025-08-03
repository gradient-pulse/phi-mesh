import os
import yaml
from collections import defaultdict

# Constants
TAG_INDEX_PATH = "meta/tag_index.yml"
PULSE_DIR = "phi-mesh/pulse"

def load_pulses():
    pulses = {}
    for root, _, files in os.walk(PULSE_DIR):
        for file in files:
            if file.endswith(".yml"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = yaml.safe_load(f)
                        if data and 'tags' in data:
                            canonical_tags = [str(tag).strip().replace("-", "_") for tag in data['tags']]
                            pulses[path] = canonical_tags
                    except yaml.YAMLError as e:
                        print(f"\n❌ YAML parsing error in: {path}")
                        print(f"   → {e}\n")
                        raise
    return pulses

def build_tag_index(pulses):
    tag_index = defaultdict(list)
    for pulse_path, tags in pulses.items():
        for tag in tags:
            tag_index[tag].append(pulse_path)
    return dict(sorted(tag_index.items()))

def write_tag_index(tag_index):
    os.makedirs(os.path.dirname(TAG_INDEX_PATH), exist_ok=True)
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)

if __name__ == "__main__":
    pulses = load_pulses()
    tag_index = build_tag_index(pulses)
    write_tag_index(tag_index)
    print(f"✅ tag_index.yml regenerated with {len(tag_index)} tags.")
