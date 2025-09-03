#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Emits: pulse/auto/YYYY-MM-DD_<dataset>.yml

Schema:
  title: '...'
  summary: >
    ...
  tags:
    - ...
  papers: []
  podcasts: []
"""

import argparse
import datetime as dt
import json
import os
import re
from typing import Any, Dict, List

import yaml


# ---------- helpers ---------------------------------------------------------

def safe_slug(s: str) -> str:
    """Conservative slug sanitizer for filenames."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Recursively coerce to plain Python builtins so PyYAML is happy."""
    # late import to avoid hard dep if numpy isn't installed
    try:
        import numpy as np
        np_generic = np.generic
    except Exception:
        class _NP:  # sentinel that won't match
            pass
        np_generic = _NP

    # scalars
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_generic):  # numpy scalar -> Python scalar
        try:
            return x.item()
        except Exception:
            return float(x)

    # pathlike / datetime
    try:
        import pathlib
        if isinstance(x, pathlib.Path):
            return str(x)
    except Exception:
        pass
    if isinstance(x, (dt.date, dt.datetime, dt.time)):
        return str(x)

    # containers
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]

    # fallback
    return str(x)


# ---------- main ------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug (for filename)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    # Load metrics and coerce defensively to builtins
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics_raw = json.load(f)
    metrics: Dict[str, Any] = to_builtin(metrics_raw)

    # Common fields with defaults (brace for absent values)
    n        = metrics.get("n") or metrics.get("count") or "?"
    mean_dt  = metrics.get("mean_dt", "?")
    cv_dt    = metrics.get("cv_dt", "?")
    src      = metrics.get("source", "")
    details  = metrics.get("details") or metrics.get("extra") or {}

    # Output path
    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    slug = safe_slug(args.dataset)
    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{today_str}_{slug}.yml")

    # Build concise summary sentence
    summary_lines: List[str] = []
    summary_lines.append(
        f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    )
    if src:
        summary_lines.append(f"Source: {src}.")
    if isinstance(details, dict) and details:
        # Show a small stable subset in a compact form
        var = details.get("var")
        xyz = details.get("xyz")
        win = details.get("window") or details.get("twin")
        ds  = details.get("dataset")
        pieces = []
        if var is not None: pieces.append(f"var={var}")
        if xyz is not None: pieces.append(f"xyz={tuple(xyz)}")
        if win is not None:
            try:
                pieces.append(f"window=[{win[0]}..{win[1]}:{win[2]}]")
            except Exception:
                pieces.append(f"window={win}")
        if ds is not None:  pieces.append(f"dataset={ds}")
        if pieces:
            summary_lines.append(f"Probe: " + ", ".join(pieces) + ".")
    summary_text = " ".join(str(s).strip() for s in summary_lines if s)

    # Tags: space-separated -> list
    tags = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Construct pulse dict with plain Python types
    pulse: Dict[str, Any] = {
        "title": str(args.title),     # we will force single quotes at dump time
        "summary": summary_text,      # we will force folded style (>)
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)  # belt-and-suspenders

    # Custom dumper to enforce:
    # - summary as folded block scalars (style '>')
    # - title as single-quoted scalars (style "'")
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                val_node = yaml.ScalarNode("tag:yaml.org,2002:str", str(v), style=">")
            elif k == "title":
                val_node = yaml.ScalarNode("tag:yaml.org,2002:str", str(v), style="'")
            else:
                val_node = dumper.represent_data(v)
            node.value.append((key_node, val_node))
        return node

    _D.add_representer(dict, _repr_mapping)

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(
            pulse,
            stream=f,
            Dumper=_D,            # custom folded summary + quoted title
            sort_keys=False,
            allow_unicode=True,   # keep m-dash “—” etc.
            width=1000,           # avoid line wrapping; site handles layout
        )

    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
