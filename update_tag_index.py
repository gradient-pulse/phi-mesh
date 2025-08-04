import os
import yaml
from collections import defaultdict

# Define source and output paths
pulse_dir = "phi-mesh/pulse"
output_file = "meta/tag_index.yml"

# Initialize tag index
tag_index = defaultdict(list)

# Only consider YAML files directly under phi-mesh/pulse/
for filename in os.listdir(pulse_dir):
    full_path = os.path.join(pulse_dir, filename)
    if (
        not filename.endswith(".yml")
        or os.path.isdir(full_path)
    ):
        continue

    with open(full_path, "r") as f:
        try:
            data = yaml.safe_load(f)
            tags = data.get("tags", [])
            for tag in tags:
                tag_index[tag].append(f"pulse/{filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Write tag index
with open(output_file, "w") as f:
    yaml.dump(dict(tag_index), f, sort_keys=True)
