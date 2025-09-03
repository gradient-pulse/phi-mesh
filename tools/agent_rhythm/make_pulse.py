#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Writes: pulse/auto/YYYY-MM-DD_<dataset>.yml
If a same-day pulse for <dataset> already exists, writes:
  YYYY-MM-DD_<dataset>_batch2.yml, _batch3.yml, ...

YAML schema:
  title: '...'
  summary: >
    ...
  tags:
    - ...
  papers: []
  podcasts: []
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import pathlib
from typing import Any, Dict, List

import yaml


# ----- helpers -------------------------------------------------------------

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Recursively coerce to plain Python builtins so PyYAML is happy."""
    # numpy is optional
    try:
        import numpy as np
        np_generic = np.generic
    except Exception:
        class _NP: ...
        np_generic = _NP  # type: ignore

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):  # numpy scalar -> Python scalar
        try:
            return x.item()
        except Exception:
            return float(x)
    try:
        import pathlib as _pl
        if isinstance(x, _pl.Path):
            return str(x)
    except Exception:
        pass
    if isinstance(x, (dt.date, dt.datetime, dt.time)):
        return str(x)
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


def next_batch_path(base_path: str) -> str:
    """
    If base_path exists, append _batch2 / _batch3 / ...
    Example:
      base: 2025-09-03_demo.yml
      -> 2025-09-03_demo_batch2.yml (if base exists)
    """
    p = pathlib.Path(base_path)
    if not p.exists():
        return str(p)
    i = 2
    while True:
        cand = p.with_name(f"{p.stem}_batch{i}{p.suffix}")
        if not cand.exists():
            return str(cand)
        i += 1


# ----- main ----------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug (for filename)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    # Load metrics JSON
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics_raw = json.load(f)
    metrics: Dict[str, Any] = to_builtin(metrics_raw)

    # Pull common fields with defaults
    n        = metrics.get("n") or metrics.get("count") or "?"
    mean_dt  = metrics.get("mean_dt", "?")
    cv_dt    = metrics.get("cv_dt", "?")
    src      = metrics.get("source", "")
    details  = metrics.get("details") or metrics.get("extra") or {}

    # Filename bits
    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    slug = safe_slug(args.dataset)

    os.makedirs(args.outdir, exist_ok=True)
    base_path = os.path.join(args.outdir, f"{today_str}_{slug}.yml")
    out_path = next_batch_path(base_path)  # batch2/batch3 if needed

    # Build summary (folded > in YAML)
    summary_lines: List[str] = []
    summary_lines.append(
        f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    )
    if src:
        summary_lines.append(f"Source: {src}.")
    if details:
        # include a small, stable subset if present
        try:
            keys = ["var", "xyz", "window", "dataset"]
            subset = {k: details[k] for k in keys if k in details}
            if subset:
                summary_lines.append(f"Probe: {subset}.")
        except Exception:
            pass
    summary_text = " ".join(str(s).strip() for s in summary_lines if s)

    # Tags: space-separated -> list
    tags = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Construct pulse dict using ONLY builtins
    pulse = {
        "title": str(args.title),    # ensure plain str
        "summary": summary_text,     # dumped folded via custom dumper
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Custom dumper to force folded style (">") for summary
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                val_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=str(v), style=">")
            else:
                val_node = dumper.represent_data(v)
            node.value.append((key_node, val_node))
        return node

    _D.add_representer(dict, _repr_mapping)

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(
            pulse,
            stream=f,
            Dumper=_D,
            sort_keys=False,
            allow_unicode=True,
            width=1000,
        )

    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
