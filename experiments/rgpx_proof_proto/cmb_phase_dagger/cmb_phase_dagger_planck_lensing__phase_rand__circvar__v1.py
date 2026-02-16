#!/usr/bin/env python3
import argparse, json
import numpy as np
import healpy as hp


def truncate_alm(alm, lmax_target: int) -> np.ndarray:
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


def extract_phases_mgt0_nonzero(alm: np.ndarray, lmax: int, amp_eps: float = 0.0) -> np.ndarray:
    """
    Extract phases for m>0 only, skipping exactly-zero (or <=amp_eps) amplitudes.
    """
    phases = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            z = alm[hp.Alm.getidx(lmax, ell, m)]
            if np.abs(z) <= amp_eps:
                continue
            phases.append(np.angle(z))
    return np.asarray(phases, dtype=float)


def circ_var_from_phases(phases: np.ndarray) -> float:
    """Circular variance in [0,1]. Lower => more phase alignment."""
    if phases.size == 0:
        return float("nan")
    R = np.abs(np.mean(np.exp(1j * phases)))
    return float(1.0 - R)


def circ_var_from_unit_phasors(unit: np.ndarray) -> np.ndarray:
    """
    unit: complex array shaped (batch, n_phases) with |unit|=1 entries.
    Returns circular variance per row.
    """
    R = np.abs(np.mean(unit, axis=1))
    return 1.0 - R


def alm_imag_diagnostics(alm: np.ndarray, eps: float = 1e-12):
    """Quick sanity check that alms are actually complex-valued."""
    im = np.imag(alm)
    imag_max = float(np.max(np.abs(im))) if alm.size else 0.0
    imag_frac_nonzero = float(np.mean(np.abs(im) > eps)) if alm.size else 0.0
    return imag_max, imag_frac_nonzero


def surrogate_scores_phase_randomize_only(
    n_phases: int,
    obs: float,
    n_sims: int,
    seed: int,
    batch_size: int,
):
    """
    Fast null for phase structure when metric depends ONLY on phases:
      - Under null: phases ~ Uniform(-pi, pi) iid
      - Compute circular variance for each surrogate from random unit phasors

    We do NOT store all sims; we stream statistics:
      - mean, std (Welford)
      - p_low, p_high, p_two_sided (tail counts)
    """
    rng = np.random.default_rng(seed)

    # Welford running mean/variance
    count = 0
    mean = 0.0
    M2 = 0.0

    ge = 0  # sims >= obs
    le = 0  # sims <= obs

    # Process in batches
    remaining = int(n_sims)
    bs = max(1, int(batch_size))

    while remaining > 0:
        k = min(bs, remaining)

        # Draw phases, convert to unit phasors on the circle
        # Shape: (k, n_phases)
        ph = rng.uniform(-np.pi, np.pi, size=(k, n_phases))
        unit = np.exp(1j * ph)

        sims = circ_var_from_unit_phasors(unit)

        # Tail counts
        ge += int(np.sum(sims >= obs))
        le += int(np.sum(sims <= obs))

        # Update Welford stats
        for x in sims:
            count += 1
            delta = float(x) - mean
            mean += delta / count
            delta2 = float(x) - mean
            M2 += delta * delta2

        remaining -= k

    mu = float(mean)
    sd = float(np.sqrt(M2 / (count - 1))) if count > 1 else float("nan")
    z = float((obs - mu) / sd) if (sd and sd > 0) else float("nan")

    # +1 smoothing
    p_high = float((ge + 1.0) / (n_sims + 1.0))
    p_low = float((le + 1.0) / (n_sims + 1.0))
    p_two = float(min(1.0, 2.0 * min(p_low, p_high)))

    return mu, sd, z, p_low, p_high, p_two


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dat_klm", required=True, help="MV dat_klm alm FITS")
    ap.add_argument("--mf_klm", required=True, help="MV mean-field alm FITS")
    ap.add_argument("--lmax", type=int, default=256)
    ap.add_argument("--n_sims", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--batch_size", type=int, default=256, help="Monte Carlo batch size (memory vs speed)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    args = ap.parse_args()

    dat = hp.read_alm(args.dat_klm)
    mf = hp.read_alm(args.mf_klm)

    lmax = int(args.lmax)
    dat = truncate_alm(dat, lmax)
    mf = truncate_alm(mf, lmax)

    # Corrected phi_lm
    alm = dat - mf

    # Diagnostics: are alms actually complex?
    imag_max, imag_frac = alm_imag_diagnostics(alm)

    # Observed phases (m>0, nonzero amplitudes)
    phases = extract_phases_mgt0_nonzero(alm, lmax, amp_eps=0.0)
    obs = circ_var_from_phases(phases)

    # Surrogates: since metric is only a function of phases, sample random phases directly
    mu, sd, z, p_low, p_high, p_two = surrogate_scores_phase_randomize_only(
        n_phases=int(phases.size),
        obs=float(obs),
        n_sims=int(args.n_sims),
        seed=int(args.seed),
        batch_size=int(args.batch_size),
    )

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
        "p_low": float(p_low),              # alignment/structure tail (lower circ var)
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
        "notes": (
            "Implementation detail: the metric depends only on phases, so surrogate generation "
            "samples random phases directly (unit phasors exp(i*phi)). "
            "Zero-amplitude observed modes (rare) are excluded."
        ),
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
