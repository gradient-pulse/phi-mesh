#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]

PAPERS_INDEX_YML = REPO_ROOT / "rgpx_scientist" / "foundational_papers_index.yml"
PAPERS_MANIFEST_YML = REPO_ROOT / "rgpx_scientist" / "foundational_papers_manifest.yml"
CLAIMS_INDEX_YML = REPO_ROOT / "rgpx_scientist" / "foundational_claims_index.yml"

OUT_BASE = REPO_ROOT / "docs" / "rgpx_scientist"

OUT_PAPERS_INDEX_JSON = OUT_BASE / "papers" / "index.json"
OUT_CLAIMS_PAPER_DIR  = OUT_BASE / "claims" / "paper"
OUT_CLAIMS_SINGLE_DIR = OUT_BASE / "claims"  # /{paper_id}/{claim_id}.json


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _as_list(obj):
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("items", "papers", "foundational_papers", "paper_index", "index"):
            v = obj.get(k)
            if isinstance(v, list):
                return v
    return []


def _index_by_paper_id(items: list[dict]) -> dict[str, dict]:
    out = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        pid = it.get("paper_id") or it.get("id") or it.get("paper")
        if isinstance(pid, str) and pid.strip():
            out[pid.strip()] = it
    return out


def _safe_write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    OUT_CLAIMS_PAPER_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CLAIMS_SINGLE_DIR.mkdir(parents=True, exist_ok=True)

    papers_index_raw = _load_yaml(PAPERS_INDEX_YML) if PAPERS_INDEX_YML.exists() else None
    papers_manifest_raw = _load_yaml(PAPERS_MANIFEST_YML) if PAPERS_MANIFEST_YML.exists() else None
    claims_index_raw = _load_yaml(CLAIMS_INDEX_YML) if CLAIMS_INDEX_YML.exists() else None

    papers_index_list = _as_list(papers_index_raw)
    papers_manifest_list = _as_list(papers_manifest_raw)

    papers_index_by_id = _index_by_paper_id(papers_index_list)
    papers_manifest_by_id = _index_by_paper_id(papers_manifest_list)

    # Claims index: usually a list of paper blocks
    claims_papers = _as_list(claims_index_raw)

    # Build papers/index.json
    paper_ids = set(papers_index_by_id.keys()) | set(papers_manifest_by_id.keys())
    # Also include any paper_id present in claims
    for p in claims_papers:
        if isinstance(p, dict) and isinstance(p.get("paper_id"), str):
            paper_ids.add(p["paper_id"])

    items_out: list[dict] = []
    for pid in sorted(paper_ids):
        idx = papers_index_by_id.get(pid, {})
        man = papers_manifest_by_id.get(pid, {})

        title = (idx.get("title") or man.get("title") or "").strip()
        date = (idx.get("date") or man.get("date") or "").strip()
        pdf_url = (idx.get("pdf_url") or man.get("pdf_url") or man.get("url") or idx.get("url") or "").strip()

        items_out.append(
            {
                "paper_id": pid,
                "title": title,
                "date": date,
                "pdf_url": pdf_url,
                "claims_url": f"https://gradient-pulse.github.io/phi-mesh/rgpx/claims/paper/{pid}.json",
            }
        )

    _safe_write_json(
        OUT_PAPERS_INDEX_JSON,
        {"generated_at": _now_iso(), "count": len(items_out), "items": items_out},
    )

    # Build claims/paper/{paper_id}.json and claims/{paper_id}/{claim_id}.json
    for p in claims_papers:
        if not isinstance(p, dict):
            continue
        pid = p.get("paper_id")
        if not isinstance(pid, str) or not pid.strip():
            continue
        pid = pid.strip()

        claim_cards = p.get("claim_cards")
        if not isinstance(claim_cards, list):
            claim_cards = []

        # paper claims file
        paper_payload = {
            "paper_id": pid,
            "generated_at": _now_iso(),
            "count": len(claim_cards),
            "claim_cards": claim_cards,
        }
        _safe_write_json(OUT_CLAIMS_PAPER_DIR / f"{pid}.json", paper_payload)

        # single-claim files
        for cc in claim_cards:
            if not isinstance(cc, dict):
                continue
            cid = cc.get("claim_id")
            if not isinstance(cid, str) or not cid.strip():
                continue
            cid = cid.strip()
            single_path = OUT_CLAIMS_SINGLE_DIR / pid / f"{cid}.json"
            _safe_write_json(
                single_path,
                {
                    "paper_id": pid,
                    "claim_id": cid,
                    "generated_at": _now_iso(),
                    "claim_card": cc,
                },
            )

    print("OK: wrote papers + claims JSON into docs/rgpx_scientist/")

if __name__ == "__main__":
    main()
