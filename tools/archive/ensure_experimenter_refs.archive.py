raise SystemExit("DEPRECATED: use agents/rgp_ns/run_agent.py")
#!/usr/bin/env python3
# tools/ensure_experimenter_refs.py
import yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PULSE_DIRS = [ROOT/"pulse", ROOT/"pulse"/"auto"]

PAPERS = [
  {"title": "Solving Navier-Stokes, Differently: What It Takes (V1.2)",
   "url":   "https://doi.org/10.5281/zenodo.15830659"},
  {"title": "Experimenter’s Guide — Solving Navier-Stokes, Differently (V1.7)",
   "url":   "https://doi.org/10.5281/zenodo.16812467"},
]
PODCASTS = [
  {"url": "https://notebooklm.google.com/notebook/d49018d3-0070-41bb-9187-242c2698c53c?artifactId=fef1bd81-e87d-41b5-a501-f862442ce3ef"},
  {"url": "https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=b1dcf5ac-5216-4a04-bc36-f509ebeeabef"},
]

def _norm_tag(s:str)->str:
    return re.sub(r"[\s\-]+","_", (s or "").strip())

def wants_fix(data:dict)->bool:
    tags = data.get("tags") or []
    if isinstance(tags,str): tags=[tags]
    has_exp = any(_norm_tag(t).lower()=="experimenterpulse" for t in tags)
    return bool(has_exp)

def ensure_refs(data:dict)->bool:
    changed = False

    # tags: ensure ExperimenterPulse + RGP present once
    tags = data.get("tags") or []
    if isinstance(tags,str): tags=[tags]
    wanted = set(t.lower() for t in ["ExperimenterPulse","RGP"])
    existing = { _norm_tag(t).lower(): t for t in tags }
    for w in wanted:
        if w not in existing:
            tags.append("ExperimenterPulse" if w=="experimenterpulse" else "RGP")
            changed = True
    # dedupe in stable order
    seen=set(); new_tags=[]
    for t in tags:
        k=_norm_tag(t).lower()
        if k not in seen:
            seen.add(k); new_tags.append(t)
    if new_tags!=tags:
        data["tags"]=new_tags; changed=True

    # force the canonical lists (drop anything else)
    if data.get("papers") != PAPERS:
        data["papers"] = PAPERS; changed = True
    if data.get("podcasts") != PODCASTS:
        data["podcasts"] = PODCASTS; changed = True

    return changed

def main():
    changed_files = 0
    for base in PULSE_DIRS:
        if not base.exists(): continue
        for yml in base.rglob("*.yml"):
            try:
                obj = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            if not isinstance(obj,dict): continue
            if not wants_fix(obj): continue
            if ensure_refs(obj):
                yml.write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True), encoding="utf-8")
                print(f"fixed: {yml.relative_to(ROOT)}")
                changed_files += 1
    print(f"OK: updated {changed_files} file(s).")

if __name__ == "__main__":
    main()
