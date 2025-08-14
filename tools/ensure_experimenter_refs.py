#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ensure ExperimenterPulse references

This script:
- Scans all pulse/**/*.yml files
- Finds pulses containing the 'ExperimenterPulse' tag (case-insensitive, normalized)
- Ensures they include the canonical ExperimenterPulse papers & podcasts
- Writes back files if changes were made

Canonical refs:
  Papers:
    - Solving Navier-Stokes, Differently: What It Takes (V1.2)
      https://doi.org/10.5281/zenodo.15830659
    - Experimenter's Guide – Solving Navier-Stokes, Differently (V1.7)
      https://doi.org/10.5281/zenodo.16812467
  Podcasts:
    - https://notebooklm.google.com/notebook/d49018d3-0070-41bb-9187-242c2698c53c?artifactId=fef1bd81-e87d-41b5-a501-f862442ce3ef
    - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=b1dcf5ac-5216-4a04-bc36-f509ebeeabef
"""

import sys
import re
from pathlib import Path
import yaml

# --- Canonical references ---
FOUNDATION_PAPERS = [
    {"title": "Solving Navier-Stokes, Differently: What It Takes (V1.2)",
     "url": "https://doi.org/10.5281/zenodo.15830659"},
    {"title": "Experimenter's Guide – Solving Navier-Stokes, Differently (V1.7)",
     "url": "https://doi.org/10.5281/zenodo.16812467"},
]
FOUNDATION_PODCASTS = [
    {"url": "https://notebooklm.google.com/notebook/d49018d3-0070-41bb-9187-242c2698c53c?artifactId=fef1bd81-e87d-41b5-a501-f862442ce3ef"},
    {"url": "https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=b1dcf5ac-5216-4a04-bc36-f509ebeeabef"},
]

# --- Helpers ---
def _norm_tag(s: str) -> str:
    return re.sub(r"[\s\-]+", "_", (s or "").strip()).casefold()

def _dedupe_links(items):
    seen, out = set(), []
    for it in items:
        if not isinstance(it, dict):
            continue
        url = it.get("url", "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(it)
    return out

# --- Main ---
def main():
    repo_root = Path(__file__).resolve().parents[1]
    pulse_dir = repo_root / "pulse"

    if not pulse_dir.exists():
        print(f"[error] No pulse/ directory found under {repo_root}", file=sys.stderr)
        sys.exit(1)

    changed_files = []

    for yml_path in pulse_dir.rglob("*.yml"):
        try:
            data = yaml.safe_load(yml_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"[warn] Failed to read {yml_path}: {e}", file=sys.stderr)
            continue

        tags = data.get("tags") or []
        norm_tags = {_norm_tag(t) for t in tags if t}

        if "experimenterpulse" not in norm_tags:
            continue  # skip

        # Ensure canonical papers/podcasts
        papers = data.get("papers") or []
        podcasts = data.get("podcasts") or []

        merged_papers = _dedupe_links(papers + FOUNDATION_PAPERS)
        merged_podcasts = _dedupe_links(podcasts + FOUNDATION_PODCASTS)

        if merged_papers != papers or merged_podcasts != podcasts:
            data["papers"] = merged_papers
            data["podcasts"] = merged_podcasts
            yml_path.write_text(
                yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                encoding="utf-8"
            )
            changed_files.append(str(yml_path.relative_to(repo_root)))
            print(f"[update] {yml_path.relative_to(repo_root)}")

    if not changed_files:
        print("[done] No changes needed.")
    else:
        print(f"[done] Updated {len(changed_files)} file(s).")

if __name__ == "__main__":
    main()
