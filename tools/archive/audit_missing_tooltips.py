#!/usr/bin/env python3
import json, re
txt = open("docs/data.js","r",encoding="utf-8").read()
m = re.search(r"window\.PHI_DATA\s*=\s*(\{.*\});\s*$", txt, re.S)
data = json.loads(m.group(1))
desc = data.get("tagDescriptions", {})
missing = sorted({n["id"] for n in data.get("nodes", []) if not desc.get(n["id"], "").strip()})
print(f"{len(missing)} tags without descriptions:")
for t in missing: print(" -", t)
