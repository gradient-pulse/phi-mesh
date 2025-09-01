#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_pulse.py — Convert NT rhythm metrics JSON into a Φ-Mesh pulse YAML.

This script is invoked by the GitHub Action (nt_rhythm_inbox.yml).
It takes rhythm metrics, a title, dataset slug, and tags, and emits
a YAML pulse into pulse/auto/YYYY-MM-DD_<dataset>.yml

Strict pulse format:
  - title
  - summary
  - tags (list)
  - papers (list)
  - podcasts (list)
"""

import re
import yaml
import json
import argparse
from datetime import datetime
from pathlib import Path


def slugify(s: str) -> str:
    """Turn a dataset string into a safe slug with no trailing separators."""
    # replace any non-alphanumeric/_/- with underscores
    s = re.sub(r'[^A-Za-z0-9_-]+', '_', s.strip())
    # collapse runs of - or _
    s = re.sub(r'[-_]{2,}', '_', s)
    # strip leading/trailing separators
    s = s.strip('-_')
    return s or "pulse"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Input metrics JSON path")
    ap.add_argument("--title", required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug")
    ap.add_argument("--tags", required=True, nargs="+", help="Space-separated tags")
    ap.add_argument("--outdir", required=True, help="Output directory for pulse")
    args = ap.parse_args()

    # load metrics
    with open(args.metrics, "r") as f:
        metrics = json.load(f)

    date = datetime.utcnow().strftime("%Y-%m-%d")
    dataset_slug = slugify(args.dataset)

    # build pulse dict
    pulse = {
        "title": f"{args.title} ({date})",
        "summary": (
            f"NT rhythm probe on '{dataset_slug}': "
            f"n={metrics.get('n','?')}, "
            f"mean_dt={metrics.get('mean_dt','?')}, "
            f"cv_dt={metrics.get('cv_dt','?')}."
        ),
        "tags": sorted(list({*args.tags})),
        "papers": [],
        "podcasts": [],
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{date}_{dataset_slug}.yml"

    with open(outpath, "w") as f:
        yaml.safe_dump(pulse, f, sort_keys=False)

    print(f"[make_pulse] wrote {outpath}")


if __name__ == "__main__":
    main()
