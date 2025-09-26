#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair auto pulses:
- Parse & normalize YAML in pulse/auto/**/*.yml(yaml)
- Recover from malformed files by regex-extracting core fields
- Canonicalize tags via meta/aliases.yml
- Enforce default auto tags (no duplicates)
- Keep only URL-backed papers/podcasts
- Trim stray backticks in summary
- Write clean YAML with document start (---)

Safe to run repeatedly (idempotent).
"""

from __future__ import annotations
import re
import sys
import glob
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTO_DIRS = [ROOT / "pulse" / "auto"]

ALIASES_PATH = ROOT / "meta" / "aliases.yml"

# Your canonical defaults for *auto* pulses only
DEFAULT_AUTO_TAGS = [
    "RGP",
    "NT (Narrative_Tick)",
    "Rhythm",
    "Navier_Stokes",
    "turbulence",
    "ExperimenterPulse",
]

# ----------------------------- alias helpers -----------------------------

def load_aliases(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("aliases") or {}
    except Exception:
        return {}

def build_alias_index(spec: Dict[str, List[str]]) -> Dict[str, str]:
    """Map every alias (and a normalized key) to its canonical."""
    idx: Dict[str, str] = {}
    def norm(s: str) -> str:
        return re.sub(r"[\s_\-]+", "_", str(s)).strip().casefold()
    for canonical, aliases in (spec or {}).items():
        if not canonical:
            continue
        c = str(canonical)
        idx[c] = c
        idx[norm(c)] = c
        for a in (aliases or []):
            if not a:
                continue
            a = str(a)
            idx[a] = c
            idx[norm(a)] = c
    return idx

def canon_tag(tag: str, idx: Dict[str, str]) -> str:
    if not isinstance(tag, str):
        return tag
    if tag in idx:
        return idx[tag]
    key = re.sub(r"[\s_\-]+", "_", tag).strip().casefold()
    return idx.get(key, tag)

# ----------------------------- yaml utils --------------------------------

def yaml_load_safe(text: str) -> Dict[str, Any]:
    return yaml.safe_load(text) or {}

def yaml_dump_doc(data: Dict[str, Any]) -> str:
    # Force document start (---) and keep unicode
    dumped = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=10000,  # don't fold URLs
    )
    if not dumped.startswith("---"):
        dumped = "---\n" + dumped
    return dumped

# ----------------------------- sanitizers --------------------------------

def strip_stray_ticks(s: str | None) -> str:
    if not s:
        return ""
    s = str(s).strip()
    # remove leading/trailing backticks (single or triple)
    s = re.sub(r"^\s*`+|\s*`+\s*$", "", s)
    # collapse internal triple backticks accidentals
    s = s.replace("```", "").strip()
    return s

def url_only_items(items: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not items:
        return out
    for x in items:
        if isinstance(x, str):
            u = x.strip()
            if u.startswith(("http://", "https://")):
                out.append({"url": u})
        elif isinstance(x, dict):
            u = str(x.get("url") or "").strip()
            if u.startswith(("http://", "https://")):
                item = {"url": u}
                ttl = x.get("title")
                if ttl:
                    item["title"] = str(ttl)
                out.append(item)
    # dedupe by lowercased url
    seen = set()
    deduped = []
    for it in out:
        u = it["url"].lower()
        if u not in seen:
            seen.add(u)
            deduped.append(it)
    return deduped

def ensure_list_of_str(x: Any) -> List[str]:
    if not x:
        return []
    if isinstance(x, str):
        return [x]
    return [str(t) for t in x if isinstance(t, (str, int, float))]

def uniq(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out

# ----------------------- broken YAML recovery ----------------------------

_TOP_KEY_RE = re.compile(r"^(title|date|tags|summary|papers|podcasts|status)\s*:\s*(.*)$")

def recover_fields_from_text(text: str) -> Dict[str, Any]:
    """
    Best-effort extractor for badly-formed auto pulses.
    Looks for top-level blocks and ignores trailing garbage.
    """
    lines = text.splitlines()
    cur_key = None
    blocks: Dict[str, List[str]] = {}
    for ln in lines:
        m = _TOP_KEY_RE.match(ln.strip())
        if m:
            cur_key = m.group(1)
            blocks.setdefault(cur_key, [])
            # keep inline part on same line if provided
            inline = m.group(2).strip()
            if inline not in ("", "|", ">"):
                blocks[cur_key].append(inline)
            continue
        if cur_key is None:
            continue
        # stop capturing if we hit a new document start
        if ln.strip().startswith("---"):
            break
        blocks[cur_key].append(ln)

    def parse_scalar(block: List[str]) -> str:
        s = "\n".join(block).strip()
        # remove YAML chomping indicators if present
        s = re.sub(r"^[\|\>]\s*", "", s)
        return s.strip()

    def parse_list(block: List[str]) -> List[str]:
        out = []
        for b in block:
            m = re.match(r"^\s*-\s*(.+)$", b)
            if m:
                out.append(m.group(1).strip())
        return out

    def parse_items(block: List[str]) -> List[Dict[str, str]]:
        # handle forms like:
        # - title: ...
        #   url: ...
        # - url: ...
        items = []
        cur: Dict[str, str] = {}
        for ln in block:
            if re.match(r"^\s*-\s", ln):
                # start of new item
                if cur:
                    items.append(cur); cur = {}
                kv = re.match(r"^\s*-\s*(\w+)\s*:\s*(.+)$", ln)
                if kv:
                    cur[kv.group(1)] = kv.group(2).strip()
                else:
                    # could be "- http://..." (string form)
                    u = ln.strip()[1:].strip()
                    if u.startswith(("http://", "https://")):
                        cur = {"url": u}
            else:
                kv = re.match(r"^\s*(\w+)\s*:\s*(.+)$", ln)
                if kv:
                    cur[kv.group(1)] = kv.group(2).strip()
        if cur:
            items.append(cur)
        return items

    data: Dict[str, Any] = {}
    if "title" in blocks:   data["title"] = parse_scalar(blocks["title"])
    if "date" in blocks:    data["date"] = parse_scalar(blocks["date"])
    if "summary" in blocks: data["summary"] = parse_scalar(blocks["summary"])
    if "tags" in blocks:    data["tags"] = parse_list(blocks["tags"])
    if "papers" in blocks:  data["papers"] = parse_items(blocks["papers"])
    if "podcasts" in blocks: data["podcasts"] = parse_items(blocks["podcasts"])
    return data

def load_pulse(path: Path) -> Dict[str, Any]:
    txt = path.read_text(encoding="utf-8")
    try:
        return yaml_load_safe(txt)
    except Exception:
        # try recovery
        rec = recover_fields_from_text(txt)
        if rec:
            return rec
        raise

# ----------------------------- main fixup --------------------------------

def fix_one(path: Path, alias_idx: Dict[str, str]) -> Tuple[bool, str]:
    orig_text = path.read_text(encoding="utf-8")
    try:
        data = load_pulse(path)
    except Exception as e:
        return False, f"FAIL parse {path.name}: {e}"

    changed = False

    # Normalize core fields
    title = str(data.get("title") or "").strip()
    date  = str(data.get("date") or "").strip()
    status = data.get("status") or "auto"

    summary = strip_stray_ticks(data.get("summary"))
    if summary != (data.get("summary") or ""):
        data["summary"] = summary
        changed = True

    # Tags
    tags = ensure_list_of_str(data.get("tags"))
    if "ExperimenterPulse" in tags or path.as_posix().startswith((ROOT/"pulse/auto").as_posix()):
        # Canonicalize and ensure defaults (for auto pulses)
        tags = [canon_tag(t, alias_idx) for t in tags]
        for t in DEFAULT_AUTO_TAGS:
            if t not in tags:
                tags.append(t)
        tags = uniq(tags)
        data["tags"] = tags
        changed = True

    # Papers / Podcasts: URL backed only + dedupe
    papers = url_only_items(data.get("papers"))
    podcasts = url_only_items(data.get("podcasts"))
    if papers != (data.get("papers") or []) or podcasts != (data.get("podcasts") or []):
        data["papers"] = papers
        data["podcasts"] = podcasts
        changed = True

    # Reassign normalized scalars
    if title and data.get("title") != title:
        data["title"] = title; changed = True
    if date and data.get("date") != date:
        data["date"] = date; changed = True
    if status and data.get("status") != status:
        data["status"] = status; changed = True

    # Write back if changed or if original text didn’t start with '---'
    needs_docstart = not orig_text.lstrip().startswith("---")
    if changed or needs_docstart:
        clean = yaml_dump_doc({
            k: data[k] for k in (
                "title","date","tags","summary","papers","podcasts","status"
            ) if k in data
        })
        path.write_text(clean, encoding="utf-8")
        return True, f"fixed {path.name}"
    return False, f"ok {path.name} (no changes)"

def main() -> None:
    aliases = load_aliases(ALIASES_PATH)
    alias_idx = build_alias_index(aliases)

    any_changed = False
    processed = 0
    for base in AUTO_DIRS:
        for fp in glob.glob(str(base / "**" / "*.yml"), recursive=True) + \
                  glob.glob(str(base / "**" / "*.yaml"), recursive=True):
            p = Path(fp)
            changed, msg = fix_one(p, alias_idx)
            print(msg)
            any_changed = any_changed or changed
            processed += 1

    print(f"[repair] processed={processed}, changed={any_changed}")

if __name__ == "__main__":
    main()
