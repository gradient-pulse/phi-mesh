# quick_loader.py
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---- settings ----
PATH = Path("Stat_Re17KM08.txt")   # <- change if needed
COMMENT = "*"                      # lines beginning with this are comments

def clean_cols(cols):
    out = []
    for c in cols:
        c = c.strip()
        c = c.lower()
        c = c.replace("+","plus").replace("/","_per_")
        c = re.sub(r"[^a-z0-9_]+","_", c).strip("_")
        out.append(c)
    return out

# ---- load ----
df = pd.read_csv(
    PATH,
    delim_whitespace=True,
    comment=COMMENT,
    engine="python"
)

# make column names safe
df.columns = clean_cols(df.columns)

print("\n✅ Loaded", PATH)
print("shape:", df.shape)
print("columns:", list(df.columns))

# try to detect y+ (many files use 'yplus' or 'y_plus')
yplus_candidates = [c for c in df.columns if c in ("yplus","y_plus","yplus_","y__","y")]
if "yplus" not in df.columns and "y_plus" in df.columns:
    df = df.rename(columns={"y_plus":"yplus"})
elif "yplus" not in df.columns and "y" in df.columns and "y_per_h" in df.columns:
    # if only y/h is present, make a placeholder (still useful for plotting)
    df = df.rename(columns={"y":"yplus"})
    print("⚠️  No explicit y+ found; using 'y' as placeholder.")

# basic numeric summary
print("\n--- describe() ---")
print(df.describe().T[["mean","std","min","max"]].round(6))

# ---- quick plots ----
plt.figure(figsize=(6,4))
if "yplus" in df.columns and "uplus" in df.columns:
    plt.semilogx(df["yplus"], df["uplus"], label="u+")
    plt.xlabel(r"$y^+$")
    plt.ylabel(r"$u^+$")
    plt.title("Mean velocity profile")
    plt.grid(True, which="both", alpha=.25)
    plt.legend()
    plt.tight_layout()
    plt.show()

rms_cols = [c for c in ("urms","vrms","wrms") if c in df.columns]
if "yplus" in df.columns and rms_cols:
    plt.figure(figsize=(6,4))
    for c in rms_cols:
        plt.semilogx(df["yplus"], df[c], label=c)
    plt.xlabel(r"$y^+$")
    plt.ylabel("RMS")
    plt.title("Velocity RMS vs $y^+$")
    plt.grid(True, which="both", alpha=.25)
    plt.legend()
    plt.tight_layout()
    plt.show()
