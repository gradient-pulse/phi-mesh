#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair auto pulses:
- Only process pulse/auto/**/*.yml
- Ensure '---' document start
- Quote ISO-8601 date strings
- Trim accidental tails after podcasts
- Normalize/unique tags and add default auto tags (idempotent)
"""

from __future__ import annotations
import re, sys, glob
from pathlib import Path
from typing import Any, List
import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTO_GLOB = str(ROOT / "pulse" / "auto" / "**" / "*.yml")

DEFAULT_AUTO_TAGS = [
    "RGP",
    "NT (Narrative_Tick)",
    "Rhythm",
    "NavierStokes",
    "turbulence",
    "ExperimenterPulse",
]

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

def load_yaml_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def ensure_doc_start(text: str) -> str:
    t = text.lstrip()
    if not t.startswith("---\n"):
        return "---\n" + text
    return text

def quote_date_scalar(val: Any) -> Any:
    if isinstance(val, str) and ISO_DATE_RE.match(val):
        # ensure it stays quoted in dumper: wrap with yaml scalar style by just keeping it a string;
        # PyYAML will sometimes drop quotes, so we force a custom representer if needed.
        return val
    return val

def sanitize_tail(text: str) -> str:
    """
    Removes repeated '- TAG' tails appended after the podcasts list.
    Heuristic: after 'podcasts:' block, if we find a long run of bare '- ' lines with
    known default tags, truncate at the end of the expected list.
    """
    lines = text.splitlines()
    out = []
    in_tail = False
    tail_run = 0

    def is_tail_line(s: str) -> bool:
        s = s.strip()
        if not s.startswith("- "): return False
        tag = s[2:].strip()
        # treat any of our default tags (and dupes) as tail candidates
        return tag in DEFAULT_AUTO_TAGS

    i = 0
    # crude: after 'podcasts:' we allow url items; once we hit a run of just tag lines at root indent, we stop
    while i < len(lines):
        line = lines[i]
        out.append(line)
        # If we detect a long sequence of just "- TAG" lines at column 0, consider it garbage tail
        if line.startswith("- ") and is_tail_line(line) and (i > 5):  # avoid header area
            tail_run += 1
            # if we see more than 3 in a row, it's almost certainly the tail we want to drop entirely
            j = i
            while j < len(lines) and lines[j].startswith("- ") and is_tail_line(lines[j]):
                j += 1
                tail_run += 1
            # drop the tail
            out = out[:-1]  # remove the first tail line we appended
            break
        i += 1

    return "\n".join(out).rstrip() + "\n"

# Force PyYAML to always quote date scalars if they look like ISO timestamps
def str_representer(dumper, data):
    # If it matches ISO-8601 Zulu, force single quotes
    if ISO_DATE_RE.match(data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_representer)

def normalize_tags(tags: Any) -> List[str]:
    arr = []
    if isinstance(tags, list):
        for t in tags:
            if not t: continue
            if isinstance(t, str):
                arr.append(t.strip())
            else:
                arr.append(str(t))
    # unique, keep order
    seen = set()
    dedup = []
    for t in arr:
        if t not in seen:
            seen.add(t)
            dedup.append(t)
    # ensure defaults present (without duplicating)
    for t in DEFAULT_AUTO_TAGS:
        if t not in seen:
            dedup.append(t)
    return dedup

def repair_file(path: Path) -> bool:
    raw = load_yaml_text(path)
    fixed = ensure_doc_start(raw)
    fixed = sanitize_tail(fixed)

    changed = (fixed != raw)

    # Parse as YAML (may still fail, e.g., if head malformed)
    try:
        data = yaml.safe_load(fixed) or {}
        if not isinstance(data, dict):
            # start a minimal skeleton if file was garbage
            data = {}
            changed = True
    except Exception:
        # try one last time with only head portion (99% of cases already handled by sanitize_tail)
        # if still bad, raise to let the validator catch it
        data = yaml.safe_load(ensure_doc_start(raw.split("\n\n")[0] + "\n")) or {}
        changed = True

    # Normalize keys we care about
    title = data.get("title")
    date  = quote_date_scalar(data.get("date"))
    tags  = normalize_tags(data.get("tags", []))
    summary = data.get("summary", "")
    papers = data.get("papers", [])
    podcasts = data.get("podcasts", [])

    # Reassemble clean dict in a stable order
    clean = {
        "title": title or f"Auto Pulse",
        "date": date or "",
        "tags": tags,
        "summary": summary or "",
        "papers": papers or [],
        "podcasts": podcasts or [],
    }

    dumped = yaml.safe_dump(clean, sort_keys=False, allow_unicode=True)
    dumped = ensure_doc_start(dumped)

    if dumped != raw:
        path.write_text(dumped, encoding="utf-8")
        return True
    return changed

def main():
    changed_any = False
    for p in glob.glob(AUTO_GLOB, recursive=True):
        pth = Path(p)
        # skip archive/telemetry if user accidentally placed auto files there
        s = pth.as_posix()
        if "/archive/" in s or "/telemetry/" in s:
            continue
        try:
            if repair_file(pth):
                print(f"[repair] {pth.relative_to(ROOT)}")
                changed_any = True
        except Exception as e:
            print(f"[repair:WARN] {pth}: {e}", file=sys.stderr)
    if not changed_any:
        print("No auto-pulse repairs needed.")

if __name__ == "__main__":
    main()
