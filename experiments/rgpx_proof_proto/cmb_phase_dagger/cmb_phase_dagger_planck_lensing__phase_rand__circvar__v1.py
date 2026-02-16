#!/usr/bin/env python3
import argparse
import json
import math
import os
from datetime import datetime, timezone

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


def phases_mgt0(alm, lmax, amp_eps=0.0):
    """
    Return phase angles for m>0 modes.
    If amp_eps > 0, exclude (ell,m) with |a_lm| <= amp_eps.
    """
    ph = []
    for ell in range(1, lmax + 1):
        for m in range(1, ell + 1):
            idx = hp.Alm.getidx(lmax, ell, m)
            z = alm[idx]
            if amp_eps > 0.0 and (np.abs(z) <= amp_eps):
                continue
            ph.append(np.angle(z))
    return np.asarray(ph, dtype=float)


def circ_var_from_phases(phases):
    """Circular variance in [0,1]. Lower => more phase alignment."""
    if phases.size == 0:
        return float("nan")
    R = np.abs(np.mean(np.exp(1j * phases)))
    return float(1.0 - R)


def monte_carlo_circvar_null(n, n_sims, seed, batch_size=256):
    """
    Null: phases are i.i.d Uniform(-pi, pi).
    Metric: circular variance of phases => 1 - |mean(exp(i phi))|.

    Implementation note:
      The circ-var depends only on phases, not amplitudes.
      So the null depends only on the number of included phases, n.
    """
    rng = np.random.default_rng(seed)

    sims = np.empty(n_sims, dtype=np.float64)
    done = 0
    batch_size = max(1, int(batch_size))

    while done < n_sims:
        b = min(batch_size, n_sims - done)

        # Generate random phases [b, n], then unit phasors exp(i phi)
        phi = rng.uniform(-math.pi, math.pi, size=(b, n))
        u = np.exp(1j * phi)

        # R = |mean(u, axis=1)| ; circvar = 1 - R
        R = np.abs(np.mean(u, axis=1))
        sims[done:done + b] = 1.0 - R
        done += b

    return sims


def tail_ps(sims, obs):
    """Return p_low, p_high, p_two with +1 smoothing."""
    n = sims.size
    p_high = float((np.sum(sims >= obs) + 1.0) / (n + 1.0))
    p_low  = float((np.sum(sims <= obs) + 1.0) / (n + 1.0))
    p_two  = float(min(1.0, 2.0 * min(p_low, p_high)))
    return p_low, p_high, p_two


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dat_klm", required=True, help="MV dat_klm alm FITS")
    ap.add_argument("--mf_klm", required=True, help="MV mean-field alm FITS")
    ap.add_argument("--lmax", type=int, default=256)
    ap.add_argument("--n_sims", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--batch_size", type=int, default=256, help="Monte Carlo batch size (memory vs speed)")
    ap.add_argument("--amp_eps", type=float, default=0.0, help="Exclude m>0 modes with |alm|<=amp_eps (default keeps all)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dat_url", default="")
    ap.add_argument("--mf_url", default="")
    args = ap.parse_args()

    # Load and align
    dat = hp.read_alm(args.dat_klm)
    mf  = hp.read_alm(args.mf_klm)
    lmax = int(args.lmax)
    dat = truncate_alm(dat, lmax)
    mf  = truncate_alm(mf,  lmax)

    # Corrected phi_lm
    alm = dat - mf

    # Diagnostics: are alms complex?
    imag_max, imag_frac = alm_imag_diagnostics(alm)

    # Observed phases (m>0)
    ph = phases_mgt0(alm, l
