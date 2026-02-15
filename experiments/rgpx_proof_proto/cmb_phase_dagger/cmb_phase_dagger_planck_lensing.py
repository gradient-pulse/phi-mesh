#!/usr/bin/env python3
import argparse, json, math
import numpy as np
import healpy as hp

def extract_phases(alm, lmax):
    # Keep only m>0 phases to avoid m=0 real-mode quirks
    phases = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            z = alm[hp.Alm.getidx(lmax, ell, m)]
            phases.append(np.angle(z))
    return np.asarray(phases, dtype=float)

def circ_var(phases):
    # Circular variance in [0,1]
    if phases.size == 0:
        return float("nan")
    R = np.abs(np.mean(np.exp(1j * phases)))
    return float(1.0 - R)

def surrogate_score(phases, n_sims, seed):
    rng = np.random.default_rng(seed)
    obs = circ_var(phases)

    sims = np.empty(n_sims, dtype=float)
    for i in range(n_sims):
        shuf = rng.permutation(phases)
        sims[i] = circ_var(shuf)

    mu = float(np.mean(sims))
    sd = float(np.std(sims, ddof=1)) if n_sims > 1 else float("nan")
    z = float((obs - mu) / sd) if sd and sd > 0 else float("nan")
    p = float((np.sum(sims >= obs) + 1.0) / (n_sims + 1.0))  # one-sided
    return obs, mu, sd, z, p

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

    # Read alms; healpy returns complex alm array with inferred lmax
    dat = hp.read_alm(args.dat_klm)
    mf  = hp.read_alm(args.mf_klm)

    # Enforce lmax slice consistently
    lmax = args.lmax
    dat = hp.almxfl(dat, np.ones(lmax + 1))  # forces shape compatibility
    mf  = hp.almxfl(mf,  np.ones(lmax + 1))

    alm = dat - mf  # corrected phi_lm
    phases = extract_phases(alm, lmax)

    obs, mu, sd, z, p = surrogate_score(phases, args.n_sims, args.seed)

    report = {
        "kind": "planck_pr3_lensing_phi_alm_phase_dagger",
        "lmax": lmax,
        "n_phases": int(phases.size),
        "n_sims": args.n_sims,
        "seed": args.seed,
        "metric": "circular_variance(m>0 phase angles)",
        "observed": obs,
        "surrogate_mean": mu,
        "surrogate_std": sd,
        "z_score": z,
        "p_one_sided": p,
        "provenance": {
            "dat_url": args.dat_url,
            "mf_url": args.mf_url,
        },
        "hint": "If phases show non-random structure, obs should sit in the extreme tail vs surrogates."
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
