#!/usr/bin/env python3
"""
make_pulse.py — turn metrics JSON into a strict Φ-Mesh pulse YAML.

Reads:  metrics JSON (from run_fd_probe.py)
Writes: pulse YAML (title single-quoted, summary folded)

Note: the *filename* (and thus batch label) is handled by the workflow.
We only write the YAML content here.
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
    try:
        import numpy as np  # type: ignore
        np_scalar = np.generic  # type: ignore[attr-defined]
    except Exception:
        class _NP: ...
        np_scalar = _NP  # type: ignore

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_scalar):
        try:
            return x.item()
        except Exception:
            return float(x)
    if isinstance(x, dict):
        return {str(k): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


# ----- main ----------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Dataset slug for filename (already includes _batchN)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    # Load metrics
    with open(args.metrics, "r", encoding="utf-8") as f:
        raw = json.load(f)
    m: Dict[str, Any] = to_builtin(raw)

    # Pull common fields (provide '?' if not present)
    n       = m.get("n", "?")
    mean_dt = m.get("mean_dt", "?")
    cv_dt   = m.get("cv_dt", "?")
    src     = m.get("source", "")
    details = m.get("details") or {}

    # Build summary
    slug = safe_slug(args.dataset)  # already batch-suffixed by workflow
    parts: List[str] = []
    parts.append(f"NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}.")
    if src:
        parts.append(f"Source: {src}.")
    if details:
        try:
            subset = {k: details[k] for k in ["dataset", "var", "xyz", "window"] if k in details}
            if subset:
                parts.append(f"Probe: {subset}.")
        except Exception:
            pass
    summary_text = " ".join(s.strip() for s in parts if s)

    # Tags
    tags = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Pulse dict
    pulse = {
        "title": str(args.title),   # single-quoted via custom dumper
        "summary": summary_text,    # folded block via custom dumper
        "tags": [str(t) for t in tags],
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Dumper that forces: title single quotes, summary folded
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            k_node = dumper.represent_data(k)
            if k == "summary":
                v_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=str(v), style=">")
            elif k == "title":
                sval = str(v)
                if (sval.startswith("'") and sval.endswith("'")) or (sval.startswith('"') and sval.endswith('"')):
                    sval = sval[1:-1]
                v_node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=sval, style="'")
            else:
                v_node = dumper.represent_data(v)
            node.value.append((k_node, v_node))
        return node

    _D.add_representer(dict, _repr_mapping)

    # Write YAML (filename is provided by the workflow's choice of slug)
    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{dt.date.today().isoformat()}_{slug}.yml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(pulse, stream=f, Dumper=_D, sort_keys=False, allow_unicode=True, width=1000)
    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
