from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


def utc_now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]  # .../phi-mesh
    docs_rgpx = repo_root / "docs" / "rgpx"
    pulse_dir = docs_rgpx / "pulse"
    tag_dir = docs_rgpx / "tag"

    if not pulse_dir.exists():
        raise SystemExit(f"Missing pulse dir: {pulse_dir} (did build_rgpx_index run?)")

    records = []
    tag_map: dict[str, list[dict]] = {}

    for p in sorted(pulse_dir.glob("*.json")):
        data = read_json(p)

        # Support either top-level fields or nested "data" block
        d = data.get("data", {}) if isinstance(data, dict) else {}
        slug = data.get("slug") or p.stem
        date = data.get("date") or d.get("date") or ""
        title = d.get("title") or data.get("title") or slug
        tags = d.get("tags") or data.get("tags") or []

        rec = {
            "slug": slug,
            "date": date,
            "title": title,
            "tags": tags,
        }
        records.append(rec)

        for t in tags:
            tag_map.setdefault(t, []).append({"slug": slug, "date": date, "title": title})

    # 1) index_min.json (small enough for Actions)
    index_min = {
        "generated_at": utc_now_z(),
        "count": len(records),
        "items": records,  # minimal: slug/date/title/tags only
    }
    write_json(docs_rgpx / "index_min.json", index_min)

    # 2) per-tag slices: rgpx/tag/<tag>.json
    tag_dir.mkdir(parents=True, exist_ok=True)

    for tag, items in tag_map.items():
        # Keep filename = tag verbatim (your tags are underscore-safe).
        # If you ever introduce "/" in tags, we’ll add a sanitizer + mapping file.
        out = {
            "generated_at": utc_now_z(),
            "tag": tag,
            "count": len(items),
            "items": items,
        }
        write_json(tag_dir / f"{tag}.json", out)

    print(f"Wrote index_min.json and {len(tag_map)} tag slices.")


if __name__ == "__main__":
    main()
