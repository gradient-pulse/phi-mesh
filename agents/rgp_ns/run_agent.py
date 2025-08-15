#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGP-NS Agent Runner (lightweight)
- Reads agents/rgp_ns/config.yml for datasets + params
- Writes per-run summaries: results/rgp_ns/<UTC_TIMESTAMP>/<dataset_id>/summary.json
- Emits auto pulses under pulse/auto/ with REQUIRED canonical tags:
    [ "RGP", "NT (Narrative_Tick)", "Rhythm", "NavierStokes", "turbulence", "ExperimenterPulse" ]
  (plus a dataset-id tag, normalized, so you can filter by dataset)

Notes
- Only URL-backed resources are written (no title-only entries)
- Dependency-light for GH Actions runners
"""

from __future__ import annotations
import os, json, random, re, datetime as dt
from pathlib import Path
from typing import Dict, Any, Iterable, List
import yaml

# ---------- paths ----------
ROOT = Path(__file__).resolve().parents[2]
CFG  = ROOT / "agents" / "rgp_ns" / "config.yml"
OUT_BASE = ROOT / "results" / "rgp_ns"
PULSE_DIR = ROOT / "pulse" / "auto"

# ---------- helpers ----------
CANONICAL_TAGS = [
    "RGP",
    "NT (Narrative_Tick)",
    "Rhythm",
    "NavierStokes",
    "turbulence",
    "ExperimenterPulse",
]

def utc_timestamp(fs: bool = True) -> str:
    now = dt.datetime.utcnow()
    return now.strftime("%Y%m%d_%H%M%S") if fs else now.strftime("%Y-%m-%dT%H:%M:%SZ")

def _norm_tag(s: str) -> str:
    return re.sub(r"[\s\-]+", "_", (s or "").strip())

def _stable_tag_union(*groups: Iterable[str]) -> List[str]:
    seen, out = set(), []
    for g in groups:
        for t in (g or []):
            if not t: 
                continue
            key = _norm_tag(t).casefold()
            if key not in seen:
                seen.add(key)
                out.append(t)
    return out

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def _url_item(url: str, title: str | None = None) -> Dict[str, str]:
    url = (url or "").strip()
    if not url: return {}
    item = {"url": url}
    if title: item["title"] = title
    return item

# ---------- simple placeholder stat ----------
def run_nt_rhythm_test(seed: int = 0) -> Dict[str, Any]:
    rng = random.Random(seed)
    p = round(max(0.0001, min(0.9999, rng.random() * rng.random())), 4)
    eff = round(rng.uniform(0.05, 0.6), 3)
    alpha = 0.01
    return {"p": p, "effect_size": eff, "significant": p < alpha}

# ---------- pulse writer ----------
def write_auto_pulse(dataset_id: str,
                     summary_text: str,
                     extra_tags: Iterable[str] | None = None,
                     papers: Iterable[Dict[str, str]] | None = None,
                     podcasts: Iterable[Dict[str, str]] | None = None) -> Path:
    """
    Create an auto pulse YML in pulse/auto/.
    - Always includes the six canonical tags (exact forms requested)
    - Adds dataset tag (normalized dataset_id) for filtering
    - Filters out any resource item missing 'url'
    """
    dataset_tag = _norm_tag(dataset_id)
    tags = _stable_tag_union(CANONICAL_TAGS, [dataset_tag], extra_tags or [])

    papers   = [d for d in (papers or [])   if isinstance(d, dict) and d.get("url")]
    podcasts = [d for d in (podcasts or []) if isinstance(d, dict) and d.get("url")]

    pulse = {
        "title":   f"{dataset_id}: Experimenter auto-pulse",
        "date":    dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": (summary_text or "").strip(),
        "tags":    tags,
        "papers":   papers,
        "podcasts": podcasts,
        "status":  "auto",
    }

    PULSE_DIR.mkdir(parents=True, exist_ok=True)
    outpath = PULSE_DIR / f"{utc_timestamp()}_{dataset_tag}.yml"
    with outpath.open("w", encoding="utf-8") as f:
        yaml.safe_dump(pulse, f, sort_keys=False, allow_unicode=True)
    print(f"[auto-pulse] wrote {outpath.relative_to(ROOT)}")
    return outpath

# ---------- main ----------
def main():
    if not CFG.exists():
        raise FileNotFoundError(f"Missing config: {CFG}")
    with CFG.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    datasets = cfg.get("datasets") or []
    if not isinstance(datasets, list) or not datasets:
        print("No datasets defined in config.yml → nothing to do.")
        return

    # Optional secret (for future papers attachment, if desired)
    zenodo_doi = (os.environ.get("ZENODO_DOI") or "").strip()

    run_stamp = utc_timestamp()
    print(f"[run] UTC stamp = {run_stamp}")

    for i, ds in enumerate(datasets):
        ds_id   = str(ds.get("id") or f"dataset_{i+1}")
        source  = str(ds.get("source") or "local")

        # Fake stat for now
        seed = abs(hash(ds_id)) % (2**32)
        nt = run_nt_rhythm_test(seed)

        # Write summary.json
        outdir = OUT_BASE / run_stamp / ds_id
        outdir.mkdir(parents=True, exist_ok=True)
        summary = {
            "dataset": ds_id,
            "variant": source,
            "nt_test": nt,
            "timestamp_utc": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        write_json(outdir / "summary.json", summary)
        print(f"[summary] {str(outdir / 'summary.json')}")

        # Human-friendly summary text
        sig = "YES" if nt["significant"] else "no"
        text = f"{ds_id} — NT rhythm test → p={nt['p']}, effect={nt['effect_size']}; significant: {sig} @ α=0.01."

        # Minimal resources (optional; URL-only policy)
        papers = []
        if zenodo_doi:
            papers.append(_url_item(f"https://doi.org/{zenodo_doi}",
                                    "Experimenter’s Guide — Solving Navier–Stokes, Differently"))

        # Emit pulse
        write_auto_pulse(
            dataset_id=ds_id,
            summary_text=text,
            extra_tags=[],       # you can add per-dataset tags here if needed
            papers=papers,
            podcasts=[],
        )

    print("[done] RGP-NS agent run complete.")

if __name__ == "__main__":
    main()
