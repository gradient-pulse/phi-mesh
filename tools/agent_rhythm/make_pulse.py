#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_pulse.py — Convert NT rhythm metrics JSON into a Φ-Mesh pulse YAML.

Outputs strict pulse format with:
  - title: '...'
  - summary: >\n  ...
  - tags: [list]
  - papers: []
  - podcasts: []
and file name: pulse/auto/YYYY-MM-DD_<dataset>.yml
"""

import re
import json
import argparse
from datetime import datetime
from pathlib import Path

import yaml


# ---------- YAML style helpers ----------

class SingleQuoted(str):
    """Render a string with single quotes in YAML (style: ')."""


class Folded(str):
    """Render a string as a folded block scalar in YAML (style: '>')."""


def _repr_single_quoted(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="'")


def _repr_folded(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style=">")


yaml.add_representer(SingleQuoted, _repr_single_quoted)
yaml.add_representer(Folded, _repr_folded)


# ---------- utils ----------

def slugify(s: str) -> str:
    """
    Turn a dataset string into a safe slug with no leading/trailing separators.
    """
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", s.strip())
    s = re.sub(r"[-_]{2,}", "_", s)
    s = s.strip("-_")
    return s or "pulse"


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title", required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug (will be normalized)")
    ap.add_argument("--tags", required=True, nargs="+", help="Space-separated tags")
    ap.add_argument("--outdir", required=True, help="Output directory for pulse")
    args = ap.parse_args()

    with open(args.metrics, "r") as f:
        metrics = json.load(f)

    date = datetime.utcnow().strftime("%Y-%m-%d")
    dataset_slug = slugify(args.dataset)

    # Build summary as folded text (no extra quotes in content needed).
    n = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt = metrics.get("cv_dt", "?")
    summary_text = (
        f"NT rhythm probe on {dataset_slug}: "
        f"n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    )

    pulse = {
        "title": SingleQuoted(f"{args.title} ({date})"),
        "summary": Folded(summary_text),
        "tags": sorted(list(set(args.tags))),
        "papers": [],
        "podcasts": [],
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{date}_{dataset_slug}.yml"

    with open(outpath, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            pulse,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )

    print(f"[make_pulse] wrote {outpath}")


if __name__ == "__main__":
    main()
