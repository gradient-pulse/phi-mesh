#!/usr/bin/env python3
# tools/agent_rhythm/cli.py
import argparse, json, sys, math
from pathlib import Path
from typing import List
from rhythm import ticks_from_message_times, ticks_from_token_log, rhythm_from_events

def parse_times_arg(s: str) -> List[float]:
    # supports: "0,3,6.1,9", or "0 3 6.1 9"
    raw = [p for p in s.replace(",", " ").split() if p]
    out = []
    for r in raw:
        try:
            out.append(float(r))
        except ValueError:
            pass
    return out

def load_csv_times(path: Path, col: str = "t") -> List[float]:
    # super-light CSV reader (expects a header row and a column named `t` by default)
    import csv
    t = []
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if col not in rdr.fieldnames:
            raise SystemExit(f"CSV missing column `{col}` (have: {rdr.fieldnames})")
        for row in rdr:
            try:
                v = float(row.get(col, ""))
                if math.isfinite(v):
                    t.append(v)
            except Exception:
                pass
    return t

def main():
    ap = argparse.ArgumentParser(description="Estimate NT rhythm metrics from event timestamps.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--times", help="Inline times, e.g. \"0, 3.1, 6.0, 9.2\"")
    src.add_argument("--csv", help="CSV file with a time column (default name `t`)")
    ap.add_argument("--col", default="t", help="CSV column containing times (default: t)")
    ap.add_argument("--json-out", default="-", help="Write metrics JSON to this path (default: stdout)")
    args = ap.parse_args()

    if args.times:
        ts = parse_times_arg(args.times)
    else:
        ts = load_csv_times(Path(args.csv), col=args.col)

    metrics = rhythm_from_events(ts)
    obj = {
        "period": metrics.period,
        "bpm": metrics.bpm,
        "confidence": metrics.confidence,
        "main_peak_freq": metrics.main_peak_freq,
        "peaks": metrics.peaks,
        "divergence_ratio": metrics.divergence_ratio,
        "reset_events": metrics.reset_events,
        "n_events": len(ts),
        "t_min": (min(ts) if ts else None),
        "t_max": (max(ts) if ts else None),
    }

    out = json.dumps(obj, indent=2)
    if args.json_out == "-" or args.json_out == "/dev/stdout":
        print(out)
    else:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(out, encoding="utf-8")
        print(f"wrote {args.json_out}")

if __name__ == "__main__":
    main()
