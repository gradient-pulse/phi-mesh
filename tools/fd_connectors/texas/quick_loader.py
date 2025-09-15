# tools/fd_connectors/texas/quick_loader.py
"""
Quick loader for Texas Data Repository ASCII tables.

Usage:
  python tools/fd_connectors/texas/quick_loader.py data/texas/Stat_Re17KM08.txt --show

Outputs:
  - <same-dir>/<basename>_clean.csv
  - <same-dir>/<basename>_clean.parquet
  - prints a small numeric summary
  - optional quick-look plots (use --show)
"""
import re
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def clean_cols(cols):
    out = []
    for c in cols:
        c = str(c).strip().lower()
        c = c.replace("+", "plus").replace("/", "_per_")
        c = re.sub(r"[^a-z0-9_]+", "_", c).strip("_")
        out.append(c)
    return out


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    # Dataverse previews sometimes sneak in stray non-numeric tokens.
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def detect_and_standardize_yplus(df: pd.DataFrame) -> pd.DataFrame:
    # common aliases we’ve seen
    candidates = [
        "yplus", "y_plus", "y__",
        "y", "y_h", "y_per_h", "y_over_h"
    ]
    have = {c for c in df.columns}
    hit = next((c for c in candidates if c in have), None)

    if hit is None:
        print("⚠️  No y+ / y/h column detected; proceeding without y-axis standardization.")
        return df

    # Normalize name to `yplus` for plotting if it looks like y+
    if hit in ("yplus", "y_plus", "y__"):
        if "yplus" not in df.columns:
            df = df.rename(columns={hit: "yplus"})
    elif hit in ("y",):
        # Often the first numeric column is 'y/h' with separate exact header 'y/h'
        # If the cleaned col became 'y', leave as is but also offer an alias
        df = df.rename(columns={"y": "y"})
    elif hit in ("y_h", "y_per_h", "y_over_h"):
        # Keep as is; some files include both y/h and y+
        pass

    return df


def guess_uplus_name(df: pd.DataFrame) -> str | None:
    for name in ("uplus", "u_plus", "u__"):
        if name in df.columns:
            return name
    # Sometimes 'u+' became 'uplus' via cleaning; already covered above.
    return None


def load_table(path: Path, comment_char: str = "*") -> pd.DataFrame:
    # Dataverse ASCII frequently is whitespace-delimited with a few banner lines
    df = pd.read_csv(
        path,
        delim_whitespace=True,
        comment=comment_char,
        engine="python",
        na_values=["nan", "NaN", "NA", "N/A", ""],
    )
    df.columns = clean_cols(df.columns)
    df = coerce_numeric(df)
    df = detect_and_standardize_yplus(df)
    return df


def summarize(df: pd.DataFrame):
    print("\n--- describe() ---")
    with pd.option_context("display.max_rows", 200, "display.width", 120):
        print(df.describe().T[["mean", "std", "min", "max"]].round(6))


def quick_plots(df: pd.DataFrame, title: str = ""):
    y_name = "yplus" if "yplus" in df.columns else None
    uplus_name = guess_uplus_name(df)

    # Mean velocity
    if y_name and uplus_name:
        plt.figure(figsize=(6, 4))
        plt.semilogx(df[y_name], df[uplus_name], label=r"$u^+$")
        plt.xlabel(r"$y^+$")
        plt.ylabel(r"$u^+$")
        plt.title(title or "Mean velocity profile")
        plt.grid(True, which="both", alpha=0.25)
        plt.legend()
        plt.tight_layout()

    # RMS curves
    rms_cols = [c for c in ("urms", "vrms", "wrms") if c in df.columns]
    if y_name and rms_cols:
        plt.figure(figsize=(6, 4))
        for c in rms_cols:
            plt.semilogx(df[y_name], df[c], label=c)
        plt.xlabel(r"$y^+$")
        plt.ylabel("RMS")
        plt.title("Velocity RMS vs $y^+$")
        plt.grid(True, which="both", alpha=0.25)
        plt.legend()
        plt.tight_layout()

    if plt.get_fignums():
        plt.show()


def save_outputs(df: pd.DataFrame, src: Path):
    out_csv = src.with_suffix("").with_name(src.stem + "_clean.csv")
    out_parq = src.with_suffix("").with_name(src.stem + "_clean.parquet")
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parq, index=False)
        print(f"💾 Saved: {out_csv.name} and {out_parq.name}")
    except Exception as e:
        print(f"💾 Saved: {out_csv.name} (Parquet skipped: {e})")


def main():
    ap = argparse.ArgumentParser(description="Quick loader for Texas ASCII tables")
    ap.add_argument("path", type=Path, help="Path to the .txt file (e.g., data/texas/Stat_Re17KM08.txt)")
    ap.add_argument("--show", action="store_true", help="Show quick-look plots")
    ap.add_argument("--comment", default="*", help="Comment banner character (default: *)")
    args = ap.parse_args()

    if not args.path.exists():
        raise SystemExit(f"File not found: {args.path}")

    df = load_table(args.path, comment_char=args.comment)

    print(f"\n✅ Loaded {args.path}")
    print("shape:", df.shape)
    print("columns:", list(df.columns))

    summarize(df)
    save_outputs(df, args.path)

    if args.show:
        title = f"{args.path.stem} — Mean/RMS"
        quick_plots(df, title=title)


if __name__ == "__main__":
    main()
