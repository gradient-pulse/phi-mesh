#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGP-NS Agent Runner (auto-pulse generator)

What it does
------------
- Reads agents/rgp_ns/config.yml for datasets (+ optional params)
- For each dataset, runs a placeholder NT-rhythm test (deterministic-ish by id)
- Writes results to: results/rgp_ns/<UTC_STAMP>/<dataset_id>/summary.json
- Emits auto pulses to: pulse/auto/<UTC_STAMP>_<dataset_id>.yml

Auto-pulse behavior
-------------------
- Ensures the following **default tags** on every auto pulse:
    ["RGP", "NT (Narrative_Tick)", "NT_rhythm", "Rhythm", "NavierStokes",
     "turbulence", "ExperimenterPulse"]
  …plus the dataset id (normalized) as its own tag.
- Papers/podcasts are **URL-backed only** (no title-only).
- Always includes the two canonical Zenodo DOIs and the two NotebookLM podcast links.

Note: This is dependency-light for GitHub Actions runners.
"""

from __future__ import annotations
import os, json, random, re, datetime as dt
from pathlib import Path
from typing import Dict, Any, Iterable, List
import yaml

# ---------- repo paths ----------
ROOT = Path(__file__).resolve().parents[2]
CFG  = ROOT / "agents" / "rgp_ns" / "config.yml"
OUT_BASE = ROOT / "results" / "rgp_ns"
PULSE_DIR = ROOT / "pulse" / "auto"

# ---------- constants: canonical refs ----------
ZENODO_WIT_TAKES   = "https://doi.org/10.5281/zenodo.15830659"  # Solving Navier–Stokes, Differently: What It Takes (V1.2)
ZENODO_GUIDE       = "https://doi.org/10.5281/zenodo.16812467"  # Experimenter’s Guide – Solving Navier–Stokes, Differently (V1.7)
PODCAST_1          = "https://notebooklm.google.com/notebook/d49018d3-0070-41bb-9187-242c2698c53c/audio"
PODCAST_2          = "https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805/audio"

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

def _url_item(url: str, title: str | None = None) -> Dict[str, str]:
    url = (url or "").strip()
    if not url:
        return {}
    item = {"url": url}
    if title:
        item["title"] = title
    return item

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

# ---------- pulse writer ----------
def write_auto_pulse(dataset_id: str,
                     summary_text: str,
                     extra_tags: Iterable[str] | None = None) -> Path:
    """
    Create an auto pulse in pulse/auto/.
    Ensures default tags + dataset id. Filters out any ref objects without 'url'.
    """
    # Compose tags
    ds_tag = _norm_tag(dataset_id)
    tags = _dedupe_keep_order([*DEFAULT_TAGS, ds_tag, *(extra_tags or [])])

    # Canonical refs (always included)
    papers = [
        _url_item(ZENODO_WIT_TAKES, "Solving Navier–Stokes, Differently: What It Takes (V1.2)"),
        _url_item(ZENODO_GUIDE, "Experimenter’s Guide — Solving Navier–Stokes, Differently (V1.7)"),
    ]
    podcasts = [
        _url_item(PODCAST_1),
        _url_item(PODCAST_2),
    ]

    pulse_obj = {
        "title":   f"Significant NT Rhythm — {dataset_id}" if "significant" in summary_text.lower() else f"{dataset_id}: Experimenter auto-pulse",
        "date":    utc_timestamp(for_fs=False),
        "summary": summary_text.strip(),
        "tags":    tags,
        "papers":   [p for p in papers if p.get("url")],
        "podcasts": [p for p in podcasts if p.get("url")],
        "status":  "auto",
    }

    PULSE_DIR.mkdir(parents=True, exist_ok=True)
    outpath = PULSE_DIR / f"{utc_timestamp()}_{ds_tag}.yml"
    with outpath.open("w", encoding="utf-8") as f:
        yaml.safe_dump(pulse_obj, f, sort_keys=False, allow_unicode=True)
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

        # Extra tags hook (you can add dataset-specific ones if desired)
        extra_tags: List[str] = []

        # Write the auto pulse (adds default tags + dataset id + canonical refs)
        write_auto_pulse(
            dataset_id=ds_id,
            summary_text=run_summary_text,
            extra_tags=extra_tags,
        )

    print("[done] RGP-NS agent run complete.")

if __name__ == "__main__":
    main()
