#!/usr/bin/env python3
import sys, yaml
from pathlib import Path

DENY = {"chronoflux", "time"}  # case-sensitive keys as they appear in tag_index.yml

idx_path = Path("meta/tag_index.yml")
if not idx_path.exists():
    print("meta/tag_index.yml not found; nothing to scrub.")
    sys.exit(0)

data = yaml.safe_load(idx_path.read_text("utf-8")) or {}
tags = data.get("tags") or data  # supports both shapes

removed = []
for k in list(tags.keys()):
    if k in DENY:
        removed.append(k)
        del tags[k]

# write back in the same shape
if "tags" in data and isinstance(data["tags"], dict):
    data["tags"] = tags
else:
    data = tags

idx_path.write_text(yaml.safe_dump(data, sort_keys=True, allow_unicode=True), encoding="utf-8")
print("Removed tags:", ", ".join(removed) if removed else "(none)")
