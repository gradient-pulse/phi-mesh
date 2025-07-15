#!/usr/bin/env python3
"""
ratio_analyze.py – compute successive NT–NT-distance ratios
Usage:
    python ratio_analyze.py nt_times.txt --out ratios.csv
"""
import numpy as np, argparse, pandas as pd

def ratios(nt):
    dt = np.diff(nt)
    return dt[1:] / dt[:-1]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file", help="nt_times.txt produced by nt_detect.py")
    p.add_argument("--out", default="ratios.csv")
    args = p.parse_args()

    nts   = np.loadtxt(args.file)
    r     = ratios(nts)
    pd.Series(r, name="ratio").to_csv(args.out, index=False)
    print(f"[✔] Saved {len(r)} ratios to {args.out}")
