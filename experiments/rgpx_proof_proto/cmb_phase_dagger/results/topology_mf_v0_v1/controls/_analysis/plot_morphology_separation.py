from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUTFILE = HERE / "cmb_morphology_separation.png"

lmax = np.array([128, 192, 256, 320])

# Observed
obs_D1 = np.array([99.56, 144.04, 198.30, 267.09])
obs_Z  = np.array([64.35, 121.29, 207.02, 326.75])

# Gaussian controls
g_D1 = np.array([19.50, 16.84, 18.41, 22.82])
g_D1_std = np.array([13.07, 6.66, 6.05, 5.19])

g_Z = np.array([1.60, 1.16, 1.17, 1.37])
g_Z_std = np.array([1.09, 0.61, 0.81, 1.23])

# ΛCDM reconstruction
l_D1 = np.array([107.00, 159.71, 218.18, 288.03])
l_D1_std = np.array([10.36, 14.76, 31.25, 48.14])

l_Z = np.array([88.48, 146.40, 223.10, 329.57])
l_Z_std = np.array([52.85, 85.45, 117.30, 151.82])

print(f"Script directory: {HERE}")
print(f"Will save to: {OUTFILE}")

plt.figure(figsize=(8, 6))

# Gaussian controls: points + error bars only, no connecting line
plt.errorbar(
    g_D1, g_Z,
    xerr=g_D1_std, yerr=g_Z_std,
    fmt='o',
    color='black',
    alpha=0.6,
    capsize=3,
    label='Gaussian control (power-matched, mean ± std)'
)

# ΛCDM: connect means + show error bars
plt.plot(
    l_D1, l_Z,
    color='blue',
    alpha=0.6,
    linewidth=1.5
)
plt.errorbar(
    l_D1, l_Z,
    xerr=l_D1_std, yerr=l_Z_std,
    fmt='o',
    color='blue',
    capsize=3,
    label='ΛCDM reconstruction (mean ± std)'
)

# Observed: connect points
plt.plot(
    obs_D1, obs_Z,
    color='red',
    alpha=0.6,
    linewidth=1.5
)
plt.scatter(
    obs_D1, obs_Z,
    s=80,
    color='red',
    label='Observed CMB lensing (Planck PR3)'
)

# Label each point by lmax
for i, ell in enumerate(lmax):
    plt.annotate(str(ell), (obs_D1[i], obs_Z[i]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    plt.annotate(str(ell), (l_D1[i], l_Z[i]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    plt.annotate(str(ell), (g_D1[i], g_Z[i]), xytext=(5, 5), textcoords="offset points", fontsize=8)

# Log scaling to open up the Gaussian cluster and preserve separation honestly
plt.xscale("log")
plt.yscale("log")

plt.xlabel("D1_L2")
plt.ylabel("Z_mf")
plt.title("Morphology Separation in CMB Lensing")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.4)
plt.tight_layout()

plt.savefig(OUTFILE, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved exists: {OUTFILE.exists()}")
print(f"Saved size: {OUTFILE.stat().st_size if OUTFILE.exists() else 'missing'} bytes")
