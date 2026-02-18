#!/usr/bin/env python3
import argparse, json
import numpy as np
import healpy as hp


def truncate_alm(alm, lmax_target):
    """Truncate healpy alm array (m>=0 storage) to lmax_target."""
    lmax_src = hp.Alm.getlmax(len(alm))
    if lmax_src == lmax_target:
        return np.asarray(alm, dtype=np.complex128)

    if lmax_src < lmax_target:
        raise ValueError(f"alm lmax {lmax_src} < requested lmax {lmax_target}")

    out = np.zeros(hp.Alm.getsize(lmax_target), dtype=np.complex128)
    for ell in range(0, lmax_target + 1):
        for m in range(0, ell + 1):
            out[hp.Alm.getidx(lmax_target, ell, m)] = alm[hp.Alm.getidx(lmax_src, ell, m)]
    return out


def alm_imag_diagnostics(alm, eps=1e-12):
    im = np.imag(alm)
    imag_max = float(np.max(np.abs(im))) if alm.size else 0.0
    imag_frac_nonzero = float(np.mean(np.abs(im) > eps)) if alm.size else 0.0
    return imag_max, imag_frac_nonzero


def standardize_map(m):
    """Return standardized map x=(m-mean)/std."""
    mu = float(np.mean(m))
    sd = float(np.std(m))
    if sd == 0:
        return m * 0.0, mu, sd
    return (m - mu) / sd, mu, sd


def v0_area_fraction_curve(x, nus):
    """V0(nu) = fraction of pixels above threshold nu."""
    x = np.asarray(x)
    return [float(np.mean(x > nu)) for nu in nus]


def surrogate_alm_phase_randomize(alm, lmax, rng):
    """
    Phase-randomized surrogate:
      - preserve amplitudes |a_lm|
      - randomize phases for m>0 ONLY
      - keep m=0 coefficients EXACTLY as observed (do NOT force positive)
    """
    amps = np.abs(alm).astype(float)
    out = np.empty_like(alm)

    # m=0: keep exactly (these are real in theory, but keep as-is)
    for ell in range(0, lmax + 1):
        idx0 = hp.Alm.getidx(lmax, ell, 0)
        out[idx0] = alm[idx0]

    # m>0: preserve amplitude, randomize phase
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            idx = hp.Alm.getidx(lmax, ell, m)
            phi = rng.uniform(-np.pi, np.pi)
            out[idx] = amps[idx] * np.exp(1j * phi)

    return out


def v1_perimeter_curve_from_alm(alm, nside, lmax, nus):
    """
    V1(nu) estimator using gradient magnitude on the sphere.
    Approximates delta(x-nu) by a threshold band of width dnu.
    Returns (v1_curve, diag_dict).
    """
    # Field + derivatives wrt theta, phi
    # NOTE: hp.alm2map_der1 does NOT accept verbose= in some healpy versions.
    m, dth, dph = hp.alm2map_der1(alm, nside=nside, lmax=lmax)

    # Standardize field x = (m-mu)/sd
    x, mu, sd = standardize_map(m)
    if sd == 0:
        return [0.0 for _ in nus], {"map_mean": float(mu), "map_std": float(sd)}

    # Derivatives of standardized field
    dx_dth = dth / sd
    dx_dph = dph / sd

    # Spherical metric factor
    npix = hp.nside2npix(nside)
    theta, _ = hp.pix2ang(nside, np.arange(npix))
    sinth = np.sin(theta)
    sinth = np.where(sinth == 0, 1e-12, sinth)

    # Gradient magnitude on the sphere
    grad = np.sqrt(dx_dth**2 + (dx_dph / sinth)**2)

    nus = np.asarray(nus, dtype=np.float64)
    dnu = float(nus[1] - nus[0]) if len(nus) >= 2 else 1.0

    pix_area = 4.0 * np.pi / float(npix)
    half = 0.5 * dnu

    v1 = []
    for nu in nus:
        band = (x >= (nu - half)) & (x < (nu + half))
        # delta approx: sum grad over band, normalize by dnu
        val = float(np.sum(grad[band]) * pix_area / max(dnu, 1e-12))
        v1.append(val)

    return v1, {"map_mean": float(mu), "map_std": float(sd), "dnu": float(dnu)}


