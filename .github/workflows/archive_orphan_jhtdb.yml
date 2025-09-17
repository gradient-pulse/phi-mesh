#!/usr/bin/env python3
# archive_orphan_jhtdb.py
#
# Moves old JHTDB evidence files (csv.gz, parquet, meta.json)
# into data/jhtdb/archive/ if they don't have a matching pulse.

import os, shutil, re
from pathlib import Path

ROOT = Path("data/jhtdb")
ARCHIVE = ROOT / "archive"
ARCHIVE.mkdir(parents=True, exist_ok=True)

# pulse files live in pulse/… with same stem reference
PULSE_DIR = Path("pulse")

def has_matching_pulse(stem: str) -> bool:
    """Check if there's any pulse file referencing this probe stem."""
    for yml in PULSE_DIR.rglob("*.yml"):
        txt = yml.read_text(encoding="utf-8", errors="ignore")
        if stem in txt:
            return True
    return False

def main():
    moved = []
    for f in ROOT.glob("*"):
        if f.is_dir() or f.name == "archive":
            continue
        if not (f.suffix in [".gz", ".parquet", ".json"] or f.suffixes[-2:] == [".csv", ".gz"]):
            continue
        stem = re.sub(r"\..*$", "", f.name)  # drop extensions
        if not has_matching_pulse(stem):
            target = ARCHIVE / f.name
            shutil.move(str(f), target)
            moved.append(f.name)
    if moved:
        print(f"Archived {len(moved)} orphan JHTDB files:")
        for m in moved:
            print(" -", m)
    else:
        print("No orphan files found.")

if __name__ == "__main__":
    main()
