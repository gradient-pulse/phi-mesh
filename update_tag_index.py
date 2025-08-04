import os
import yaml
from collections import defaultdict

PULSE_DIR = "phi-mesh/pulse"
TAG_INDEX_PATH = "phi-mesh/meta/tag_index.yml"

def load_pulses():
    pulse_files = []
    for root, _, files in os.walk(PULSE_DIR):
        for file in files:
            if file.endswith(".yml") and "archive" not in root and "telemetry" not in root:
                pulse_files.append(os.path.join(root, file))
    if not pulse_files:
        raise RuntimeError("❌ No pulse files found to scan.")
    print(f"✅ Found {len(pulse_files)} pulse files.")
    return pulse_files

def extract_tags(pulse_files):
    tag_index = defaultdict(list)
    for file in pulse_files:
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                tags = data.get("tags", [])
                if not tags:
                    continue
                for tag in tags:
                    tag_index[tag].append(file)
            except Exception as e:
                print(f"⚠️ Failed to parse {file}: {e}")
    if not tag_index:
        raise RuntimeError("❌ No tags found in any pulse files.")
    print(f"✅ Extracted {len(tag_index)} tags.")
    return dict(tag_index)

def write_tag_index(tag_index):
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)
    print(f"✅ Wrote tag index to {TAG_INDEX_PATH}")

if __name__ == "__main__":
    pulses = load_pulses()
    tag_index = extract_tags(pulses)
    write_tag_index(tag_index)
