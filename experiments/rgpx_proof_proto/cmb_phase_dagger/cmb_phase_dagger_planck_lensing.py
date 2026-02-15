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


def extract_phases_mgt0(alm, lmax):
    """Keep only m>0 phases to avoid m=0 real-mode quirks."""
    phases = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            z = alm[hp.Alm.getidx(lmax, ell, m)]
            phases.append(np.angle(z))
    return np.asarray(phases, dtype=float)


def circ_var(phases):
    """Circular variance in [0,1]. Lower => more phase alignment."""
    if phases.size == 0:
        return float("nan")
    R = np.abs(np.mean(np.exp(1j * phases)))
    return float(1.0 - R)


def alm_imag_diagnostics(alm, eps=1e-12):
    """Quick sanity check that alms are actually complex-valued."""
    im = np.imag(alm)
    imag_max = float(np.max(np.abs(im))) if alm.size else 0.0
    imag_frac_nonzero = float(np.mean(np.abs(im) > eps)) if alm.size else 0.0
    return imag_max, imag_frac_nonzero


def surrogate_scores_phase_randomize(alm, lmax, n_sims, seed):
    """
    Null for phase structure:
      - keep amplitudes |a_lm|
      - randomize phases ~ Uniform(-pi, pi) for m>0
      - keep m=0 real (positive amplitude)
    Metric: circular variance of m>0 phase angles.

    Returns:
      obs, mu, sd, z, p_low, p_high, p_two
    """
    rng = np.random.default_rng(seed)

    phases_obs = extract_phases_mgt0(alm, lmax)
    obs = circ_var(phases_obs)

    amps = np.abs(alm).astype(float)

    sims = np.empty(n_sims, dtype=float)
    for i in range(n_sims):
        alm_s = np.empty_like(alm)

        # m=0 modes: real, positive amplitude
        for ell in range(0, lmax + 1):
            idx0 = hp.Alm.getidx(lmax, ell, 0)
            alm_s[idx0] = amps[idx0] + 0j

        # m>0 modes: independent random phases
        for ell in range(1, lmax + 1):
            for m in range(1, ell + 1):
                idx = hp.Alm.getidx(lmax, ell, m)
                phi = rng.uniform(-np.pi, np.pi)
                alm_s[idx] = amps[idx] * np.exp(1j * phi)

        sims[i] = circ_var(extract_phases_mgt0(alm_s, lmax))

    mu = float(np.mean(sims))
    sd = float(np.std(sims, ddof=1)) if n_sims > 1 else float("nan")
    z = float((obs - mu) / sd) if (sd and sd > 0) else float("nan")

    # Tail probabilities with +1 smoothing
    p_high = float((np.sum(sims >= obs) + 1.0) / (n_sims + 1.0))  # upper tail
    p_low  = float((np.sum(sims <= obs) + 1.0) / (n_sims + 1.0))  # lower tail
    p_two  = float(min(1.0, 2.0 * min(p_low, p_high)))            # two-sided

    return obs, mu, sd, z, p_low, p_high, p_two


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dat_klm", required=True, help="MV dat_klm alm FITS")
    ap.add_argument("--mf_klm", required=True, help="MV mean-field alm FITS")
    ap.add_argument("--lmax", type=int, default=128)
    ap.add_argument("--n_sims", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    args = ap.parse_args()

    dat = hp.read_alm(args.dat_klm)
    mf  = hp.read_alm(args.mf_klm)

    lmax = int(args.lmax)
    dat = truncate_alm(dat, lmax)
    mf  = truncate_alm(mf,  lmax)

    # Corrected phi_lm
    alm = dat - mf

    imag_max, imag_frac = alm_imag_diagnostics(alm)

    obs, mu, sd, z, p_low, p_high, p_two = surrogate_scores_phase_randomize(
        alm=alm,
        lmax=lmax,
        n_sims=int(args.n_sims),
        seed=int(args.seed),
    )

    phases = extract_phases_mgt0(alm, lmax)

    report = {
        "kind": "planck_pr3_lensing_phi_alm_phase_dagger",
        "lmax": lmax,
        "n_phases": int(phases.size),
        "n_sims": int(args.n_sims),
        "seed": int(args.seed),
        "metric": "circular_variance(m>0 phase angles)",
        "observed": float(obs),
        "surrogate_mean": float(mu),
        "surrogate_std": float(sd),
        "z_score": float(z),
        "p_low": float(p_low),              # alignment / structure tail
        "p_high": float(p_high),
        "p_two_sided": float(p_two),
        "diagnostics": {
            "imag_max_abs": float(imag_max),
            "imag_frac_nonzero_eps1e-12": float(imag_frac),
        },
        "provenance": {
            "dat_url": args.dat_url,
            "mf_url": args.mf_url,
        },
        "hint": (
            "Null: random m>0 phases (uniform) with observed amplitudes. "
            "Lower circular variance => more phase alignment. "
            "Use p_low for 'structure' evidence."
        ),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
