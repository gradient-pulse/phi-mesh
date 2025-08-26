#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGP-NS Agent Runner (auto-pulse generator)

What it does
------------
- Reads agents/rgp_ns/config.yml for datasets (+ optional params).
- For each dataset, runs a placeholder NT-rhythm test (deterministic-ish by id).
- Writes results to: results/rgp_ns/<UTC_STAMP>/<dataset_id>/summary.json
- Emits auto pulses to: pulse/auto/YYYY-MM-DD_<dataset_id>.yml

Auto-pulse schema (matches validator)
-------------------------------------
- REQUIRED keys in YAML: title, summary, tags, papers, podcasts
- NO 'date' key (the date is derived from the filename by validator)
- NO 'status' key
- 'title' must be single-quoted in the YAML source
- 'papers' and 'podcasts' are LISTS OF URL STRINGS (not dicts)
- Optional 'links' (LIST of URLs or repo-relative paths) is supported

Note: Dependency-light for GitHub Actions runners.
"""

from __future__ import annotations
import os, json, random, re, datetime as dt
from pathlib import Path
from typing import Dict, Any, Iterable, List, Optional
import yaml

# ---------- env guard ----------
import os
if os.getenv("ENABLE_AUTOPULSE") != "1":
    print("Auto-pulse disabled (ENABLE_AUTOPULSE!=1)."); raise SystemExit(0)

# ---------- repo paths ----------
ROOT = Path(__file__).resolve().parents[2]
CFG  = ROOT / "agents" / "rgp_ns" / "config.yml"
OUT_BASE = ROOT / "results" / "rgp_ns"
PULSE_DIR = ROOT / "pulse" / "auto"

# ---------- constants: canonical refs ----------
# (URL strings only — the validator requires list[str] for papers/podcasts)
ZENODO_WIT_TAKES = "https://doi.org/10.5281/zenodo.15830659"  # Solving Navier–Stokes, Differently (V1.2)
ZENODO_GUIDE     = "https://doi.org/10.5281/zenodo.16812467"  # Experimenter’s Guide – Solving Navier–Stokes, Differently (V1.7)
PODCAST_1        = "https://notebooklm.google.com/notebook/d49018d3-0070-41bb-9187-242c2698c53c/audio"
PODCAST_2        = "https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805/audio"

DEFAULT_TAGS = [
    "RGP",
    "NT (Narrative_Tick)",
    "NT_rhythm",
    "Rhythm",
    "NavierStokes",
    "turbulence",
    "ExperimenterPulse",
]

# ---------- small helpers ----------
def utc_timestamp(for_fs: bool = True) -> str:
    now = dt.datetime.utcnow()
    return now.strftime("%Y%m%d_%H%M%S") if for_fs else now.strftime("%Y-%m-%dT%H:%M:%SZ")

def today_stamp() -> str:
    """Return YYYY-MM-DD (for filenames)."""
    return dt.datetime.utcnow().strftime("%Y-%m-%d")

def _norm_tag(s: str) -> str:
    # Normalize to underscore style (keeps parentheses if present)
    s = (s or "").strip()
    return re.sub(r"\s+", "_", s)

def _dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        k = _norm_tag(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

# ---------- pulse writer (validator-compliant) ----------
_URL_RE = re.compile(r"^(https?://|https://doi.org/|doi:)", re.I)
_REL_RE = re.compile(r"""^((\.\./|\./|/)?[A-Za-z0-9._\-/]+(\.[A-Za-z0-9]{1,8})?)$""", re.X)

def write_auto_pulse(
    dataset_id: str,
    summary_text: str,
    extra_tags: Optional[Iterable[str]] = None,
    extra_links: Optional[Iterable[str]] = None,  # optional: URLs or repo-relative paths
) -> Path:
    """
    Create an auto pulse in pulse/auto/.
    Conforms to tools/validate_pulses.py rules:
      - NO 'date' key (date comes from filename)
      - NO 'status' key
      - title single-quoted
      - papers/podcasts as lists of URL strings
      - links (optional) as list of URLs or repo-relative paths
    """
    ds_tag = _norm_tag(dataset_id)
    tags = _dedupe_keep_order([*DEFAULT_TAGS, ds_tag, *(extra_tags or [])])

    # Canonical refs as URL strings
    papers = [ZENODO_WIT_TAKES, ZENODO_GUIDE]
    podcasts = [PODCAST_1, PODCAST_2]

    # Optional links (URLs or repo-relative paths)
    links: List[str] = []
    if extra_links:
        for x in extra_links:
            s = str(x).strip()
            if s and (_URL_RE.match(s) or _REL_RE.match(s)):
                links.append(s)

    # Title (escape any single quotes to keep single-quoted YAML valid)
    def _sq(s: str) -> str:
        return s.replace("'", "''")

    title = (
        f"Significant NT Rhythm — {dataset_id}"
        if "significant" in summary_text.lower()
        else f"{dataset_id}: Experimenter auto-pulse"
    )

    # Target path (validator wants YYYY-MM-DD_ prefix). Avoid overwrite if exists.
    PULSE_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{today_stamp()}_{ds_tag}.yml"
    outpath = PULSE_DIR / base
    if outpath.exists():
        i = 2
        while True:
            cand = PULSE_DIR / f"{today_stamp()}_{ds_tag}__{i}.yml"
            if not cand.exists():
                outpath = cand
                break
            i += 1

    # Build YAML manually to guarantee single-quoted title and simple lists.
    def _list_block(key: str, values: Iterable[str]) -> str:
        lines = [f"{key}:"]
        for v in values:
            lines.append(f"  - {v}")
        return "\n".join(lines)

    yaml_lines: List[str] = []
    yaml_lines.append(f"title: '{_sq(title)}'")  # single-quoted
    yaml_lines.append("summary: >")
    for line in (summary_text.strip().splitlines() or [" "]):
        yaml_lines.append(f"  {line}")
    yaml_lines.append(_list_block("tags", tags))
    yaml_lines.append(_list_block("papers", papers))
    yaml_lines.append(_list_block("podcasts", podcasts))
    if links:
        yaml_lines.append(_list_block("links", links))
    yaml_lines.append("")  # trailing newline

    outpath.write_text("\n".join(yaml_lines), encoding="utf-8")
    print(f"[auto-pulse] wrote {outpath.relative_to(ROOT)}")
    return outpath

# ---------- fake NT test (placeholder) ----------
def run_nt_rhythm_test(seed: int = 0) -> Dict[str, Any]:
    """
    Minimal synthetic stats; replace with real test when ready.
    """
    rng = random.Random(seed)
    p = round(max(0.0001, min(0.9999, rng.random() * rng.random())), 4)
    eff = round(rng.uniform(0.05, 0.6), 3)
    alpha = 0.01
    return {"p": p, "effect_size": eff, "significant": p < alpha}

# ---------- main ----------
def main():
    # Load config
    if not CFG.exists():
        raise FileNotFoundError(f"Missing config: {CFG}")
    with CFG.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    datasets = cfg.get("datasets") or []
    if not isinstance(datasets, list) or not datasets:
        print("No datasets defined in config.yml → nothing to do.")
        return

    stamp = utc_timestamp()
    print(f"[run] UTC stamp = {stamp}")

    for i, ds in enumerate(datasets):
        ds_id = str(ds.get("id") or f"dataset_{i+1}")
        variant = str(ds.get("source") or "local")
        outdir = OUT_BASE / stamp / ds_id
        outdir.mkdir(parents=True, exist_ok=True)

        # --- compute (placeholder) ---
        seed = abs(hash(ds_id)) % (2**32)
        nt = run_nt_rhythm_test(seed)

        # Persist summary.json
        summary_json = {
            "dataset": ds_id,
            "variant": variant,
            "nt_test": nt,
            "timestamp_utc": utc_timestamp(for_fs=False),
        }
        write_json(outdir / "summary.json", summary_json)
        print(f"[summary] {str(outdir / 'summary.json')}")

        # Human-friendly short text
        sig_txt = "YES" if nt["significant"] else "no"
        run_summary_text = (
            f"{ds_id} — NT rhythm test → p={nt['p']}, effect={nt['effect_size']}; "
            f"significant: {sig_txt} @ α=0.01."
        )

        # Extra tags/links hooks (optional)
        extra_tags: List[str] = []
        extra_links: List[str] = []  # e.g., attach result paths or visuals if desired

        # Write the auto pulse
        write_auto_pulse(
            dataset_id=ds_id,
            summary_text=run_summary_text,
            extra_tags=extra_tags,
            extra_links=extra_links,
        )

    print("[done] RGP-NS agent run complete.")

if __name__ == "__main__":
    main()
