#!/usr/bin/env python3
"""
Gate 2B (MF V0+V1) postprocess:

- Robustly discovers run folders by searching for manifest.txt under --runs_dir.
- Optionally filters runs by 'control: <control_name>' found in manifest.txt.
- For each run:
  * Extracts lmax/nside/n_phase_sims/seed0/sims_used from manifest (preferred) or aggregate JSON.
  * Extracts D_stats from aggregate JSON.
  * Extracts per-sim V1 peak statistics from per-sim JSONs (v1_curve).
- Writes:
  * gate2b_mf_v0_v1__lmax_sweep.(md|csv|json)
  * gate2b_mf_v0_v1__v1_peaks.(md|csv|json)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------
# Utilities
# -----------------------------
def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)


def linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 1:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]


def fmt(x: Any, nd: int = 4) -> str:
    if x is None:
        return ""
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def safe_int(x: Any) -> Optional[int]:
    try:
        return int(x)
    except Exception:
        return None


def safe_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


# -----------------------------
# Manifest parsing
# -----------------------------
_MANIFEST_KV_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*:\s*(.*)\s*$")


def parse_manifest(manifest_path: Path) -> Dict[str, str]:
    """
    Parses a simple 'key: value' manifest.txt into a dict[str,str].
    Ignores lines that don't match the pattern.
    """
    out: Dict[str, str] = {}
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return out

    for line in lines:
        m = _MANIFEST_KV_RE.match(line)
        if not m:
            continue
        k = m.group(1).strip()
        v = m.group(2).strip()
        out[k] = v
    return out


def manifest_contains_control(manifest_path: Path, control_name: str) -> bool:
    try:
        txt = manifest_path.read_text(encoding="utf-8")
    except Exception:
        return False
    return f"control: {control_name}" in txt


# -----------------------------
# Run discovery
# -----------------------------
def discover_run_folders(search_root: Path) -> List[Path]:
    """
    Discover run folders by finding manifest.txt, then taking its parent folder.
    Expected shape: .../<run_id>/manifest.txt
    """
    if not search_root.exists():
        raise SystemExit(f"Not found: {search_root}")

    manifests = sorted(search_root.rglob("manifest.txt"))
    run_folders = sorted({m.parent for m in manifests if m.parent.is_dir()})
    return run_folders


# -----------------------------
# JSON discovery inside a run
# -----------------------------
def find_aggregate_json(run_folder: Path) -> Optional[Path]:
    """
    Prefer an aggregate json if present; otherwise detect json containing
    keys: D_stats + inputs + per_sim
    """
    # Common case: file includes "aggregate" in name
    cands = sorted(run_folder.glob("*aggregate*.json"))
    if cands:
        return cands[0]

    # Fallback: detect by content
    for p in sorted(run_folder.glob("*.json")):
        try:
            d = load_json(p)
        except Exception:
            continue
        if isinstance(d, dict) and ("D_stats" in d) and ("inputs" in d) and ("per_sim" in d):
            return p
    return None


def iter_per_sim_jsons(run_folder: Path) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    """
    Per-sim result jsons usually contain observed curves:
      - d["observed"]["v1_curve"] OR d["v1_curve"]
    Avoid aggregate-like records.
    """
    for p in sorted(run_folder.glob("*.json")):
        try:
            d = load_json(p)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue

        # Skip aggregate-like jsons
        if ("D_stats" in d) and ("per_sim" in d):
            continue

        obs = d.get("observed")
        if isinstance(obs, dict) and (isinstance(obs.get("v1_curve"), list) or isinstance(obs.get("v0_curve"), list)):
            yield p, d
            continue

        if isinstance(d.get("v1_curve"), list) or isinstance(d.get("v0_curve"), list):
            yield p, d
            continue


def get_v1_curve(d: Dict[str, Any]) -> Optional[List[float]]:
    if isinstance(d.get("v1_curve"), list):
        return d["v1_curve"]  # type: ignore[return-value]
    obs = d.get("observed")
    if isinstance(obs, dict) and isinstance(obs.get("v1_curve"), list):
        return obs["v1_curve"]  # type: ignore[return-value]
    return None


def infer_sim_id(d: Dict[str, Any], filename: str) -> str:
    for k in ("sim_id", "sim", "simIdx"):
        if k in d:
            s = str(d[k])
            return s.zfill(3) if s.isdigit() else s

    # Try patterns like "__sim000__" or "sim000"
    m = re.search(r"sim(\d{3})", filename)
    if m:
        return m.group(1)
    return "unknown"


def peak_stats(v1_curve: List[float], nus: List[float]) -> Tuple[float, int, Optional[float]]:
    peak_val = max(v1_curve)
    peak_idx = v1_curve.index(peak_val)
    nu_at_peak = nus[peak_idx] if 0 <= peak_idx < len(nus) else None
    return peak_val, peak_idx, nu_at_peak


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class SweepRow:
    lmax: int
    run_id: str
    seed0: Optional[int]
    nside: Optional[int]
    n_phase_sims: Optional[int]
    sims_used: str

    D0_mean: Optional[float]
    D0_std: Optional[float]
    D0_min: Optional[float]
    D0_max: Optional[float]

    D1_mean: Optional[float]
    D1_std: Optional[float]
    D1_min: Optional[float]
    D1_max: Optional[float]

    Dmf_mean: Optional[float]
    Dmf_std: Optional[float]
    Dmf_min: Optional[float]
    Dmf_max: Optional[float]


@dataclass
class PeakSimRow:
    lmax: int
    run_id: str
    sim_id: str
    v1_peak: float
    peak_idx: int
    nu_at_peak: Optional[float]
    source_json: str


@dataclass
class PeakRunRow:
    lmax: int
    run_id: str
    peak_mean: Optional[float]
    peak_min: Optional[float]
    peak_max: Optional[float]
    mode_idx: Optional[int]
    mode_nu: Optional[float]


# -----------------------------
# Extraction per run
# -----------------------------
def extract_run_meta(run_folder: Path, agg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Returns a dict with best-effort:
      run_id, lmax, nside, n_phase_sims, seed0, sims_used, n_nu, nu_min, nu_max
    Preference order:
      1) manifest.txt keys if present
      2) agg["inputs"] if present
    """
    meta: Dict[str, Any] = {}

    manifest_path = run_folder / "manifest.txt"
    m = parse_manifest(manifest_path) if manifest_path.exists() else {}

    # run_id
    meta["run_id"] = m.get("run_id", run_folder.name)

    # numeric fields
    for k in ("lmax", "nside", "n_sims", "seed", "n_nu", "nu_min", "nu_max"):
        if k in m:
            meta[k] = m[k]

    # control-specific manifest includes seed0 / n_phase_sims / sims_used sometimes
    if "seed0" in m:
        meta["seed0"] = m["seed0"]

    if "n_phase_sims" in m:
        meta["n_phase_sims"] = m["n_phase_sims"]

    # sims_used often not present; fall back to agg inputs
    if "sims_used" in m:
        meta["sims_used"] = m["sims_used"]

    # fallback to aggregate inputs
    if agg and isinstance(agg.get("inputs"), dict):
        inp = agg["inputs"]
        meta.setdefault("lmax", inp.get("lmax"))
        meta.setdefault("nside", inp.get("nside"))
        meta.setdefault("seed0", inp.get("seed0"))
        meta.setdefault("n_phase_sims", inp.get("n_phase_sims"))
        meta.setdefault("n_nu", inp.get("n_nu", inp.get("n_nu", 61)))
        meta.setdefault("nu_min", inp.get("nu_min", -3.0))
        meta.setdefault("nu_max", inp.get("nu_max", 3.0))
        if "sims_used" not in meta:
            sims = inp.get("sims_used", [])
            if isinstance(sims, list):
                meta["sims_used"] = ",".join([str(x) for x in sims])
            else:
                meta["sims_used"] = str(sims)

    # Normalize types
    meta["lmax"] = safe_int(meta.get("lmax"))
    meta["nside"] = safe_int(meta.get("nside"))
    # manifest calls it n_sims, aggregate calls it n_phase_sims
    meta["n_phase_sims"] = safe_int(meta.get("n_phase_sims", meta.get("n_sims")))
    meta["seed0"] = safe_int(meta.get("seed0", meta.get("seed")))
    meta["n_nu"] = safe_int(meta.get("n_nu", 61)) or 61
    meta["nu_min"] = safe_float(meta.get("nu_min", -3.0)) or -3.0
    meta["nu_max"] = safe_float(meta.get("nu_max", 3.0)) or 3.0
    meta["sims_used"] = str(meta.get("sims_used", "") or "")

    return meta


