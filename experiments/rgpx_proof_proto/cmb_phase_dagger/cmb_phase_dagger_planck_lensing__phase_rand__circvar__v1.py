#!/usr/bin/env python3
import argparse
import json
import math
import numpy as np
import healpy as hp


def truncate_alm(alm, lmax_target: int) -> np.ndarray:
    """Truncate healpy alm array (m>=0 storage) to lmax_target."""
    lmax_src = hp.Alm.getlmax(len(alm))
    alm = np.asarray(alm, dtype=np.complex128)

    if lmax_src == lmax_target:
        return alm

    if lmax_src < lmax_target:
        raise ValueError(f"alm lmax {lmax_src} < requested lmax {lmax_target}")

    out = np.zeros(hp.Alm.getsize(lmax_target), dtype=np.complex128)
    for ell in range(0, lmax_target + 1):
        for m in range(0, ell + 1):
            out[hp.Alm.getidx(lmax_target, ell, m)] = alm[hp.Alm.getidx(lmax_src, ell, m)]
    return out


def extract_phases_mgt0(alm: np.ndarray, lmax: int) -> np.ndarray:
    """Extract phases for m>0 only (avoid m=0 real-mode quirks)."""
    phases = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            z = alm[hp.Alm.getidx(lmax, ell, m)]
            phases.append(np.angle(z))
    return np.asarray(phases, dtype=np.float64)


def circ_var_from_phases(phases: np.ndarray) -> float:
    """Circular variance in [0,1]. Lower => more phase alignment."""
    if phases.size == 0:
        return float("nan")
    R = np.abs(np.mean(np.exp(1j * phases)))
    return float(1.0 - R)


def alm_imag_diagnostics(alm: np.ndarray, eps: float = 1e-12):
    """Sanity check that alms are complex-valued."""
    im = np.imag(alm)
    imag_max = float(np.max(np.abs(im))) if alm.size else 0.0
    imag_frac_nonzero = float(np.mean(np.abs(im) > eps)) if alm.size else 0.0
    return imag_max, imag_frac_nonzero


def mc_null_circvar_uniform_phases(
    n_phases: int,
    n_sims: int,
    seed: int,
    batch_size: int,
):
    """
    Null for phase structure:
      - phases i.i.d. Uniform(-pi, pi)
    Statistic:
      - circular variance of phases (m>0)

    We simulate phases directly (fast), because the metric depends only on phases.
    """
    rng = np.random.default_rng(seed)
    sims = np.empty(n_sims, dtype=np.float64)

    # Generate in batches to keep RAM bounded
    k = 0
    while k < n_sims:
        b = min(batch_size, n_sims - k)
        # shape (b, n_phases)
        ph = rng.uniform(-np.pi, np.pi, size=(b, n_phases))
        # mean resultant length R for each sim
        R = np.abs(np.mean(np.exp(1j * ph), axis=1))
        sims[k:k + b] = 1.0 - R
        k += b

    mu = float(np.mean(sims))
    sd = float(np.std(sims, ddof=1)) if n_sims > 1 else float("nan")
    return sims, mu, sd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dat_klm", required=True, help="MV dat_klm alm FITS")
    ap.add_argument("--mf_klm", required=True, help="MV mean-field alm FITS")
    ap.add_argument("--lmax", type=int, default=256)
    ap.add_argument("--n_sims", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--batch_size", type=int, default=256, help="MC batch size (RAM vs speed)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    args = ap.parse_args()

    dat = hp.read_alm(args.dat_klm)
    mf = hp.read_alm(args.mf_klm)

    lmax = int(args.lmax)
    dat = truncate_alm(dat, lmax)
    mf = truncate_alm(mf, lmax)

    alm = dat - mf  # corrected phi_lm

    imag_max, imag_frac = alm_imag_diagnostics(alm)

    phases_obs = extract_phases_mgt0(alm, lmax)

    # Exclude exactly-zero amplitude modes (phase undefined); rare but makes definition clean.
    # This is conservative and makes obs + null consistent.
    # Note: phase-only null doesn't depend on amplitudes; exclusion is just definitional hygiene.
    amp_obs = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            z = alm[hp.Alm.getidx(lmax, ell, m)]
            amp_obs.append(np.abs(z))
    amp_obs = np.asarray(amp_obs, dtype=np.float64)
    mask = amp_obs > 0.0
    phases_obs = phases_obs[mask]
    n_phases = int(phases_obs.size)

    obs = circ_var_from_phases(phases_obs)

    sims, mu, sd = mc_null_circvar_uniform_phases(
        n_phases=n_phases,
        n_sims=int(args.n_sims),
        seed=int(args.seed),
        batch_size=int(args.batch_size),
    )

    z = float((obs - mu) / sd) if (sd and sd > 0) else float("nan")

    # Tail probabilities (+1 smoothing)
    n = int(args.n_sims)
    p_high = float((np.sum(sims >= obs) + 1.0) / (n + 1.0))
    p_low = float((np.sum(sims <= obs) + 1.0) / (n + 1.0))
    p_two = float(min(1.0, 2.0 * min(p_low, p_high)))

    report = {
        "kind": "planck_pr3_lensing_phi_alm_phase_dagger",
        "lmax": lmax,
        "n_phases": n_phases,
        "n_sims": int(args.n_sims),
        "seed": int(args.seed),
        "metric": "circular_variance(m>0 phase angles)",
        "observed": float(obs),
        "surrogate_mean": float(mu),
        "surrogate_std": float(sd),
        "z_score": float(z),
        "p_low": float(p_low),
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
            "Null: random m>0 phases (uniform). Lower circular variance => more phase alignment. "
            "Use p_low for 'structure' evidence."
        ),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
