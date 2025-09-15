# tools/fd_connectors/texas/quick_loader.py
import argparse, io, re
from pathlib import Path
import pandas as pd
import numpy as np

COMMENT = "*"  # treat lines starting with this as comments

def clean_cols(cols):
    out = []
    for c in cols:
        c = (c or "").strip().lower()
        c = c.replace("+", "plus").replace("/", "_per_")
        c = re.sub(r"[^a-z0-9_]+", "_", c).strip("_")
        out.append(c)
    return out

def load_table(path: Path, comment_char: str = "*") -> pd.DataFrame:
    """
    Robust loader for Texas text tables:
      - skips comment/banner lines
      - detects header line
      - keeps only numeric-looking data rows
      - parses with whitespace separation
    """
    txt = path.read_text(encoding="utf-8", errors="ignore")
    # keep non-empty lines
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]

    # find header: first non-comment, non-banner line
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith(comment_char):
            continue
        # ignore pure banner lines of symbols
        if re.fullmatch(r"[*=\-_/\\ ]+", ln):
            continue
        header_idx = i
        break

    if header_idx is None:
        raise RuntimeError("Could not find a header line in the file.")

    header = re.sub(r"\s+", " ", lines[header_idx]).strip()
    cols = header.split()

    # keep only numeric-looking rows after header
    num_line = re.compile(r"^[\s+\-0-9.eE]+$")  # allow spaces, signs, digits, dot, e/E
    data_rows = []
    for ln in lines[header_idx + 1:]:
        if ln.startswith(comment_char):
            continue
        # stop if a second header sneaks in
        if any(tok in ln for tok in (" y+", " y/h", "  y ")):
            break
        if num_line.match(ln):
            data_rows.append(re.sub(r"\s+", " ", ln).strip())

    if not data_rows:
        raise RuntimeError("Found header but no numeric data rows — please check the file contents.")

    # build an in-memory "clean" table for pandas
    buf = io.StringIO()
    buf.write(" ".join(cols) + "\n")
    buf.write("\n".join(data_rows) + "\n")
    buf.seek(0)

    df = pd.read_csv(buf, sep=r"\s+", engine="python")
    df.columns = clean_cols(df.columns)

    # normalize yplus naming if present in any form
    if "yplus" in df.columns:
        pass
    elif "y_plus" in df.columns:
        df = df.rename(columns={"y_plus": "yplus"})
    elif "y" in df.columns and "y_per_h" in df.columns:
        # fallback if only y and y/h exist — keep y as proxy for plotting
        df = df.rename(columns={"y": "yplus"})
        print("⚠️  No explicit y+ found; using 'y' as placeholder for yplus.")

    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, help="Path to Texas data text file")
    ap.add_argument("--comment", default=COMMENT, help="Comment char (default '*')")
    args = ap.parse_args()

    df = load_table(args.path, comment_char=args.comment)

    print(f"\n✅ Loaded {args.path}")
    print("shape:", df.shape)
    print("columns:", list(df.columns))

    # basic numeric summary
    with pd.option_context("display.max_rows", 200, "display.width", 120):
        print("\n--- describe() ---")
        print(df.describe().T[["mean", "std", "min", "max"]].round(6))

    # save cleaned artifacts next to the raw file
    out_base = args.path.with_suffix("")  # drop .txt
    csv_path = out_base.parent / (out_base.name + "_clean.csv")
    pq_path  = out_base.parent / (out_base.name + "_clean.parquet")

    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(pq_path, index=False)
        print(f"\n💾 Saved: {csv_path.name} and {pq_path.name}")
    except Exception as e:
        print(f"\n💾 Saved: {csv_path.name}")
        print(f"⚠️  Parquet not saved ({e}); install pyarrow/fastparquet if desired.")

if __name__ == "__main__":
    main()
