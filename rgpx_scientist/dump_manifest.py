from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

try:
    from pypdf import PdfReader  # type: ignore
except Exception:
    PdfReader = None  # pages will be omitted if pypdf isn't available


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count(path: Path) -> int | None:
    if PdfReader is None:
        return None
    try:
        reader = PdfReader(str(path))
        return len(reader.pages)
    except Exception:
        return None


def main() -> int:
    here = Path(__file__).resolve().parent                 # .../phi-mesh/rgpx_scientist
    outer_repo_root = here.parent.parent                  # .../ (repo root)
    index_path = here / "foundational_papers_index.yml"

    if not index_path.exists():
        print(f"ERROR: index not found: {index_path}", file=sys.stderr)
        return 2

    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    papers = index.get("foundational_papers", [])

    out_items = []
    missing = []

    for p in papers:
        paper_id = p["paper_id"]
        repo_path = p["repo_path"]                         # e.g. "phi-mesh/foundational_rgp-papers/..."
        pdf_path = outer_repo_root / repo_path

        if not pdf_path.exists():
            missing.append((paper_id, repo_path))
            continue

        b = pdf_path.stat().st_size
        s = sha256_file(pdf_path)
        pc = page_count(pdf_path)

        item = {"paper_id": paper_id, "sha256": s, "bytes": b}
        if pc is not None:
            item["pages"] = pc
        out_items.append(item)

    result = {"foundational_papers": out_items}

    # Print YAML to logs for copy/paste into foundational_papers_manifest.yml
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True).strip())

    if missing:
        print("\n# MISSING FILES (fix index repo_path or upload the PDFs):", file=sys.stderr)
        for paper_id, repo_path in missing:
            print(f"# - {paper_id}: {repo_path}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
