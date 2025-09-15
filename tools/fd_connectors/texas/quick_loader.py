# tools/fd_connectors/texas/quick_loader.py
# Robust Texas TXT loader/cleaner with bad-line logging.
# - Tolerates ragged rows
# - Auto-detects comment chars
# - Saves cleaned CSV + Parquet
# - Writes a sidecar .log describing any skipped ragged lines

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, Optional, Tuple, List

import numpy as np
import pandas as pd


# ----------------------------
# Utilities
# ----------------------------

COMMENT_CANDIDATES = ("*", "#", "%", "!", ";", "//")

def detect_comment_char(path: Path, sample_lines: int = 200) -> Optional[str]:
    """
    Heuristic comment marker detection:
      - If a line (ignoring leading spaces) starts with a known marker, we treat it as a comment line.
      - Returns the first matching marker, else None.
    """
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, raw in enumerate(f):
                if i >= sample_lines:
                    break
                s = raw.lstrip()
                for c in COMMENT_CANDIDATES:
                    if s.startswith(c):
                        return c
    except Exception:
        pass
    return None


def clean_cols(cols: Iterable[str]) -> List[str]:
    """
    Sanitize column names: lowercase, trim, convert + and /, remove non [a-z0-9_]
    """
    out = []
    for c in cols:
        c = (c or "").strip().lower()
        c = c.replace("+", "plus").replace("/", "_per_")
        c = re.sub(r"[^a-z0-9_]+", "_", c).strip("_")
        if not c:
            c = "col"
        out.append(c)
    # ensure uniqueness
    seen = {}
    uniq = []
    for c in out:
        if c not in seen:
            seen[c] = 0
            uniq.append(c)
        else:
            seen[c] += 1
            uniq.append(f"{c}_{seen[c]}")
    return uniq


def first_data_header_tokens(path: Path, comment_char: Optional[str]) -> Tuple[List[str], int]:
    """
    Returns (tokens_of_first_noncomment_nonempty_line, line_number)
    """
    sep_re = re.compile(r"\s+")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for ln, raw in enumerate(f, start=1):
            s = raw.strip()
            if not s:
                continue
            if comment_char and raw.lstrip().startswith(comment_char):
                continue
            # treat obvious decoration lines as comments
            if set(s) <= {"*", "-", "=", "~"}:
                continue
            tokens = [t for t in sep_re.split(s) if t]
            if tokens:
                return tokens, ln
    return [], -1


def find_ragged_lines(path: Path, comment_char: Optional[str], expected_cols: int,
                      start_line: int) -> List[int]:
    """
    Scan file and return line numbers where #fields != expected_cols
    Only scans subsequent lines after the header was found.
    """
    bad = []
    sep_re = re.compile(r"\s+")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for ln, raw in enumerate(f, start=1):
            if ln <= start_line:
                continue
            s = raw.strip()
            if not s:
                continue
            if comment_char and raw.lstrip().startswith(comment_char):
                continue
            if set(s) <= {"*", "-", "=", "~"}:
                continue
            fields = [t for t in sep_re.split(s) if t]
            if len(fields) != expected_cols:
                bad.append(ln)
    return bad


# ----------------------------
# Core loader
# ----------------------------

def load_table(path: Path, comment_char: Optional[str]) -> pd.DataFrame:
    """
    Robust whitespace-delimited parsing with ragged rows tolerated.
    - Uses sep=r"\s+" and engine='python'
    - on_bad_lines='skip' to avoid hard failures; skipped rows get logged separately
    """
    df = pd.read_csv(
        path,
        sep=r"\s+",
        comment=comment_char,
        engine="python",
        on_bad_lines="skip",
    )
    # Drop empty columns that can appear when pandas tries to align ragged lines
    df = df.dropna(axis=1, how="all")
    # Clean headers
    df.columns = clean_cols(df.columns)
    return df


