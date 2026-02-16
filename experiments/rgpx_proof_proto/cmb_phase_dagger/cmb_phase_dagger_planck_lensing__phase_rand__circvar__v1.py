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
    """Quick sanity check that alms are actually complex-valued."""
    im = np.imag(alm)
    imag_max = float(np.max(np.abs(im))) if alm.size else 0.0
    imag_frac_nonzero = float(np.mean(np.abs(im) > eps)) if alm.size else 0.0
    return imag_max, imag_frac_nonzero


def build_mgt0_indices(lmax):
    """Return numpy array of Alm indices for all (ell,m) with ell>=1 and 1<=m<=ell."""
    idxs = []
    for ell in range(1, lmax + 1):
        # m = 1..ell
        for m in range(1, ell + 1):
            idxs.append(hp.Alm.getidx(lmax, ell, m))
    return np.asarray(idxs, dtype=np.int64)


def circ_var_from_unit_phasors(u):
    """
    Circular variance for angles whose unit phasors are u = exp(i*theta).
    V = 1 - |mean(u)|
    """
    if u.size == 0:
        return float("nan")
    R = np.abs(np.mean(u))
    return float(1.0 - R)


def surrogate_scores_phase_randomize(alm, lmax, n_sims, seed, batch_size=256):
    """
    Null for phase structure:
      - m>0 phases ~ Uniform(-pi, pi), independent
      - amplitudes conceptually preserved, but the chosen metric uses phases only
    Metric: circular variance of m>0 phase angles.

    Returns:
      obs, mu, sd, z, p_low, p_high, p_two, n_phases_used
    """
    rng = np.random.default_rng(seed)

    # m>0 indices
    idx_mgt0 = build_mgt0_indices(lmax)

    # Observed unit phasors u = z/|z| (exclude exact zeros to avoid 0/0)
    z = alm[idx_mgt0]
    amps = np.abs(z)
    good = amps > 0.0
    z = z[good]
    amps = amps[good]
    n_phases_used = int(z.size)

    u_obs = z / amps  # complex unit phasors
    obs = circ_var_from_unit_phasors(u_obs)

    # Simulated circular variance under uniform phases:
    # for each sim: u_sim = exp(i*phi), phi ~ U(-pi, pi)
    sims = np.empty(int(n_sims), dtype=np.float64)

    remaining = int(n_sims)
    out_i = 0
    N = n_phases_used

    # Chunked to control memory
    while remaining > 0:
        b = min(batch_size, remaining)

        # random phases: shape (b, N)
        phi = rng.uniform(-np.pi, np.pi, size=(b, N)).astype(np.float32, copy=False)

        # unit phasors: exp(i*phi) -> complex64
        u = np.exp(1j * phi).astype(np.complex64, copy=False)

        # mean phasor length per sim
        R = np.abs(np.mean(u, axis=1)).astype(np.float64, copy=False)

        sims[out_i:out_i + b] = 1.0 - R  # circular variance
        out_i += b
        remaining -= b

    mu = float(np.mean(sims))
    sd = float(np.std(sims, ddof=1)) if n_sims > 1 else float("nan")
    zscore = float((obs - mu) / sd) if (sd and sd > 0) else float("nan")

    # Tail probabilities with +1 smoothing (works for one- and two-sided)
    n = float(n_sims)
    p_high = float((np.sum(sims >= obs) + 1.0) / (n + 1.0))  # upper tail
    p_low  = float((np.sum(sims <= obs) + 1.0) / (n + 1.0))  # lower tail
    p_two  = float(min(1.0, 2.0 * min(p_low, p_high)))

    return obs, mu, sd, zscore, p_low, p_high, p_two, n_phases_used


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
    ap.add_argument("--batch_size", type=int, default=256, help="Monte Carlo batch size (memory vs speed)")
    args = ap.parse_args()

    dat = hp.read_alm(args.dat_klm)
    mf  = hp.read_alm(args.mf_klm)

    lmax = int(args.lmax)
    dat = truncate_alm(dat, lmax)
    mf  = truncate_alm(mf,  lmax)

    # Corrected phi_lm
    alm = dat - mf

    imag_max, imag_frac = alm_imag_diagnostics(alm)

    obs, mu, sd, zscore, p_low, p_high, p_two, n_used = surrogate_scores_phase_randomize(
        alm=alm,
        lmax=lmax,
        n_sims=int(args.n_sims),
        seed=int(args.seed),
        batch_size=int(args.batch_size),
    )

    report = {
        "kind": "planck_pr3_lensing_phi_alm_phase_dagger",
        "lmax": lmax,
        "n_phases": int(n_used),
        "n_sims": int(args.n_sims),
        "seed": int(args.seed),
        "metric": "circular_variance(m>0 phase angles)",
        "observed": float(obs),
        "surrogate_mean": float(mu),
        "surrogate_std": float(sd),
        "z_score": float(zscore),
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
        "notes": (
            "Implementation detail: the metric depends only on phases, so surrogate generation "
            "uses random unit phasors exp(i*phi). Zero-amplitude observed modes (rare) are excluded."
        ),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
