#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGP-NS Agent Runner (lightweight demo)
- Reads agents/rgp_ns/config.yml for datasets + params
- Produces per-run summaries under results/rgp_ns/<UTC_TIMESTAMP>/<dataset_id>/
- Emits auto pulses into pulse/auto/ with proper tags:
    - always includes ["RGP", "ExperimenterPulse"] plus dataset-related tags
- Papers/podcasts entries are URL-backed only (no title-only items)

This file is intentionally dependency-light and file-system friendly so it runs well
inside GitHub Actions runners.
"""

from __future__ import annotations
import os, json, math, random, re, datetime as dt
from pathlib import Path
from typing import Dict, Any, Iterable, List
import yaml

# ---------- paths ----------
ROOT = Path(__file__).resolve().parents[2]  # repo root
CFG  = ROOT / "agents" / "rgp_ns" / "config.yml"
OUT_BASE = ROOT / "results" / "rgp_ns"
PULSE_DIR = ROOT / "pulse" / "auto"

# ---------- small helpers ----------
def utc_timestamp(for_fs: bool = True) -> str:
    now = dt.datetime.utcnow()
    return now.strftime("%Y%m%d_%H%M%S") if for_fs else now.strftime("%Y-%m-%dT%H:%M:%SZ")

def _norm_tag(s: str) -> str:
    return re.sub(r"[\s\-]+", "_", (s or "").strip())

def _ensure_experimenter_pulse(tags: Iterable[str]) -> List[str]:
    base = [t for t in (tags or []) if t]
    lower = { _norm_tag(t).casefold() for t in base }
    if "experimenterpulse" not in lower:
        base.append("ExperimenterPulse")
    if "rgp" not in lower:
        base.append("RGP")
    # stable-ish order
    seen, out = set(), []
    for t in base:
        key = _norm_tag(t)
        if key not in seen:
            seen.add(key)
            out.append(t)
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
                     summary: str,
                     extra_tags: Iterable[str] | None = None,
                     papers: Iterable[Dict[str, str]] | None = None,
                     podcasts: Iterable[Dict[str, str]] | None = None) -> Path:
    """
    Create an auto pulse YML in pulse/auto/.
    Ensures tags contain 'ExperimenterPulse' and 'RGP'.
    Filters out any paper/podcast items without a 'url'.
    """
    extra_tags   = list(extra_tags or [])
    papers       = [it for it in (papers or []) if isinstance(it, dict) and it.get("url")]
    podcasts     = [it for it in (podcasts or []) if isinstance(it, dict) and it.get("url")]

    ts_iso = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    pulse = {
        "title":   f"{dataset_id}: Experimenter auto-pulse",
        "date":    ts_iso,
        "summary": (summary or "").strip(),
        "tags":    _ensure_experimenter_pulse(["RGP"] + extra_tags),
        "papers":   papers,
        "podcasts": podcasts,
        "status":  "auto",
    }

    PULSE_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{utc_timestamp()}_{_norm_tag(dataset_id)}.yml"
    outpath = PULSE_DIR / fname
    with outpath.open("w", encoding="utf-8") as f:
        yaml.safe_dump(pulse, f, sort_keys=False, allow_unicode=True)
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

    # Optional secrets
    zenodo_doi = (os.environ.get("ZENODO_DOI") or "").strip()  # e.g., 10.5281/zenodo.15830659

    # One timestamp folder per agent run
    run_stamp = utc_timestamp()
    print(f"[run] UTC stamp = {run_stamp}")

    for i, ds in enumerate(datasets):
        ds_id = str(ds.get("id") or f"dataset_{i+1}")
        variant = str(ds.get("source") or "local")
        outdir = OUT_BASE / run_stamp / ds_id
        outdir.mkdir(parents=True, exist_ok=True)

        # --- compute (placeholder) ---
        # Here you can branch by 'source' (e.g., 'jhtdb' vs 'local') and load real arrays.
        # For now we synthesize a deterministic-ish test per dataset id.
        seed = abs(hash(ds_id)) % (2**32)
        nt = run_nt_rhythm_test(seed)

        summary = {
            "dataset": ds_id,
            "variant": variant,
            "nt_test": nt,
            "timestamp_utc": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        write_json(outdir / "summary.json", summary)
        print(f"[summary] {str(outdir / 'summary.json')}")

        # --- pulse summary text (concise, human-friendly) ---
        sig = "YES" if nt["significant"] else "no"
        run_summary_text = (
            f"{ds_id} — NT rhythm test → p={nt['p']}, effect={nt['effect_size']}; "
            f"significant: {sig} @ α=0.01."
        )

        # --- extra tags: basic heuristics ---
        extra_tags = [ds_id]  # let the dataset id become a tag (alias map will normalize)
        if variant.lower() in ("jhtdb", "navier-stokes", "ns", "ns_solution"):
            extra_tags += ["NavierStokes", "NT_rhythm"]
        else:
            extra_tags += ["NT_rhythm"]

        # --- papers/podcasts (URL-backed only) ---
        papers = []
        if zenodo_doi:
            papers.append(_url_item(f"https://doi.org/{zenodo_doi}",
                                    "Experimenter’s Guide — Solving Navier–Stokes, Differently"))

        # --- write auto pulse (guarantees ExperimenterPulse + RGP) ---
        write_auto_pulse(
            dataset_id=ds_id,
            summary=run_summary_text,
            extra_tags=extra_tags,
            papers=papers,
            podcasts=[],
        )

    print("[done] RGP-NS agent run complete.")

if __name__ == "__main__":
    main()
