#!/usr/bin/env python3
"""
make_pulse.py — turn a metrics JSON into a single Pulse YAML + update “recent” JSONL.

Usage:
  --metrics  path/to/*.metrics.json   (required)
  --title    "NT Rhythm — FD Probe"   (required)
  --dataset  short dataset id/slug    (optional; used only as a fallback)
  --tags     "a b c" or "a, b, c"     (optional)
  --outdir   pulse/auto               (default)
  --recent   results/rgp_ns/YYYY-MM-DD_fundamentals.jsonl  (optional)

Notes
- Filenames now use a SHORT slug that is derived primarily from
  metrics.details.dataset (URL or path) instead of whatever was passed as --dataset.
- The full URL/path is still written inside the pulse under `details:`.
"""

from __future__ import annotations
import argparse, json, os, sys, datetime, re, hashlib
from typing import Any, Dict, List, Tuple

# ------------------------ helpers ------------------------

def _slug(s: str, maxlen: int = 40) -> str:
    """Conservative slug: lower, non-alnum->'_', collapse, trim, cap length."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("_")
    return s or "dataset"

def _basename_no_ext(path_or_url: str) -> str:
    """Best-effort filename stem from a URL or path (drops query/fragment)."""
    s = (path_or_url or "").split("#", 1)[0].split("?", 1)[0]
    base = os.path.basename(s.rstrip("/"))
    # drop extension(s)
    base = re.sub(r"\.(csv|json|txt|zip|xz|gz|bz2|tar)$", "", base, flags=re.I)
    return base

def _tidy_stem(stem: str) -> str:
    """
    Clean noisy NASA/test stems, e.g.:
      'Testing_Now_rows'      -> 'testing_now'
      'sine_0p8hz_timeseries' -> 'sine_0p8hz'
    Also trims trailing noise tokens like 'rows', 'timeseries', 'dataset', 'data'.
    """
    s = stem.strip()
    # remove very common trailing tokens
    s = re.sub(r"_(rows|timeseries|dataset|data)$", "", s, flags=re.I)
    # collapse leftover punctuation to underscores in the slug function
    return s

def _short_slug_from_details_dataset(details: Dict[str, Any]) -> str:
    """
    Prefer metrics.details.dataset when present (URL/path).
    Derive a short, human slug from its basename.
    """
    ds = (details or {}).get("dataset", "")
    if not ds:
        return ""
    stem = _basename_no_ext(str(ds))
    stem = _tidy_stem(stem)
    return _slug(stem)

def _hash_suffix(s: str, n: int = 6) -> str:
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()[:n]

def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _ensure_dir(p: str) -> None:
    if p:
        os.makedirs(p, exist_ok=True)

def _as_list(s: str) -> List[str]:
    if not s:
        return []
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return [x.strip() for x in s.split() if x.strip()]

def compute_ladder_and_dominance(metrics: Dict[str, Any]) -> Tuple[int, float]:
    peaks = metrics.get("peaks") or []
    ladder = 0
    dom = 1.0
    if isinstance(peaks, list) and peaks:
        ladder = len(peaks)
        try:
            p0 = float(peaks[0][1])
            p1 = float(peaks[1][1]) if len(peaks) > 1 else 0.0
            dom = (p0 / p1) if p1 > 0 else float("inf") if p0 > 0 else 1.0
        except Exception:
            dom = 1.0
    return ladder, dom

def classify(ladder: int, dominance: float) -> str:
    if ladder >= 3 and dominance >= 1.5:
        return "Strong"
    if ladder >= 2 and dominance >= 1.1:
        return "Suggestive"
    return "Inconclusive"

def _infer_batch_label(metrics_path: str) -> str:
    """
    Try to pull 'batchN' from the metrics filename.
    e.g., '..._batch7.metrics.json' -> 'batch7'
    Fallback: 'batch1'
    """
    m = re.search(r"_batch(\d+)\.metrics\.json$", metrics_path)
    return f"batch{m.group(1)}" if m else "batch1"

# -------------------------- main --------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--dataset", default="")          # fallback only
    ap.add_argument("--tags", default="")
    ap.add_argument("--outdir", default="pulse/auto")
    ap.add_argument("--recent", default="")
    args = ap.parse_args()

    # Read metrics JSON
    m = _read_json(args.metrics)

    # Defensive pulls
    period = m.get("period")
    f0 = m.get("main_peak_freq")
    if f0 is None and isinstance(m.get("peaks"), list) and m["peaks"]:
        try:
            f0 = float(m["peaks"][0][0])
        except Exception:
            f0 = None

    ladder, dominance = compute_ladder_and_dominance(m)
    status = classify(ladder, dominance)

    # Determine a SHORT dataset slug for filenames:
    # 1) derive from metrics.details.dataset URL/path
    # 2) else fallback to provided --dataset
    # 3) ensure short & stable; disambiguate with a tiny hash if still huge/empty
    details = m.get("details") or {}
    ds_slug = _short_slug_from_details_dataset(details)
    if not ds_slug:
        ds_slug = _slug(args.dataset)
    if not ds_slug:
        ds_slug = "dataset"
    # add tiny disambiguation when the metrics path contains unique info
    batch_label = _infer_batch_label(args.metrics)
    # keep slug short; if already very short, append batch; else rely on batch in filename separately
    if len(ds_slug) <= 30:
        ds_slug = f"{ds_slug}"

    # Assemble tags (ensure core set)
    tags = _as_list(args.tags)
    for core in ["nt_rhythm", "turbulence", "navier_stokes", "rgp"]:
        if core not in tags:
            tags.append(core)

    # Build pulse YAML text (minimal, robust)
    today = datetime.date.today().isoformat()

    yaml_lines = []
    yaml_lines.append(f"title: '{args.title}'")
    yaml_lines.append("summary: >-")
    yaml_lines.append(f"  Metrics: period={period!r}, f0={f0!r}, ladder={ladder}, dominance={dominance:.3g}.")
    yaml_lines.append(f"  Status: {status}. Dataset: {details.get('dataset', args.dataset) or args.dataset}.")
    yaml_lines.append("tags:")
    for t in tags:
        yaml_lines.append(f"  - {t}")
    yaml_lines.append("papers: []")
    yaml_lines.append("podcasts: []")
    yaml_lines.append("artifacts:")
    yaml_lines.append(f"  metrics_json: {args.metrics}")
    yaml_lines.append(f"  source: {m.get('source','unknown')}")

    if details:
        yaml_lines.append("details:")
        # Write deterministic order for common keys, then the rest
        ordered_keys = ["dataset", "var", "xyz", "window", "nasa_csv_env", "fallback"]
        written = set()
        for k in ordered_keys:
            if k in details:
                yaml_lines.append(f"  {k}: {details[k]}")
                written.add(k)
        for k, v in sorted(details.items()):
            if k not in written:
                yaml_lines.append(f"  {k}: {v}")

    # Write pulse YAML (short filename!)
    _ensure_dir(args.outdir)
    out_name = f"{today}_{ds_slug}_{batch_label}.yml"
    out_path = os.path.join(args.outdir, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")
    print(f"Wrote Pulse → {out_path}")

    # Append a fundamentals line (non-fatal)
    if args.recent:
        try:
            _ensure_dir(os.path.dirname(args.recent) or ".")
            line = {
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
                "dataset": details.get("dataset", args.dataset) or args.dataset,
                "dataset_slug": ds_slug,
                "status": status,
                "ladder": ladder,
                "dominance": dominance,
                "period": period,
                "f0": f0,
                "metrics": args.metrics,
                "pulse": out_path,
            }
            with open(args.recent, "a", encoding="utf-8") as f:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
            print(f"Appended fundamentals → {args.recent}")
        except Exception as e:
            print(f"[make_pulse] WARN: could not append to recent: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
