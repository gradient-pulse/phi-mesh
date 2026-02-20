#!/usr/bin/env python3
"""
extract_gc_features.py

Scans results directories for MF V0+V1 (and optionally V0-only) run outputs that
contain stored curves, extracts "Gradient Choreography" (GC) features, and writes
a single CSV summary.

Why:
- Gate 3 needs *shape* comparators, not only scalar distances.
- This produces the envelope table needed for observed vs end-to-end ΛCDM recon.

Usage:
  python extract_gc_features.py \
    --root results/topology_mf_v0_v1 \
    --out results/topology_mf_v0_v1/gc_features.csv

Optional:
  --include-v0  (also extracts V0 features if curves present)

Assumptions:
- JSON result files exist somewhere under --root
- Curves are stored as arrays keyed by one of several common names.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ----------------------------
# Helpers: curve extraction
# ----------------------------

def _as_floats(x: Any) -> Optional[List[float]]:
    if x is None:
        return None
    if isinstance(x, list):
        try:
            return [float(v) for v in x]
        except Exception:
            return None
    return None


def _get_first_key(d: Dict[str, Any], keys: List[str]) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return None


def extract_curves(payload: Dict[str, Any]) -> Tuple[Optional[List[float]], Optional[List[float]], Optional[List[float]]]:
    """
    Returns (nu, v1, v0) if available. Any may be None.
    Tries multiple key variants to be compatible with evolving pipeline outputs.
    """

    # Common key variants seen in similar pipelines
    nu = _as_floats(_get_first_key(payload, [
        "nu_grid", "nu", "nu_vals", "nu_values", "nu_axis"
    ]))

    # Some outputs nest curves under "curves" / "data" / "observed"
    container = payload
    for nest_key in ["curves", "curve_data", "data", "observed", "obs", "summary"]:
        if isinstance(payload.get(nest_key), dict):
            container = payload[nest_key]
            # don't break immediately; prefer deepest useful nesting
            payload = container

    v1 = _as_floats(_get_first_key(container, [
        "v1_obs", "V1_obs", "v1_curve", "V1_curve", "v1", "V1"
    ]))

    v0 = _as_floats(_get_first_key(container, [
        "v0_obs", "V0_obs", "v0_curve", "V0_curve", "v0", "V0"
    ]))

    # If nu is still missing, see if curves are paired as list of [nu, val]
    if nu is None:
        paired = _get_first_key(container, ["v1_pairs", "V1_pairs", "v0_pairs", "V0_pairs"])
        if isinstance(paired, list) and paired and isinstance(paired[0], (list, tuple)) and len(paired[0]) == 2:
            try:
                nu = [float(p[0]) for p in paired]
                # do not overwrite v1/v0 here; those are ambiguous
            except Exception:
                pass

    return nu, v1, v0


def infer_metadata(path: Path) -> Dict[str, Any]:
    """
    Infers run_id / gate-ish metadata from directory structure.
    Works with your layout: .../runs/<run_id>/... or .../controls/<name>/runs/<run_id>/...
    """
    parts = path.parts
    meta: Dict[str, Any] = {
        "json_path": str(path),
        "run_id": "",
        "control": "",
        "category": "",  # runs | controls
    }

    # run_id is often the parent folder name if it's all digits
    for i in range(len(parts) - 1, -1, -1):
        p = parts[i]
        if p.isdigit():
            meta["run_id"] = p
            break

    if "controls" in parts:
        meta["category"] = "controls"
        try:
            idx = parts.index("controls")
            meta["control"] = parts[idx + 1] if idx + 1 < len(parts) else ""
        except Exception:
            pass
    elif "runs" in parts:
        meta["category"] = "runs"

    return meta


# ----------------------------
# GC feature computation
# ----------------------------

@dataclass
class GCFeatures:
    nu_peak: float
    peak_height: float
    fwhm: float
    bump_count: int
    d2_sign_changes: int
    shape_energy: float  # L2 norm of curve (relative magnitude)


def finite_diff(x: List[float], y: List[float]) -> List[float]:
    """Simple first derivative dy/dx with endpoints using one-sided diff."""
    n = len(x)
    if n < 2:
        return [0.0] * n
    dy = [0.0] * n
    for i in range(1, n - 1):
        dx = x[i + 1] - x[i - 1]
        dy[i] = (y[i + 1] - y[i - 1]) / dx if dx != 0 else 0.0
    dy[0] = (y[1] - y[0]) / (x[1] - x[0]) if (x[1] - x[0]) != 0 else 0.0
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2]) if (x[-1] - x[-2]) != 0 else 0.0
    return dy


def count_local_maxima(y: List[float]) -> int:
    """Counts strict local maxima."""
    c = 0
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            c += 1
    return c


def count_sign_changes(arr: List[float], eps: float = 1e-12) -> int:
    """Counts sign changes ignoring near-zero values."""
    sgn = []
    for v in arr:
        if abs(v) <= eps:
            continue
        sgn.append(1 if v > 0 else -1)
    if len(sgn) < 2:
        return 0
    changes = 0
    for a, b in zip(sgn, sgn[1:]):
        if a != b:
            changes += 1
    return changes


def compute_fwhm(nu: List[float], y: List[float], peak_idx: int) -> float:
    """Full width at half maximum around peak, using linear scan."""
    peak = y[peak_idx]
    if peak <= 0:
        return 0.0
    half = 0.5 * peak

    # left crossing
    left = peak_idx
    while left > 0 and y[left] >= half:
        left -= 1
    # right crossing
    right = peak_idx
    while right < len(y) - 1 and y[right] >= half:
        right += 1

    # Approximate width using nu positions at the first below-half indices
    nu_left = nu[left]
    nu_right = nu[right]
    return float(nu_right - nu_left)


def gc_features(nu: List[float], y: List[float]) -> GCFeatures:
    if len(nu) != len(y) or len(nu) < 5:
        raise ValueError("nu/y length mismatch or too short to compute features")

    peak_idx = max(range(len(y)), key=lambda i: y[i])
    nu_peak = float(nu[peak_idx])
    peak_height = float(y[peak_idx])

    fwhm = compute_fwhm(nu, y, peak_idx)

    dy = finite_diff(nu, y)
    d2y = finite_diff(nu, dy)
    d2_sign_changes = count_sign_changes(d2y)

    bump_count = count_local_maxima(y)

    # L2 energy with nu-grid spacing (approx)
    # assumes roughly uniform spacing
    dnu = abs(nu[1] - nu[0]) if len(nu) > 1 else 1.0
    shape_energy = math.sqrt(sum(v * v for v in y) * dnu)

    return GCFeatures(
        nu_peak=nu_peak,
        peak_height=peak_height,
        fwhm=float(fwhm),
        bump_count=int(bump_count),
        d2_sign_changes=int(d2_sign_changes),
        shape_energy=float(shape_energy),
    )


# ----------------------------
# Main scan & write
# ----------------------------

def iter_json_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.json"):
        # skip obvious large metadata dumps if you have them
        if p.name.lower().startswith("manifest"):
            continue
        yield p


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def write_csv(rows: List[Dict[str, Any]], out_path: Path) -> None:
    if not rows:
        raise RuntimeError("No rows to write. (Did the script find any curves in JSON outputs?)")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, required=True, help="Root results directory to scan (e.g., results/topology_mf_v0_v1)")
    ap.add_argument("--out", type=str, required=True, help="Output CSV path")
    ap.add_argument("--include-v0", action="store_true", help="Also extract V0 features if curves are present")
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out)

    rows: List[Dict[str, Any]] = []
    scanned = 0
    used = 0

    for jf in iter_json_files(root):
        scanned += 1
        payload = load_json(jf)
        if not isinstance(payload, dict):
            continue

        nu, v1, v0 = extract_curves(payload)

        if nu is None:
            continue
        if v1 is None and not (args.include_v0 and v0 is not None):
            continue

        meta = infer_metadata(jf)

        row: Dict[str, Any] = {
            **meta,
            "root": str(root),
        }

        # V1 GC features
        if v1 is not None:
            try:
                f = gc_features(nu, v1)
                row.update({
                    "gc_v1_nu_peak": f.nu_peak,
                    "gc_v1_peak_height": f.peak_height,
                    "gc_v1_fwhm": f.fwhm,
                    "gc_v1_bump_count": f.bump_count,
                    "gc_v1_d2_sign_changes": f.d2_sign_changes,
                    "gc_v1_shape_energy": f.shape_energy,
                })
            except Exception:
                # if curve too short or malformed, skip
                continue

        # Optional V0 features (less important for your next step, but useful)
        if args.include_v0 and v0 is not None:
            try:
                f0 = gc_features(nu, v0)
                row.update({
                    "gc_v0_nu_peak": f0.nu_peak,
                    "gc_v0_peak_height": f0.peak_height,
                    "gc_v0_fwhm": f0.fwhm,
                    "gc_v0_bump_count": f0.bump_count,
                    "gc_v0_d2_sign_changes": f0.d2_sign_changes,
                    "gc_v0_shape_energy": f0.shape_energy,
                })
            except Exception:
                pass

        rows.append(row)
        used += 1

    write_csv(rows, out)

    print(f"[extract_gc_features] scanned_json={scanned} used_with_curves={used} out={out}")


if __name__ == "__main__":
    main()
