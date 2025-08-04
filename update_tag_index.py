import os
import yaml
from collections import defaultdict

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
                        if not data:
                            print(f"⚠️ Empty YAML: {path}")
                            continue
                        tags = data.get('tags', [])
                        if not tags:
                            print(f"ℹ️ No tags in: {path}")
                            continue
                        canonical_tags = [str(tag).strip().replace("-", "_") for tag in tags]
                        pulses[path] = canonical_tags
                    except yaml.YAMLError as e:
                        print(f"❌ Invalid YAML in {path}: {e}")
    return pulses

def build_tag_index(pulses):
    tag_index = defaultdict(list)
    for pulse_path, tags in pulses.items():
        for tag in tags:
            tag_index[tag].append(pulse_path)
    return dict(sorted(tag_index.items()))

def write_tag_index(tag_index):
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)
    print(f"✅ Wrote {len(tag_index)} tags to {TAG_INDEX_PATH}")

if __name__ == "__main__":
    print("🔍 Scanning pulses...")
    pulses = load_pulses()
    print(f"📄 Found {len(pulses)} pulse files with tags.")
    tag_index = build_tag_index(pulses)
    write_tag_index(tag_index)
