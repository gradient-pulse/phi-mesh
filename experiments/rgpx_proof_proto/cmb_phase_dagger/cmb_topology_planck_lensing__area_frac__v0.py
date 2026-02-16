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
    # Vectorized: for each nu, compute mean(x > nu)
    return [float(np.mean(x > nu)) for nu in nus]


def surrogate_alm_phase_randomize(alm, lmax, rng):
    """
    Phase-randomized surrogate:
      - preserve amplitudes |a_lm|
      - randomize phases for m>0
      - keep m=0 real positive amplitude
    """
    amps = np.abs(alm).astype(float)
    out = np.empty_like(alm)

    # m=0: real positive
    for ell in range(0, lmax + 1):
        idx0 = hp.Alm.getidx(lmax, ell, 0)
        out[idx0] = amps[idx0] + 0j

    # m>0: random phases
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            idx = hp.Alm.getidx(lmax, ell, m)
            phi = rng.uniform(-np.pi, np.pi)
            out[idx] = amps[idx] * np.exp(1j * phi)

    return out


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
    ap.add_argument("--nu_max", type=float, default= 3.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    args = ap.parse_args()

    lmax = int(args.lmax)
    nside = int(args.nside)
    n_sims = int(args.n_sims)
    rng = np.random.default_rng(int(args.seed))

    dat = hp.read_alm(args.dat_klm)
    mf  = hp.read_alm(args.mf_klm)

    dat = truncate_alm(dat, lmax)
    mf  = truncate_alm(mf,  lmax)

    alm = dat - mf  # corrected phi_lm

    imag_max, imag_frac = alm_imag_diagnostics(alm)

    # Observed map + standardized field
    m_obs = hp.alm2map(alm, nside=nside, lmax=lmax, verbose=False)
    x_obs, mu_obs, sd_obs = standardize_map(m_obs)

    nus = np.linspace(float(args.nu_min), float(args.nu_max), int(args.n_nu))
    v0_obs = v0_area_fraction_curve(x_obs, nus)

    # Surrogates: curves + a single scalar deviation statistic
    v0_sims = np.empty((n_sims, len(nus)), dtype=np.float64)
    D_sims  = np.empty(n_sims, dtype=np.float64)

    # We compare each sim curve to the *mean* sim curve, so we need 2-pass
    for i in range(n_sims):
        alm_s = surrogate_alm_phase_randomize(alm, lmax, rng)
        m_s   = hp.alm2map(alm_s, nside=nside, lmax=lmax, verbose=False)
        x_s, _, _ = standardize_map(m_s)
        v0_sims[i, :] = v0_area_fraction_curve(x_s, nus)

    v0_mean = np.mean(v0_sims, axis=0)
    v0_std  = np.std(v0_sims, axis=0, ddof=1) if n_sims > 1 else np.zeros_like(v0_mean)

    # L2 distance from the surrogate mean curve
    v0_obs_arr = np.asarray(v0_obs, dtype=np.float64)
    D_obs = float(np.sum((v0_obs_arr - v0_mean) ** 2))

    for i in range(n_sims):
        D_sims[i] = float(np.sum((v0_sims[i, :] - v0_mean) ** 2))

    # p-values (with +1 smoothing)
    p_high = float((np.sum(D_sims >= D_obs) + 1.0) / (n_sims + 1.0))  # "more deviant than null"
    p_low  = float((np.sum(D_sims <= D_obs) + 1.0) / (n_sims + 1.0))  # "more null-like than null"
    p_two  = float(min(1.0, 2.0 * min(p_low, p_high)))

    report = {
        "kind": "planck_pr3_lensing_phi_topology_area_fraction_v0",
        "lmax": lmax,
        "nside": nside,
        "n_sims": n_sims,
        "seed": int(args.seed),
        "metric": "V0 area-fraction curve (excursion sets) + L2 distance",
        "thresholds": {
            "nu_min": float(args.nu_min),
            "nu_max": float(args.nu_max),
            "n_nu": int(args.n_nu),
            "nus": [float(x) for x in nus],
        },
        "observed": {
            "map_mean": mu_obs,
            "map_std": sd_obs,
            "v0_curve": v0_obs,
            "D_L2": D_obs,
        },
        "surrogate": {
            "v0_mean_curve": [float(x) for x in v0_mean],
            "v0_std_curve":  [float(x) for x in v0_std],
            "D_mean": float(np.mean(D_sims)),
            "D_std":  float(np.std(D_sims, ddof=1)) if n_sims > 1 else float("nan"),
        },
        "p_high": p_high,
        "p_low": p_low,
        "p_two_sided": p_two,
        "diagnostics": {
            "imag_max_abs": float(imag_max),
            "imag_frac_nonzero_eps1e-12": float(imag_frac),
        },
        "provenance": {
            "dat_url": args.dat_url,
            "mf_url": args.mf_url,
        },
        "hint": (
            "Topology v0: compare observed excursion-set area fraction curve V0(nu) "
            "against phase-randomized surrogates (preserve |a_lm|, randomize phases). "
            "Statistic D is L2 distance to surrogate-mean curve. High D => more non-null morphology."
        ),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
