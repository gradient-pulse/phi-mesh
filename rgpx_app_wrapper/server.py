from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
import yaml
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

APP = FastAPI(title="RGPx Wrapper", version="0.1.0")

# GitHub Pages base (good for pulse JSON + generated artifacts)
BASE = "https://gradient-pulse.github.io/phi-mesh"
PULSE_BASE = f"{BASE}/rgpx/pulse"
TAG_INDEX_URL = f"{BASE}/meta/tag_index.yml"
ALIASES_URL = f"{BASE}/meta/aliases.yml"

# Raw GitHub base (good for source files that may not be published to Pages)
TAG_DESCRIPTIONS_URL = "https://raw.githubusercontent.com/gradient-pulse/phi-mesh/main/meta/tag_descriptions.yml"

_cache: Dict[str, Tuple[float, Any]] = {}
CACHE_TTL_S = 300


def _norm(s: str) -> str:
    s = s.strip()
    s = s.replace("–", "-").replace("—", "-")
    s = s.lower()
    s = re.sub(r"[()\[\]{}\"']", "", s)
    s = re.sub(r"\s+", "_", s)
    s = s.replace("-", "_")
    s = re.sub(r"_+", "_", s)
    return s


async def _fetch_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Upstream fetch failed: {url} ({r.status_code})",
            )
        return r.text


async def _cached_yaml(url: str) -> Any:
    now = time.time()
    if url in _cache:
        ts, obj = _cache[url]
        if now - ts < CACHE_TTL_S:
            return obj
    text = await _fetch_text(url)
    obj = yaml.safe_load(text)
    _cache[url] = (now, obj)
    return obj


async def _build_alias_lookup() -> Dict[str, str]:
    data = await _cached_yaml(ALIASES_URL)
    aliases = (data or {}).get("aliases", {}) if isinstance(data, dict) else {}
    lookup: Dict[str, str] = {}

    # canonical keys map to themselves
    for canon in aliases.keys():
        lookup[_norm(canon)] = _norm(canon)

    # variants map to canonical
    for canon, variants in aliases.items():
        canon_n = _norm(canon)
        if not isinstance(variants, list):
            continue
        for v in variants:
            if not isinstance(v, str):
                continue
            lookup[_norm(v)] = canon_n

    return lookup


async def resolve_tag(tag: str) -> str:
    tag_n = _norm(tag)
    lookup = await _build_alias_lookup()
    if tag_n in lookup:
        return lookup[tag_n]
    # fallback: accept already-normalized tags (lets “some AI guess” happen safely)
    return tag_n


def _extract_description(tag_desc_doc: Any, canon: str) -> Optional[str]:
    """
    Supports a few likely schemas for tag_descriptions.yml.

    Examples supported:
      tags:
        my_tag: "string description"
      tags:
        my_tag:
          description: "..."
          summary: "..."
          one_liner: "..."
          text: "..."
      my_tag: "string description"
      my_tag:
        description: "..."
    """
    if not isinstance(tag_desc_doc, dict):
        return None

    # Prefer the common pattern: { tags: { <canon>: ... } }
    candidates: List[Any] = []

    tags_block = tag_desc_doc.get("tags")
    if isinstance(tags_block, dict) and canon in tags_block:
        candidates.append(tags_block.get(canon))

    # Fallback: top-level mapping
    if canon in tag_desc_doc:
        candidates.append(tag_desc_doc.get(canon))

    for desc_obj in candidates:
        if isinstance(desc_obj, str):
            return desc_obj.strip() or None
        if isinstance(desc_obj, dict):
            for k in ("description", "summary", "one_liner", "text"):
                v = desc_obj.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

    return None


@APP.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@APP.get("/getPulse")
async def get_pulse(slug: str = Query(..., min_length=3)) -> JSONResponse:
    url = f"{PULSE_BASE}/{slug}.json"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Pulse not found for slug={slug}")
        return JSONResponse(content=r.json())


@APP.get("/getTag")
async def get_tag(tag: str = Query(..., min_length=2)) -> Dict[str, Any]:
    canon = await resolve_tag(tag)

    tag_index = await _cached_yaml(TAG_INDEX_URL)
    tag_desc_doc = await _cached_yaml(TAG_DESCRIPTIONS_URL)
    description = _extract_description(tag_desc_doc, canon)

    # Expected structure (you already generate it): a mapping tag -> list(slugs) OR tag -> {count, pulses}
    slugs: List[str] = []

    if isinstance(tag_index, dict):
        # common patterns:
        if canon in tag_index and isinstance(tag_index[canon], list):
            slugs = [s for s in tag_index[canon] if isinstance(s, str)]
        elif canon in tag_index and isinstance(tag_index[canon], dict):
            maybe = tag_index[canon].get("pulses") or tag_index[canon].get("slugs") or []
            if isinstance(maybe, list):
                slugs = [s for s in maybe if isinstance(s, str)]
        else:
            # sometimes nested under a top key
            for k in ("tags", "index", "tag_index"):
                if k in tag_index and isinstance(tag_index[k], dict) and canon in tag_index[k]:
                    v = tag_index[k][canon]
                    if isinstance(v, list):
                        slugs = [s for s in v if isinstance(s, str)]
                    elif isinstance(v, dict):
                        maybe = v.get("pulses") or v.get("slugs") or []
                        if isinstance(maybe, list):
                            slugs = [s for s in maybe if isinstance(s, str)]
                    break

    return {"tag": canon, "count": len(slugs), "slugs": slugs, "description": description}
