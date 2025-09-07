#!/usr/bin/env python3
"""
make_pulse.py — turn rhythm metrics JSON into a strict Φ-Mesh pulse YAML.

Inputs
------
--metrics  path/to/*.metrics.json   (raw metrics JSON produced by fd_probe)
--title    pulse title              (single quotes will be enforced in output)
--dataset  dataset slug             (e.g., "isotropic1024coarse_jhtdb_batch4")
--tags     space-separated tags     (e.g., "nt_rhythm turbulence navier_stokes rgp")
--outdir   output directory         (e.g., "pulse/auto")
--recent   OPTIONAL: path to JSONL file with recent fundamentals (Hz), one per line

Output
------
pulse/auto/YYYY-MM-DD_<dataset>.yml  (YAML only; no metrics duplication)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

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


def read_recent_fundamentals(path: Optional[str]) -> List[float]:
    if not path:
        return []
    out: List[float] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # allow either raw float or JSON number
                    if line[0] in "[{\"":
                        val = json.loads(line)
                        if isinstance(val, (int, float)):
                            out.append(float(val))
                    else:
                        out.append(float(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return out


# ---------- spectrum interpretation ------------------------------------------

def _sorted_peaks(metrics: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Return peaks sorted by *power* desc, then by freq asc."""
    peaks = metrics.get("peaks") or []
    # peaks may be [[f,p], [f,p], ...] or {"freq":f,"power":p} items; normalize
    norm: List[Tuple[float, float]] = []
    for p in peaks:
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                freq = float(p[0]); power = float(p[1])
            elif isinstance(p, dict):
                freq = float(p.get("freq", 0.0)); power = float(p.get("power", 0.0))
            else:
                continue
            if freq > 0 and power >= 0:
                norm.append((freq, power))
        except Exception:
            continue
    # sort by power desc, freq asc
    norm.sort(key=lambda t: (-t[1], t[0]))
    return norm


def infer_fundamental_and_ladder(peaks: List[Tuple[float, float]],
                                 tol: float = 0.06) -> Tuple[Optional[float], int]:
    """
    Choose dominant peak as fundamental f0, then count harmonics near n*f0 (n=2,3,...).
    tol = fractional tolerance for matching (±tol).
    Returns (f0, ladder_count) where ladder_count = number of *harmonics beyond f0*
    that match (i.e., fund+2 harmonics -> ladder=2).
    """
    if not peaks:
        return None, 0
    f0 = peaks[0][0]
    ladder = 0
    # Build a set of available freqs for quick matching
    freqs = [fp[0] for fp in sorted(peaks, key=lambda t: t[0])]  # ascending by freq
    for n in (2, 3, 4, 5):
        target = n * f0
        lo = target * (1 - tol)
        hi = target * (1 + tol)
        hit = any(lo <= f <= hi for f in freqs)
        if hit:
            ladder += 1
        else:
            # stop early if a harmonic is missing; conservative ladder
            break
    return f0, ladder


def dominance_ratio(peaks: List[Tuple[float, float]]) -> float:
    if not peaks:
        return 0.0
    if len(peaks) == 1:
        return float("inf") if peaks[0][1] > 0 else 0.0
    p1 = peaks[0][1]
    # find the strongest *other* component not equal in freq (defensive)
    p2 = None
    for _, pw in peaks[1:]:
        if pw > 0:
            p2 = pw
            break
    if p2 is None or p2 == 0:
        return float("inf") if p1 > 0 else 0.0
    return p1 / p2


def decisive_with_recent(f0: Optional[float], ladder: int, dom: float,
                         recent: Iterable[float], agree_tol: float = 0.10) -> bool:
    """
    'decisive' requires: ladder≥2 and dominance≥2 and ≥3 recent fundamentals
    agree within ±10% of f0.
    """
    if f0 is None:
        return False
    if ladder < 2 or dom < 2.0:
        return False
    # agreement check
    votes = 0
    lo = f0 * (1 - agree_tol)
    hi = f0 * (1 + agree_tol)
    for r in recent:
        if lo <= r <= hi:
            votes += 1
    return votes >= 3


def hint_text(ladder: int, dom: float, decisive: bool) -> str:
    if decisive:
        return f"decisive — spatially coherent fundamental + harmonics (ladder={ladder}), dominance={dom:.2f}"
    if ladder >= 2 and dom >= 2.0:
        return f"strong — clean peak + {ladder} harmonics (ladder={ladder}), dominance={dom:.2f}"
    if ladder >= 1 or dom >= 1.2:
        return f"weak — single dominant peak (ladder={ladder}), dominance={dom:.2f}"
    return "inconclusive"


# ---------- main --------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="Path to metrics JSON")
    ap.add_argument("--title",   required=True, help="Pulse title")
    ap.add_argument("--dataset", required=True, help="Pulse slug (e.g. iso_jhtdb_batch3)")
    ap.add_argument("--tags",    required=True, help="Space-separated tags")
    ap.add_argument("--outdir",  required=True, help="Output directory (e.g., pulse/auto)")
    ap.add_argument("--recent",  required=False, help="Optional JSONL file with recent fundamentals (Hz)")
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

    # Spectrum interpretation → ladder / dominance / f0
    peaks = _sorted_peaks(metrics)
    f0, ladder = infer_fundamental_and_ladder(peaks)
    dom = dominance_ratio(peaks)
    recent_f = read_recent_fundamentals(args.recent)
    decisive = decisive_with_recent(f0, ladder, dom, recent_f)

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
    summary_text = " ".join(str(b).strip() for b in summary_bits if b)

    # Tags -> list
    tag_list = [t for t in re.split(r"\s+", args.tags.strip()) if t]

    # Pulse dict (builtins only)
    pulse = {
        "title": str(args.title),
        "summary": summary_text,
        # explicit hint key (short, scannable in diffs)
        "hint": hint_text(ladder, dom, decisive),
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

    # optional: echo a compact line for the agent to append to recent fundamentals file
    if f0 is not None:
        print(f"fundamental_hz={f0:.6f} ladder={ladder} dominance={dom:.2f}")
    print(f"Pulse written: {out_path}")


if __name__ == "__main__":
    main()
