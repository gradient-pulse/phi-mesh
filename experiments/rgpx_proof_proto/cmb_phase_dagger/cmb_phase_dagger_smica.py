#!/usr/bin/env python3
"""
RGPx "dagger" for Planck SMICA (PR3) temperature map:
Rao-style phase-spacing statistic across multipole bins + phase-randomized surrogates.

This version is robust to:
- field passed as "0" (string) -> converted to int 0
- field passed as a string column name -> read_map called safely
- missing mask field -> warning + continue unmasked (instead of hard crash)

Requires:
  pip install healpy numpy

Example (real FITS):
  python cmb_phase_dagger_smica.py \
    --fits COM_CMB_IQU-smica_2048_R3.00_full.fits \
    --field 0 \
    --lmax 128 --nside 256 --n_sims 2000 --seed 0 --n_bins 8 \
    --out cmb_phase_dagger_report.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import numpy as np
import healpy as hp


FieldSpec = Union[int, str]


def _coerce_field(field: str) -> FieldSpec:
    """Convert numeric strings like '0' -> int(0). Otherwise keep as string."""
    s = (field or "").strip()
    if s == "":
        return ""
    if s.isdigit():
        return int(s)
    return s


def _read_map_safe(fits_path: str, field: FieldSpec) -> np.ndarray:
    """
    Robust hp.read_map wrapper:
    - int field: pass through
    - str field: try field name safely (wrap list), then fallback to direct string
    """
    if isinstance(field, int):
        return hp.read_map(fits_path, field=field, verbose=False)

    # string field: healpy sometimes treats raw string oddly; prefer [field]
    try:
        return hp.read_map(fits_path, field=[field], verbose=False)
    except Exception:
        return hp.read_map(fits_path, field=field, verbose=False)


def rao_spacing_stat(phases: np.ndarray) -> float:
    """
    Rao's spacing statistic (U) for circular uniformity.
    phases: angles in [0, 2π), length n>=4 recommended.
    Returns U = 0.5 * sum_i |d_i - 2π/n|, where d_i are circular spacings.
    """
    phases = np.asarray(phases, dtype=float)
    n = phases.size
    if n < 4:
        return np.nan
    ph = np.sort(phases % (2 * np.pi))
    diffs = np.diff(ph, append=ph[0] + 2 * np.pi)
    expected = 2 * np.pi / n
    U = 0.5 * np.sum(np.abs(diffs - expected))
    return float(U)


def alm_to_phase_dict(alm: np.ndarray, lmax: int) -> Dict[int, np.ndarray]:
    """Return phases per multipole l, using m=1..l (exclude m=0)."""
    phases_by_l: Dict[int, List[float]] = {l: [] for l in range(0, lmax + 1)}
    for l in range(1, lmax + 1):
        for m in range(1, l + 1):
            idx = hp.Alm.getidx(lmax, l, m)
            phases_by_l[l].append(np.angle(alm[idx]))
    return {l: np.array(v, dtype=float) for l, v in phases_by_l.items()}


def phase_coherence_metric(
    alm: np.ndarray, lmax: int, n_bins: int = 8, lmin: int = 2
) -> Tuple[float, Dict[str, float]]:
    """
    Primary scalar metric:
      M = Var( mean(Rao_U) across l-bins )
    where Rao_U(l) is computed from phases at each l (m=1..l).
    """
    phases_by_l = alm_to_phase_dict(alm, lmax)
    U = np.full(lmax + 1, np.nan, dtype=float)
    for l in range(lmin, lmax + 1):
        U[l] = rao_spacing_stat(phases_by_l[l])

    ls = np.arange(lmin, lmax + 1)
    bins = np.array_split(ls, n_bins)
    bin_means = []
    for b in bins:
        vals = U[b]
        mu = np.nanmean(vals)
        bin_means.append(mu)

    bin_means = np.array(bin_means, dtype=float)
    metric = float(np.nanvar(bin_means, ddof=1))  # sample variance

    extras = {
        "mean_RaoU_overall": float(np.nanmean(U[lmin:])),
        "var_RaoU_overall": float(np.nanvar(U[lmin:], ddof=1)),
        "bin_means": [float(x) for x in bin_means],
    }
    return metric, extras


def randomize_phases(alm: np.ndarray, lmax: int, rng: np.random.Generator) -> np.ndarray:
    """
    Phase-randomized surrogate:
    - keep |a_lm| fixed
    - randomize phases for m>0 uniformly in [0, 2π)
    - keep m=0 real
    """
    out = alm.copy()
    for l in range(0, lmax + 1):
        idx0 = hp.Alm.getidx(lmax, l, 0)
        out[idx0] = np.real(out[idx0])  # enforce real for m=0
        for m in range(1, l + 1):
            idx = hp.Alm.getidx(lmax, l, m)
            amp = np.abs(out[idx])
            phi = rng.uniform(0.0, 2 * np.pi)
            out[idx] = amp * (math.cos(phi) + 1j * math.sin(phi))
    return out


def load_map(
    fits_path: str,
    field: FieldSpec,
    nside: int,
    mask_field: FieldSpec | None,
    mask_thresh: float,
) -> Tuple[np.ndarray, np.ndarray | None]:
    """
    Load HEALPix map and optional mask from a FITS.
    - If mask field is missing, warn and proceed unmasked.
    Returns (map, mask_bool or None).
    """
    m = _read_map_safe(fits_path, field)

    mask_bool = None
    if mask_field is not None and mask_field != "":
        try:
            msk = _read_map_safe(fits_path, mask_field)
            mask_bool = np.asarray(msk) >= float(mask_thresh)
        except Exception as e:
            print(f"[WARN] Mask field '{mask_field}' not found or unreadable in FITS; continuing unmasked. ({e})")
            mask_bool = None

    # Downgrade to target NSIDE for speed/stability
    if hp.get_nside(m) != nside:
        m = hp.ud_grade(m, nside_out=nside, order_in="RING", order_out="RING", power=-2)

    if mask_bool is not None and hp.get_nside(mask_bool) != nside:
        mask_bool = hp.ud_grade(mask_bool.astype(float), nside_out=nside, order_in="RING", order_out="RING", power=0) >= 0.5

    return m.astype(float), mask_bool


def compute_alm(m: np.ndarray, mask_bool: np.ndarray | None, lmax: int) -> np.ndarray:
    """Compute a_lm up to lmax. If mask is provided, apply as 0/1 weight."""
    if mask_bool is not None:
        m_use = m * mask_bool.astype(float)
    else:
        m_use = m
    alm = hp.map2alm(m_use, lmax=lmax, iter=3)
    return alm


@dataclass
class Report:
    observed_metric: float
    null_metrics: List[float]
    p_value: float
    z_score: float
    extras_observed: Dict[str, float]
    extras_null_summary: Dict[str, float]


def run_dagger(
    fits_path: str,
    field: FieldSpec,
    mask_field: FieldSpec | None,
    mask_thresh: float,
    lmax: int,
    nside: int,
    n_sims: int,
    seed: int,
    n_bins: int,
) -> Report:
    rng = np.random.default_rng(seed)

    m, mask_bool = load_map(fits_path, field, nside, mask_field, mask_thresh)
    alm_obs = compute_alm(m, mask_bool, lmax)
    obs_metric, obs_extras = phase_coherence_metric(alm_obs, lmax=lmax, n_bins=n_bins)

    null_metrics: List[float] = []
    for _ in range(n_sims):
        alm_surr = randomize_phases(alm_obs, lmax=lmax, rng=rng)
        met, _ = phase_coherence_metric(alm_surr, lmax=lmax, n_bins=n_bins)
        null_metrics.append(met)

    null = np.array(null_metrics, dtype=float)
    p = float((np.sum(null >= obs_metric) + 1.0) / (null.size + 1.0))  # one-sided high

    mu = float(np.mean(null))
    sd = float(np.std(null, ddof=1)) if null.size > 1 else float("nan")
    z = float((obs_metric - mu) / sd) if sd > 0 else float("nan")

    extras_null = {
        "null_mean": mu,
        "null_std": sd,
        "null_p95": float(np.quantile(null, 0.95)),
        "null_p99": float(np.quantile(null, 0.99)),
        "n_sims": int(n_sims),
    }

    return Report(
        observed_metric=float(obs_metric),
        null_metrics=[float(x) for x in null_metrics],
        p_value=p,
        z_score=z,
        extras_observed=obs_extras,
        extras_null_summary=extras_null,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fits", required=True, help="Path to Planck SMICA FITS")
    ap.add_argument("--field", default="0", help="Temperature field: use 0 (recommended) or a column name")
    ap.add_argument("--mask_field", default="", help="Mask field inside FITS; blank disables mask")
    ap.add_argument("--mask_thresh", type=float, default=0.9)
    ap.add_argument("--lmax", type=int, default=128)
    ap.add_argument("--nside", type=int, default=256)
    ap.add_argument("--n_sims", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_bins", type=int, default=8)
    ap.add_argument("--out", default="cmb_phase_dagger_report.json")
    ap.add_argument("--fits_url", default="", help="Source URL for the FITS used (for provenance).")
    ap.add_argument("--fits_sha256", default="", help="SHA256 of the FITS file used (for provenance).")
    ap.add_argument("--fits_bytes", default="", help="Byte size of the FITS file used (for provenance).")

    args = ap.parse_args()

    field = _coerce_field(args.field)
    mask_field = _coerce_field(args.mask_field)
    if mask_field == "":
        mask_field = None

    rep = run_dagger(
        fits_path=args.fits,
        field=field,
        mask_field=mask_field,
        mask_thresh=args.mask_thresh,
        lmax=args.lmax,
        nside=args.nside,
        n_sims=args.n_sims,
        seed=args.seed,
        n_bins=args.n_bins,
    )

    payload = {
        "inputs": {
            "fits": os.path.basename(args.fits),
            "field": field,
            "mask_field": mask_field,
            "mask_thresh": args.mask_thresh,
            "lmax": args.lmax,
            "nside": args.nside,
            "n_sims": args.n_sims,
            "seed": args.seed,
            "n_bins": args.n_bins,
        },
   
        "fits_provenance": {
            "fits_basename": os.path.basename(args.fits) if args.fits else "",
            "fits_url": args.fits_url or "",
            "fits_sha256": args.fits_sha256 or "",
            "fits_bytes": int(args.fits_bytes) if str(args.fits_bytes).strip().isdigit() else None,
        },

        "observed_metric": rep.observed_metric,
        "null_summary": rep.extras_null_summary,
        "p_value_one_sided_high": rep.p_value,
        "z_score": rep.z_score,
        "observed_extras": rep.extras_observed,
        "notes": {
            "interpretation": "If p_value is not small (e.g., >0.01), this particular phase-coherence dagger does NOT support a primordial phase-structure claim.",
            "mask_note": "If mask field is missing, run proceeds unmasked. For robustness, later add a dedicated Planck common mask FITS and pass it explicitly.",
        },
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("Wrote:", args.out)
    print("Observed metric:", rep.observed_metric)
    print("Null mean/std:", rep.extras_null_summary["null_mean"], rep.extras_null_summary["null_std"])
    print("p (one-sided, high):", rep.p_value)
    print("z:", rep.z_score)


if __name__ == "__main__":
    main()
