#!/usr/bin/env python3
"""
Harvest significant NT-rhythm findings from results/rgp_ns/**/summary.json
and emit minimal pulses under pulse/auto/.

Minimal pulse schema:
  title: str
  date: "YYYY-MM-DD"
  summary: str
  tags: [str, ...]
  papers: [str or {title,url}, ...]
  podcasts: [str, ...]

De-dupe across runs by hashing each summary.json content and tracking it in
meta/harvest_log.txt (committed to the repo).
"""

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import re
import sys
try:
    import yaml
except Exception:
    yaml = None  # We’ll guard & fail cleanly if missing

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = REPO_ROOT / "results" / "rgp_ns"
PULSE_ROOT = REPO_ROOT / "pulse" / "auto"
LOG_PATH = REPO_ROOT / "meta" / "harvest_log.txt"

REQUIRED_KEYS = ["dataset", "nt_test"]
NT_REQUIRED = ["p", "effect_size", "significant"]

DEFAULT_TAGS = [
    "RGP",
    "Navier_Stokes",
    "NT_rhythm",
    "rhythm-of-least-divergence",
]

def load_log():
    seen = set()
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                seen.add(line)
    return seen

def append_log(entry: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Could not parse JSON: {p} :: {e}")
        return None

def is_significant(obj: dict) -> bool:
    try:
        nt = obj.get("nt_test", {})
        return bool(nt.get("significant") is True)
    except Exception:
        return False

def extract_paper_urls(obj: dict):
    # If summaries someday include papers, collect them; else return [].
    papers = obj.get("papers") or []
    out = []
    for it in papers:
        if isinstance(it, str):
            out.append(it)
        elif isinstance(it, dict):
            url = it.get("url") or ""
            title = it.get("title") or ""
            if url:
                out.append({"title": title or url, "url": url})
    return out

def extract_podcast_urls(obj: dict):
    pods = obj.get("podcasts") or []
    out = []
    for it in pods:
        if isinstance(it, str):
            out.append(it)
    return out

def to_minimal_pulse(obj: dict) -> dict:
    dataset = str(obj.get("dataset", "")).strip() or "unknown_dataset"
    variant = str(obj.get("variant", "")).strip()
    nt = obj.get("nt_test", {}) or {}
    p = nt.get("p", None)
    es = nt.get("effect_size", None)

    # Prefer date in JSON if present; else file-based today (UTC)
    date_str = obj.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    title = f"Significant NT Rhythm — {dataset}" + (f" ({variant})" if variant else "")
    summary = (
        f"Automated detection found statistically significant NT rhythm in dataset `{dataset}`"
        + (f" (variant: {variant})" if variant else "")
        + (f". Effect size = {es}" if es is not None else "")
        + (f", p = {p}" if p is not None else "")
        + "."
    )

    pulse = {
        "title": title,
        "date": str(date_str),
        "summary": summary,
        "tags": list(DEFAULT_TAGS),
        "papers": extract_paper_urls(obj),
        "podcasts": extract_podcast_urls(obj),
    }
    return pulse

def write_yaml(path: Path, data: dict):
    if yaml is None:
        print("[ERROR] PyYAML not installed; cannot write YAML cleanly.")
        sys.exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=90,
            default_flow_style=False,
        )

def main():
    if not RESULTS_ROOT.exists():
        print("[INFO] No results/rgp_ns directory yet; nothing to harvest.")
        return 0

    seen = load_log()
    created = 0

    # Find all summary.json files
    summaries = list(RESULTS_ROOT.rglob("summary.json"))
    if not summaries:
        print("[INFO] No summary.json files found; nothing to harvest.")
        return 0

    # Process newest first
    summaries.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for s in summaries:
        raw = s.read_bytes()
        sig = sha256_bytes(raw)
        if sig in seen:
            continue

        obj = read_json(s)
        if not isinstance(obj, dict):
            append_log(sig)  # mark as seen even if malformed, to avoid loops
            continue

        # Quick schema guards
        if any(k not in obj for k in REQUIRED_KEYS):
            append_log(sig)
            continue

        nt = obj.get("nt_test", {})
        if any(k not in nt for k in NT_REQUIRED):
            append_log(sig)
            continue

        if not is_significant(obj):
            # Non-significant: mark as seen to avoid repeated scans
            append_log(sig)
            continue

        pulse = to_minimal_pulse(obj)

        # Name: UTC timestamp + dataset slug
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dataset_slug = safe_slug(str(obj.get("dataset", "dataset")))
        fname = f"{ts}_{dataset_slug}.yml"
        out_path = PULSE_ROOT / fname
        write_yaml(out_path, pulse)
        print(f"[NEW PULSE] {out_path.relative_to(REPO_ROOT)}")

        append_log(sig)
        created += 1

    print(f"[DONE] Created {created} new pulse(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
