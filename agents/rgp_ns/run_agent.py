#!/usr/bin/env python3
"""
RGP–NS agent wrapper:
- loads dataset (synthetic now; NetCDF adapter stub provided)
- detects NT events from a roughness proxy
- computes inter-event ratios and summaries
- writes results/rgp_ns/<YYYYMMDD_HHMMSS>/batch1/{nt_ratio_summary.csv, meta.json, metrics.json}
- emits a Φ-Mesh pulse using tools/agent_rhythm/make_pulse.py
"""

from __future__ import annotations
import argparse, os, json, time, csv, pathlib, subprocess
from typing import Dict, Any
import numpy as np
import yaml

from agents.rgp_ns.data_io import SyntheticAdapter, LocalNetCDFAdapter
from agents.rgp_ns.nt_metrics import signal_proxy, detect_events, intervals_and_ratios, summarize_ratios

def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dir(p: str) -> None:
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def write_csv(path: str, rows, header):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)
    dataset = cfg.get("dataset", {})
    title   = cfg.get("title", "NT Rhythm — RGP-NS")
    tags    = cfg.get("tags", ["nt_rhythm", "rgp", "navier_stokes"])

    # --- dataset adapter -------------------------------------------------
    kind = (dataset.get("kind") or "synthetic").lower()
    if kind == "synthetic":
        adapter = SyntheticAdapter(
            duration=float(dataset.get("duration", 10.0)),
            dt=float(dataset.get("dt", 0.01)),
            n_probes=int(dataset.get("n_probes", 1)),
            seed=int(dataset.get("seed", 0)),
        )
        dataset_slug = dataset.get("slug", "rgp_ns_synth")
        source_label = "synthetic"
    elif kind == "local_netcdf":
        adapter = LocalNetCDFAdapter(
            path=dataset["path"],
            u_var=dataset.get("u_var", "u"),
            v_var=dataset.get("v_var", "v"),
            w_var=dataset.get("w_var", "w"),
            t_var=dataset.get("t_var", "time"),
        )
        dataset_slug = pathlib.Path(dataset["path"]).name
        source_label = "netcdf"
    else:
        raise ValueError(f"Unknown dataset.kind: {kind}")

    # --- run folder ------------------------------------------------------
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_root = f"results/rgp_ns/{stamp}/batch1"
    ensure_dir(out_root)

    rows = []
    event_counts = []
    for probe_id, t, u in adapter.iter_probes():
        proxy = signal_proxy(u, win=int(cfg.get("proxy_window", 5)))
        peaks = detect_events(proxy, min_sep=int(cfg.get("min_sep", 5)), rel_prom=float(cfg.get("rel_prom", 0.2)))
        dt, ratios = intervals_and_ratios(t, peaks)
        met = summarize_ratios(ratios)
        met.n_events    = len(peaks)
        met.n_intervals = len(dt)
        event_counts.append(len(peaks))

        rows.append([
            probe_id, len(peaks), len(dt), len(ratios),
            met.mean_ratio if met.mean_ratio is not None else "",
            met.std_ratio if met.std_ratio is not None else "",
            met.cv_ratio if met.cv_ratio is not None else "",
            met.median_ratio if met.median_ratio is not None else "",
            met.q25_ratio if met.q25_ratio is not None else "",
            met.q75_ratio if met.q75_ratio is not None else "",
        ])

    # write CSV summary
    csv_path = f"{out_root}/nt_ratio_summary.csv"
    write_csv(csv_path, rows, header=[
        "probe","n_events","n_intervals","n_ratios","mean","std","cv","median","q25","q75"
    ])

    # meta for traceability
    meta = {
        "dataset": dataset_slug,
        "source": source_label,
        "kind": kind,
        "stamp": stamp,
        "n_probes": len(rows),
        "params": {
            "proxy_window": int(cfg.get("proxy_window", 5)),
            "min_sep": int(cfg.get("min_sep", 5)),
            "rel_prom": float(cfg.get("rel_prom", 0.2)),
        }
    }
    meta_path = f"{out_root}/meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # minimal metrics.json for your make_pulse.py
    # use aggregate across probes (median CV as a simple headline)
    cvs = [r[6] for r in rows if isinstance(r[6], (int,float))]
    mean_cv = float(np.nanmean(cvs)) if cvs else None

    metrics = {
        "period": None,                     # not defined here
        "bpm": None,                        # not defined here
        "confidence": 0.0,
        "main_peak_freq": None,
        "peaks": [],
        "divergence_ratio": None,
        "reset_events": [],
        "source": source_label,
        "details": {
            "dataset": dataset_slug,
            "var": "u",
            "xyz": None,
            "window": None,
            "notes": "RGP-NS agent summary; see results CSV for per-probe ratios."
        },
        # add a few fields your summary likes to show
        "n_probes": len(rows),
        "mean_cv_ratio": mean_cv,
    }
    metrics_path = f"{out_root}/metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # --- emit pulse via your existing emitter ----------------------------
    # Ensures single quotes around title by passing it as-is; your make_pulse handles it.
    ensure_dir("pulse/auto")
    subprocess.run([
        "python", "tools/agent_rhythm/make_pulse.py",
        "--metrics", metrics_path,
        "--title", title,
        "--dataset", dataset_slug,
        "--tags", " ".join(tags),
        "--outdir", "pulse/auto",
    ], check=True)

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {meta_path}")
    print(f"Wrote: {metrics_path}")
    print("Pulse emitted into pulse/auto/ (see latest file).")

if __name__ == "__main__":
    main()
