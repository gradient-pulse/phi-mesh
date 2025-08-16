#!/usr/bin/env python3
"""
Clean pulses to a minimal schema:

Kept keys (in this order of insertion):
  - title (str, fallback to filename)
  - date  (str; left as-is)
  - summary (str, folded; empty -> "")
  - tags (list[str], flattened, de-duped, trimmed)
  - papers (list[str] URLs or DOIs; dedup)
  - podcasts (list[str] URLs; dedup)

Everything else is removed.

Also fixes a common failure mode where the YAML top-level is a LIST
(e.g. starting with "- title: ..."). If it's a single-item list that
is a mapping, we unwrap it; otherwise we skip with a warning.
"""

import argparse
import glob
import os
import sys
import yaml

ALLOWED_KEYS = ("title", "date", "summary", "tags", "papers", "podcasts")


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path, data):
    # Regular dicts in Python 3.10+ preserve insertion order.
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            dict(data),
            f,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
            default_flow_style=False,
        )


def norm_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def flatten_tags(value):
    """Flatten/trim/de-dup tags; only strings make it through."""
    out = []
    seen = set()
    for item in norm_list(value):
        if isinstance(item, list):
            for s in item:
                if isinstance(s, str):
                    s2 = s.strip()
                    if s2 and s2 not in seen:
                        out.append(s2)
                        seen.add(s2)
        elif isinstance(item, str):
            s2 = item.strip()
            if s2 and s2 not in seen:
                out.append(s2)
                seen.add(s2)
        # ignore dicts/others
    return out


def extract_urls(items):
    """
    Accept either:
      - list[str] (URLs/DOIs)
      - list[dict] with 'url' or 'doi'
    Return list[str] (dedup, trimmed).
    """
    out, seen = [], set()
    for it in norm_list(items):
        s = None
        if isinstance(it, str):
            s = it.strip()
        elif isinstance(it, dict):
            # prefer url; fall back to doi
            if it.get("url"):
                s = str(it["url"]).strip()
            elif it.get("doi"):
                s = "https://doi.org/" + str(it["doi"]).strip()
        # else ignore other shapes
        if s and s not in seen:
            out.append(s)
            seen.add(s)
    return out


def as_minimal_mapping(src, filename_fallback):
    """
    Convert a raw YAML object (dict-like) into our minimal pulse mapping.
    """
    title = (src.get("title") or "").strip()
    if not title:
        title = filename_fallback

    date = (src.get("date") or "").strip()
    summary = src.get("summary")
    if summary is None:
        summary = ""
    else:
        summary = str(summary).strip()

    tags = flatten_tags(src.get("tags"))
    papers = extract_urls(src.get("papers"))
    podcasts = extract_urls(src.get("podcasts"))

    # Build a plain dict in desired order
    out = {}
    out["title"] = title
    out["date"] = date
    out["summary"] = summary
    out["tags"] = tags
    out["papers"] = papers
    out["podcasts"] = podcasts
    return out


def looks_same(a, b):
    return yaml.safe_dump(a, sort_keys=False) == yaml.safe_dump(b, sort_keys=False)


def iter_pulse_paths():
    # recursive search
    for p in sorted(glob.glob("pulse/**/*.yml", recursive=True) + glob.glob("pulse/**/*.yaml", recursive=True)):
        p = p.replace("\\", "/")
        # skip archives/telemetry
        if "/archive/" in p or "/telemetry/" in p:
            continue
        yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Only report files that would change; exit 1 if any.")
    ap.add_argument("--write", action="store_true", help="Apply changes in-place.")
    args = ap.parse_args()

    if not (args.check or args.write):
        print("Nothing to do: pass --check or --write", file=sys.stderr)
        return 2

    changed = []

    for path in iter_pulse_paths():
        try:
            data = load_yaml(path)
        except Exception as e:
            print(f"[WARN] YAML load failed: {path}: {e}", file=sys.stderr)
            continue

        # Unwrap "list at top-level" if it's a single mapping
        if isinstance(data, list):
            if len(data) == 1 and isinstance(data[0], dict):
                data = data[0]
            else:
                print(f"[WARN] Skipping (top-level list not a single mapping): {path}", file=sys.stderr)
                continue

        if not isinstance(data, dict):
            print(f"[WARN] Skipping (top-level is {type(data).__name__}, expected mapping): {path}", file=sys.stderr)
            continue

        filename_fallback = os.path.splitext(os.path.basename(path))[0]
        minimal = as_minimal_mapping(data, filename_fallback)

        try:
            before_norm = as_minimal_mapping(data, filename_fallback)
            same = looks_same(before_norm, minimal)
        except Exception:
            same = False

        if not same:
            changed.append(path)
            if args.write:
                dump_yaml(path, minimal)

    if args.check:
        if changed:
            print("Would change the following files:")
            for p in changed:
                print(" -", p)
            return 1
        print("All pulses already conform to the minimal schema.")
        return 0

    if args.write:
        if changed:
            print("Updated files:")
            for p in changed:
                print(" -", p)
        else:
            print("No changes were necessary.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
