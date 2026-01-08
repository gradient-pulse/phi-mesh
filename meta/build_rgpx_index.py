#!/usr/bin/env python3
"""
Build a lightweight, public JSON index for the Phi-Mesh pulses.

Outputs (GitHub Pages via docs/):
  docs/rgpx/index.json
  docs/rgpx/pulse/<slug>.json

Slug = pulse filename without extension.
Date  = inferred from leading YYYY-MM-DD in filename if present.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PULSE_DIR = REPO_ROOT / "pulse"
OUT_DIR = REPO_ROOT / "docs" / "rgpx"
OUT_PULSE_DIR = OUT_DIR / "pulse"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

def safe_str(x: Any) -> str:
    return "" if x is None else str(x)

def safe_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [safe_str(i).strip() for i in x if safe_str(i).strip()]
    # allow single string
    s = safe_str(x).strip()
    return [s] if s else []

def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}

def infer_date_from_filename(name: str) -> Optional[str]:
    m = DATE_RE.match(name)
    return m.group(1) if m else None

def ensure_dirs() -> None:
    OUT_PULSE_DIR.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def build() -> None:
    ensure_dirs()

    pulses_out: List[Dict[str, Any]] = []

    if not PULSE_DIR.exists():
        raise SystemExit(f"Pulse directory not found: {PULSE_DIR}")

    pulse_files = sorted(PULSE_DIR.glob("*.yml"))
    for p in pulse_files:
        slug = p.stem  # filename without extension
        date = infer_date_from_filename(p.name)

        data = load_yaml(p)

        title = safe_str(data.get("title") or data.get("name") or slug)
        summary = safe_str(data.get("summary") or data.get("core_claim") or "")
        tags = safe_list(data.get("tags"))
        papers = safe_list(data.get("papers"))
        podcasts = safe_list(data.get("podcasts"))

        # A compact index record
        rec = {
            "slug": slug,
            "date": date,
            "title": title,
            "tags": tags,
            "summary": summary,
            "papers": papers,
            "podcasts": podcasts,
            "source_path": f"pulse/{p.name}",
        }
        pulses_out.append(rec)

        # Full pulse JSON for deep citation
        full = {
            "slug": slug,
            "date": date,
            "source_path": f"pulse/{p.name}",
            "data": data,
        }
        write_json(OUT_PULSE_DIR / f"{slug}.json", full)

    index = {
        "generated_at": __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "count": len(pulses_out),
        "pulses": pulses_out,
    }
    write_json(OUT_DIR / "index.json", index)

if __name__ == "__main__":
    build()
