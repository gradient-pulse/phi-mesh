#!/usr/bin/env python3
import argparse, glob, json, os, sys, yaml
from collections import defaultdict

def safe_load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None

def load_tag_index(path):
    if not os.path.isfile(path):
        return {}
    data = safe_load_yaml(path) or {}
    # Accept either {} or the richer meta/map formats; normalize to {tag: {pulses: [...], links: [...]}}
    if isinstance(data, dict) and data:
        return data
    return {}

def merge_alias_map(path):
    if not os.path.isfile(path):
        return {}
    data = safe_load_yaml(path) or {}
    # Expect {canonical: [aliases...]} but tolerate {canonical: {aliases: [...]}}
    out = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) and "aliases" in v and isinstance(v["aliases"], list):
                out[k] = [str(a) for a in v["aliases"]]
            elif isinstance(v, list):
                out[k] = [str(a) for a in v]
    return out

def expand_globs(glob_arg):
    parts = [p.strip() for p in glob_arg.split(",") if p.strip()]
    files = []
    for pat in parts:
        files.extend(glob.glob(pat, recursive=True))
    # de-dup while keeping order
    seen, dedup = set(), []
    for f in files:
        if f not in seen:
            seen.add(f); dedup.append(f)
    return dedup

def scan_pulses_for_tags(pulse_globs, verbose=False):
    paths = expand_globs(pulse_globs)
    tag_to_pulses = defaultdict(list)
    pulse_to_tags = {}
    pulse_resources = {}

    for p in paths:
        y = safe_load_yaml(p)
        if not isinstance(y, dict):  # skip lists/nulls/strings
            if verbose: print(f"[skip] {p}: not a mapping", file=sys.stderr)
            continue

        # tags: list[str]
        tags = y.get("tags") or y.get("Tags") or []
        if not isinstance(tags, list):
            if verbose: print(f"[skip] {p}: tags not a list", file=sys.stderr)
            continue
        tags = [str(t).strip() for t in tags if t is not None and str(t).strip()]

        # resources (optional)
        papers = y.get("papers") or []
        podcasts = y.get("podcasts") or []
        r = {}
        if isinstance(papers, list) and papers:
            r["papers"] = [str(u) for u in papers]
        if isinstance(podcasts, list) and podcasts:
            r["podcasts"] = [str(u) for u in podcasts]
        if r:
            pulse_resources[p] = r

        pulse_to_tags[p] = tags
        for t in tags:
            if p not in tag_to_pulses[t]:
                tag_to_pulses[t].append(p)

    return tag_to_pulses, pulse_to_tags, pulse_resources, paths

def apply_aliases(tag_to_pulses, alias_map, soft=True):
    """Return (canonical_tag_to_pulses, alias_edges) where alias_edges are (alias -> canonical)."""
    if not alias_map:
        return tag_to_pulses, []

    canon = defaultdict(list)
    edges = []
    alias_lookup = {}
    for k, aliases in alias_map.items():
        for a in aliases:
            alias_lookup[a] = k

    for t, plist in tag_to_pulses.items():
        if t in alias_lookup:
            k = alias_lookup[t]
            # soft = merge alias into canonical, still keep canonical key only
            for p in plist:
                if p not in canon[k]:
                    canon[k].append(p)
            edges.append((t, k))
        else:
            for p in plist:
                if p not in canon[t]:
                    canon[t].append(p)

    # if soft=False, also keep alias tags explicitly (edge case rarely needed)
    if not soft:
        for alias, k in alias_lookup.items():
            if alias in tag_to_pulses:
                for p in tag_to_pulses[alias]:
                    if p not in canon[alias]:
                        canon[alias].append(p)
                edges.append((alias, k))

    return canon, edges

def write_data_js(out_path, tags_map, resources, alias_edges):
    payload = {
        "tags": tags_map,                  # {tag: [pulses]}
        "resources": resources,            # {pulse_path: {papers:[], podcasts:[]}}
        "aliasEdges": alias_edges          # [[alias, canonical], ...]
    }
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("const tagData = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-index", default="meta/tag_index.yml")
    ap.add_argument("--alias-map", default="")
    ap.add_argument("--pulse-glob", default="pulse/**/*.yml,pulse/**/*.yaml",
                    help="comma-separated globs")
    ap.add_argument("--out-js", default="docs/data.js")
    ap.add_argument("--no-soft-alias", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    verbose = args.verbose
    os.makedirs(os.path.dirname(args.out_js), exist_ok=True)

    tag_index = load_tag_index(args.tag_index)
    alias_map = merge_alias_map(args.alias_map) if args.alias_map else {}

    # Prefer scanning pulses; tag_index in your repo is sometimes transient/empty
    if verbose:
        print("INFO: scanning pulses …", file=sys.stderr)

    t2p, p2t, resources, seen_paths = scan_pulses_for_tags(args.pulse_glob, verbose=verbose)

    if verbose:
        print(f"INFO: scanned files: {len(seen_paths)}", file=sys.stderr)
        print(f"INFO: pulses with tags: {sum(1 for _ in p2t)}", file=sys.stderr)
        print(f"INFO: unique tags: {len(t2p)}", file=sys.stderr)

    if not t2p:
        # fallback: try tag_index if present
        if tag_index:
            if verbose:
                print("WARN: no tags from pulses; using tag_index.yml fallback", file=sys.stderr)
            t2p = defaultdict(list)
            for tag, entry in tag_index.items():
                plist = (entry or {}).get("pulses") or []
                for p in plist:
                    if p not in t2p[tag]:
                        t2p[tag].append(p)

    if not t2p:
        # still empty → write a harmless file but fail clearly
        write_data_js(args.out_js, {}, {}, [])
        print("ERROR: No tags discovered. Check pulse YAML format and globs.", file=sys.stderr)
        sys.exit(3)

    merged, edges = apply_aliases(t2p, alias_map, soft=(not args.no_soft_alias))
    write_data_js(args.out_js, merged, resources, edges)

    # Basic sanity check
    if os.path.isfile(args.out_js) and os.path.getsize(args.out_js) < 200:
        print("ERROR: docs/data.js is suspiciously small.", file=sys.stderr)
        sys.exit(2)

    if verbose:
        print(f"OK: wrote {args.out_js} with {len(merged)} tags.", file=sys.stderr)

if __name__ == "__main__":
    main()
