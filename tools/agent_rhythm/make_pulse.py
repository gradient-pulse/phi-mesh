#!/usr/bin/env python3
"""
make_pulse.py
Builds a strict-format pulse YAML from computed NT-rhythm metrics.
"""

import argparse
import datetime as dt
import json
import os
import sys
import yaml

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--metrics', required=True, help='Path to JSON metrics from cli.py')
    p.add_argument('--title',   required=True, help='Base pulse title (date will be appended)')
    p.add_argument('--dataset', required=True, help='Dataset slug for filename')
    p.add_argument('--tags',    required=True, help='Space-separated tags or a single string')
    p.add_argument('--outdir',  required=True, help='Output directory for pulse YAML')
    return p.parse_args()

def normalize_tags(tags_arg):
    # Accept "a b c" or already-list in future updates
    if isinstance(tags_arg, str):
        return [t for t in tags_arg.split() if t]
    try:
        return list(tags_arg)
    except Exception:
        return [str(tags_arg)]

def load_metrics(path):
    with open(path, 'r') as f:
        return json.load(f)

def build_summary(dataset, m):
    # One-line, tag-map friendly summary (no bullets/newlines)
    n       = m.get('n', '?')
    mean_dt = m.get('mean_dt', '?')
    cv_dt   = m.get('cv_dt', '?')
    return (f"NT rhythm probe on '{dataset}': "
            f"n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}.")

def main():
    args = parse_args()

    tags = normalize_tags(args.tags)
    metrics = load_metrics(args.metrics)

    today = dt.date.today().isoformat()
    title = f"{args.title} ({today})"
    summary = build_summary(args.dataset, metrics)

    pulse_doc = {
        'title': title,
        'summary': summary,          # single line
        'tags': tags,                # YAML list
        'papers': [],                # keep lists even when empty
        'podcasts': [],
    }

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{args.dataset}_{today}.yml")

    with open(out_path, 'w') as f:
        yaml.safe_dump(pulse_doc, f, sort_keys=False, allow_unicode=True)

    print(f"[make_pulse] wrote {out_path}")

if __name__ == '__main__':
    sys.exit(main())
