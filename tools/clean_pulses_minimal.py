#!/usr/bin/env python3
# tools/clean_pulses_minimal.py

import argparse
import io
import os
import re
import sys
import glob
import yaml

# ---------- utils ----------

URL_RE = re.compile(r'^https?://', re.IGNORECASE)

def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text(path: str, text: str) -> None:
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def to_plain(x):
    """Recursively convert to plain Python types safe_dump can represent."""
    if isinstance(x, dict):
        return {str(k): to_plain(v) for k, v in x.items()}
    if isinstance(x, list):
        return [to_plain(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    # Fallback: string form
    return str(x)

def safe_load_yaml(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[WARN] YAML load failed for {path}: {e}", file=sys.stderr)
        return None

def yaml_dump_minimal(obj) -> str:
    """Dump with doc start and stable key order, UTF-8."""
    stream = io.StringIO()
    yaml.safe_dump(
        obj,
        stream,
        allow_unicode=True,
        sort_keys=False,
        width=80,
        default_flow_style=False,
    )
    return "---\n" + stream.getvalue()

def guess_date_from_filename(path: str) -> str:
    """Try to extract YYYY-MM-DD from filename."""
    name = os.path.basename(path)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', name)
    if m:
        return m.group(1)
    m = re.search(r'(\d{8})', name)  # YYYYMMDD
    if m:
        s = m.group(1)
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return ""

def norm_summary(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        # join multi-line lists into a paragraph
        s = " ".join(str(x) for x in val)
    elif isinstance(val, dict):
        s = " ".join(f"{k}: {v}" for k, v in val.items())
    else:
        s = str(val)
    # trim stray backticks and whitespace
    s = s.strip().strip('`').strip()
    return s

def norm_tags(val) -> list:
    out, seen = [], set()
    def push(tag):
        t = (tag or "").strip()
        if not t:
            return
        if t not in seen:
            out.append(t)
            seen.add(t)
    if val is None:
        return out
    if isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                push(item)
            elif isinstance(item, dict):
                push(item.get("tag") or item.get("name") or "")
            else:
                push(str(item))
        return out
    if isinstance(val, str):
        for part in re.split(r'[,\n]+', val):
            push(part)
        return out
    # fallback
    push(str(val))
    return out

def norm_links(val) -> list:
    """Return only http(s) URLs, deduped, keep order."""
    urls, seen = [], set()
    if not val:
        return urls
    items = val if isinstance(val, list) else [val]
    for item in items:
        if isinstance(item, dict):
            u = item.get("url") or item.get("href") or ""
        else:
            u = str(item or "")
        u = u.strip()
        if u and URL_RE.match(u) and u not in seen:
            urls.append(u)
            seen.add(u)
    return urls

def to_minimal(path: str, data) -> dict | None:
    """
    Normalize one pulse YAML object to:
    title, date, summary, tags, papers, podcasts
    """
    # Unwrap "- title: ..." single-item list
    if isinstance(data, list):
        if len(data) == 1 and isinstance(data[0], dict):
            data = data[0]
        else:
            print(f"[WARN] Skipping multi-item or non-mapping list: {path}", file=sys.stderr)
            return None

    if not isinstance(data, dict):
        print(f"[WARN] Skipping (top-level {type(data).__name__}): {path}", file=sys.stderr)
        return None

    title = (data.get("title") or "").strip()
    if not title:
        # derive from filename
        stem = os.path.splitext(os.path.basename(path))[0]
        title = stem.replace('_', ' ').replace('-', ' ').strip()

    date = (data.get("date") or "").strip()
    if not date:
        date = guess_date_from_filename(path)

    summary = norm_summary(data.get("summary"))

    tags = norm_tags(data.get("tags"))

    papers = norm_links(data.get("papers"))
    podcasts = norm_links(data.get("podcasts"))

    minimal = {
        "title": title,
        "date": date,
        "summary": summary,
        "tags": tags,
        "papers": papers,
        "podcasts": podcasts,
    }
    return to_plain(minimal)

def process_file(path: str, write: bool) -> tuple[bool, str]:
    raw = read_text(path)
    data = safe_load_yaml(path)
    if data is None:
        return False, "yaml-error"
    minimal = to_minimal(path, data)
    if minimal is None:
        return False, "skipped"
    new_text = yaml_dump_minimal(minimal)
    changed = (raw.strip() != new_text.strip())
    if changed and write:
        write_text(path, new_text)
        return True, "fixed"
    return changed, "would-fix" if changed else "ok"

def main():
    ap = argparse.ArgumentParser(description="Clean pulses to minimal schema.")
    ap.add_argument("--write", action="store_true", help="Write changes back to files.")
    ap.add_argument("--check", action="store_true", help="Exit nonzero if any file would change.")
    ap.add_argument("--glob", default="pulse/**/*.yml,pulse/**/*.yaml", help="Comma-separated globs.")
    args = ap.parse_args()

    globs = [g.strip() for g in args.glob.split(",") if g.strip()]
    files = []
    for g in globs:
        files.extend(sorted(glob.glob(g, recursive=True)))

    changed_any = False
    fixed = 0
    for path in files:
        changed, status = process_file(path, args.write)
        if status == "yaml-error":
            continue
        if status == "skipped":
            continue
        if changed:
            changed_any = True
        if status == "fixed":
            fixed += 1
        print(f"[{status:10}] {path}")

    if args.check and changed_any:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
