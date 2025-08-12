# meta/update_tag_index.py
from pathlib import Path
import yaml
from datetime import datetime

PULSE_DIR = Path("pulse")
OUT_PATH  = Path("meta/tag_index.yml")
EXCLUDE_TOP = {"archive", "telemetry"}

def list_pulse_files():
    files = []
    for p in PULSE_DIR.rglob("*.yml"):
        rel = p.relative_to(PULSE_DIR)
        top = rel.parts[0] if len(rel.parts) > 1 else ""
        if top in EXCLUDE_TOP:
            continue
        files.append(p)
    return sorted(files)

def load_yaml(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def norm_title(d):
    t = d.get("title") or d.get("name") or d.get("slug") or path.stem  # fallback
    return str(t)

def pulse_record(path: Path, data: dict):
    title = data.get("title") or path.stem
    date  = data.get("date") or ""
    href  = str(path.as_posix())  # repo-relative
    papers = data.get("papers") or []
    podcasts = data.get("podcasts") or []
    tags = data.get("tags") or []
    # coerce papers/podcasts into simple dicts
    def to_pair(x):
        if isinstance(x, dict): return {"title": x.get("title",""), "doi": x.get("doi",""), "link": x.get("link","")}
        if isinstance(x, str):  return {"title": x, "doi": "", "link": x}
        return {"title":"", "doi":"", "link":""}
    return {
        "title": str(title),
        "date":  str(date),
        "path":  href,
        "papers": [to_pair(p) for p in papers],
        "podcasts": [to_pair(p) for p in podcasts],
        "tags": [str(t) for t in tags if isinstance(t, (str,int,float))],
    }

def build_index():
    index = {}  # tag -> {pulses: [...], papers: [...], podcasts: [...]}
    for p in list_pulse_files():
        data = load_yaml(p)
        if not isinstance(data, dict): 
            continue
        rec = pulse_record(p, data)
        for tag in rec["tags"]:
            bucket = index.setdefault(tag, {"pulses": [], "papers": [], "podcasts": []})
            bucket["pulses"].append({"title": rec["title"], "path": rec["path"], "date": rec["date"]})
            # de-dup papers/podcasts by title
            def add_unique(lst, item, key="title"):
                if item.get(key):
                    if all(x.get(key) != item.get(key) for x in lst):
                        lst.append(item)
            for paper in rec["papers"]:
                add_unique(bucket["papers"], paper)
            for pod in rec["podcasts"]:
                add_unique(bucket["podcasts"], pod)
    # sort for stability
    for tag, bucket in index.items():
        bucket["pulses"].sort(key=lambda x: (x.get("date",""), x["title"]))
        bucket["papers"].sort(key=lambda x: x.get("title",""))
        bucket["podcasts"].sort(key=lambda x: x.get("title",""))
    return {"generated": datetime.utcnow().isoformat()+"Z", "tags": index}

def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    idx = build_index()
    with OUT_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(idx, f, sort_keys=True, allow_unicode=True)

if __name__ == "__main__":
    main()