def l2_curve_distance(curve, mean_curve):
    a = np.asarray(curve, dtype=np.float64)
    b = np.asarray(mean_curve, dtype=np.float64)
    return float(np.sum((a - b) ** 2))


def pvals_from_null(null_vals, obs_val):
    """
    +1 smoothing p-values for a one-sided high-tail and two-sided via min(p_low,p_high).
    """
    null_vals = np.asarray(null_vals, dtype=np.float64)
    n = null_vals.size
    p_high = float((np.sum(null_vals >= obs_val) + 1.0) / (n + 1.0))
    p_low = float((np.sum(null_vals <= obs_val) + 1.0) / (n + 1.0))
    p_two = float(min(1.0, 2.0 * min(p_low, p_high)))
    return p_high, p_low, p_two


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dat_klm", required=True)
    ap.add_argument("--mf_klm", required=True)
    ap.add_argument("--lmax", type=int, default=256)
    ap.add_argument("--nside", type=int, default=256)
    ap.add_argument("--n_sims", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_nu", type=int, default=61)   # thresholds count
    ap.add_argument("--nu_min", type=float, default=-3.0)
    ap.add_argument("--nu_max", type=float, default=3.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    ap.add_argument(
        "--selftest_observed_surrogate_seed",
        type=int,
        default=None,
        help="If set, replace the observed alm by a single phase-randomized surrogate (for null calibration).",
    )
    args = ap.parse_args()

    lmax = int(args.lmax)
    nside = int(args.nside)
    n_sims = int(args.n_sims)

    rng = np.random.default_rng(int(args.seed))

    dat = hp.read_alm(args.dat_klm)
    mf = hp.read_alm(args.mf_klm)

    dat = truncate_alm(dat, lmax)
    mf = truncate_alm(mf, lmax)

    baseline_alm = dat - mf  # corrected phi_lm (baseline for null surrogates)

    imag_max, imag_frac = alm_imag_diagnostics(baseline_alm)

    # Observed alm: either baseline, or a single phase-randomized surrogate for selftest
    if args.selftest_observed_surrogate_seed is None:
        alm_obs = baseline_alm
    else:
        rng_obs = np.random.default_rng(int(args.selftest_observed_surrogate_seed))
        alm_obs = surrogate_alm_phase_randomize(baseline_alm, lmax, rng_obs)

    nus = np.linspace(float(args.nu_min), float(args.nu_max), int(args.n_nu))

    # Observed V0 from standardized map
    m_obs = hp.alm2map(alm_obs, nside=nside, lmax=lmax)
    x_obs, mu_obs, sd_obs = standardize_map(m_obs)
    v0_obs = v0_area_fraction_curve(x_obs, nus)

    # Observed V1 from gradient estimator
    v1_obs, v1_obs_diag = v1_perimeter_curve_from_alm(alm_obs, nside=nside, lmax=lmax, nus=nus)

    # Surrogates: curves + scalar deviation statistics
    v0_sims = np.empty((n_sims, len(nus)), dtype=np.float64)
    v1_sims = np.empty((n_sims, len(nus)), dtype=np.float64)

    # Build surrogate curves (always from the same baseline_alm)
    for i in range(n_sims):
        alm_s = surrogate_alm_phase_randomize(baseline_alm, lmax, rng)

        # V0
        m_s = hp.alm2map(alm_s, nside=nside, lmax=lmax)
        x_s, _, _ = standardize_map(m_s)
        v0_sims[i, :] = v0_area_fraction_curve(x_s, nus)

        # V1
        v1_curve, _ = v1_perimeter_curve_from_alm(alm_s, nside=nside, lmax=lmax, nus=nus)
        v1_sims[i, :] = v1_curve

    v0_mean = np.mean(v0_sims, axis=0)
    v0_std = np.std(v0_sims, axis=0, ddof=1) if n_sims > 1 else np.zeros_like(v0_mean)

    v1_mean = np.mean(v1_sims, axis=0)
    v1_std = np.std(v1_sims, axis=0, ddof=1) if n_sims > 1 else np.zeros_like(v1_mean)

    # Distances to surrogate mean curves
    D0_obs = l2_curve_distance(v0_obs, v0_mean)
    D1_obs = l2_curve_distance(v1_obs, v1_mean)

    D0_sims = np.sum((v0_sims - v0_mean) ** 2, axis=1).astype(np.float64)
    D1_sims = np.sum((v1_sims - v1_mean) ** 2, axis=1).astype(np.float64)

    # Combined score (transparent; no weights)
    Dmf_obs = float(np.sqrt(D0_obs**2 + D1_obs**2))
    Dmf_sims = np.sqrt(D0_sims**2 + D1_sims**2)

    # p-values (with +1 smoothing)
    p_high, p_low, p_two = pvals_from_null(D0_sims, D0_obs)
    p_high_mf, p_low_mf, p_two_mf = pvals_from_null(Dmf_sims, Dmf_obs)

    provenance = {
        "dat_url": args.dat_url,
        "mf_url": args.mf_url,
    }
    if args.selftest_observed_surrogate_seed is not None:
        provenance["selftest_observed_surrogate_seed"] = int(args.selftest_observed_surrogate_seed)

    report = {
        "kind": "planck_pr3_lensing_phi_topology_mf_v0_v1",
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": int(args.seed),
        "metric": "Minkowski-style morphology: V0(area) + V1(perimeter proxy) vs phase-random surrogates",
        "thresholds": {
            "nu_min": float(args.nu_min),
            "nu_max": float(args.nu_max),
            "n_nu": int(args.n_nu),
            "nus": [float(x) for x in nus],
        },
        "observed": {
            "map_mean": float(mu_obs),
            "map_std": float(sd_obs),
            "v0_curve": v0_obs,
            "v1_curve": v1_obs,
            "D0_L2": float(D0_obs),
            "D1_L2": float(D1_obs),
            "D_mf": float(Dmf_obs),
        },
        "surrogate": {
            "v0_mean_curve": [float(x) for x in v0_mean],
            "v0_std_curve": [float(x) for x in v0_std],
            "v1_mean_curve": [float(x) for x in v1_mean],
            "v1_std_curve": [float(x) for x in v1_std],
            "D0_mean": float(np.mean(D0_sims)),
            "D0_std": float(np.std(D0_sims, ddof=1)) if n_sims > 1 else float("nan"),
            "D1_mean": float(np.mean(D1_sims)),
            "D1_std": float(np.std(D1_sims, ddof=1)) if n_sims > 1 else float("nan"),
            "D_mf_mean": float(np.mean(Dmf_sims)),
            "D_mf_std": float(np.std(Dmf_sims, ddof=1)) if n_sims > 1 else float("nan"),
        },
        "p_high": p_high,
        "p_low": p_low,
        "p_two_sided": p_two,
        "p_high_mf": p_high_mf,
        "p_low_mf": p_low_mf,
        "p_two_sided_mf": p_two_mf,
        "diagnostics": {
            "imag_max_abs": float(imag_max),
            "imag_frac_nonzero_eps1e-12": float(imag_frac),
            "v1_delta_bandwidth_dnu": float(v1_obs_diag.get("dnu", float("nan"))),
        },
        "provenance": provenance,
        "hint": (
            "This script compares observed morphology against phase-randomized surrogates that preserve |a_lm|. "
            "V0(nu) is excursion-set area fraction; V1(nu) is a perimeter proxy estimated from |∇x| in a nu-band. "
            "Distances D0 and D1 are L2 distances to surrogate-mean curves. D_mf combines them as sqrt(D0^2 + D1^2)."
        ),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
