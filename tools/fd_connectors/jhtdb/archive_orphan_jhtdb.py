#!/usr/bin/env python3
"""
Archive orphan JHTDB evidence:
- For each meta in data/jhtdb/*.meta.json, extract x,y,z
- If no pulse filename in pulse/ matches "jhtdb-probe_{x}_{y}_{z}",
  move the evidence group to data/jhtdb/archive/.
"""

import json, shutil
from pathlib import Path

ROOT     = Path("data/jhtdb")
ARCHIVE  = ROOT / "archive"
PULSEDIR = Path("pulse")

ARCHIVE.mkdir(parents=True, exist_ok=True)

def pulse_exists_for_xyz(x, y, z) -> bool:
    token = f"jhtdb-probe_{x}_{y}_{z}"
    for yml in PULSEDIR.rglob("*.yml"):
        if yml.parent.name == "archive":
            continue
        if token in yml.name:
            return True
    return False

def evidence_group(meta_path: Path):
    """Return all sibling evidence files sharing the stem of meta."""
    stem = meta_path.with_suffix("").name  # drop .json
    parent = meta_path.parent
    candidates = [
        parent / f"{stem}.meta.json",
        parent / f"{stem}.csv.gz",
        parent / f"{stem}.csv",
        parent / f"{stem}.parquet",
        Path("results/fd_probe") / f"{stem}.analysis.json",
    ]
    return [p for p in candidates if p.exists()]

def main():
    moved = 0
    for meta in sorted(ROOT.glob("*.meta.json")):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            continue
        pt = data.get("point") or {}
        x, y, z = pt.get("x"), pt.get("y"), pt.get("z")
        if x is None or y is None or z is None:
            continue

        if pulse_exists_for_xyz(x, y, z):
            # referenced by a pulse → keep
            continue

        # orphan → archive the group
        for f in evidence_group(meta):
            dest = ARCHIVE / f.name
            # if a namesake exists, keep the newest (overwrite)
            if dest.exists():
                dest.unlink()
            shutil.move(str(f), str(dest))
            moved += 1
            print(f"[moved] {f} → {dest}")

    print(f"Done. Files moved: {moved}")

if __name__ == "__main__":
    main()
