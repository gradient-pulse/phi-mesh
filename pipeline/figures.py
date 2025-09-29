import matplotlib
matplotlib.use("Agg")  # headless backend for CI
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .utils import ensure_dir

__all__ = ["plot_time_and_spectrum"]

def plot_time_and_spectrum(outdir: str | Path, t: np.ndarray, x: dict[str, np.ndarray],
                           freq: np.ndarray, power: np.ndarray, f0: float | None = None) -> dict:
    outdir = ensure_dir(outdir)
    # time-domain
    fig1, ax1 = plt.subplots(figsize=(8,3))
    for k, v in x.items():
        ax1.plot(t, v, label=k)
    ax1.set_xlabel("t")
    ax1.set_ylabel("amplitude")
    ax1.legend()
    p1 = Path(outdir) / "time.png"
    fig1.tight_layout(); fig1.savefig(p1, dpi=150); plt.close(fig1)

    # spectrum
    fig2, ax2 = plt.subplots(figsize=(8,3))
    ax2.plot(freq, power)
    if f0:
        ax2.axvline(f0, ls="--")
        ax2.axvline(2*f0, ls=":", alpha=0.7)
        ax2.axvline(3*f0, ls=":", alpha=0.7)
    ax2.set_xlim(0, freq.max() if freq.size else 1)
    ax2.set_xlabel("Hz")
    ax2.set_ylabel("power (arb.)")
    p2 = Path(outdir) / "spectrum.png"
    fig2.tight_layout(); fig2.savefig(p2, dpi=150); plt.close(fig2)

    return {"time_png": p1.as_posix(), "spectrum_png": p2.as_posix()}

# ------------------------------ self-test ------------------------------ #

if __name__ == "__main__":
    import numpy as np
    t = np.linspace(0, 6, 6001)
    x = {"u": np.sin(2*np.pi*0.8*t)}
    from .spectrum import rfft_spectrum
    sp = rfft_spectrum(t, x["u"])
    out = plot_time_and_spectrum("tmp_figs", t, x, sp["freq"], sp["power"], f0=0.8)
    print("figures OK:", out)
