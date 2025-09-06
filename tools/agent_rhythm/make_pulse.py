#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Inputs
  --metrics: Path to metrics JSON (produced by run_fd_probe.py)
  --title:   Pulse title (single quotes enforced in YAML)
  --dataset: Dataset slug (used in pulse filename; may include _batchN)
  --tags:    Space-separated tag list
  --outdir:  Output directory for pulse YAML (e.g., pulse/auto)

Output
  pulse/auto/YYYY-MM-DD_<dataset>.yml

Notes
  • Title is always single-quoted (per pulse style).
  • Summary is folded (">") and now includes n, mean_dt, cv_dt when present.
  • If <dataset> ends with “_batchN”, batchN is echoed in the summary
    after the Probe: {...} block for easy visual traceability.
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
    """Sanitize a string into a filesystem- and URL-friendly slug."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """
    Recursively coerce to plain Python builtins so PyYAML is happy.
    Handles numpy scalars, pathlib, datetimes, dict/list/tuple/set.
    """
    # late import to avoid hard dependency if numpy isn’t present
    try:
        import numpy as np  # type: ignore
        np_generic = np.generic  # type: ignore[attr-defined]
    except Exception:
        class _NP: ...
        np_generic = _NP  # sentinel that never matches

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x

    if isinstance(x, np_generic):  # numpy scalar -> Python scalar
        try:
            return x.item()
        except Exception:
            # last resort: best-effort float conversion
            try:
                return float(x)
            except Exception:
                return str(x)

    # pathlike
    try:
        import pathlib  # type: ignore
        if isinstance(x, pathlib.Path):
            return str(x)
    except Exception:
        pass

    # datetimes
    if isinstance(x, (dt.date, dt.datetime, dt.time)):
        return str(x)

    # containers
    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]

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

    # Pull common fields with defaults (sources may vary slightly)
    n        = metrics.get("n") or metrics.get("count") or "?"
    mean_dt  = metrics.get("mean_dt", "?")
    cv_dt    = metrics.get("cv_dt", "?")
    src      = metrics.get("source", "")
    details  = metrics.get("details") or metrics.get("extra") or {}

    # Filename bits
    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    slug = safe_slug(args.dataset)

    # Detect trailing batchN in slug like "..._batch3"
    batch_label = None
    m = re.search(r"(?:^|_)batch(\d+)$", slug)
    if m:
        batch_label = f"batch{m.group(1)}"

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{today_str}_{slug}.yml")

    # Build summary (folded style)
    summary_lines: List[str] = []
    summary_lines.append(
        f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}."
    )
    if src:
        summary_lines.append(f"Source: {src}.")
    if details:
        # Only include the salient probe fields if present
        keys = ["dataset", "var", "xyz", "window"]
        subset = {k: details[k] for k in keys if k in details}
        if subset:
            if batch_label:
                summary_lines.append(f"Probe: {subset} ({batch_label}).")
            else:
                summary_lines.append(f"Probe: {subset}.")
    elif batch_label:
        # No details, but do show batch if we detected it
        summary_lines.append(f"Batch: {batch_label}.")

    summary_text = " ".join(str(s).strip() for s in summary_lines if s)

    # Tags: space-separated -> list
    tags = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Construct pulse dict using ONLY builtins
    pulse = {
        "title": str(args.title),   # quoting handled by dumper below
        "summary": summary_text,    # folded style via dumper
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Custom dumper to force folded style for summary and SINGLE QUOTES for title
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
                # force single quotes per strict pulse rule
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
