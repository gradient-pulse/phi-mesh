#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Outputs (always batch-stamped):
  pulse/auto/YYYY-MM-DD_<dataset>_batchN.yml

Schema:
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
    # Late import to avoid hard dep if numpy isn't installed.
    try:
        import numpy as np  # type: ignore
        np_generic = np.generic  # type: ignore[attr-defined]
    except Exception:  # numpy not installed
        class _NP: ...
        np_generic = _NP  # sentinel that never matches

    # Scalars
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):  # numpy scalar -> Python scalar
        try:
            return x.item()
        except Exception:
            return float(x)

    # Pathlike / datetime
    try:
        import pathlib
        if isinstance(x, pathlib.Path):
            return str(x)
    except Exception:
        pass
    if isinstance(x, (dt.date, dt.datetime, dt.time)):
        return str(x)

    # Containers
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]

    # Fallback
    return str(x)


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

    # Pull commonly-used fields (fallbacks ok)
    n        = metrics.get("n") or metrics.get("count") or "?"
    mean_dt  = metrics.get("mean_dt", "?")
    cv_dt    = metrics.get("cv_dt", "?")
    src      = metrics.get("source", "")
    details  = metrics.get("details") or metrics.get("extra") or {}
    meta     = metrics.get("meta") or {}

    # Batch (ALWAYS present in filename; default to 1)
    try:
        batch = int(details.get("batch", meta.get("batch", 1)))
    except Exception:
        batch = 1

    # Filename bits
    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    slug = safe_slug(args.dataset)

    os.makedirs(args.outdir, exist_ok=True)
    out_name = f"{today_str}_{slug}_batch{batch}.yml"
    out_path = os.path.join(args.outdir, out_name)

    # Summary (compact, folded)
    summary_lines: List[str] = []
    summary_lines.append(
        f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    )
    if src:
        summary_lines.append(f"Source: {src}.")
    # Include probe subset if available
    if isinstance(details, dict) and details:
        try:
            keys = ["dataset", "var", "xyz", "window", "batch"]
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
        "title": str(args.title),   # single-quoted by custom dumper
        "summary": summary_text,    # folded style by custom dumper
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Custom dumper: folded summary + single-quoted title
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                # folded block scalar '>'
                val_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=str(v), style=">")
            elif k == "title":
                # Force single quotes per strict pulse rule
                sval = str(v)
                if (sval.startswith("'") and sval.endswith("'")) or (sval.startswith('"') and sval.endswith('"')):
                    sval = sval[1:-1]
                val_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=sval, style="'")
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
            allow_unicode=True,  # keep m-dash, smart quotes, etc.
            width=1000,
        )

    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
