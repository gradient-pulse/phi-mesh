#!/usr/bin/env python3
"""
Archive JHTDB evidence based on *pulse YAML links*.

Rules
- Valid pulses live under pulse/ (NOT pulse/archive/).
- Pulses list evidence under the key `links:` (strings).
- We consider an evidence "live" if any pulse links to a file in data/jhtdb/
  with the same base stem (regardless of extension).

This script:
- Builds the set of referenced evidence stems from all non-archived pulses.
- For each meta in data/jhtdb/*.meta.json, if its stem is *not* referenced
  (or --force-all), move the evidence group (csv/csv.gz/parquet/meta/analysis)
  into data/jhtdb/archive/.

Options
  --dry-run   : list actions only, do not move files
  --force-all : archive all evidence regardless of references
"""

import argparse, re, json, shutil
from pathlib import Path

try:
    import yaml
except Exception as e:
    raise SystemExit("PyYAML is required. pip install pyyaml") from e


ROOT_JHTDB = Path("data/jhtdb")
ROOT_PULSE = Path("pulse")
ROOT_RESULTS = Path("results/fd_probe")
ARCHIVE = ROOT_JHTDB / "archive"

# All filename extensions we treat as the same evidence stem
EVIDENCE_EXTS = (
    ".meta.json", ".csv.gz", ".csv", ".parquet", ".analysis.json"
)

def stem_of(path: Path) -> str:
    """
    Normalize an evidence stem by stripping any of the known extensions.
    Works for standalone names too.
    """
    s = path.name
    for ext in EVIDENCE_EXTS:
        if s.endswith(ext):
            return s[: -len(ext)]
    # also handle double suffix (.csv.gz) if not in list for some reason
    if s.endswith(".gz"):
        s = s[:-3]
    if s.endswith(".csv"):
        s = s[:-4]
    return s

def extract_links_stems_from_pulse(pulse_path: Path) -> set[str]:
    """
    Read a pulse YAML and return a set of evidence stems it links to
    under data/jhtdb/. We scan:
      - links: [ "data/jhtdb/....", ... ]
    Also robustly searches the raw text for 'data/jhtdb/...' in case links
    are formatted differently.
    """
    stems: set[str] = set()

    text = pulse_path.read_text(encoding="utf-8", errors="ignore")
    data = {}
    try:
        data = yaml.safe_load(text) or {}
    except Exception:
        # Fall back to raw-text scrape only
        pass

    # 1) From structured links list
    links = data.get("links")
    if isinstance(links, str):
        links = [links]
    if isinstance(links, list):
        for item in links:
            if not isinstance(item, str):
                continue
            m = re.search(r"(data/jhtdb/[^\s\"']+)", item)
            if m:
                stems.add(stem_of(Path(m.group(1))))

    # 2) Raw-text scrape (fallback / extra)
    for m in re.finditer(r"data/jhtdb/[^\s\"']+", text):
        stems.add(stem_of(Path(m.group(0))))

    return stems

def build_referenced_stems() -> set[str]:
    """
    Walk pulse/, ignore pulse/archive/**, aggregate all evidence stems
    mentioned in links.
    """
    allow = set()
    for yml in ROOT_PULSE.rglob("*.yml"):
        # ignore any archived pulses
        if "archive" in yml.parts:
            continue
        try:
            allow |= extract_links_stems_from_pulse(yml)
        except Exception:
            # keep going; one bad file shouldn't stop the sweep
            continue
    return allow

def evidence_group(meta_path: Path) -> list[Path]:
    """
    For a meta file, return all peer files that belong to the same stem.
    """
    s = stem_of(meta_path)
    candidates = [
        ROOT_JHTDB / f"{s}.meta.json",
        ROOT_JHTDB / f"{s}.csv.gz",
        ROOT_JHTDB / f"{s}.csv",
        ROOT_JHTDB / f"{s}.parquet",
        ROOT_RESULTS / f"{s}.analysis.json",
    ]
    return [p for p in candidates if p.exists()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="List actions only, do not move files")
    ap.add_argument("--force-all", action="store_true", help="Archive all evidence regardless of pulses")
    args = ap.parse_args()

    ARCHIVE.mkdir(parents=True, exist_ok=True)

    referenced = set()
    if not args.force_all:
        referenced = build_referenced_stems()

    moved = 0
    for meta in sorted(ROOT_JHTDB.glob("*.meta.json")):
        s = stem_of(meta)
        if not args.force_all and s in referenced:
            # evidence is referenced by at least one pulse
            continue

        group = evidence_group(meta)
        if not group:
            continue

        for f in group:
            dest = ARCHIVE / f.name
            print(f"[plan] {f} → {dest}")
            if not args.dry_run:
                if dest.exists():
                    dest.unlink()
                # ensure archive dir exists (already created, but be safe)
                ARCHIVE.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(dest))
                moved += 1

    print(f"Done. Files moved: {moved}{' (dry-run)' if args.dry_run else ''}")

if __name__ == "__main__":
    main()
