from fastapi import FastAPI, HTTPException, Query
from pathlib import Path
import yaml
import re
from typing import Any, Dict, List

APP_ROOT = Path(__file__).resolve().parents[1]  # repo root
ALIASES_PATH = APP_ROOT / "meta" / "aliases.yml"
TAG_INDEX_PATH = APP_ROOT / "meta" / "tag_index.yml"
PULSE_DIR = APP_ROOT / "phi-mesh" / "pulse"

app = FastAPI(title="RGPx Repo Wrapper", version="0.1")

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def normalize_tag(s: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", s.strip().lower()).strip("_")

def list_pulse_files() -> List[Path]:
    if not PULSE_DIR.exists():
        return []
    return sorted(PULSE_DIR.glob("*.yml"))

def pulse_slug_from_path(p: Path) -> str:
    return p.stem

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/aliases")
def aliases():
    try:
        data = load_yaml(ALIASES_PATH)
    except FileNotFoundError:
        raise HTTPException(404, f"Missing {ALIASES_PATH}")
    return data

@app.get("/tag_index")
def tag_index():
    try:
        data = load_yaml(TAG_INDEX_PATH)
    except FileNotFoundError:
        raise HTTPException(404, f"Missing {TAG_INDEX_PATH}")
    return data

@app.get("/tag/{tag}")
def get_tag(tag: str):
    t = normalize_tag(tag)
    # Prefer tag_index if present (deterministic “does this exist?”)
    tag_data = {}
    try:
        ti = load_yaml(TAG_INDEX_PATH)
        # common layouts: {tags: {...}} or {...}
        tags_obj = ti.get("tags", ti)
        if isinstance(tags_obj, dict) and t in tags_obj:
            tag_data = tags_obj[t]
    except FileNotFoundError:
        pass

    # aliases are a convenience layer, not authority
    try:
        a = load_yaml(ALIASES_PATH).get("aliases", {})
    except FileNotFoundError:
        a = {}

    alias_list = a.get(t, [])
    return {
        "tag": t,
        "exists_in_tag_index": bool(tag_data),
        "tag_index_record": tag_data,
        "aliases": alias_list,
    }

@app.get("/pulse/{slug}")
def get_pulse(slug: str):
    path = PULSE_DIR / f"{slug}.yml"
    if not path.exists():
        raise HTTPException(404, f"Pulse not found: {slug}")
    data = load_yaml(path)
    data["_slug"] = slug
    return data

@app.get("/tag/{tag}/pulses")
def pulses_for_tag(tag: str):
    t = normalize_tag(tag)
    hits = []
    for p in list_pulse_files():
        y = load_yaml(p)
        tags = y.get("tags", []) or []
        tags_norm = [normalize_tag(x) for x in tags if isinstance(x, str)]
        if t in tags_norm:
            hits.append(pulse_slug_from_path(p))
    return {"tag": t, "slugs": hits, "count": len(hits)}

@app.get("/search")
def search(q: str = Query(..., min_length=2), limit: int = 25):
    """
    Deterministic textual search across pulse YAMLs.
    """
    q_l = q.lower()
    results = []
    for p in list_pulse_files():
        txt = p.read_text(encoding="utf-8", errors="ignore").lower()
        if q_l in txt:
            results.append(pulse_slug_from_path(p))
            if len(results) >= limit:
                break
    return {"q": q, "slugs": results, "count": len(results)}
