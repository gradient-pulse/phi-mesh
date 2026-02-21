#!/usr/bin/env python3
"""
gate2b_mf_postprocess.py — canonical postprocess for MF V0+V1

Produces ONLY:
  mf_sweep_table.csv/.md
  v1_peak_table.csv/.md
  gc_features_table.csv

Robust:
- never fails due to empty tables (writes diagnostic rows instead)
- selects the correct MF result JSON per run directory via filename signatures
- guards sweep distances: only accept D0_L2/D1_L2 if verify_l2_from_curves is present and matches
- observed mode filters ONLY true observed Planck run directories (no /controls leakage)
- fail-safe run_role override if a JSON path points into /controls
- selftest role is set ONLY if selftest_observed_surrogate_seed has a non-empty value in manifest

Supports two modes:
- mode=control  : filter run folders by manifest line "control: <control_name>"
- mode=observed : scan immediate subfolders under runs_dir that contain observed Planck MF JSONs
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
# utilities
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
        return None if x is None else float(x)
    except Exception:
        return None


def to_int(x: Any):
    try:
        return None if x is None else int(x)
    except Exception:
        return None


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_csv_allow_empty(path: Path, rows: List[Dict[str, Any]], empty_note: str) -> None:
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
# discovery
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
    Select the MF result JSON(s) in a run folder, and ignore postprocess JSON.

    Accept if filename contains:
      - 'topology_mf_v0_v1'  (observed-run naming)
      OR
      - 'mf_v0_v1' and 'run' (control naming like ...__run2222.json)

    Reject if filename starts with postprocess prefixes:
      gate2b_, mf_, v1_, gc_
    """
    all_json = sorted(run_dir.glob("*.json"))
    if not all_json:
        all_json = sorted(run_dir.rglob("*.json"))

    def reject(p: Path) -> bool:
        n = p.name
        return n.startswith(("gate2b_", "mf_", "v1_", "gc_"))

    def accept(p: Path) -> bool:
        n = p.name
        if reject(p):
            return False
        if "topology_mf_v0_v1" in n:
            return True
        if ("mf_v0_v1" in n) and ("run" in n):
            return True
        return False

    return [p for p in all_json if accept(p)]


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
    v1 = safe_get(obj, "observed.v1_curve")
    if not isinstance(v1, list) or len(v1) < 10:
        return False
    return True


def parse_run_role_from_manifest(manifest_text: str, mode: str) -> str:
    """
    Conservative role classifier.

    - Mark selftest ONLY if the manifest line 'selftest_observed_surrogate_seed:' has a non-empty value.
      (Some manifests include the key but leave it blank; those are NOT selftests.)
    - Else if mode=observed -> observed
    - Else -> control
    """
    for line in manifest_text.splitlines():
        if line.strip().startswith("selftest_observed_surrogate_seed:"):
            val = line.split(":", 1)[1].strip()
            if val != "":
                return "selftest"
            break  # key present but empty => not a selftest

    if mode == "observed":
        return "observed"
    return "control"


