#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Outputs:  pulse/auto/YYYY-MM-DD_<dataset>.yml
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


# ------------------------------- helpers --------------------------------- #

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Coerce objects to plain Python types so PyYAML is happy."""
    # optional numpy handling
    try:
        import numpy as np  # type: ignore
        np_scalar = np.generic
    except Exception:  # numpy not available
        class _S: ...
        np_scalar = _S  # type: ignore

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_scalar):
        try:
            return x.item()
        except Exception:
            return float(x)
    # pathlib / datetime to strings
    try:
        import pathlib
        if isinstance(x, pathlib.Path):
            return str(x)
    except Exception:
        pass
    import datetime as _dt
    if isinstance(x, (_dt.date, _dt.datetime, _dt.time)):
        return str(x)
    # containers
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    # fallback
    return str(x)


# ------------------------------- main ------------------------------------ #

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug for filename (already includes any batch)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    # Load & sanitize metrics
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics_raw = json.load(f)
    metrics: Dict[str, Any] = to_builtin(metrics_raw)

    n        = metrics.get("n", "?")
    mean_dt  = metrics.get("mean_dt", "?")
    cv_dt    = metrics.get("cv_dt", "?")
    src      = metrics.get("source", "")
    details  = metrics.get("details") or {}

    # File name: date + provided dataset slug (no extra batch logic here)
    today_str = dt.date.today().isoformat()
    slug = safe_slug(args.dataset)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{today_str}_{slug}.yml")

    # Summary (compact, folded)
    summary_lines: List[str] = [
        f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    ]
    if src:
        summary_lines.append(f"Source: {src}.")
    if isinstance(details, dict) and details:
        keep = {k: details[k] for k in ("dataset", "var", "xyz", "window") if k in details}
        if keep:
            summary_lines.append(f"Probe: {keep}.")
    summary_text = " ".join(s.strip() for s in summary_lines if s)

    # Tags -> list
    tags = [t for t in re.split(r"\s+", (args.tags or "").strip()) if t]

    pulse = {
        "title": str(args.title),
        "summary": summary_text,
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Custom dumper: title single-quoted; summary folded (>-)
    class _D(yaml.SafeDumper):
        pass

    def _repr_top_mapping(dumper: yaml.SafeDumper, data: dict) -> yaml.nodes.MappingNode:
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                val_node = yaml.ScalarNode("tag:yaml.org,2002:str", str(v), style=">")
            elif k == "title":
                # force single quotes
                val_node = yaml.ScalarNode("tag:yaml.org,2002:str", str(v), style="'")
            else:
                val_node = dumper.represent_data(v)
            node.value.append((key_node, val_node))
        return node

    _D.add_representer(dict, _repr_top_mapping)

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
