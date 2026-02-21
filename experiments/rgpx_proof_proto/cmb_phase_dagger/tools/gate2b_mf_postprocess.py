#!/usr/bin/env python3
"""
gate2b_mf_postprocess.py

Gate 2B postprocess for MF V0+V1:
- discovers archived runs under --runs_dir by searching for manifest.txt
  containing: "control: <control_name>"
- extracts key MF metrics into a sweep table (csv + md)
- extracts V1 peak info (csv + md)
- extracts GC features from curves (csv)

Robust behavior:
- will not hard-fail if some runs are missing expected JSONs
- will still write outputs with diagnostic rows so GitHub Actions can commit them

Expected JSON schema (confirmed by your example):
  thresholds.nus
  observed.v0_curve, observed.v1_curve
  surrogate.v0_mean_curve, surrogate.v1_mean_curve
  plus scalar metrics in observed / surrogate blocks
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


# ----------------------------
# Small utilities
# ----------------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def safe_get(d: Dict[str, Any], path: str, default=None):
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def to_float(x: Any):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def to_int(x: Any):
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_csv_allow_empty(path: Path, rows: List[Dict[str, Any]], empty_note: str) -> None:
    """
    Always writes a CSV. If rows is empty, writes a one-row diagnostic.
    """
    ensure_dir(path.parent)
    if not rows:
        rows = [{"note": empty_note}]
    keys = set()
    for r in rows:
        keys.update(r.keys())
    fieldnames = sorted(keys)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def fmt(x: Any, nd: int = 6) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        return f"{x:.{nd}g}"
    return str(x)


def write_md_table(path: Path, rows: List[Dict[str, Any]], columns: List[str], title: str) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if not rows:
            f.write("_No rows._\n")
            return
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("| " + " | ".join(["---"] * len(columns)) + " |\n")
        for r in rows:
            f.write("| " + " | ".join(fmt(r.get(c, "")) for c in columns) + " |\n")
        f.write("\n")


# ----------------------------
# Run discovery
# ----------------------------

def iter_manifest_paths(runs_dir: Path) -> Iterable[Path]:
    yield from runs_dir.rglob("manifest.txt")


def manifest_has_control(manifest_text: str, control_name: str) -> bool:
    return f"control: {control_name}" in manifest_text


def derive_run_id_from_path(p: Path) -> str:
    for part in reversed(p.parts):
        if part.isdigit():
            return part
    return p.parent.name


def find_json_for_run(run_dir: Path) -> List[Path]:
    """
    Robust JSON selection:
      1) prefer *aggregate*.json
      2) else any *mf_v0_v1*.json
      3) else any .json (last resort)
    """
    all_json = sorted(run_dir.rglob("*.json"))
    if not all_json:
        return []

    agg = [p for p in all_json if ("aggregate" in p.name and "mf_v0_v1" in p.name)]
    if agg:
        return agg

    mf = [p for p in all_json if ("mf_v0_v1" in p.name)]
    if mf:
        return mf

    return all_json


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


def looks_like_mf_json(obj: Dict[str, Any]) -> bool:
    if not isinstance(obj, dict):
        return False
    if not isinstance(obj.get("observed"), dict):
        return False
    thr = obj.get("thresholds")
    if not isinstance(thr, dict):
        return False
    nus = thr.get("nus")
    if not isinstance(nus, list) or len(nus) < 10:
        return False
    # require v1_curve to exist (key diagnostic for MF)
    if not isinstance(safe_get(obj, "observed.v1_curve"), list):
        return False
    return True


# ----------------------------
# V1 peak extraction
# ----------------------------

@dataclass
class PeakInfo:
    peak_idx: int
    nu_peak: float
    peak_height: float


def peak_info(nu: List[float], y: List[float]) -> PeakInfo:
    if len(nu) != len(y) or len(nu) < 3:
        raise ValueError("nu/y mismatch or too short for peak extraction")
    i = max(range(len(y)), key=lambda k: y[k])
    return PeakInfo(peak_idx=i, nu_peak=float(nu[i]), peak_height=float(y[i]))


# ----------------------------
# GC features
# ----------------------------

def _count_local_maxima(y: List[float]) -> int:
    c = 0
    for i in range(1, len(y) - 1):
        if y[i] > y[i - 1] and y[i] > y[i + 1]:
            c += 1
    return c


def _finite_diff(x: List[float], y: List[float]) -> List[float]:
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


def _count_sign_changes(arr: List[float], eps: float = 1e-12) -> int:
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


def _fwhm(nu: List[float], y: List[float], peak_idx: int) -> float:
    peak = y[peak_idx]
    if peak <= 0:
        return 0.0
    half = 0.5 * peak
    left = peak_idx
    while left > 0 and y[left] >= half:
        left -= 1
    right = peak_idx
    while right < len(y) - 1 and y[right] >= half:
        right += 1
    return float(nu[right] - nu[left])


def _curve_energy(nu: List[float], y: List[float]) -> float:
    if len(nu) < 2:
        return float("nan")
    dnu = abs(nu[1] - nu[0])
    return math.sqrt(sum(v * v for v in y) * dnu)


def gc_features_from_mf_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    nu = safe_get(obj, "thresholds.nus")
    nu = [float(v) for v in nu]

    obs = obj.get("observed", {})
    sur = obj.get("surrogate", {})

    v1_obs = obs.get("v1_curve")
    v0_obs = obs.get("v0_curve")
    v1_mean = sur.get("v1_mean_curve")
    v0_mean = sur.get("v0_mean_curve")

    out: Dict[str, Any] = {}

    def add(prefix: str, y_raw: Any):
        if not isinstance(y_raw, list) or not y_raw:
            return
        y = [float(v) for v in y_raw]
        if len(y) != len(nu):
            raise ValueError(f"{prefix}: curve length mismatch vs nu grid")
        pk = peak_info(nu, y)
        out[f"{prefix}_nu_peak"] = pk.nu_peak
        out[f"{prefix}_peak_height"] = pk.peak_height
        out[f"{prefix}_fwhm"] = _fwhm(nu, y, pk.peak_idx)
        out[f"{prefix}_bump_count"] = int(_count_local_maxima(y))
        d2 = _finite_diff(nu, _finite_diff(nu, y))
        out[f"{prefix}_d2_sign_changes"] = int(_count_sign_changes(d2))
        out[f"{prefix}_shape_energy"] = float(_curve_energy(nu, y))

    add("gc_v1_obs", v1_obs)
    add("gc_v1_mean", v1_mean)
    add("gc_v0_obs", v0_obs)
    add("gc_v0_mean", v0_mean)

    return out


# ----------------------------
# Per-run summarization
# ----------------------------

def summarize_mf_run(json_path: Path, run_id: str, control_name: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    obj = load_json(json_path)
    if not looks_like_mf_json(obj):
        raise ValueError("JSON does not match MF schema")

    lmax = to_int(obj.get("lmax"))
    nside = to_int(obj.get("nside"))
    n_sims = to_int(obj.get("n_sims"))
    seed = to_int(obj.get("seed"))
    kind = obj.get("kind")

    D0 = to_float(safe_get(obj, "observed.D0_L2"))
    D1 = to_float(safe_get(obj, "observed.D1_L2"))
    Dmf = to_float(safe_get(obj, "observed.D_mf"))
    Zmf = to_float(safe_get(obj, "observed.Z_mf"))
    p2 = to_float(obj.get("p_two_sided_mf", obj.get("p_two_sided")))

    D0m = to_float(safe_get(obj, "surrogate.D0_mean"))
    D0s = to_float(safe_get(obj, "surrogate.D0_std"))
    D1m = to_float(safe_get(obj, "surrogate.D1_mean"))
    D1s = to_float(safe_get(obj, "surrogate.D1_std"))
    Dmfm = to_float(safe_get(obj, "surrogate.D_mf_mean"))
    Dmfs = to_float(safe_get(obj, "surrogate.D_mf_std"))

    nu = [float(v) for v in safe_get(obj, "thresholds.nus")]
    v1_obs = [float(v) for v in safe_get(obj, "observed.v1_curve")]
    v1_mean = safe_get(obj, "surrogate.v1_mean_curve")
    v1_mean = [float(v) for v in v1_mean] if isinstance(v1_mean, list) else None

    # peak row
    peak_row: Dict[str, Any] = {
        "control": control_name,
        "run_id": run_id,
        "json": str(json_path),
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": seed,
    }
    pk = peak_info(nu, v1_obs)
    peak_row.update({
        "v1_obs_nu_peak": pk.nu_peak,
        "v1_obs_peak_height": pk.peak_height,
    })
    if v1_mean and len(v1_mean) == len(nu):
        pk2 = peak_info(nu, v1_mean)
        peak_row.update({
            "v1_mean_nu_peak": pk2.nu_peak,
            "v1_mean_peak_height": pk2.peak_height,
        })

    # sweep row
    sweep_row: Dict[str, Any] = {
        "control": control_name,
        "run_id": run_id,
        "json": str(json_path),
        "kind": kind,
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": seed,
        "p_two_sided_mf": p2,
        "D0_L2": D0,
        "D1_L2": D1,
        "D_mf": Dmf,
        "Z_mf": Zmf,
        "D0_mean": D0m,
        "D0_std": D0s,
        "D1_mean": D1m,
        "D1_std": D1s,
        "D_mf_mean": Dmfm,
        "D_mf_std": Dmfs,
    }

    # gc row
    gc_row: Dict[str, Any] = {
        "control": control_name,
        "run_id": run_id,
        "json": str(json_path),
        "kind": kind,
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": seed,
        "p_two_sided_mf": p2,
    }
    try:
        gc_row.update(gc_features_from_mf_json(obj))
    except Exception as e:
        gc_row["gc_error"] = str(e)

    return sweep_row, peak_row, gc_row


# ----------------------------
# Main
# ----------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", required=True)
    ap.add_argument("--control_name", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--strict", action="store_true", help="Fail if peak/sweep/gc tables are empty.")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    control = args.control_name

    if not runs_dir.exists():
        raise SystemExit(f"ERROR: runs_dir not found: {runs_dir}")
    ensure_dir(out_dir)

    matched_run_dirs: List[Path] = []
    for mp in iter_manifest_paths(runs_dir):
        if manifest_has_control(read_text(mp), control):
            matched_run_dirs.append(mp.parent)

    matched_run_dirs = sorted(set(matched_run_dirs))
    if not matched_run_dirs:
        raise SystemExit(f"ERROR: No manifests in {runs_dir} contained: control: {control}")

    sweep_rows: List[Dict[str, Any]] = []
    peak_rows: List[Dict[str, Any]] = []
    gc_rows: List[Dict[str, Any]] = []

    for run_dir in matched_run_dirs:
        run_id = derive_run_id_from_path(run_dir)
        json_files = find_json_for_run(run_dir)
        if not json_files:
            sweep_rows.append({
                "control": control,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "error": "No JSON files found under run dir",
            })
            continue

        # process all candidate jsons; keep the ones that match schema
        any_success = False
        last_err = None
        for jf in json_files:
            try:
                srow, prow, grow = summarize_mf_run(jf, run_id, control)
                sweep_rows.append(srow)
                peak_rows.append(prow)
                gc_rows.append(grow)
                any_success = True
            except Exception as e:
                last_err = str(e)

        if not any_success:
            sweep_rows.append({
                "control": control,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "error": f"No usable MF JSON in candidates; last_error={last_err}",
            })

    def sort_key(r: Dict[str, Any]):
        return (r.get("lmax") or 0, str(r.get("run_id", "")))

    sweep_rows = sorted(sweep_rows, key=sort_key)
    peak_rows = sorted(peak_rows, key=sort_key)
    gc_rows = sorted(gc_rows, key=sort_key)

    sweep_csv = out_dir / "mf_sweep_table.csv"
    peaks_csv = out_dir / "v1_peak_table.csv"
    gc_csv = out_dir / "gc_features_table.csv"

    # always write outputs (diagnostic rows if empty)
    write_csv_allow_empty(sweep_csv, sweep_rows, "No sweep rows produced (unexpected).")
    write_csv_allow_empty(peaks_csv, peak_rows, "No peak rows produced. Likely no MF JSON matched schema or v1_curve missing.")
    write_csv_allow_empty(gc_csv, gc_rows, "No GC rows produced. Likely no MF JSON matched schema.")

    # md tables only if we have real rows
    sweep_md = out_dir / "mf_sweep_table.md"
    peaks_md = out_dir / "v1_peak_table.md"

    sweep_cols = [
        "lmax", "nside", "n_sims", "seed", "run_id",
        "D0_L2", "D1_L2", "D_mf", "Z_mf", "p_two_sided_mf",
        "D0_mean", "D0_std", "D1_mean", "D1_std", "D_mf_mean", "D_mf_std",
        "json", "error"
    ]
    peak_cols = [
        "lmax", "nside", "n_sims", "seed", "run_id",
        "v1_obs_nu_peak", "v1_obs_peak_height",
        "v1_mean_nu_peak", "v1_mean_peak_height",
        "json", "error"
    ]

    # for MD, only include rows that have lmax (real rows), else show the diagnostic row
    write_md_table(sweep_md, sweep_rows if sweep_rows else [{"error": "No rows"}], sweep_cols, "Gate 2B — MF V0+V1 Sweep Table")
    write_md_table(peaks_md, peak_rows if peak_rows else [{"error": "No rows"}], peak_cols, "Gate 2B — V1 Peak Table")

    if args.strict and (not sweep_rows or not peak_rows or not gc_rows):
        raise SystemExit("STRICT mode: one or more tables were empty.")

    print("Wrote:")
    print(f"  {sweep_csv}")
    print(f"  {sweep_md}")
    print(f"  {peaks_csv}")
    print(f"  {peaks_md}")
    print(f"  {gc_csv}")


if __name__ == "__main__":
    main()
