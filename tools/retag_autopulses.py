#!/usr/bin/env python3
"""
One-time script to retro-tag all auto pulses with ExperimenterPulse.
Run locally or via GitHub Actions. It will:
- Find all YAML pulses under pulse/auto/
- If 'tags:' exists and does not contain 'ExperimenterPulse', append it
- If no 'tags:' exists, create it with ['ExperimenterPulse']
"""
import os
import yaml

PULSE_DIR = "pulse/auto"
TAG = "ExperimenterPulse"
count_updated = 0

for fname in os.listdir(PULSE_DIR):
    if not fname.endswith(".yml"):
        continue
    path = os.path.join(PULSE_DIR, fname)
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        continue

    tags = data.get("tags", [])
    if TAG not in tags:
        tags.append(TAG)
        data["tags"] = tags
        with open(path, "w") as f:
            yaml.dump(data, f, sort_keys=False)
        count_updated += 1

print(f"Updated {count_updated} auto-pulses with tag '{TAG}'.")
