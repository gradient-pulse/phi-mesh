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
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


INDEX_FILENAME = "foundational_papers_index.yml"
MANIFEST_FILENAME = "foundational_papers_manifest.yml"


@dataclass(frozen=True)
class PaperIndexEntry:
    paper_id: str
    repo_path: str  # path inside repo, e.g. "phi-mesh/foundational_rgp-papers/....pdf"


@dataclass(frozen=True)
class PaperManifestEntry:
    paper_id: str
    sha256: str
    bytes: int
    pages: Optional[int] = None


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _try_pdf_page_count(path: Path) -> Optional[int]:
    # Optional dependency: pypdf or PyPDF2
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
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
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


def _infer_repo_root(script_path: Path) -> Path:
    # Expected location: <repo_root>/phi-mesh/rgpx_scientist/verify_corpus.py
    # So repo_root = script_path.parents[2]
    try:
        repo_root = script_path.resolve().parents[2]
    except Exception:
        repo_root = Path.cwd().resolve()
    return repo_root


def verify(repo_root: Path, strict_pages: bool = False) -> Tuple[bool, List[str], List[str]]:
    """
    Returns: (ok, errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    index_path = repo_root / "phi-mesh" / "rgpx_scientist" / INDEX_FILENAME
    manifest_path = repo_root / "phi-mesh" / "rgpx_scientist" / MANIFEST_FILENAME

    if not index_path.exists():
        errors.append(f"Missing index file: {index_path}")
        return False, errors, warnings
    if not manifest_path.exists():
        errors.append(f"Missing manifest file: {manifest_path}")
        return False, errors, warnings

    index_data = _load_yaml(index_path)
    manifest_data = _load_yaml(manifest_path)

    index_entries = _parse_index(index_data)
    manifest_map = _parse_manifest(manifest_data)

    # Cross-check: every index paper must be in manifest, and vice versa
    index_ids = {e.paper_id for e in index_entries}
    manifest_ids = set(manifest_map.keys())

    missing_in_manifest = sorted(index_ids - manifest_ids)
    extra_in_manifest = sorted(manifest_ids - index_ids)

    if missing_in_manifest:
        errors.append(f"Manifest missing paper_id(s) present in index: {missing_in_manifest}")
    if extra_in_manifest:
        errors.append(f"Manifest contains paper_id(s) not present in index: {extra_in_manifest}")

    # Determine whether we can page-check
    can_page_check = False
    if strict_pages:
        can_page_check = True
    else:
        # probe once
        probe = None
        for e in index_entries:
            probe = repo_root / e.repo_path
            if probe.exists():
                break
        if probe and probe.exists():
            can_page_check = _try_pdf_page_count(probe) is not None

    if strict_pages and not can_page_check:
        warnings.append("Strict page checking requested, but PDF reader not available (install `pypdf`).")
        # still continue; will fail per-file below if pages are required

    for e in index_entries:
        m = manifest_map.get(e.paper_id)
        if m is None:
            # already reported in cross-check
            continue

        pdf_path = repo_root / e.repo_path

        if not pdf_path.exists():
            errors.append(f"[{e.paper_id}] Missing PDF at repo_path: {e.repo_path}")
            continue

        # bytes
        actual_bytes = pdf_path.stat().st_size
        if actual_bytes != m.bytes:
            errors.append(f"[{e.paper_id}] bytes mismatch: manifest={m.bytes} actual={actual_bytes}")

        # sha256
        actual_sha = _sha256_file(pdf_path)
        if actual_sha.lower() != m.sha256.lower():
            errors.append(f"[{e.paper_id}] sha256 mismatch: manifest={m.sha256} actual={actual_sha}")

        # pages (optional)
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

    ok = len(errors) == 0
    return ok, errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify RGPx Scientist frozen corpus integrity.")
    ap.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Path to repository root (default: infer from script location).",
    )
    ap.add_argument(
        "--strict-pages",
        action="store_true",
        help="Fail if page count cannot be verified or does not match.",
    )
    args = ap.parse_args()

    script_path = Path(__file__)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else _infer_repo_root(script_path)

    ok, errors, warnings = verify(repo_root=repo_root, strict_pages=args.strict_pages)

    print(f"Repo root: {repo_root}")
    print(f"Index:     {repo_root / 'phi-mesh' / 'rgpx_scientist' / INDEX_FILENAME}")
    print(f"Manifest:  {repo_root / 'phi-mesh' / 'rgpx_scientist' / MANIFEST_FILENAME}")
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