def save_outputs(df: pd.DataFrame, src: Path) -> Tuple[Path, Path]:
    out_csv = src.with_name(src.stem + "_clean.csv")
    out_parq = src.with_name(src.stem + "_clean.parquet")
    df.to_csv(out_csv, index=False)
    # use fast parquet if available, otherwise pandas fallback
    try:
        df.to_parquet(out_parq, index=False)
    except Exception:
        # optional fallback to pyarrow-less CSV only
        out_parq = None
    return out_csv, out_parq


def write_log(src: Path, header_tokens: List[str], header_line: int,
              bad_lines: List[int], df: pd.DataFrame, comment_char: Optional[str]) -> Path:
    """
    Write a sidecar .log with parsing details (comment char, header, ragged lines count, preview).
    """
    log_path = src.with_name(src.stem + "_clean.log")
    with log_path.open("w", encoding="utf-8") as w:
        w.write(f"Source file : {src}\n")
        w.write(f"Comment     : {repr(comment_char)}\n")
        w.write(f"Header line : {header_line}\n")
        w.write(f"Header cols : {len(header_tokens)} -> {header_tokens}\n")
        w.write(f"Bad lines   : {len(bad_lines)}\n")
        if bad_lines:
            # avoid huge logs
            preview = bad_lines[:200]
            w.write("Bad line nos: " + ", ".join(map(str, preview)))
            if len(bad_lines) > len(preview):
                w.write(f", ... (+{len(bad_lines)-len(preview)} more)")
            w.write("\n")
        w.write("\n--- DataFrame summary (first 8 cols) ---\n")
        try:
            w.write(df.iloc[:, :8].describe().to_string())
        except Exception:
            w.write("(describe failed)\n")
        w.write("\n")
    return log_path


# ----------------------------
# CLI
# ----------------------------

def process_one(path: Path, verbose: bool = True) -> None:
    if verbose:
        print(f"Processing: {path}")

    comment = detect_comment_char(path)
    header_tokens, header_line = first_data_header_tokens(path, comment)

    # If we can't find a header, still try to read and let pandas decide
    expected_cols = len(header_tokens) if header_tokens else None
    bad_lines: List[int] = []
    if expected_cols and header_line > 0:
        bad_lines = find_ragged_lines(path, comment, expected_cols, header_line)

    # Load table with robust settings
    df = load_table(path, comment)

    # Save cleaned versions
    out_csv, out_parq = save_outputs(df, path)

    # Write log
    log_path = write_log(path, header_tokens, header_line, bad_lines, df, comment)

    # Console report
    print(f"✅ Loaded {path.name}")
    print("shape:", df.shape)
    print("columns:", list(df.columns))
    print("\n--- describe() ---")
    try:
        print(df.describe().T[["mean", "std", "min", "max"]].round(6))
    except Exception:
        print(df.describe().T.round(6))
    print(f"\n🧾 Log   : {log_path.name}")
    if out_parq:
        print(f"💾 Saved : {out_csv.name} and {out_parq.name}")
    else:
        print(f"💾 Saved : {out_csv.name} (Parquet unavailable)")

def main():
    ap = argparse.ArgumentParser(description="Clean Texas TXT datasets → CSV/Parquet with logs.")
    ap.add_argument("path", nargs="?", default=None,
                    help="A file or directory/glob (e.g. data/texas/*.txt). If omitted, defaults to data/texas/*.txt")
    ap.add_argument("--comment", dest="comment_char", default=None,
                    help="Force a comment character (overrides auto-detect).")
    args = ap.parse_args()

    # Resolve paths (file, folder, or glob)
    targets: List[Path] = []
    if args.path:
        p = Path(args.path)
        if p.is_dir():
            targets = sorted(p.glob("*.txt"))
        else:
            # Could be a file or a glob string
            if any(ch in str(p) for ch in "*?[]"):
                targets = sorted(Path().glob(str(p)))
            else:
                targets = [p]
    else:
        # default
        targets = sorted(Path("data/texas").glob("*.txt"))

    if not targets:
        print("No .txt files found.")
        return

    for t in targets:
        process_one(t)

if __name__ == "__main__":
    main()
