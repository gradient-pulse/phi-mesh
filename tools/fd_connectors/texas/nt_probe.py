# nt_probe.py
import re
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from pathlib import Path

PATH = Path("Stat_Re17KM08.txt")   # <- change if needed
COMMENT = "*"

def clean_cols(cols):
    out = []
    for c in cols:
        c = c.strip().lower().replace("+","plus").replace("/","_per_")
        out.append(re.sub(r"[^a-z0-9_]+","_", c).strip("_"))
    return out

df = pd.read_csv(PATH, delim_whitespace=True, comment=COMMENT, engine="python")
df.columns = clean_cols(df.columns)

# normalize y+
if "yplus" not in df.columns and "y_plus" in df.columns:
    df = df.rename(columns={"y_plus":"yplus"})

if "yplus" not in df.columns:
    raise SystemExit("No y+ column found (looked for 'yplus' or 'y_plus').")

# candidate signals to probe
signals = [c for c in ("urms","vrms","wrms") if c in df.columns]
if not signals:
    raise SystemExit("No urms/vrms/wrms columns found to probe.")

yplus = df["yplus"].to_numpy()
mask = np.isfinite(yplus) & (yplus > 0)
yplus = yplus[mask]

print(f"\nNT probe on {PATH.name}")
print(f"rows after mask: {yplus.size}")

def probe_one(series, name):
    s = series.to_numpy()[mask]
    # smooth a bit (optional)
    # s = pd.Series(s).rolling(5, center=True, min_periods=1).mean().to_numpy()

    # find peaks in log(y+) space by giving more weight where spacing is dense
    # we just detect peaks on the raw s and then sort by yplus
    peaks, _ = find_peaks(s, prominence=np.nanmax(s)*0.02)  # tweak if needed
    yp = yplus[peaks]
    sp = s[peaks]

    if yp.size < 3:
        print(f"\n[{name}] Not enough peaks to assess spacing ({yp.size}).")
        return

    # sort by y+
    idx = np.argsort(yp)
    yp = yp[idx]; sp = sp[idx]

    ratios = yp[1:] / yp[:-1]
    log_spacing = np.log(yp[1:]) - np.log(yp[:-1])

    print(f"\n[{name}] peaks: {yp.size}")
    print("first 8 peaks (y+):", np.array2string(yp[:8], precision=2))
    print("ratios (y+_{k+1}/y+_k):", np.array2string(ratios[:8], precision=3))
    print(f"mean ratio: {ratios.mean():.3f} | median ratio: {np.median(ratios):.3f}")
    print(f"mean log spacing: {log_spacing.mean():.3f} | std: {log_spacing.std():.3f}")

for c in signals:
    probe_one(df[c], c)
