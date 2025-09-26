#!/usr/bin/env python3
import sys, pathlib, re, yaml

ROOT = pathlib.Path(".")
PULSE_DIR = ROOT / "pulse"
TAG_DESC = ROOT / "meta" / "tag_descriptions.yml"  # optional for warnings

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_")
URL = re.compile(r"^(https?://|https://doi.org/|doi:)")
REL_PATH = re.compile(r"""^(
    (\.\./|\./|/)?                # optional relative/absolute prefix
    [A-Za-z0-9._\-/]+             # path body
    (\.[A-Za-z0-9]{1,8})?         # optional short extension
)$""", re.X)

REQUIRED_KEYS = ["title", "summary", "tags", "papers", "podcasts"]
ALLOWED_KEYS = set(REQUIRED_KEYS) | {"links"}  # ← allow links

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def warn(msg):
    print(f"⚠️  {msg}")

def load_yaml(p: pathlib.Path):
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{p}: YAML parse error: {e}")

def validate_single_quoted_title(raw_text: str, path: pathlib.Path):
    """
    Enforce single-quoted title using raw line regex.
    Accepts: title: '...'
    Rejects: title: "..." or title: ...
    """
    m = re.search(r'(?m)^\s*title\s*:\s*(.+)$', raw_text)
    if not m:
        fail(f"{path}: missing 'title' line")
    val = m.group(1).strip()
    if not (val.startswith("'") and val.endswith("'") and len(val) >= 2):
        fail(f"{path}: title must be single-quoted (e.g., title: 'Your Title')")

def is_list_of_urls(lst):
    if not isinstance(lst, list):
        return False
    return all(isinstance(x, str) and URL.match(x) for x in lst)

def is_list_of_generic_links(lst):
    """
    Accept list of strings, each either a URL or a repo-relative path.
    """
    if lst is None:
        return True
    if not isinstance(lst, list):
        return False
    for x in lst:
        if not isinstance(x, str):
            return False
        s = x.strip()
        if not s:
            return False
        if URL.match(s):
            continue
        if REL_PATH.match(s):
            continue
        return False
    return True

def main():
    # optional: load tag descriptions to warn on missing tooltips
    tag_desc = {}
    if TAG_DESC.exists():
        try:
            tag_desc = yaml.safe_load(TAG_DESC.read_text(encoding="utf-8")) or {}
        except Exception as e:
            warn(f"{TAG_DESC}: YAML parse warning: {e}")

    files = sorted(PULSE_DIR.rglob("*.yml"))
    if not files:
        print("No pulse/*.yml files found.")
        return

    errors = 0
    for f in files:
        raw = f.read_text(encoding="utf-8")
        data = load_yaml(f)

        # 0) filename date prefix
        if not DATE_PREFIX.match(f.name):
            errors += 1
            print(f"❌ {f}: filename must start with YYYY-MM-DD_")
            continue

        # 1) disallow 'date' key in YAML
        if isinstance(data, dict) and "date" in data:
            errors += 1
            print(f"❌ {f}: 'date' key is not allowed (date comes from filename)")
            continue

        # 2) structure
        if not isinstance(data, dict):
            errors += 1
            print(f"❌ {f}: top-level YAML must be a mapping")
            continue

        extra = set(data.keys()) - ALLOWED_KEYS
        missing = [k for k in REQUIRED_KEYS if k not in data]
        if extra:
            errors += 1
            print(f"❌ {f}: extra keys not allowed: {sorted(extra)}")
        if missing:
            errors += 1
            print(f"❌ {f}: missing required keys: {missing}")

        # 3) title (single-quoted in file, non-empty value)
        try:
            validate_single_quoted_title(raw, f)
        except SystemExit:
            raise
        except Exception as e:
            errors += 1
            print(f"❌ {f}: title validation error: {e}")
            continue

        title = data.get("title", "")
        if not isinstance(title, str) or not title.strip():
            errors += 1
            print(f"❌ {f}: 'title' must be a non-empty string")

        # 4) summary
        if not isinstance(data.get("summary", ""), str) or not data["summary"].strip():
            errors += 1
            print(f"❌ {f}: 'summary' must be a non-empty string")

        # 5) tags
        tags = data.get("tags", [])
        if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t.strip() for t in tags):
            errors += 1
            print(f"❌ {f}: 'tags' must be a non-empty list of strings")
        else:
            if isinstance(tag_desc, dict):
                missing_tooltips = [t for t in tags if t not in tag_desc]
                if missing_tooltips:
                    warn(f"{f}: tags missing tooltips in tag_descriptions.yml: {missing_tooltips}")

        # 6) papers / podcasts must be lists of URL links
        for k in ("papers", "podcasts"):
            lst = data.get(k, [])
            if not is_list_of_urls(lst):
                errors += 1
                print(f"❌ {f}: '{k}' must be a list of URL links")

        # 7) links (optional): list of URLs or repo-relative paths
        if "links" in data and not is_list_of_generic_links(data.get("links")):
            errors += 1
            print(f"❌ {f}: 'links' must be a list of URLs or repo-relative paths")

        if errors == 0:
            print(f"✅ {f} OK")

    if errors:
        fail(f"Validation failed with {errors} error(s).")
    else:
        print("All pulses validated successfully.")

if __name__ == "__main__":
    main()
