# tools/fd_connectors/texas/quick_loader.py
import re
import argparse
import pandas as pd
from pathlib import Path

def clean_cols(cols):
    out = []
    for c in cols:
        c = (c or "").strip().lower()
        c = c.replace("+", "plus").replace("/", "_per_")
        c = re.sub(r"[^a-z0-9_]+", "_", c).strip("_")
        out.append(c or "col")
    return out

def detect_comment_char(path: Path, default="*"):
    """
    Peek a few lines: if a line starts with a likely comment char (#, %, *),
    return it. Otherwise fall back to the default.
    """
    likely = {"#", "%", "*", "!"}
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                s = line.strip()
                if s and s[0] in likely:
                    return s[0]
    except Exception:
        pass
    return default

def load_table(path: Path, comment_char=None):
    if comment_char is None:
        comment_char = detect_comment_char(path)

    # Pandas warning: use sep=r"\s+" instead of delim_whitespace
    df = pd.read_csv(
        path,
        sep=r"\s+",
        comment=comment_char,
        engine="python"
    )

    # normalize/sanitize column names
    df.columns = clean_cols(list(df.columns))

    # Convenience: unify common y+/u+ names when present
    # (non-fatal; only helps quick plots/probes later)
    alias_map = {
        "y_plus": "yplus",
        "y__": "yplus",
        "y": "y",                # leave 'y' literal, but mapped below if useful
        "u_plus": "uplus",
    }
    for a, b in alias_map.items():
        if a in df.columns and b not in df.columns:
            df = df.rename(columns={a: b})

    # If we only have 'y' and 'y_per_h', keep them as-is; we won't force yplus.
    return df

def save_clean(df, src_path: Path):
    stem = src_path.with_suffix("").name + "_clean"
    out_csv = src_path.parent / f"{stem}.csv"
    out_parq = src_path.parent / f"{stem}.parquet"

    df.to_csv(out_csv, index=False)
    try:
        import pyarrow  # noqa: F401
        df.to_parquet(out_parq, index=False)
        wrote_parquet = True
    except Exception:
        wrote_parquet = False

    return out_csv, (out_parq if wrote_parquet else None)

def main():
    ap = argparse.ArgumentParser(description="Quick-load & clean Texas TDR text tables.")
    ap.add_argument("path", type=str, help="Path to the .txt dataset (e.g., data/texas/Foo.txt)")
    ap.add_argument("--comment", type=str, default=None, help="Comment char to ignore (auto-detect if omitted)")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    df = load_table(p, comment_char=args.comment)

    print(f"\n✅ Loaded {p}")
    print("shape:", df.shape)
    print("columns:", list(df.columns))

    # small numeric peek
    try:
        desc = df.describe().T[["mean","std","min","max"]].round(6)
        print("\n--- describe() ---")
        print(desc)
    except Exception:
        pass

    out_csv, out_parq = save_clean(df, p)
    if out_parq:
        print(f"\n💾 Saved: {out_csv.name} and {out_parq.name}")
    else:
        print(f"\n💾 Saved: {out_csv.name} (pyarrow not installed; parquet skipped)")

if __name__ == "__main__":
    main()
