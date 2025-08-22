# tools/mesh_maint.py
#!/usr/bin/env python3
import argparse, re, shutil, subprocess, sys
from pathlib import Path

try:
    import yaml  # PyYAML
except Exception as e:
    print("ERROR: PyYAML not installed. In Actions we install it; locally: pip install pyyaml")
    raise

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "pulse" / "auto"
ARCH = ROOT / "pulse" / "archive" / "auto"
META = ROOT / "meta"
DOCS = ROOT / "docs"

PAT = re.compile(r"^(\d{8}_\d{6})_(.+)\.ya?ml$")  # YYYYMMDD_HHMMSS_DATASET.yml

def info(msg): print(f"[maint] {msg}")

def archive_old_autopulses(keep:int, dry:bool)->int:
    """Keep newest N per dataset; move the rest to pulse/archive/auto."""
    if not AUTO.exists():
        info("No pulse/auto directory — skipping archive.")
        return 0
    ARCH.mkdir(parents=True, exist_ok=True)
    groups = {}
    for p in list(AUTO.glob("*.yml")) + list(AUTO.glob("*.yaml")):
        m = PAT.match(p.name)
        if not m: 
            continue
        ts, dataset = m.group(1), m.group(2)
        groups.setdefault(dataset, []).append((ts, p))
    moves = []
    for dataset, items in groups.items():
        items.sort(key=lambda t: t[0], reverse=True)  # newest first
        for ts, p in items[keep:]:
            moves.append((p, ARCH / p.name))
    if not moves:
        info("Auto-pulse archive: nothing to move.")
        return 0
    info(f"Auto-pulse archive: moving {len(moves)} file(s) to {ARCH} (keep={keep}).")
    for src, dst in moves:
        info(f"  - {src.name} -> archive/")
        if not dry:
            shutil.move(str(src), str(dst))
    return len(moves)

def load_yaml(path:Path)->dict:
    if not path.exists(): return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}

def merge_tag_descriptions(merge_file:str, dry:bool)->int:
    """Merge merge_file into meta/tag_descriptions.yml (new keys overwrite)."""
    if not merge_file:
        info("No descriptions file provided — skipping merge.")
        return 0
    src = (ROOT / merge_file).resolve()
    if not src.exists():
        info(f"Descriptions file not found: {src} — skipping.")
        return 0
    dest = META / "tag_descriptions.yml"
    cur = load_yaml(dest)
    inc = load_yaml(src)
    if not inc:
        info("Incoming descriptions file empty or invalid — skipping.")
        return 0
    changed = 0
    for k, v in inc.items():
        if cur.get(k) != v:
            cur[k] = v
            changed += 1
    if changed == 0:
        info("Descriptions merge: no changes.")
        return 0
    # sort keys for readability
    cur_sorted = {k: cur[k] for k in sorted(cur)}
    info(f"Descriptions merge: {changed} key(s) updated -> {dest}")
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as f:
            yaml.safe_dump(cur_sorted, f, sort_keys=False, allow_unicode=True)
    return changed

def rebuild_data_js(rebuild:bool)->bool:
    if not rebuild:
        info("Rebuild data.js disabled.")
        return False
    gen = ROOT / "generate_graph_data.py"
    if not gen.exists():
        info("generate_graph_data.py not found — skipping data.js rebuild.")
        return False
    DOCS.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(gen),
        "--pulse-glob", "pulse/**/*.yml",
        "--alias-map", "meta/aliases.yml",
        "--tag-descriptions", "meta/tag_descriptions.yml",
        "--out-js", "docs/data.js",
    ]
    info("Rebuilding docs/data.js …")
    subprocess.check_call(cmd, cwd=str(ROOT))
    return True

def main():
    ap = argparse.ArgumentParser(description="Phi-Mesh maintenance batch")
    ap.add_argument("--keep", type=int, default=3, help="Keep last N auto-pulses per dataset (default 3)")
    ap.add_argument("--merge-file", type=str, default="", help="Path to new descriptions YAML (relative to repo)")
    ap.add_argument("--rebuild-data", action="store_true", help="Rebuild docs/data.js")
    ap.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    args = ap.parse_args()

    moved = archive_old_autopulses(args.keep, args.dry_run)
    merged = merge_tag_descriptions(args.merge_file, args.dry_run)
    rebuilt = rebuild_data_js(args.rebuild_data and not args.dry_run)

    info(f"Summary: archived={moved}, merged={merged}, rebuilt_data={rebuilt}, dry_run={args.dry_run}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
