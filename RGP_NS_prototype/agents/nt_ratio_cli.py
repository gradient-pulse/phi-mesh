#!/usr/bin/env python3
"""
Compute successive-distance ratios from nt_times.txt files in batch.

Usage:
    python agents/nt_ratio_cli.py results/run1/nt_times.txt \
           --outdir results/run1 --sigma 1.5
"""
import argparse, numpy as np, pathlib as pl
from ratio_analyze import ratios    # already in agents

def compute(infile, outdir, sigma):
    nts = np.loadtxt(infile)
    rs  = ratios(nts)                # your helper
    outfile = pl.Path(outdir, pl.Path(infile).stem + "_ratios.txt")
    np.savetxt(outfile, rs)
    print(f"[✓] {infile} → {outfile} ({len(rs)} ratios; σ={sigma})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+", help="nt_times.txt files")
    p.add_argument("--outdir", default=".", help="Output directory")
    p.add_argument("--sigma", type=float, default=1.5,
                   help="Threshold multiplier (for log)")
    args = p.parse_args()

    pl.Path(args.outdir).mkdir(parents=True, exist_ok=True)
    for f in args.files:
        compute(f, args.outdir, args.sigma)