def extract_d_stats(agg: Dict[str, Any]) -> Dict[str, Optional[float]]:
    ds = agg.get("D_stats", {}) if isinstance(agg, dict) else {}
    def g(k: str) -> Optional[float]:
        return safe_float(ds.get(k))
    return {
        "D0_mean": g("D0_mean"),
        "D0_std": g("D0_std"),
        "D0_min": g("D0_min"),
        "D0_max": g("D0_max"),
        "D1_mean": g("D1_mean"),
        "D1_std": g("D1_std"),
        "D1_min": g("D1_min"),
        "D1_max": g("D1_max"),
        "Dmf_mean": g("D_mf_mean"),
        "Dmf_std": g("D_mf_std"),
        "Dmf_min": g("D_mf_min"),
        "Dmf_max": g("D_mf_max"),
    }


# -----------------------------
# Output writers
# -----------------------------
def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", required=True,
                    help="Root folder to search under for run folders (manifest.txt). Can be broad.")
    ap.add_argument("--out_dir", required=True,
                    help="Output directory for postprocess artifacts.")
    ap.add_argument("--control_name", default="",
                    help="If set, only include runs whose manifest.txt contains 'control: <control_name>'.")
    args = ap.parse_args()

    runs_root = Path(args.runs_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    run_folders = discover_run_folders(runs_root)
    if not run_folders:
        raise SystemExit(f"No run folders found under: {runs_root}")

    # Filter by control_name if provided
    if args.control_name:
        filtered: List[Path] = []
        for rf in run_folders:
            mp = rf / "manifest.txt"
            if mp.exists() and manifest_contains_control(mp, args.control_name):
                filtered.append(rf)
        run_folders = filtered
        if not run_folders:
            raise SystemExit(f"No runs matched control_name='{args.control_name}' under: {runs_root}")

    sweep: List[SweepRow] = []
    peak_run_rows: List[PeakRunRow] = []
    peak_sim_rows: List[PeakSimRow] = []

    # Process each run folder
    for rf in sorted(run_folders):
        agg_path = find_aggregate_json(rf)
        agg = load_json(agg_path) if agg_path else None
        meta = extract_run_meta(rf, agg)

        lmax = meta.get("lmax")
        if lmax is None:
            # cannot place in sweep without lmax
            continue

        run_id = str(meta.get("run_id", rf.name))

        # D_stats (from aggregate only)
        d_stats = extract_d_stats(agg) if isinstance(agg, dict) else {k: None for k in [
            "D0_mean","D0_std","D0_min","D0_max",
            "D1_mean","D1_std","D1_min","D1_max",
            "Dmf_mean","Dmf_std","Dmf_min","Dmf_max"
        ]}

        sweep.append(SweepRow(
            lmax=lmax,
            run_id=run_id,
            seed0=meta.get("seed0"),
            nside=meta.get("nside"),
            n_phase_sims=meta.get("n_phase_sims"),
            sims_used=meta.get("sims_used", ""),
            D0_mean=d_stats["D0_mean"],
            D0_std=d_stats["D0_std"],
            D0_min=d_stats["D0_min"],
            D0_max=d_stats["D0_max"],
            D1_mean=d_stats["D1_mean"],
            D1_std=d_stats["D1_std"],
            D1_min=d_stats["D1_min"],
            D1_max=d_stats["D1_max"],
            Dmf_mean=d_stats["Dmf_mean"],
            Dmf_std=d_stats["Dmf_std"],
            Dmf_min=d_stats["Dmf_min"],
            Dmf_max=d_stats["Dmf_max"],
        ))

        # Peaks config
        n_nu = int(meta.get("n_nu", 61))
        nu_min = float(meta.get("nu_min", -3.0))
        nu_max = float(meta.get("nu_max", 3.0))
        nus = linspace(nu_min, nu_max, n_nu)

        per_sim_peaks: List[Tuple[str, float, int, Optional[float], str]] = []

        for p, d in iter_per_sim_jsons(rf):
            v1 = get_v1_curve(d)
            if not v1:
                continue
            sim_id = infer_sim_id(d, p.name)
            pv, pi, pnu = peak_stats(v1, nus)
            per_sim_peaks.append((sim_id, pv, pi, pnu, p.name))
            peak_sim_rows.append(PeakSimRow(
                lmax=lmax,
                run_id=run_id,
                sim_id=sim_id,
                v1_peak=pv,
                peak_idx=pi,
                nu_at_peak=pnu,
                source_json=p.name
            ))

        # Per-run summary of peaks
        if per_sim_peaks:
            vals = [x[1] for x in per_sim_peaks]
            idxs = [x[2] for x in per_sim_peaks]
            # mode index (tie-break to smallest idx)
            counts: Dict[int, int] = {}
            for idx in idxs:
                counts[idx] = counts.get(idx, 0) + 1
            mode_idx = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            mode_nu = nus[mode_idx] if 0 <= mode_idx < len(nus) else None

            peak_run_rows.append(PeakRunRow(
                lmax=lmax,
                run_id=run_id,
                peak_mean=sum(vals) / len(vals),
                peak_min=min(vals),
                peak_max=max(vals),
                mode_idx=mode_idx,
                mode_nu=mode_nu
            ))
        else:
            peak_run_rows.append(PeakRunRow(
                lmax=lmax,
                run_id=run_id,
                peak_mean=None,
                peak_min=None,
                peak_max=None,
                mode_idx=None,
                mode_nu=None
            ))

    # Sort by lmax (ascending)
    sweep.sort(key=lambda r: r.lmax)
    peak_run_rows.sort(key=lambda r: r.lmax)
    peak_sim_rows.sort(key=lambda r: (r.lmax, r.run_id, r.sim_id))

    # -----------------------------
    # Write SWEEP outputs
    # -----------------------------
    sweep_md_lines: List[str] = []
    sweep_md_lines.append("# Gate 2B — ΛCDM recon control (MF V0+V1): ℓmax sweep\n")
    sweep_md_lines.append(f"- Search root: `{runs_root}`")
    if args.control_name:
        sweep_md_lines.append(f"- Control filter: `{args.control_name}`")
    sweep_md_lines.append(f"- Runs found: **{len(sweep)}**\n")

    sweep_md_lines.append("| lmax | run_id | seed0 | sims_used | D1_mean ± std | D1_min..max | Dmf_mean ± std | Dmf_min..max | D0_mean ± std |")
    sweep_md_lines.append("|---:|---:|---:|---|---|---|---|---|---|")

    for r in sweep:
        sweep_md_lines.append(
            f"| {r.lmax} | {r.run_id} | {r.seed0 if r.seed0 is not None else ''} | {r.sims_used} | "
            f"{fmt(r.D1_mean)} ± {fmt(r.D1_std)} | {fmt(r.D1_min)}..{fmt(r.D1_max)} | "
            f"{fmt(r.Dmf_mean)} ± {fmt(r.Dmf_std)} | {fmt(r.Dmf_min)}..{fmt(r.Dmf_max)} | "
            f"{fmt(r.D0_mean, 6)} ± {fmt(r.D0_std, 6)} |"
        )

    sweep_md_lines.append("\n## Derived ratios\n")
    for r in sweep:
        if r.D1_mean is not None:
            sweep_md_lines.append(f"- D1_mean / lmax @ lmax={r.lmax}: {(r.D1_mean / r.lmax):.3f}")

    out_sweep_md = out_dir / "gate2b_mf_v0_v1__lmax_sweep.md"
    out_sweep_md.write_text("\n".join(sweep_md_lines) + "\n", encoding="utf-8")

    sweep_rows_for_csv = [{
        "lmax": r.lmax,
        "run_id": r.run_id,
        "seed0": r.seed0,
        "nside": r.nside,
        "n_phase_sims": r.n_phase_sims,
        "sims_used": r.sims_used,
        "D0_mean": r.D0_mean,
        "D0_std": r.D0_std,
        "D0_min": r.D0_min,
        "D0_max": r.D0_max,
        "D1_mean": r.D1_mean,
        "D1_std": r.D1_std,
        "D1_min": r.D1_min,
        "D1_max": r.D1_max,
        "Dmf_mean": r.Dmf_mean,
        "Dmf_std": r.Dmf_std,
        "Dmf_min": r.Dmf_min,
        "Dmf_max": r.Dmf_max,
    } for r in sweep]

    out_sweep_csv = out_dir / "gate2b_mf_v0_v1__lmax_sweep.csv"
    write_csv(out_sweep_csv, sweep_rows_for_csv, list(sweep_rows_for_csv[0].keys()) if sweep_rows_for_csv else [])

    out_sweep_json = out_dir / "gate2b_mf_v0_v1__lmax_sweep.json"
    dump_json(out_sweep_json, sweep_rows_for_csv)

    # -----------------------------
    # Write PEAK outputs
    # -----------------------------
    peaks_md_lines: List[str] = []
    peaks_md_lines.append("# Gate 2B — MF V0+V1: V1 peak summary\n")
    peaks_md_lines.append(f"- Search root: `{runs_root}`")
    if args.control_name:
        peaks_md_lines.append(f"- Control filter: `{args.control_name}`")
    peaks_md_lines.append(f"- Runs found: **{len(peak_run_rows)}**\n")

    peaks_md_lines.append("## Per-run summary\n")
    peaks_md_lines.append("| lmax | run_id | peak(V1) mean | peak(V1) min..max | peak idx (mode) | ν at peak (mode) |")
    peaks_md_lines.append("|---:|---:|---:|---:|---:|---:|")

    for r in peak_run_rows:
        peaks_md_lines.append(
            f"| {r.lmax} | {r.run_id} | {fmt(r.peak_mean,3)} | {fmt(r.peak_min,3)}..{fmt(r.peak_max,3)} | "
            f"{'' if r.mode_idx is None else r.mode_idx} | {fmt(r.mode_nu,3)} |"
        )

    peaks_md_lines.append("\n## Per-sim detail\n")
    last_key = None
    for ps in peak_sim_rows:
        key = (ps.lmax, ps.run_id)
        if key != last_key:
            peaks_md_lines.append(f"\n### lmax={ps.lmax} (run {ps.run_id})\n")
            peaks_md_lines.append("| sim_id | v1_peak | peak_idx | ν_at_peak | source_json |")
            peaks_md_lines.append("|---:|---:|---:|---:|---|")
            last_key = key
        peaks_md_lines.append(
            f"| {ps.sim_id} | {ps.v1_peak:.3f} | {ps.peak_idx} | {fmt(ps.nu_at_peak,3)} | `{ps.source_json}` |"
        )

    out_peaks_md = out_dir / "gate2b_mf_v0_v1__v1_peaks.md"
    out_peaks_md.write_text("\n".join(peaks_md_lines) + "\n", encoding="utf-8")

    peaks_run_for_csv = [{
        "lmax": r.lmax,
        "run_id": r.run_id,
        "peak_mean": r.peak_mean,
        "peak_min": r.peak_min,
        "peak_max": r.peak_max,
        "mode_idx": r.mode_idx,
        "mode_nu": r.mode_nu,
    } for r in peak_run_rows]

    out_peaks_run_csv = out_dir / "gate2b_mf_v0_v1__v1_peaks__per_run.csv"
    write_csv(out_peaks_run_csv, peaks_run_for_csv, list(peaks_run_for_csv[0].keys()) if peaks_run_for_csv else [])

    peaks_sim_for_csv = [{
        "lmax": r.lmax,
        "run_id": r.run_id,
        "sim_id": r.sim_id,
        "v1_peak": r.v1_peak,
        "peak_idx": r.peak_idx,
        "nu_at_peak": r.nu_at_peak,
        "source_json": r.source_json,
    } for r in peak_sim_rows]

    out_peaks_sim_csv = out_dir / "gate2b_mf_v0_v1__v1_peaks__per_sim.csv"
    write_csv(out_peaks_sim_csv, peaks_sim_for_csv, list(peaks_sim_for_csv[0].keys()) if peaks_sim_for_csv else [])

    out_peaks_json = out_dir / "gate2b_mf_v0_v1__v1_peaks.json"
    dump_json(out_peaks_json, {
        "per_run": peaks_run_for_csv,
        "per_sim": peaks_sim_for_csv,
    })

    print(f"Wrote:\n- {out_sweep_md}\n- {out_sweep_csv}\n- {out_sweep_json}\n- {out_peaks_md}\n- {out_peaks_run_csv}\n- {out_peaks_sim_csv}\n- {out_peaks_json}")


if __name__ == "__main__":
    main()
