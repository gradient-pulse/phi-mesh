# pipeline/figures.py
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def plot_ts(t, x, probe_id: str, var: str, outdir: str):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    ax.plot(t, x)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(var)
    ax.set_title(f"{probe_id} — {var}")
    fig.tight_layout()
    fig.savefig(Path(outdir) / f"ts__{safe(probe_id)}__{var}.png", dpi=150)
    plt.close(fig)

def plot_psd(f, Pxx, det, probe_id: str, var: str, outdir: str):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    ax.plot(f, Pxx)
    if det.f_base:
        ax.axvline(det.f_base, linestyle="--")
        ax.axvline(2*det.f_base, linestyle="--")
        ax.axvline(3*det.f_base, linestyle="--")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD")
    ax.set_title(f"{probe_id} — {var} (1–2–3 ladder {'✔' if det.passed else '✖'})")
    fig.tight_layout()
    fig.savefig(Path(outdir) / f"psd__{safe(probe_id)}__{var}.png", dpi=150)
    plt.close(fig)

def safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in s)
