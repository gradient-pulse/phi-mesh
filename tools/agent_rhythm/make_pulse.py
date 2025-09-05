#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

- Always single-quotes the title
- Always writes filename with _batchN, stripping any accidental double-batch
- Summary is folded (">") and compact
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from typing import Any, Dict, List

import yaml


def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Recursively coerce to plain Python builtins so PyYAML is happy."""
    try:
        import numpy as np
        np_generic = np.generic  # type: ignore[attr-defined]
    except Exception:
        class _NP: ...
        np_generic = _NP

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):
        try:
            return x.item()
        except Exception:
            return float(x)
    try:
        import pathlib
        if isinstance(x, pathlib.Path):
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug (for filename)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics_raw = json.load(f)
    metrics: Dict[str, Any] = to_builtin(metrics_raw)

    n       = metrics.get("n") or metrics.get("count") or "?"
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt   = metrics.get("cv_dt", "?")
    src     = metrics.get("source", "")
    details = metrics.get("details") or {}

    # batch guard (always produce _batchN)
    try:
        batch = int(metrics.get("batch"))
    except Exception:
        batch = 1

    # filename slug — strip any accidental *_batchN from dataset
    slug = safe_slug(args.dataset)
    slug = re.sub(r"_batch\d+$", "", slug)

    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{today_str}_{slug}_batch{batch}.yml")

    # Summary (folded)
    parts: List[str] = [f"NT rhythm probe on “{slug}_batch{batch}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."]
    if src:
        parts.append(f"Source: {src}.")
    if details:
        try:
            subset = {k: details[k] for k in ["dataset", "var", "xyz", "window", "batch"] if k in details}
            if subset:
                parts.append(f"Probe: {subset}.")
        except Exception:
            pass
    summary_text = " ".join(str(s).strip() for s in parts if s)

    # tag list
    tags = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    pulse = {
        "title": str(args.title),
        "summary": summary_text,
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # custom dumper: single quotes for title, folded summary
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                val_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=str(v), style=">")
            elif k == "title":
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
        yaml.dump(pulse, stream=f, Dumper=_D, sort_keys=False, allow_unicode=True, width=1000)

    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
