#!/usr/bin/env python3
"""
repair_pulse_tags.py

Scans pulse/**/*.yml and flattens any nested 'tags' entries into a clean list of strings.
Backups are written as *.bak before overwriting.
"""

import glob
import io
import os
import re
import sys
import yaml

PULSE_GLOB = "pulse/**/*.yml"

_slug_re = re.compile(r"[^\w\-]+", re.UNICODE)

def norm_tag(tag: str) -> str:
    tag = str(tag).strip()
    tag = tag.replace(" ", "_")
    tag = _slug_re.sub("_", tag)
    tag = re.sub(r"_+", "_", tag)
    return tag.strip("_")

def listify(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

def flatten_tags(raw_tags):
    flat = []
    for t in listify(raw_tags):
        if isinstance(t, (list, tuple)):
            flat.extend(t)
        else:
            flat.append(t)
    normed = [norm_tag(t) for t in flat if t is not None]
    # de-dup while preserving order
    seen, out = set(), []
    for t in normed:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def repair_file(path):
    with io.open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] Could not parse {path}: {e}", file=sys.stderr)
            return False

    if not isinstance(data, dict) or "tags" not in data:
        return False

    old_tags = data.get("tags")
    new_tags = flatten_tags(old_tags)

    if new_tags == old_tags:
        return False  # no change needed

    data["tags"] = new_tags

    # Backup
    backup = path + ".bak"
    if not os.path.exists(backup):
        os.rename(path, backup)

    with io.open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"[FIXED] {path} (tags: {old_tags} -> {new_tags})")
    return True

def main():
    changed = 0
    for path in glob.glob(PULSE_GLOB, recursive=True):
        if repair_file(path):
            changed += 1
    print(f"[DONE] {changed} file(s) repaired.")

if __name__ == "__main__":
    sys.exit(main())
