#!/usr/bin/env python3
"""
make_pulse.py — turn a metrics JSON into a single Pulse YAML + update “recent” JSONL.

Usage:
  --metrics  path/to/*.metrics.json   (required)
  --title    "NT Rhythm — FD Probe"   (required)
  --dataset  short dataset id/slug    (optional; fallback label)
  --tags     "a b c" or "a, b, c"     (optional)
  --outdir   pulse/auto               (default)
  --recent   results/rgp_ns/YYYY-MM-DD_fundamentals.jsonl  (optional)

Notes
- Pulse YAML is strict/minimal: title, summary, tags, papers, podcasts (no artifacts/details).
- The output filename uses a SHORT slug primarily derived from metrics.details.dataset (URL/path).
- The full dataset string is still mentioned in `summary:` for provenance.
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
    base = re.sub(r"\.(csv|json|txt|zip|xz|gz|bz2|tar)$", "", base, flags=re.I)
    return base

def _tidy_stem(stem: str) -> str:
    """
    Clean noisy stems, e.g.:
      'Testing_Now_rows'      -> 'testing_now'
      'sine_0p8hz_timeseries' -> 'sine_0p8hz'
    Removes trailing tokens like 'rows', 'timeseries', 'dataset', 'data'.
    """
    s = stem.strip()
    s = re.sub(r"_(rows|timeseries|dataset|data)$", "", s, flags=re.I)
    return s

def _short_slug_from_details_dataset(details: Dict[str, Any]) -> str:
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
    m = re.search(r"_batch(\d+)\.metrics\.json$", metrics_path)
    return f"batch{m.group(1)}" if m else "batch1"

# -------------------------- main --------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--dataset", default="")  # fallback label
    ap.add_argument("--tags", default="")
    ap.add_argument("--outdir", default="pulse/auto")
    ap.add_argument("--recent", default="")
    args = ap.parse_args()

    m = _read_json(args.metrics)

    period = m.get("period")
    f0 = m.get("main_peak_freq")
    if f0 is None and isinstance(m.get("peaks"), list) and m["peaks"]:
        try:
            f0 = float(m["peaks"][0][0])
        except Exception:
            f0 = None

    ladder, dominance = compute_ladder_and_dominance(m)
    status = classify(ladder, dominance)

    details = m.get("details") or {}
    ds_slug = _short_slug_from_details_dataset(details)
    if not ds_slug:
        ds_slug = _slug(args.dataset) or "dataset"

    batch_label = _infer_batch_label(args.metrics)

    tags = _as_list(args.tags)
    for core in ["nt_rhythm", "turbulence", "navier_stokes", "rgp"]:
        if core not in tags:
            tags.append(core)

    today = datetime.date.today().isoformat()
    safe_title = (args.title or "").replace("'", "’")

    yaml_lines: List[str] = []
    yaml_lines.append(f"title: '{safe_title}'")
    yaml_lines.append("summary: >-")
    yaml_lines.append(f"  Metrics: period={period!r}, f0={f0!r}, ladder={ladder}, dominance={dominance:.3g}.")
    yaml_lines.append(f"  Status: {status}. Dataset: {details.get('dataset', args.dataset) or args.dataset}.")
    yaml_lines.append("tags:")
    for t in tags:
        yaml_lines.append(f"  - {t}")
    yaml_lines.append("papers: []")
    yaml_lines.append("podcasts: []")

    _ensure_dir(args.outdir)
    out_name = f"{today}_{ds_slug}_{batch_label}.yml"
    out_path = os.path.join(args.outdir, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")
    print(f"Wrote Pulse → {out_path}")

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
