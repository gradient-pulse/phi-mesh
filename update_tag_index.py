import os
import yaml
from collections import defaultdict

# Define directories
PULSE_DIR = "phi-pulses"
TAG_INDEX_PATH = "phi-mesh/meta/tag_index.yml"

def load_pulses():
    pulse_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(PULSE_DIR)
        for f in files
        if f.endswith(".yml")
           and "archive" not in root
           and "telemetry" not in root
    ]
    if not pulse_files:
        raise RuntimeError(f"❌ No pulse files found in {PULSE_DIR}")
    print(f"✅ Found {len(pulse_files)} pulse files.")
    return pulse_files

def extract_tags(pulse_files):
    tag_index = defaultdict(list)

    for file_path in pulse_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Error loading {file_path}: {e}")
            continue

        tags = data.get("tags", [])
        title = data.get("title", os.path.basename(file_path))

        for tag in tags:
            if tag not in tag_index:
                tag_index[tag] = []
            tag_index[tag].append({
                "file": file_path,
                "title": title
            })

    print(f"✅ Extracted {len(tag_index)} tags.")
    return dict(sorted(tag_index.items()))

def write_tag_index(tag_index):
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)
    print(f"✅ Wrote tag index to {TAG_INDEX_PATH}")

def main():
    pulses = load_pulses()
    tag_index = extract_tags(pulses)
    write_tag_index(tag_index)

if __name__ == "__main__":
    main()
