#!/usr/bin/env python3
# tools/agent_rhythm/cli.py
import argparse, json, math, os, re, sys, datetime as dt
from pathlib import Path
from typing import List, Tuple

# Support running both as a module and as a script
try:
    from .rhythm import ticks_from_message_times, ticks_from_token_log, rhythm_from_events
except Exception:
    from rhythm import ticks_from_message_times, ticks_from_token_log, rhythm_from_events  # type: ignore

# ---------- small helpers -----------------------------------------------------

def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def _today_str() -> str:
    # UTC on GH runners
    return dt.date.today().isoformat()

def _next_batch(today: str, slug: str) -> int:
    root = Path("pulse/auto")
    root.mkdir(parents=True, exist_ok=True)
    paths = sorted(root.glob(f"{today}_{slug}_batch*.yml"))
    if not paths:
        return 1
    nums: List[int] = []
    rx = re.compile(r"_batch(\d+)\.yml$")
    for p in paths:
        m = rx.search(p.name)
        if m:
            try:
                nums.append(int(m.group(1)))
            except Exception:
                pass
    return (max(nums) + 1) if nums else 1

def _hint_from_metrics(m: dict) -> str:
    f = float(m.get("main_peak_freq") or 0.0)
    conf = float(m.get("confidence") or 0.0)
    bpm  = float(m.get("bpm") or 0.0)
    if math.isfinite(f) and f > 0:
        return f"fundamental≈{f:.4g} Hz, bpm≈{bpm:.1f}, confidence≈{conf:.2f}"
    return "no fundamental detected"

# ---------- io conveniences ---------------------------------------------------

def parse_times_arg(s: str) -> List[float]:
    raw = [p for p in (s or "").replace(",", " ").split() if p]
    out: List[float] = []
    for r in raw:
        try:
            v = float(r)
            if math.isfinite(v):
                out.append(v)
        except Exception:
            pass
    return out

def load_csv_times(path: Path, col: str = "t") -> List[float]:
    import csv
    t: List[float] = []
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames or col not in rdr.fieldnames:
            raise SystemExit(f"CSV missing column `{col}` (have: {rdr.fieldnames})")
        for row in rdr:
            try:
                v = float(row.get(col, ""))
                if math.isfinite(v):
                    t.append(v)
            except Exception:
                pass
    return t

# ---------- main --------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Estimate NT rhythm metrics from event timestamps and (optionally) write a pulse."
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--times", help="Inline times, e.g. \"0, 3.1, 6.0, 9.2\"")
    src.add_argument("--csv", help="CSV file with a time column (default name `t`)")

    ap.add_argument("--col", default="t", help="CSV column containing times (default: t)")

    # Outputs
    ap.add_argument("--json-out", default="", help="Write metrics JSON to this path. If omitted but --slug is given, a standard path is used.")
    ap.add_argument("--slug", default="", help="Dataset/job slug for filenames (enables auto metrics + pulse)")
    ap.add_argument("--title", default="NT Rhythm — Events", help="Pulse title (default: 'NT Rhythm — Events')")
    ap.add_argument("--no-pulse", action="store_true", help="Compute metrics only (do not write a pulse even if --slug is given)")

    args = ap.parse_args()

    # 1) Load timestamps
    if args.times:
        ts = parse_times_arg(args.times)
    else:
        ts = load_csv_times(Path(args.csv), col=args.col)

    # 2) Compute metrics
    m = rhythm_from_events(ts)
    obj = {
        "period": m.period,
        "bpm": m.bpm,
        "confidence": m.confidence,
        "main_peak_freq": m.main_peak_freq,
        "peaks": m.peaks,
        "divergence_ratio": m.divergence_ratio,
        "reset_events": m.reset_events,
        "n_events": len(ts),
        "t_min": (min(ts) if ts else None),
        "t_max": (max(ts) if ts else None),
    }

    # 3) Metrics output path
    metrics_path: Path | None = None
    if args.json_out:
        metrics_path = Path(args.json_out)
    elif args.slug:
        today = _today_str()
        slug = _slug(args.slug)
        batch = _next_batch(today, slug)  # reserve a batch number that pulse will also use
        metrics_path = Path("results/rgp_ns") / f"{today}_{slug}_batch{batch}.metrics.json"
    # else: stdout only

    # Write metrics (file or stdout)
    if metrics_path:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        print(f"wrote {metrics_path}")
    else:
        print(json.dumps(obj, indent=2))

    # 4) Optional pulse (mirrors JHTDB pulse schema)
    if args.slug and not args.no_pulse:
        today = _today_str()
        slug = _slug(args.slug)
        # if we already reserved a batch above, reuse it; else compute
        if metrics_path and metrics_path.name.startswith(f"{today}_{slug}_batch"):
            mo = re.search(r"_batch(\d+)\.metrics\.json$", metrics_path.name)
            batch = int(mo.group(1)) if mo else _next_batch(today, slug)
        else:
            batch = _next_batch(today, slug)

        analysis_path = metrics_path.as_posix() if metrics_path else "(stdout)"
        hint = _hint_from_metrics(obj)

        # Pulse YAML
        pulse_lines: List[str] = []
        pulse_lines.append(f"title: '{args.title}'")
        pulse_lines.append("summary: >-")
        pulse_lines.append(
            f"  NT rhythm from events — analysis: '{analysis_path}'. "
            f"hint: {hint}"
        )
        pulse_lines.append("tags:")
        for tag in ("nt_rhythm", "turbulence", "navier_stokes", "rgp"):
            pulse_lines.append(f"  - {tag}")
        pulse_lines.append("papers:")
        pulse_lines.append("  - https://doi.org/10.5281/zenodo.15830659")
        pulse_lines.append("podcasts:")
        pulse_lines.append("  - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a")
        pulse_text = "\n".join(pulse_lines) + "\n"

        outdir = Path("pulse/auto")
        outdir.mkdir(parents=True, exist_ok=True)
        pulse_path = outdir / f"{today}_{slug}_batch{batch}.yml"
        pulse_path.write_text(pulse_text, encoding="utf-8")
        print(f"wrote {pulse_path}")

if __name__ == "__main__":
    main()
