#!/usr/bin/env python3
"""
gate2b_mf_analysis_v1.py — cohort analysis for Gate 2B MF(V0,V1)

Goal
----
Compare OBSERVED Planck vs control cohorts (Gaussian, ΛCDM recon) using the
postprocess outputs already committed to the repo.

Inputs (per cohort)
-------------------
- gc_features_table.csv   (required)
- mf_sweep_table.csv      (optional but recommended; auto-detected next to gc csv)

Outputs (written to --out_dir)
------------------------------
- analysis_summary.csv
- analysis_summary.md
- analysis_stats_observed.csv
- analysis_stats_gaussian.csv
- analysis_stats_lcdm_recon.csv

Decision block (GitHub screenshot-friendly)
------------------------------------------
- decision_block/decision_block.md
- decision_block/decision_block_transposed.md

Key behavior
------------
- Dedup within each cohort keeping the newest run_id (max numeric).
  * observed + lcdm_recon: dedupe key = (lmax, seed)
  * gaussian:             dedupe key = (lmax, gauss_seed)  [parsed from json path]
- Merges gc_features with mf_sweep on (run_id, lmax, seed) when sweep exists.
- Produces per-lmax summaries and z-scores of OBSERVED vs control means.
- Guards z-scores: if std is too small (default < 1e-6), z-score is blank.
  This prevents numerical artifacts (e.g., peak-shift) from exploding.

Notes
-----
- Missing/blank values are handled gracefully.
- If a sweep row is missing verify_l2 (so D0/D1/D_mf/Z_mf blank), those fields are
  treated as None and excluded from means/stds for that metric.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# helpers
# -----------------------------

GAUSS_SEED_RE = re.compile(r"__gauss(\d+)__")


def to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return None
        return float(s)
    except Exception:
        return None


def to_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "":
            return None
        return int(float(s))
    except Exception:
        return None


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        rows = [{"note": "no rows"}]
    keys = sorted({k for r in rows for k in r.keys()})
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def fmt(x: Any, nd: int = 6) -> str:
    if x is None:
        return ""
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        return f"{x:.{nd}g}"
    return str(x)


def write_md_table(path: Path, title: str, columns: List[str], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        if not rows:
            f.write("_No rows._\n")
            return
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("| " + " | ".join(["---"] * len(columns)) + " |\n")
        for r in rows:
            f.write("| " + " | ".join(fmt(r.get(c)) for c in columns) + " |\n")
        f.write("\n")


def mean_std(vals: List[float]) -> Tuple[Optional[float], Optional[float]]:
    vals = [v for v in vals if v is not None and not math.isnan(v)]
    if not vals:
        return None, None
    m = sum(vals) / len(vals)
    if len(vals) < 2:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return m, math.sqrt(var)


def safe_z(obs: Optional[float], mu: Optional[float], sd: Optional[float], *, z_min_std: float) -> Optional[float]:
    """
    Guard z-score against tiny sd. If sd < z_min_std, return None (blank in tables).
    """
    if obs is None or mu is None or sd is None:
        return None
    if sd < z_min_std:
        return None
    return (obs - mu) / sd


def infer_sweep_path(gc_csv: Path) -> Path:
    return gc_csv.parent / "mf_sweep_table.csv"


def extract_gauss_seed(row: Dict[str, str]) -> Optional[int]:
    """
    Extract gauss seed from json filename like:
      ...__gauss901__run<id>.json
    Returns int or None if not found.
    """
    j = (row.get("json") or "").strip()
    if not j:
        return None
    m = GAUSS_SEED_RE.search(j)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def dedupe_keep_newest(rows: List[Dict[str, str]], cohort: str) -> List[Dict[str, str]]:
    """
    Keep newest by cohort-specific key using max run_id.
      - gaussian: (lmax, gauss_seed)
      - others:   (lmax, seed)
    """
    best: Dict[Tuple[int, int], Dict[str, str]] = {}

    for r in rows:
        lmax = to_int(r.get("lmax")) or -1
        rid = to_int(r.get("run_id")) or -1

        if cohort == "gaussian":
            gseed = extract_gauss_seed(r)
            k2 = gseed if gseed is not None else -1
            k = (lmax, k2)
        else:
            seed = to_int(r.get("seed")) or -1
            k = (lmax, seed)

        if k not in best:
            best[k] = r
        else:
            rid2 = to_int(best[k].get("run_id")) or -1
            if rid > rid2:
                best[k] = r

    out = list(best.values())

    # Stable sort for readability
    if cohort == "gaussian":
        out.sort(key=lambda r: (
            to_int(r.get("lmax")) or 0,
            extract_gauss_seed(r) or 0,
            to_int(r.get("run_id")) or 0
        ))
    else:
        out.sort(key=lambda r: (
            to_int(r.get("lmax")) or 0,
            to_int(r.get("seed")) or 0,
            to_int(r.get("run_id")) or 0
        ))
    return out


def merge_gc_with_sweep(gc_rows: List[Dict[str, str]], sweep_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    # index sweep by (run_id, lmax, seed)
    idx: Dict[Tuple[int, int, int], Dict[str, str]] = {}
    for s in sweep_rows:
        k = (to_int(s.get("run_id")) or -1, to_int(s.get("lmax")) or -1, to_int(s.get("seed")) or -1)
        idx[k] = s

    merged: List[Dict[str, Any]] = []
    for g in gc_rows:
        k = (to_int(g.get("run_id")) or -1, to_int(g.get("lmax")) or -1, to_int(g.get("seed")) or -1)
        out: Dict[str, Any] = dict(g)
        s = idx.get(k)
        if s:
            # prefix sweep_ to avoid collisions
            for kk, vv in s.items():
                if kk in ("control", "run_id", "lmax", "seed", "run_role", "kind", "json"):
                    continue
                out[f"sweep_{kk}"] = vv
        merged.append(out)
    return merged


# -----------------------------
# analysis metrics
# -----------------------------

METRICS = [
    # From sweep (if present)
    ("D1_L2", "sweep_D1_L2"),
    ("Z_mf", "sweep_Z_mf"),
    ("D_mf", "sweep_D_mf"),
    ("p_two_sided_mf", "sweep_p_two_sided_mf"),
    # From gc
    ("v1_energy_ratio", "v1_energy_ratio"),
    ("v1_peak_shift", "v1_peak_shift"),
]


def cohort_per_lmax_stats(rows: List[Dict[str, Any]], cohort: str) -> Dict[int, Dict[str, Any]]:
    by_l: Dict[int, List[Dict[str, Any]]] = {}
    for r in rows:
        lmax = to_int(r.get("lmax"))
        if lmax is None:
            continue
        by_l.setdefault(lmax, []).append(r)

    out: Dict[int, Dict[str, Any]] = {}
    for lmax, rr in sorted(by_l.items()):
        d: Dict[str, Any] = {"cohort": cohort, "lmax": lmax, "n_rows": len(rr)}
        for label, col in METRICS:
            vals: List[float] = []
            for r in rr:
                v = to_float(r.get(col))
                if v is None:
                    continue
                vals.append(v)
            m, sd = mean_std(vals)
            d[f"{label}_mean"] = m
            d[f"{label}_std"] = sd
        out[lmax] = d
    return out


# -----------------------------
# decision block writers
# -----------------------------

DECISION_METRICS = [
    ("D1_L2", "obs_D1_L2", "gauss_D1_L2_mean", "gauss_D1_L2_std", "lcdm_D1_L2_mean", "lcdm_D1_L2_std"),
    ("Z_mf", "obs_Z_mf", "gauss_Z_mf_mean", "gauss_Z_mf_std", "lcdm_Z_mf_mean", "lcdm_Z_mf_std"),
    ("v1_energy_ratio", "obs_v1_energy_ratio", "gauss_v1_energy_ratio_mean", "gauss_v1_energy_ratio_std",
     "lcdm_v1_energy_ratio_mean", "lcdm_v1_energy_ratio_std"),
    ("v1_peak_shift", "obs_v1_peak_shift", "gauss_v1_peak_shift_mean", "gauss_v1_peak_shift_std",
     "lcdm_v1_peak_shift_mean", "lcdm_v1_peak_shift_std"),
]


def write_decision_block(out_dir: Path, summary_rows: List[Dict[str, Any]]) -> None:
    """
    Writes two MD files under out_dir/decision_block:
      - decision_block.md                 (wide, like analysis_summary but fewer cols)
      - decision_block_transposed.md      (narrow, screenshot-friendly)
    """
    ddir = out_dir / "decision_block"
    ddir.mkdir(parents=True, exist_ok=True)

    # 1) decision_block.md (compact wide)
    cols = [
        "lmax", "n_obs", "n_gauss", "n_lcdm",
        "obs_D1_L2", "gauss_D1_L2_mean", "gauss_D1_L2_std", "lcdm_D1_L2_mean", "lcdm_D1_L2_std",
        "obs_Z_mf", "gauss_Z_mf_mean", "gauss_Z_mf_std", "lcdm_Z_mf_mean", "lcdm_Z_mf_std",
        "obs_v1_energy_ratio", "gauss_v1_energy_ratio_mean", "gauss_v1_energy_ratio_std", "lcdm_v1_energy_ratio_mean", "lcdm_v1_energy_ratio_std",
        "obs_v1_peak_shift", "gauss_v1_peak_shift_mean", "gauss_v1_peak_shift_std", "lcdm_v1_peak_shift_mean", "lcdm_v1_peak_shift_std",
    ]
    write_md_table(
        ddir / "decision_block.md",
        "Gate 2B — MF(V0,V1) Decision Block (means ± std)",
        cols,
        summary_rows,
    )

    # 2) decision_block_transposed.md (metrics as rows; lmax as columns)
    # build list of lmax values in order
    lmaxs = [to_int(r.get("lmax")) for r in summary_rows]
    lmaxs = [x for x in lmaxs if x is not None]
    lmaxs = sorted(lmaxs)

    # index by lmax
    by_l: Dict[int, Dict[str, Any]] = {to_int(r.get("lmax")): r for r in summary_rows if to_int(r.get("lmax")) is not None}

    # header columns
    tcols = ["metric", "cohort"] + [str(l) for l in lmaxs]

    trows: List[Dict[str, Any]] = []

    # include counts row first
    for cohort_key, label in [("n_obs", "n_obs"), ("n_gauss", "n_gauss"), ("n_lcdm", "n_lcdm")]:
        rr: Dict[str, Any] = {"metric": "n", "cohort": label}
        for l in lmaxs:
            rr[str(l)] = by_l.get(l, {}).get(cohort_key)
        trows.append(rr)

    # then metric blocks with mean±std where relevant
    def cell_mean_std(l: int, mean_key: str, std_key: str) -> str:
        r = by_l.get(l, {})
        m = r.get(mean_key)
        s = r.get(std_key)
        if m is None and s is None:
            return ""
        if s is None:
            return fmt(m)
        return f"{fmt(m)} ± {fmt(s)}"

    def cell_val(l: int, key: str) -> str:
        return fmt(by_l.get(l, {}).get(key))

    for metric_name, obs_key, g_mean, g_std, c_mean, c_std in DECISION_METRICS:
        # observed row (single value)
        rr_obs: Dict[str, Any] = {"metric": metric_name, "cohort": "observed"}
        for l in lmaxs:
            rr_obs[str(l)] = cell_val(l, obs_key)
        trows.append(rr_obs)

        # gaussian row (mean±std)
        rr_g: Dict[str, Any] = {"metric": metric_name, "cohort": "gaussian (mean±std)"}
        for l in lmaxs:
            rr_g[str(l)] = cell_mean_std(l, g_mean, g_std)
        trows.append(rr_g)

        # lcdm row (mean±std)
        rr_c: Dict[str, Any] = {"metric": metric_name, "cohort": "lcdm_recon (mean±std)"}
        for l in lmaxs:
            rr_c[str(l)] = cell_mean_std(l, c_mean, c_std)
        trows.append(rr_c)

    write_md_table(
        ddir / "decision_block_transposed.md",
        "Gate 2B — MF(V0,V1) Decision Block (transposed)",
        tcols,
        trows,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)

    ap.add_argument("--observed_gc", default="experiments/rgpx_proof_proto/cmb_phase_dagger/results/topology_mf_v0_v1/controls/_postprocess/observed_planck_pr3__mf_v0_v1/gc_features_table.csv")
    ap.add_argument("--gaussian_gc", default="experiments/rgpx_proof_proto/cmb_phase_dagger/results/topology_mf_v0_v1/controls/_postprocess/gaussian_synalm_from_(dat_minus_mf)_cl/gc_features_table.csv")
    ap.add_argument("--lcdm_gc", default="experiments/rgpx_proof_proto/cmb_phase_dagger/results/topology_mf_v0_v1/controls/_postprocess/decision_gate_2b__lcdm_recon__mf_v0_v1/gc_features_table.csv")

    ap.add_argument(
        "--dedupe",
        default="newest",
        choices=["newest", "none"],
        help="Deduplicate within cohort keeping newest run_id. Gaussian uses (lmax, gauss_seed). Others use (lmax, seed).",
    )
    ap.add_argument(
        "--z_min_std",
        type=float,
        default=1e-6,
        help="If control std < this threshold, z-score is blank (prevents numerical blowups).",
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cohorts = [
        ("observed", Path(args.observed_gc)),
        ("gaussian", Path(args.gaussian_gc)),
        ("lcdm_recon", Path(args.lcdm_gc)),
    ]

    cohort_rows: Dict[str, List[Dict[str, Any]]] = {}

    for name, gc_path in cohorts:
        if not gc_path.exists():
            raise SystemExit(f"ERROR: missing gc_features_table.csv for {name}: {gc_path}")

        gc_raw = read_csv_dicts(gc_path)
        if args.dedupe == "newest":
            gc_raw = dedupe_keep_newest(gc_raw, cohort=name)

        sweep_path = infer_sweep_path(gc_path)
        if sweep_path.exists():
            sweep_raw = read_csv_dicts(sweep_path)
            if args.dedupe == "newest":
                sweep_raw = dedupe_keep_newest(sweep_raw, cohort=name)
            merged = merge_gc_with_sweep(gc_raw, sweep_raw)
        else:
            merged = [dict(r) for r in gc_raw]

        for r in merged:
            r["cohort"] = name

        cohort_rows[name] = merged

    # Per-lmax stats
    stats_obs = cohort_per_lmax_stats(cohort_rows["observed"], "observed")
    stats_g = cohort_per_lmax_stats(cohort_rows["gaussian"], "gaussian")
    stats_l = cohort_per_lmax_stats(cohort_rows["lcdm_recon"], "lcdm_recon")

    # Comparison summary
    summary_rows: List[Dict[str, Any]] = []
    lmaxs = sorted(set(stats_obs.keys()) | set(stats_g.keys()) | set(stats_l.keys()))

    for lmax in lmaxs:
        row: Dict[str, Any] = {"lmax": lmax}

        o = stats_obs.get(lmax, {})
        g = stats_g.get(lmax, {})
        c = stats_l.get(lmax, {})

        row["n_obs"] = o.get("n_rows")
        row["n_gauss"] = g.get("n_rows")
        row["n_lcdm"] = c.get("n_rows")

        # Expand full summary columns used by analysis_summary.md and decision block
        for label, _col in METRICS:
            o_m = o.get(f"{label}_mean")
            g_m = g.get(f"{label}_mean")
            g_s = g.get(f"{label}_std")
            c_m = c.get(f"{label}_mean")
            c_s = c.get(f"{label}_std")

            row[f"obs_{label}"] = o_m

            row[f"gauss_{label}_mean"] = g_m
            row[f"gauss_{label}_std"] = g_s

            row[f"lcdm_{label}_mean"] = c_m
            row[f"lcdm_{label}_std"] = c_s

        summary_rows.append(row)

    # Write outputs
    csv_out = out_dir / "analysis_summary.csv"
    md_out = out_dir / "analysis_summary.md"

    write_csv(csv_out, summary_rows)

    md_cols = [
        "lmax", "n_obs", "n_gauss", "n_lcdm",
        "obs_D1_L2", "gauss_D1_L2_mean", "gauss_D1_L2_std", "lcdm_D1_L2_mean", "lcdm_D1_L2_std",
        "obs_Z_mf", "gauss_Z_mf_mean", "gauss_Z_mf_std", "lcdm_Z_mf_mean", "lcdm_Z_mf_std",
        "obs_v1_energy_ratio", "gauss_v1_energy_ratio_mean", "gauss_v1_energy_ratio_std", "lcdm_v1_energy_ratio_mean", "lcdm_v1_energy_ratio_std",
        "obs_v1_peak_shift", "gauss_v1_peak_shift_mean", "gauss_v1_peak_shift_std", "lcdm_v1_peak_shift_mean", "lcdm_v1_peak_shift_std",
    ]

    write_md_table(md_out, "Gate 2B — MF(V0,V1) Cohort Analysis Summary", md_cols, summary_rows)

    # Per-cohort stats dumps
    write_csv(out_dir / "analysis_stats_observed.csv", list(stats_obs.values()))
    write_csv(out_dir / "analysis_stats_gaussian.csv", list(stats_g.values()))
    write_csv(out_dir / "analysis_stats_lcdm_recon.csv", list(stats_l.values()))

    # Decision block outputs (GitHub screenshot-friendly)
    write_decision_block(out_dir, summary_rows)

    print("Wrote:")
    print(f"  {csv_out}")
    print(f"  {md_out}")
    print(f"  {out_dir / 'analysis_stats_observed.csv'}")
    print(f"  {out_dir / 'analysis_stats_gaussian.csv'}")
    print(f"  {out_dir / 'analysis_stats_lcdm_recon.csv'}")
    print(f"  {out_dir / 'decision_block/decision_block.md'}")
    print(f"  {out_dir / 'decision_block/decision_block_transposed.md'}")


if __name__ == "__main__":
    main()
