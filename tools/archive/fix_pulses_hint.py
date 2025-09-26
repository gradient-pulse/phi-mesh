#!/usr/bin/env python3
import pathlib, yaml

root = pathlib.Path("pulse/auto")
changed = 0

for yml in sorted(root.glob("*.yml")):
    data = yaml.safe_load(yml.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "hint" in data:
        hint = str(data.pop("hint")).strip()
        if hint:
            base = (data.get("summary") or "").rstrip()
            sep = "" if base.endswith((".", "!", "?")) else "."
            data["summary"] = f"{base}{sep} Hint: {hint}."
        yml.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        changed += 1

print(f"Updated {changed} pulse(s).")
