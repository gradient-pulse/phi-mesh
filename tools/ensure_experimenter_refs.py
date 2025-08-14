#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autofix ExperimenterPulse references

What it does
- Scans all pulse/**/*.yml (skips archive/ and telemetry/)
- For pulses that include the 'ExperimenterPulse' tag (case-insensitive),
  it ENSURES the canonical papers & podcasts are present (URL-backed only),
  de-duplicates by normalized URL, and WRITES the file back if needed.

Exit code is always 0 (warn-only), so CI doesn't fail.

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

import re
from pathlib import Path
import yaml

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

def _norm_tag(s: str) -> str:
    return re.sub(r"[\s\-]+", "_", (s or "").strip()).casefold()

def _norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    # normalize DOI host
    u = re.sub(r"^https?://(dx\.)?doi\.org/", "https://doi.org/", u, flags=re.I)
    return u.lower()

def _as_dict_items(items):
    """Coerce list items to {url,title?} dicts; drop empties."""
    out = []
    if not items:
        return out
    for it in items:
        if isinstance(it, dict):
            url = (it.get("url") or "").strip()
            if url:
                d = {"url": url}
                if it.get("title"):
                    d["title"] = str(it["title"])
                out.append(d)
        elif isinstance(it, str):
            s = it.strip()
            if s.startswith(("http://", "https://")):
                out.append({"url": s})
    return out

def _dedupe_by_url(items):
    seen, out = set(), []
    for it in items:
        key = _norm_url(it.get("url", ""))
        if key and key not in seen:
            seen.add(key)
            # write back the original URL string (not lowercased), keep title if any
            out.append({"url": it["url"], **({"title": it["title"]} if "title" in it else {})})
    return out

def main():
    repo = Path(__file__).resolve().parents[1]
    pulse_root = repo / "pulse"
    if not pulse_root.exists():
        print("[ensure] No pulse/ directory; nothing to do.")
        return 0

    changed = 0
    for yml in pulse_root.rglob("*.yml"):
        p = yml.as_posix()
        if "/pulse/archive/" in p or "/pulse/telemetry/" in p:
            continue

        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"[ensure] WARN: skip {yml} (bad YAML): {e}")
            continue

        tags = data.get("tags") or data.get("Tags") or []
        tags = [str(t).strip() for t in (tags if isinstance(tags, list) else [tags]) if str(t).strip()]
        if "experimenterpulse" not in {_norm_tag(t) for t in tags}:
            continue  # not an ExperimenterPulse

        # Coerce current lists to dicts
        papers   = _as_dict_items(data.get("papers"))
        podcasts = _as_dict_items(data.get("podcasts"))

        # Merge + dedupe
        merged_papers   = _dedupe_by_url(papers + FOUNDATION_PAPERS)
        merged_podcasts = _dedupe_by_url(podcasts + FOUNDATION_PODCASTS)

        if merged_papers != papers or merged_podcasts != podcasts:
            data["papers"]   = merged_papers
            data["podcasts"] = merged_podcasts
            yml.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
            changed += 1
            print(f"[ensure] UPDATED {yml.relative_to(repo)}")

    print(f"[ensure] Done. Files updated: {changed}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
