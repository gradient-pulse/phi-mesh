import os
import yaml
from collections import defaultdict

# Configuration: use script-relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PULSE_DIR = os.path.join(SCRIPT_DIR, "pulse")
TAG_INDEX_PATH = os.path.join(SCRIPT_DIR, "meta", "tag_index.yml")


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
    for filepath in pulse_files:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if not data:
                    print(f"⚠️  Skipping empty file: {filepath}")
                    continue
                pulse_tags = data.get("tags", [])
                if not pulse_tags:
                    print(f"⚠️  No tags in: {filepath}")
                    continue
                for tag in pulse_tags:
                    # Normalize to forward slashes for GitHub
                    relative_path = os.path.relpath(filepath, SCRIPT_DIR).replace("\\", "/")
                    tag_index[tag].append(relative_path)
                print(f"✅ {os.path.basename(filepath)}: {pulse_tags}")
            except Exception as e:
                print(f"❌ Failed to parse {filepath}: {e}")
    return dict(tag_index)


def write_tag_index(tag_index):
    if not tag_index:
        print("⚠️ No tags extracted; tag index will be empty.")
    else:
        print(f"✅ Extracted {sum(len(v) for v in tag_index.values())} tag links across {len(tag_index)} tags.")
    with open(TAG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, default_flow_style=False, sort_keys=True)
    print(f"✅ Tag index written to {TAG_INDEX_PATH}")


if __name__ == "__main__":
    pulses = load_pulses()
    tag_index = extract_tags(pulses)
    write_tag_index(tag_index)
