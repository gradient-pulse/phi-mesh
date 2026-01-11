#!/usr/bin/env python3
"""
dump_manifest.py — regenerate foundational_papers_manifest.yml from PDFs

Goal:
- Print ONLY valid YAML to stdout (safe to copy/paste into the manifest file).
- Send any PDF parser noise (e.g. "Ignoring wrong pointing object ...") to stderr.

Exit codes:
  0 = ok (YAML emitted)
  2 = index missing / load error
  3 = one or more PDFs missing (YAML still emitted for the ones found)
"""

from __future__ import annotations

import hashlib
import io
import sys
import warnings
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

import yaml

try:
    from pypdf import PdfReader  # type: ignore
except Exception:
    PdfReader = None  # pages will be omitted if pypdf isn't available


INDEX_FILENAME = "foundational_papers_index.yml"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_page_count(path: Path) -> int | None:
    """
    Return page count if possible.
    Suppress/redirect any noisy output from PDF parsing to stderr,
    and never pollute stdout (stdout must remain pure YAML).
    """
    if PdfReader is None:
        return None

    buf_out = io.StringIO()
    buf_err = io.StringIO()

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # pypdf can print/log odd messages; keep them off stdout.
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                reader = PdfReader(str(path))
                n = len(reader.pages)
    except Exception:
        n = None

    # Forward any captured noise to stderr (optional, but keeps logs honest)
    noise = (buf_out.getvalue() + buf_err.getvalue()).strip()
    if noise:
        print(noise, file=sys.stderr)

    return n


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to read YAML: {path} ({e})") from e
    if not isinstance(data, dict):
        raise RuntimeError(f"YAML root must be a mapping/dict: {path}")
    return data


def find_repo_root_and_index(script_path: Path) -> tuple[Path, Path]:
    """
    Supports either layout:
      A) <repo_root>/phi-mesh/rgpx_scientist/foundational_papers_index.yml
      B) <repo_root>/rgpx_scientist/foundational_papers_index.yml
    by walking up from the script location.
    """
    start = script_path.resolve().parent
    for base in [start] + list(start.parents)[:6]:
        idx_a = base / "phi-mesh" / "rgpx_scientist" / INDEX_FILENAME
        if idx_a.exists():
            return base, idx_a

        idx_b = base / "rgpx_scientist" / INDEX_FILENAME
        if idx_b.exists():
            return base, idx_b

    # fallback: try cwd-based probes (useful in Actions if script is invoked oddly)
    cwd = Path.cwd().resolve()
    idx_a = cwd / "phi-mesh" / "rgpx_scientist" / INDEX_FILENAME
    if idx_a.exists():
        return cwd, idx_a
    idx_b = cwd / "rgpx_scientist" / INDEX_FILENAME
    if idx_b.exists():
        return cwd, idx_b

    raise FileNotFoundError("Could not locate foundational_papers_index.yml in expected locations.")


def main() -> int:
    script_path = Path(__file__)
    try:
        repo_root, index_path = find_repo_root_and_index(script_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    try:
        index = _load_yaml_mapping(index_path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    papers = index.get("foundational_papers", [])
    if not isinstance(papers, list):
        print(f"ERROR: `foundational_papers` must be a list in {index_path}", file=sys.stderr)
        return 2

    out_items: list[dict[str, Any]] = []
    missing: list[tuple[str, str]] = []

    for i, p in enumerate(papers):
        if not isinstance(p, dict):
            print(f"WARNING: index entry #{i} is not a dict; skipping", file=sys.stderr)
            continue

        paper_id = p.get("paper_id")
        repo_path = p.get("repo_path")

        if not isinstance(paper_id, str) or not paper_id.strip():
            print(f"WARNING: index entry #{i} missing/invalid paper_id; skipping", file=sys.stderr)
            continue
        if not isinstance(repo_path, str) or not repo_path.strip():
            print(f"WARNING: index entry #{i} missing/invalid repo_path; skipping", file=sys.stderr)
            continue

        pdf_path = repo_root / repo_path

        if not pdf_path.exists():
            missing.append((paper_id, repo_path))
            continue

        b = pdf_path.stat().st_size
        s = sha256_file(pdf_path)
        pc = safe_page_count(pdf_path)

        item: dict[str, Any] = {"paper_id": paper_id, "sha256": s, "bytes": b}
        if pc is not None:
            item["pages"] = pc
        out_items.append(item)

    result = {"foundational_papers": out_items}

    # CRITICAL: stdout must be YAML only (no banners, no warnings).
    sys.stdout.write(yaml.safe_dump(result, sort_keys=False, allow_unicode=True).strip() + "\n")

    if missing:
        print("\n# MISSING FILES (fix index repo_path or upload the PDFs):", file=sys.stderr)
        for paper_id, repo_path in missing:
            print(f"# - {paper_id}: {repo_path}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
