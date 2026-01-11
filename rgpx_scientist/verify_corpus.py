#!/usr/bin/env python3
"""
verify_corpus.py — RGPx Scientist corpus verifier

Hard checks:
  - every indexed PDF exists
  - file size (bytes) matches manifest
  - sha256 matches manifest

Soft/optional:
  - PDF page count matches manifest (only if pypdf/PyPDF2 is installed)

Exit codes:
  0 = all good
  2 = verification failed
  3 = config/index/manifest load error
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

INDEX_FILENAME = "foundational_papers_index.yml"
MANIFEST_FILENAME = "foundational_papers_manifest.yml"


@dataclass(frozen=True)
class PaperIndexEntry:
    paper_id: str
    repo_path: str


@dataclass(frozen=True)
class PaperManifestEntry:
    paper_id: str
    sha256: str
    bytes: int
    pages: Optional[int] = None


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _try_pdf_page_count(path: Path) -> Optional[int]:
    try:
        from pypdf import PdfReader  # type: ignore
        return len(PdfReader(str(path)).pages)
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore
        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("YAML root must be a mapping/dict.")
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to load YAML: {path} ({e})") from e


def _parse_index(data: Dict[str, Any]) -> List[PaperIndexEntry]:
    raw = data.get("foundational_papers")
    if not isinstance(raw, list):
        raise ValueError("Index must contain key `foundational_papers:` as a list.")
    out: List[PaperIndexEntry] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Index entry #{i} is not a dict.")
        pid = item.get("paper_id")
        rpath = item.get("repo_path")
        if not isinstance(pid, str) or not pid.strip():
            raise ValueError(f"Index entry #{i} missing/invalid `paper_id`.")
        if not isinstance(rpath, str) or not rpath.strip():
            raise ValueError(f"Index entry #{i} missing/invalid `repo_path`.")
        out.append(PaperIndexEntry(paper_id=pid.strip(), repo_path=rpath.strip()))
    return out


def _parse_manifest(data: Dict[str, Any]) -> Dict[str, PaperManifestEntry]:
    raw = data.get("foundational_papers")
    if not isinstance(raw, list):
        raise ValueError("Manifest must contain key `foundational_papers:` as a list.")
    out: Dict[str, PaperManifestEntry] = {}
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Manifest entry #{i} is not a dict.")
        pid = item.get("paper_id")
        sha = item.get("sha256")
        bts = item.get("bytes")
        pgs = item.get("pages", None)

        if not isinstance(pid, str) or not pid.strip():
            raise ValueError(f"Manifest entry #{i} missing/invalid `paper_id`.")
        if not isinstance(sha, str) or len(sha.strip()) != 64:
            raise ValueError(f"Manifest entry #{i} missing/invalid `sha256` (expect 64 hex chars).")
        if not isinstance(bts, int) or bts <= 0:
            raise ValueError(f"Manifest entry #{i} missing/invalid `bytes` (expect positive int).")
        if pgs is not None and (not isinstance(pgs, int) or pgs <= 0):
            raise ValueError(f"Manifest entry #{i} invalid `pages` (expect positive int).")

        pid = pid.strip()
        if pid in out:
            raise ValueError(f"Duplicate `paper_id` in manifest: {pid}")
        out[pid] = PaperManifestEntry(
            paper_id=pid,
            sha256=sha.strip().lower(),
            bytes=bts,
            pages=pgs,
        )
    return out


def _detect_layout(start: Path) -> Tuple[Path, Path]:
    """
    Returns (repo_root, project_root).

    repo_root: top checkout root
    project_root: either repo_root (Layout A) or repo_root/'phi-mesh' (Layout B)
    """
    start = start.resolve()
    for cand in [start] + list(start.parents)[:8]:
        # Layout A
        if (cand / "rgpx_scientist" / INDEX_FILENAME).exists():
            return cand, cand
        # Layout B
        if (cand / "phi-mesh" / "rgpx_scientist" / INDEX_FILENAME).exists():
            return cand, cand / "phi-mesh"
    raise RuntimeError("Could not detect project layout (no rgpx_scientist/foundational_papers_index.yml found).")


def _resolve_pdf(repo_root: Path, project_root: Path, repo_path: str) -> Optional[Path]:
    """
    Try to resolve repo_path against repo_root first (recommended),
    then against project_root (fallback for nested layouts).
    """
    p = Path(repo_path)
    candidates = [
        (repo_root / p),
        (project_root / p),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def verify(repo_root: Path, project_root: Path, strict_pages: bool = False) -> Tuple[bool, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    index_path = project_root / "rgpx_scientist" / INDEX_FILENAME
    manifest_path = project_root / "rgpx_scientist" / MANIFEST_FILENAME

    if not index_path.exists():
        errors.append(f"Missing index file: {index_path}")
        return False, errors, warnings
    if not manifest_path.exists():
        errors.append(f"Missing manifest file: {manifest_path}")
        return False, errors, warnings

    index_entries = _parse_index(_load_yaml(index_path))
    manifest_map = _parse_manifest(_load_yaml(manifest_path))

    index_ids = {e.paper_id for e in index_entries}
    manifest_ids = set(manifest_map.keys())

    missing_in_manifest = sorted(index_ids - manifest_ids)
    extra_in_manifest = sorted(manifest_ids - index_ids)

    if missing_in_manifest:
        errors.append(f"Manifest missing paper_id(s) present in index: {missing_in_manifest}")
    if extra_in_manifest:
        errors.append(f"Manifest contains paper_id(s) not present in index: {extra_in_manifest}")

    for e in index_entries:
        m = manifest_map.get(e.paper_id)
        if m is None:
            continue

        pdf_path = _resolve_pdf(repo_root, project_root, e.repo_path)
        if pdf_path is None:
            errors.append(f"[{e.paper_id}] Missing PDF at repo_path: {e.repo_path}")
            continue

        actual_bytes = pdf_path.stat().st_size
        if actual_bytes != m.bytes:
            errors.append(f"[{e.paper_id}] bytes mismatch: manifest={m.bytes} actual={actual_bytes}")

        actual_sha = _sha256_file(pdf_path)
        if actual_sha.lower() != m.sha256.lower():
            errors.append(f"[{e.paper_id}] sha256 mismatch: manifest={m.sha256} actual={actual_sha}")

        if m.pages is not None:
            page_count = _try_pdf_page_count(pdf_path)
            if page_count is None:
                msg = f"[{e.paper_id}] pages check skipped (install `pypdf` to enable)."
                if strict_pages:
                    errors.append(msg.replace("skipped", "FAILED (required)"))
                else:
                    warnings.append(msg)
            else:
                if page_count != m.pages:
                    errors.append(f"[{e.paper_id}] pages mismatch: manifest={m.pages} actual={page_count}")

    return len(errors) == 0, errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify RGPx Scientist frozen corpus integrity.")
    ap.add_argument("--repo-root", type=str, default=None, help="Path to repository root (optional).")
    ap.add_argument("--strict-pages", action="store_true", help="Fail if page count cannot be verified or does not match.")
    args = ap.parse_args()

    script_path = Path(__file__).resolve()
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
        # derive project root from that
        _, project_root = _detect_layout(repo_root)
    else:
        repo_root, project_root = _detect_layout(script_path.parent)

    ok, errors, warnings = verify(repo_root=repo_root, project_root=project_root, strict_pages=args.strict_pages)

    print(f"Repo root:    {repo_root}")
    print(f"Project root: {project_root}")
    print(f"Index:        {project_root / 'rgpx_scientist' / INDEX_FILENAME}")
    print(f"Manifest:     {project_root / 'rgpx_scientist' / MANIFEST_FILENAME}")
    print("")

    for w in warnings:
        print(f"WARNING: {w}")

    if not ok:
        print("")
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\nRESULT: FAIL ({len(errors)} error(s))")
        return 2

    print("RESULT: PASS (corpus verified)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(3)