def has_verify_l2_ok(obj: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (ok, reason_tag).
    ok only if diagnostics.verify_l2_from_curves exists AND D0_match & D1_match are true.
    """
    v = safe_get(obj, "diagnostics.verify_l2_from_curves")
    if not isinstance(v, dict):
        return False, "missing_verify_l2"
    d0m = v.get("D0_match")
    d1m = v.get("D1_match")
    if d0m is True and d1m is True:
        return True, ""
    return False, "verify_l2_failed"


# ----------------------------
# peaks + GC features
# ----------------------------

@dataclass
class PeakInfo:
    peak_idx: int
    nu_peak: float
    peak_height: float


def peak_info(nu: List[float], y: List[float]) -> PeakInfo:
    i = max(range(len(y)), key=lambda k: y[k])
    return PeakInfo(peak_idx=i, nu_peak=float(nu[i]), peak_height=float(y[i]))


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
    return sum(1 for a, b in zip(sgn, sgn[1:]) if a != b)


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
    dnu = abs(nu[1] - nu[0])
    return math.sqrt(sum(v * v for v in y) * dnu)


def gc_features_from_mf_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    nu = [float(v) for v in safe_get(obj, "thresholds.nus")]
    obs = obj["observed"]
    sur = obj.get("surrogate", {})

    v1_obs = obs.get("v1_curve")
    v0_obs = obs.get("v0_curve")
    v1_mean = sur.get("v1_mean_curve")
    v0_mean = sur.get("v0_mean_curve")

    out: Dict[str, Any] = {}

    def add(prefix: str, y_raw: Any):
        if not isinstance(y_raw, list) or len(y_raw) != len(nu):
            return
        y = [float(v) for v in y_raw]
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


def summarize_mf_run(
    json_path: Path,
    run_id: str,
    control_name: str,
    run_role: str,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    obj = load_json(json_path)
    if not looks_like_mf_json(obj):
        raise ValueError("JSON does not match MF schema")

    lmax = to_int(obj.get("lmax"))
    nside = to_int(obj.get("nside"))
    n_sims = to_int(obj.get("n_sims"))
    seed = to_int(obj.get("seed"))
    kind = obj.get("kind")

    # Verify-L2 guard: ONLY accept distances if verify_l2_from_curves exists and matches.
    verify_ok, verify_tag = has_verify_l2_ok(obj)
    has_verify = bool(safe_get(obj, "diagnostics.verify_l2_from_curves") is not None)

    # scalar metrics (guarded)
    D0 = to_float(safe_get(obj, "observed.D0_L2")) if verify_ok else None
    D1 = to_float(safe_get(obj, "observed.D1_L2")) if verify_ok else None
    Dmf = to_float(safe_get(obj, "observed.D_mf")) if verify_ok else None
    Zmf = to_float(safe_get(obj, "observed.Z_mf")) if verify_ok else None
    p2 = to_float(obj.get("p_two_sided_mf", obj.get("p_two_sided")))

    D0m = to_float(safe_get(obj, "surrogate.D0_mean")) if verify_ok else None
    D0s = to_float(safe_get(obj, "surrogate.D0_std")) if verify_ok else None
    D1m = to_float(safe_get(obj, "surrogate.D1_mean")) if verify_ok else None
    D1s = to_float(safe_get(obj, "surrogate.D1_std")) if verify_ok else None
    Dmfm = to_float(safe_get(obj, "surrogate.D_mf_mean")) if verify_ok else None
    Dmfs = to_float(safe_get(obj, "surrogate.D_mf_std")) if verify_ok else None

    # peaks (curve-based; independent of verify_l2)
    nu = [float(v) for v in safe_get(obj, "thresholds.nus")]
    v1_obs = [float(v) for v in safe_get(obj, "observed.v1_curve")]
    v1_mean = safe_get(obj, "surrogate.v1_mean_curve")
    v1_mean = [float(v) for v in v1_mean] if isinstance(v1_mean, list) else None

    pk = peak_info(nu, v1_obs)
    peak_row: Dict[str, Any] = {
        "control": control_name,
        "run_role": run_role,
        "run_id": run_id,
        "json": str(json_path),
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": seed,
        "v1_obs_nu_peak": pk.nu_peak,
        "v1_obs_peak_height": pk.peak_height,
    }
    if v1_mean and len(v1_mean) == len(nu):
        pk2 = peak_info(nu, v1_mean)
        peak_row.update({
            "v1_mean_nu_peak": pk2.nu_peak,
            "v1_mean_peak_height": pk2.peak_height,
        })

    # sweep row (guarded)
    sweep_row: Dict[str, Any] = {
        "control": control_name,
        "run_role": run_role,
        "run_id": run_id,
        "json": str(json_path),
        "kind": kind,
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": seed,
        "p_two_sided_mf": p2,
        "has_verify_l2": has_verify,
        "verify_l2_ok": verify_ok,
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
    if verify_tag:
        sweep_row["error"] = verify_tag

    # gc row (curve-based; independent)
    gc_row: Dict[str, Any] = {
        "control": control_name,
        "run_role": run_role,
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
# main
# ----------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", required=True)
    ap.add_argument("--control_name", default="", help="Used only in mode=control (matches manifest 'control: ...').")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--mode", default="control", choices=["control", "observed"],
                    help="control = filter by manifest control line; observed = scan observed Planck run dirs")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)

    if not runs_dir.exists():
        raise SystemExit(f"ERROR: runs_dir not found: {runs_dir}")
    ensure_dir(out_dir)

    matched_run_dirs: List[Path] = []
    control_label: str

    if args.mode == "control":
        if not args.control_name:
            raise SystemExit("ERROR: mode=control requires --control_name")
        control_label = args.control_name
        for mp in iter_manifest_paths(runs_dir):
            if manifest_has_control(read_text(mp), control_label):
                matched_run_dirs.append(mp.parent)
        matched_run_dirs = sorted(set(matched_run_dirs))
        if not matched_run_dirs:
            raise SystemExit(f"ERROR: No manifests in {runs_dir} contained: control: {control_label}")

    else:
        control_label = "observed_planck_pr3__mf_v0_v1"
        candidates = [p for p in runs_dir.iterdir() if p.is_dir()]

        # Only keep dirs that contain an observed Planck MF output JSON
        matched_run_dirs = []
        for d in candidates:
            js = sorted(d.glob("*.json"))
            if any("planck_lensing_topology_mf_v0_v1" in p.name for p in js):
                matched_run_dirs.append(d)

        matched_run_dirs = sorted(matched_run_dirs)

        if not matched_run_dirs:
            raise SystemExit(
                f"ERROR: No observed Planck run dirs found under: {runs_dir} "
                f"(expected JSON names containing 'planck_lensing_topology_mf_v0_v1')."
            )

    sweep_rows: List[Dict[str, Any]] = []
    peak_rows: List[Dict[str, Any]] = []
    gc_rows: List[Dict[str, Any]] = []

    for run_dir in matched_run_dirs:
        run_id = derive_run_id_from_path(run_dir)
        json_files = find_json_for_run(run_dir)

        manifest_path = run_dir / "manifest.txt"
        manifest_text = read_text(manifest_path) if manifest_path.exists() else ""
        run_role = parse_run_role_from_manifest(manifest_text, args.mode)

        # Fail-safe: if any JSON path points into /controls/, do not label as observed.
        if any("/controls/" in str(p).replace("\\", "/") for p in json_files):
            run_role = "control_like"

        if not json_files:
            sweep_rows.append({
                "control": control_label,
                "run_role": run_role,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "error": "No MF result JSON found (expected filename containing topology_mf_v0_v1 OR mf_v0_v1+run)",
            })
            continue

        last_err = None
        ok = False
        for jf in json_files:
            try:
                srow, prow, grow = summarize_mf_run(jf, run_id, control_label, run_role)
                sweep_rows.append(srow)
                peak_rows.append(prow)
                gc_rows.append(grow)
                ok = True
            except Exception as e:
                last_err = str(e)

        if not ok:
            sweep_rows.append({
                "control": control_label,
                "run_role": run_role,
                "run_id": run_id,
                "run_dir": str(run_dir),
                "error": f"Found JSON candidates but none matched schema; last_error={last_err}",
                "candidates": ";".join([p.name for p in json_files]),
            })

    def sort_key(r: Dict[str, Any]):
        return (r.get("lmax") or 0, str(r.get("run_id", "")))

    sweep_rows = sorted(sweep_rows, key=sort_key)
    peak_rows = sorted(peak_rows, key=sort_key)
    gc_rows = sorted(gc_rows, key=sort_key)

    sweep_csv = out_dir / "mf_sweep_table.csv"
    peaks_csv = out_dir / "v1_peak_table.csv"
    gc_csv = out_dir / "gc_features_table.csv"

    write_csv_allow_empty(sweep_csv, sweep_rows, "No sweep rows produced.")
    write_csv_allow_empty(peaks_csv, peak_rows, "No peak rows produced (no MF JSON matched schema).")
    write_csv_allow_empty(gc_csv, gc_rows, "No GC rows produced (no MF JSON matched schema).")

    sweep_md = out_dir / "mf_sweep_table.md"
    peaks_md = out_dir / "v1_peak_table.md"

    sweep_cols = [
        "lmax", "nside", "n_sims", "seed", "run_id",
        "run_role", "has_verify_l2", "verify_l2_ok",
        "D0_L2", "D1_L2", "D_mf", "Z_mf", "p_two_sided_mf",
        "D0_mean", "D0_std", "D1_mean", "D1_std", "D_mf_mean", "D_mf_std",
        "json", "error"
    ]
    peak_cols = [
        "lmax", "nside", "n_sims", "seed", "run_id",
        "run_role",
        "v1_obs_nu_peak", "v1_obs_peak_height",
        "v1_mean_nu_peak", "v1_mean_peak_height",
        "json"
    ]

    write_md_table(sweep_md, sweep_rows, sweep_cols, "Gate 2B — MF V0+V1 Sweep Table")
    write_md_table(peaks_md, peak_rows, peak_cols, "Gate 2B — V1 Peak Table")

    print("Wrote:")
    print(f"  {sweep_csv}")
    print(f"  {sweep_md}")
    print(f"  {peaks_csv}")
    print(f"  {peaks_md}")
    print(f"  {gc_csv}")


if __name__ == "__main__":
    main()
