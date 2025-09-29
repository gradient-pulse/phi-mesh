# pipeline/figures.py
from __future__ import annotations

# Use a headless backend for CI before importing pyplot
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .utils import ensure_dir
from .spectrum import rfft_spectrum  # only used in the self-test

__all__ = ["plot_time_and_spectrum"]


def plot_time_and_spectrum(
    outdir: str | Path,
    t: np.ndarray,
    x: dict[str, np.ndarray],
    freq: np.ndarray,
    power: np.ndarray,
    f0: float | None = None,
) -> dict:
    """
    Save time-series and spectrum figures to `outdir`.

    Returns a dict with absolute paths to the saved PNGs.
    """
    outdir = ensure_dir(outdir)

    # ---- time-domain plot
    fig1, ax1 = plt.subplots(figsize=(8, 3))
    for k, v in (x or {}).items():
        if v is not None and np.size(v):
            ax1.plot(t, v, label=k)
    ax1.set_xlabel("t")
    ax1.set_ylabel("amplitude")
    if x:
        ax1.legend()
    p_time = Path(outdir) / "time.png"
    fig1.tight_layout()
    fig1.savefig(p_time, dpi=150)
    plt.close(fig1)

    # ---- spectrum plot
    fig2, ax2 = plt.subplots(figsize=(8, 3))
    if np.size(freq) and np.size(power):
        ax2.plot(freq, power)
        if f0 and f0 > 0:
            ax2.axvline(f0, ls="--")
            ax2.axvline(2 * f0, ls=":", alpha=0.7)
            ax2.axvline(3 * f0, ls=":", alpha=0.7)
        ax2.set_xlim(0, float(freq.max()))
    ax2.set_xlabel("Hz")
    ax2.set_ylabel("power (arb.)")
    p_spec = Path(outdir) / "spectrum.png"
    fig2.tight_layout()
    fig2.savefig(p_spec, dpi=150)
    plt.close(fig2)

    return {"time_png": p_time.as_posix(), "spectrum_png": p_spec.as_posix()}


# ------------------------------ self-test ------------------------------ #
if __name__ == "__main__":
    # Minimal smoke test
    t = np.linspace(0, 6, 6001)
    sig = np.sin(2 * np.pi * 0.8 * t)
    sp = rfft_spectrum(t, sig)
    out = plot_time_and_spectrum(
        "tmp_figs",
        t,
        {"u": sig},
        sp["freq"],
        sp["power"],
        f0=0.8,
    )
    print("figures OK:", out)
