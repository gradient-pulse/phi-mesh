#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML,
with a compact “closing-in” rhythm hint appended to the summary.

Inputs:
  --metrics  path/to/*.metrics.json  (raw metrics JSON produced by fd_probe)
  --title    pulse title (single quotes will be enforced in output)
  --dataset  dataset slug for pulse (e.g., "isotropic1024coarse_jhtdb_batch3")
  --tags     space-separated tags (e.g., "nt_rhythm turbulence navier_stokes rgp")
  --outdir   output directory (e.g., "pulse/auto")

Output:
  pulse/auto/YYYY-MM-DD_<dataset>.yml   (YAML only; no metrics duplication)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from typing import Any, Dict, List, Sequence, Tuple

import yaml


# ---------- helpers -----------------------------------------------------------

def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"


def to_builtin(x: Any) -> Any:
    """Recursively coerce to plain Python builtins so PyYAML is happy."""
    # Optional numpy support (don’t hard-require it)
    try:
        import numpy as np  # type: ignore
        np_scalar = np.generic  # type: ignore[attr-defined]
    except Exception:
        class _NP: ...
        np_scalar = _NP  # sentinel

    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, np_scalar):  # numpy scalar -> Python scalar
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

    if isinstance(x, dict):
        return {str(to_builtin(k)): to_builtin(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [to_builtin(v) for v in x]
    return str(x)


def _as_float(x: Any, default: float | None = None) -> float | None:
    try:
        return float(x)
    except Exception:
        return default


def _compute_hint(peaks: Sequence[Sequence[float]] | None,
                  f0: float | None,
                  divergence_ratio: float | None) -> Tuple[str, Dict[str, Any]]:
    """
    Return (hint_text, debug_dict).
    - dominance = power(f0) / max other power
    - ladder = count of harmonics within ±5% around 2*f0, 3*f0, ...
    Gates (tweakable):
      decisive: dominance ≥ 2.0 and ladder ≥ 3 and divergence_ratio ≤ 1e-10
      strong:   dominance ≥ 1.6 and ladder ≥ 2
      weak:     dominance ≥ 1.3 or  ladder ≥ 2
    """
    debug: Dict[str, Any] = {"dominance": None, "ladder": 0, "f0": f0, "divergence_ratio": divergence_ratio}
    if not peaks or f0 is None:
        return "hint: inconclusive", debug

    # sanitize peaks as [(freq, power), ...] with numeric values
    clean: List[Tuple[float, float]] = []
    for p in peaks:
        if not isinstance(p, (list, tuple)) or len(p) < 2:
            continue
        f = _as_float(p[0])
        a = _as_float(p[1])
        if f is None or a is None:
            continue
        clean.append((f, a))
    if not clean:
        return "hint: inconclusive", debug

    # locate f0 power and best "other" power
    # allow slight mismatch in f0 by nearest frequency within 2%
    tol_f0 = 0.02
    target_low, target_high = f0 * (1 - tol_f0), f0 * (1 + tol_f0)
    p0 = 0.0
    others: List[float] = []
    for f, a in clean:
        if target_low <= f <= target_high:
            p0 = max(p0, a)
        else:
            others.append(a)
    if p0 <= 0.0 or not others:
        debug["dominance"] = None
        return "hint: inconclusive", debug

    dom = p0 / max(others)
    debug["dominance"] = dom

    # count harmonics within ±5%
    tol = 0.05
    def _exists_near(freq: float) -> bool:
        low, high = freq * (1 - tol), freq * (1 + tol)
        return any((low <= f <= high) for f, _ in clean)

    ladder = 0
    # check up to k=5 harmonics (lightweight)
    for k in (2, 3, 4, 5):
        if _exists_near(k * f0):
            ladder += 1
    debug["ladder"] = ladder

    # gates
    dr = divergence_ratio if divergence_ratio is not None else float("inf")
    if dom >= 2.0 and ladder >= 3 and dr <= 1e-10:
        level = "decisive"
    elif dom >= 1.6 and ladder >= 2:
        level = "strong"
    elif dom >= 1.3 or ladder >= 2:
        level = "weak"
    else:
        level = "inconclusive"

    # brief text; include small numbers for debugging intuition
    if debug["dominance"] is None:
        return "hint: inconclusive", debug

    # round for readability
    dom_txt = f"{dom:.2f}"
    hint_core = {
        "decisive": f"decisive — stable ladder {ladder}+ and low divergence",
        "strong":   f"strong — clean peak + {ladder} harmonics (ladder={ladder})",
        "weak":     f"weak — single dominant peak (ladder={ladder})",
        "inconclusive": "inconclusive",
    }[level]

    if divergence_ratio is not None and divergence_ratio == divergence_ratio:  # not NaN
        return f"hint: {hint_core}, dominance={dom_txt}", debug
    else:
        return f"hint: {hint_core}, dominance={dom_txt}", debug


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Pulse slug (e.g. iso_jhtdb_batch3)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    args = ap.parse_args()

    # Load metrics JSON (builtins only)
    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics_raw = json.load(f)
    metrics: Dict[str, Any] = to_builtin(metrics_raw)

    # Extract commonly used numbers (fallbacks for older files)
    n       = metrics.get("n", "?")
    mean_dt = metrics.get("mean_dt", "?")
    cv_dt   = metrics.get("cv_dt", "?")
    src     = metrics.get("source", "")
    details = metrics.get("details") or {}

    # Rhythm-hint inputs
    peaks = metrics.get("peaks")  # expected [[freq, power], ...]
    f0    = _as_float(metrics.get("main_peak_freq"))
    dr    = _as_float(metrics.get("divergence_ratio"))

    hint_text, _hint_dbg = _compute_hint(peaks, f0, dr)

    # Build filename parts
    today_str = dt.date.today().isoformat()  # YYYY-MM-DD
    slug = safe_slug(args.dataset)

    os.makedirs(args.outdir, exist_ok=True)
    out_path = os.path.join(args.outdir, f"{today_str}_{slug}.yml")

    # Summary (folded, compact)
    probe_subset = {}
    for k in ("dataset", "var", "xyz", "window"):
        if k in details:
            probe_subset[k] = details[k]

    summary_bits: List[str] = []
    summary_bits.append(
        f'NT rhythm probe on “{slug}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}.'
    )
    if src:
        summary_bits.append(f"Source: {src}.")
    if probe_subset:
        summary_bits.append(f"Probe: {probe_subset}.")
    # append the compact hint
    summary_bits.append(hint_text)

    summary_text = " ".join(str(b).strip() for b in summary_bits if b)

    # Tags -> list
    tag_list = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Pulse dict (builtins only)
    pulse = {
        "title": str(args.title),
        "summary": summary_text,
        "tags": tag_list,
        "papers": [],
        "podcasts": [],
    }
    pulse = to_builtin(pulse)

    # Custom dumper: folded summary; single-quote title explicitly
    class _D(yaml.SafeDumper):
        pass

    def _repr_mapping(dumper, data):
        node = yaml.nodes.MappingNode(tag="tag:yaml.org,2002:map", value=[])
        for k, v in data.items():
            key_node = dumper.represent_data(k)
            if k == "summary":
                val_node = yaml.ScalarNode(
                    tag="tag:yaml.org,2002:str", value=str(v), style=">"
                )
            elif k == "title":
                sval = str(v)
                if (sval.startswith("'") and sval.endswith("'")) or (sval.startswith('"') and sval.endswith('"')):
                    sval = sval[1:-1]
                val_node = yaml.ScalarNode(
                    tag="tag:yaml.org,2002:str", value=sval, style="'"
                )
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
