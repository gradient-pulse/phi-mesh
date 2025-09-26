#!/usr/bin/env python3
import sys, yaml, pathlib

META = pathlib.Path("meta")
TAG_INDEX = META / "tag_index.yml"            # produced by your workflow
ALIASES = META / "aliases.yml"                # optional
DESCS = META / "tag_descriptions.yml"

def load_yaml(p):
    return yaml.safe_load(p.read_text()) if p.exists() else {}

def main(write=False):
    idx = load_yaml(TAG_INDEX) or {}
    desc = load_yaml(DESCS) or {}
    tags = set((idx.get("tags") or {}).keys())

    # pull alias targets too (so you can decide if they need separate entries)
    aliases = (load_yaml(ALIASES) or {}).get("aliases") or {}
    tags |= set(aliases.keys()) | set(aliases.values())

    existing = set((desc.get("tags") or {}).keys())
    missing = sorted(t for t in tags if t not in existing)

    if not write:
        print(f"{len(missing)} tags missing descriptions:\n")
        for t in missing: print(f" - {t}")
        return

    # write TODO stubs (non-destructive: keeps existing)
    desc.setdefault("version", 1)
    desc.setdefault("tags", {})
    for t in missing:
        desc["tags"][t] = "TODO: add one-line description."

    DESCS.write_text(yaml.safe_dump(desc, sort_keys=False, allow_unicode=True))
    print(f"Wrote {len(missing)} TODO entries to {DESCS}")

if __name__ == "__main__":
    write = "--write" in sys.argv
    main(write)
