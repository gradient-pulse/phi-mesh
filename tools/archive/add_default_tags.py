#!/usr/bin/env python3
"""
Ensure all auto-generated pulses (under pulse/auto/) have the 6 default tags.
Skips manual pulses and anything in pulse/archive or pulse/telemetry.
"""

import os
import yaml
import re

AUTO_DIR = os.path.join("pulse", "auto")

DEFAULT_TAGS = [
    "RGP",
    "NT (Narrative_Tick)",
    "Rhythm",
    "NavierStokes",
    "turbulence",
    "ExperimenterPulse",
]

def norm_tag(s: str) -> str:
    """case/space/underscore/hyphen-insensitive key for dedupe"""
    s = (s or "").strip()
    s = re.sub(r"[\s_\-]+", "_", s)
    return s.casefold()

def ensure_defaults(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return False

    tags = data.get("tags", [])
    if tags is None:
        tags = []
    if not isinstance(tags, list):
        tags = [str(tags)]

    # dedupe-aware append (preserve existing order)
    seen = {norm_tag(t) for t in tags if isinstance(t, str)}
    changed = False
    for t in DEFAULT_TAGS:
        if norm_tag(t) not in seen:
            tags.append(t)
            seen.add(norm_tag(t))
            changed = True

    if changed:
        data["tags"] = tags
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return changed

def main():
    changed = 0
    if not os.path.isdir(AUTO_DIR):
        print("No pulse/auto directory — nothing to do.")
        return
    for root, _, files in os.walk(AUTO_DIR):
        # (AUTO_DIR is already outside archive/telemetry; keep simple)
        for fn in files:
            if fn.endswith((".yml", ".yaml")):
                fp = os.path.join(root, fn)
                if ensure_defaults(fp):
                    changed += 1
    print(f"Updated {changed} auto pulse file(s)." if changed else "No auto pulses needed tag updates.")

if __name__ == "__main__":
    main()
