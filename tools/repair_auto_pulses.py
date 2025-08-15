#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair auto-generated pulses by removing trailing junk and normalizing tags.

- Operates on pulse/auto/**/*.yml
- Pre-trims tail lines that are just quotes/backticks or the repeated default-tag block
- Parses YAML and rewrites a clean document (idempotent)
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import List
import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "pulse" / "auto"

# The four lines that have been duplicated at the end in some files:
DEFAULT_TAIL = {
    "NT (Narrative_Tick)",
    "Rhythm",
    "NavierStokes",
    "turbulence",
}

CANON_DEFAULTS = [
    "RGP",
    "ExperimenterPulse",
    "Rhythm",
    "Navier_Stokes",
    "turbulence",
    "NT (Narrative_Tick)",
]

def _norm_tag(t: str) -> str:
    t = (t or "").strip()
    if t == "NavierStokes":
        return "Navier_Stokes"
    return t

def dedupe_keep_order(xs: List[str]) -> List[str]:
    seen, out = set(), []
    for x in xs:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out

def _trim_tail_garbage(text: str) -> str:
    lines = text.splitlines()
    # remove trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    # remove trailing lone quotes/backticks
    while lines and lines[-1].strip() in {"'", '"', "`", "```"}:
        lines.pop()

    # remove repeated default-tag blocks at end (any number of lines consisting only of "- <tag>")
    tag_line_re = re.compile(r"^\s*-\s+(.*)\s*$")
    # walk upward while the last line is a default tag
    changed = True
    while changed and lines:
        changed = False
        while lines:
            m = tag_line_re.match(lines[-1])
            if not m:
                break
            last_tag = m.group(1).strip()
            if last_tag in DEFAULT_TAIL:
                lines.pop()
                changed = True
            else:
                break

    return "\n".join(lines) + ("\n" if lines else "")

def repair_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    cleaned_text = _trim_tail_garbage(raw)

    # Try to parse; if it still fails, give up gracefully (we won't worsen it)
    try:
        data = yaml.safe_load(cleaned_text)
    except Exception:
        # One more attempt: parse original (in case we trimmed a needed trailing newline)
        try:
            data = yaml.safe_load(raw)
            cleaned_text = raw
        except Exception as e:
            print(f"[ERR] Cannot parse YAML: {path} → {e}")
            return False

    if not isinstance(data, dict):
        print(f"[skip] Not a mapping: {path}")
        return False

    # normalize tags
    existing = data.get("tags")
    if existing is None:
        tags: List[str] = []
    elif isinstance(existing, list):
        tags = [ _norm_tag(str(t)) for t in existing ]
    else:
        tags = [ _norm_tag(str(existing)) ]

    # add defaults
    for d in CANON_DEFAULTS:
        if d not in tags:
            tags.append(d)

    tags = [ _norm_tag(t) for t in tags ]
    tags = dedupe_keep_order(tags)
    data["tags"] = tags

    # write back clean YAML (blows away any leftover junk safely)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return True

def main():
    if not AUTO.exists():
        print(f"[info] {AUTO} missing — nothing to do.")
        return
    changed = 0
    for y in AUTO.rglob("*.yml"):
        if repair_file(y):
            print(f"[ok] repaired: {y.relative_to(ROOT)}")
            changed += 1
    print(f"[done] repaired {changed} files.")

if __name__ == "__main__":
    main()
