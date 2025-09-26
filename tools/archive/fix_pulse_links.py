#!/usr/bin/env python3
"""
Find title-only 'papers' entries in pulse/*.yml (incl. pulse/auto/)
and attach canonical URLs (e.g., DOIs) when we recognize the title.
Safe, idempotent: only adds url when missing.
"""

import glob, os, yaml, re

# Map normalized title -> URL
CANON = {
    # Your two guides
    "experimenter’s guide — solving navier–stokes, differently":
        "https://doi.org/10.5281/zenodo.15830659",
    "experimenter’s guide — rgp vs navier–stokes":
        "https://doi.org/10.5281/zenodo.15830659",   # or separate DOI if you split later
    # add more mappings here as you publish them
}

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def scan_and_fix():
    changed = []
    for fp in sorted(glob.glob("pulse/**/*.yml", recursive=True)):
        # skip folders we never index
        if "/pulse/archive/" in fp or "/pulse/telemetry/" in fp:
            continue

        with open(fp, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception:
                continue

        papers = data.get("papers")
        if not isinstance(papers, list):
            continue

        updated = False
        for item in papers:
            if isinstance(item, dict):
                title = item.get("title", "")
                url = item.get("url", "")
                if title and not url:
                    u = CANON.get(norm(title))
                    if u:
                        item["url"] = u
                        updated = True
            elif isinstance(item, str):
                # convert string-only paper entries into dicts if known
                u = CANON.get(norm(item))
                if u:
                    idx = papers.index(item)
                    papers[idx] = {"title": item, "url": u}
                    updated = True

        if updated:
            data["papers"] = papers
            with open(fp, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
            changed.append(fp)
    return changed

if __name__ == "__main__":
    ch = scan_and_fix()
    if ch:
        print("Updated papers with DOIs/URLs in:")
        for p in ch: print(" -", p)
    else:
        print("No changes needed.")
