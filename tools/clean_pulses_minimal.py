#!/usr/bin/env python3
"""
Strict cleaner to keep only: title, date, summary, tags, papers, podcasts.

- Always rewrites (unless --check), so diffs are visible.
- Prints exactly what fields were removed/normalized per file.
- Tolerates datetime dates; serializes to ISO (YYYY-MM-DD) when possible.
- Normalizes scalar-or-list to list for papers/podcasts.
- Trims blank strings; omits empty keys.
- Handles YAML docs that are a list (warns & skips) or invalid (warns).
"""

import argparse, sys, os, io, re, datetime as dt
from collections import OrderedDict
from glob import glob
import yaml

yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
def _repr_str(dumper, data):
    # Keep Unicode, avoid line wrapping
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=None)
yaml.SafeDumper.represent_str = _repr_str  # type: ignore

KEEP_KEYS = ["title", "date", "summary", "tags", "papers", "podcasts"]

def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), None
    except Exception as e:
        return None, f"[WARN] YAML load failed for {path}: {e}"

def dump_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )

def norm_date(x):
    if x is None: return ""
    if isinstance(x, str):
        s = x.strip()
        # keep ISO date/time if present; otherwise best-effort to YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}", s):
            return s
        try:
            return dt.datetime.fromisoformat(s.replace("Z","+00:00")).date().isoformat()
        except Exception:
            return s
    if isinstance(x, (dt.date, dt.datetime)):
        try:
            return x.date().isoformat() if isinstance(x, dt.datetime) else x.isoformat()
        except Exception:
            return str(x)
    return str(x)

def listify(x):
    if x is None: return []
    if isinstance(x, list): return [str(i).strip() for i in x if str(i).strip()]
    return [str(x).strip()] if str(x).strip() else []

def to_minimal(path, data):
    changes = []
    if not isinstance(data, dict):
        raise TypeError(f"{os.path.basename(path)} is not a mapping (found {type(data).__name__}).")

    minimal = OrderedDict()
    # title
    title = str(data.get("title") or "").strip()
    if not title:
        # try to synthesize from filename
        title = os.path.splitext(os.path.basename(path))[0].replace("_", " ").strip()
        changes.append("title:synthesized")
    minimal["title"] = title

    # date
    date_raw = data.get("date")
    date = norm_date(date_raw)
    if date != (date_raw if isinstance(date_raw,str) else str(date_raw) if date_raw is not None else ""):
        changes.append("date:normalized")
    if date: minimal["date"] = date

    # summary
    summary = str(data.get("summary") or "").strip()
    if summary:
        minimal["summary"] = summary
    elif "summary" in data:
        changes.append("summary:trimmed-empty")

    # tags
    tags = data.get("tags")
    if isinstance(tags, (list, tuple)):
        tags_norm = []
        for t in tags:
            if isinstance(t, str):
                s = t.strip()
                if s: tags_norm.append(s)
            else:
                # ignore nested structures
                changes.append("tags:dropped-nonstring")
        # de-dupe preserve order
        seen = set(); dedup = []
        for t in tags_norm:
            if t not in seen:
                seen.add(t); dedup.append(t)
        if dedup:
            minimal["tags"] = dedup
    elif isinstance(tags, str) and tags.strip():
        minimal["tags"] = [tags.strip()]
        changes.append("tags:listified")
    elif "tags" in data:
        changes.append("tags:empty-removed")

    # papers
    papers = listify(data.get("papers"))
    if papers: minimal["papers"] = papers
    elif "papers" in data:
        changes.append("papers:empty-removed")

    # podcasts
    podcasts = listify(data.get("podcasts"))
    if podcasts: minimal["podcasts"] = podcasts
    elif "podcasts" in data:
        changes.append("podcasts:empty-removed")

    # report removed keys
    removed = [k for k in data.keys() if k not in minimal and k in data and k not in KEEP_KEYS]
    for k in removed:
        changes.append(f"removed:{k}")

    return minimal, changes

def iter_pulse_files():
    pats = ["pulse/**/*.yml", "pulse/**/*.yaml"]
    seen = set()
    for pat in pats:
        for p in glob(pat, recursive=True):
            if p not in seen:
                seen.add(p)
                yield p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dry-run; do not write files")
    ap.add_argument("--write", action="store_true", help="write changes to disk")
    ap.add_argument("--verbose", action="store_true", help="print per-file diffs/actions")
    args = ap.parse_args()

    if not args.check and not args.write:
        # default to check (safe)
        args.check = True

    any_issue = False
    changed_count = 0

    for path in iter_pulse_files():
        data, err = load_yaml(path)
        if err:
            print(err)
            any_issue = True
            continue
        if data is None:
            print(f"[WARN] Empty YAML: {path}")
            any_issue = True
            continue
        if isinstance(data, list):
            print(f"[WARN] Top-level sequence (not mapping), skipping: {path}")
            any_issue = True
            continue

        try:
            minimal, changes = to_minimal(path, data)
        except Exception as e:
            print(f"[WARN] {path}: {e}")
            any_issue = True
            continue

        if args.verbose:
            if changes:
                print(f"[fix-ready ] {path}")
                for c in changes:
                    print(f"  - {c}")
            else:
                print(f"[ok        ] {path} (already minimal)")

        if args.write:
            dump_yaml(path, minimal)
            changed_count += 1

    if args.check:
        print("[check done] Use --write to apply changes.")
    if args.write:
        print(f"[write done] Files rewritten: {changed_count}")

    return 1 if any_issue and not args.write else 0

if __name__ == "__main__":
    sys.exit(main())
