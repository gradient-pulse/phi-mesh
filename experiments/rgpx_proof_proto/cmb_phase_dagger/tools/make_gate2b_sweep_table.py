#!/usr/bin/env python3
import json
import argparse
from pathlib import Path

def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def fmt(x, nd=6):
    if x is None:
        return ""
    return f"{x:.{nd}f}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--runs_dir",
        required=True,
        help="Path to .../topology_mf_v0_v1/controls/lcdm_recon/runs"
    )
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir).expanduser().resolve()
    if not runs_dir.exists():
        raise SystemExit(f"Not found: {runs_dir}")

    rows = []
    for run_folder in sorted([p for p in runs_dir.iterdir() if p.is_dir()]):
        # pick the aggregate json in that run folder
        agg = sorted(run_folder.glob("*aggregate*.json"))
        if not agg:
            continue
        data = load_json(agg[0])
        inp = data.get("inputs", {})
        ds = data.get("D_stats", {})

        rows.append({
            "lmax": inp.get("lmax"),
            "run_id": data.get("run_id"),
            "seed0": inp.get("seed0"),
            "D0_mean": ds.get("D0_mean"),
            "D0_std": ds.get("D0_std"),
            "D0_min": ds.get("D0_min"),
            "D0_max": ds.get("D0_max"),
            "D1_mean": ds.get("D1_mean"),
            "D1_std": ds.get("D1_std"),
            "D1_min": ds.get("D1_min"),
            "D1_max": ds.get("D1_max"),
            "Dmf_mean": ds.get("D_mf_mean"),
            "Dmf_std": ds.get("D_mf_std"),
            "Dmf_min": ds.get("D_mf_min"),
            "Dmf_max": ds.get("D_mf_max"),
        })

    rows = [r for r in rows if r["lmax"] is not None]
    rows.sort(key=lambda r: int(r["lmax"]))

    # print markdown table
    print("## Sweep table — Gate 2B (ΛCDM recon control, MF V0+V1)\n")
    print("| lmax | run_id | seed0 | D0_mean ± std | D0_min..max | D1_mean ± std | D1_min..max | Dmf_mean ± std | Dmf_min..max |")
    print("|---:|---:|---:|---|---|---|---|---|---|")
    for r in rows:
        print(
            f"| {r['lmax']} | {r['run_id']} | {r['seed0']} | "
            f"{fmt(r['D0_mean'])} ± {fmt(r['D0_std'])} | {fmt(r['D0_min'])}..{fmt(r['D0_max'])} | "
            f"{fmt(r['D1_mean'],4)} ± {fmt(r['D1_std'],4)} | {fmt(r['D1_min'],4)}..{fmt(r['D1_max'],4)} | "
            f"{fmt(r['Dmf_mean'],4)} ± {fmt(r['Dmf_std'],4)} | {fmt(r['Dmf_min'],4)}..{fmt(r['Dmf_max'],4)} |"
        )

    # optional: derived ratio
    print("\n### Derived: D1_mean / lmax")
    for r in rows:
        ratio = float(r["D1_mean"]) / float(r["lmax"])
        print(f"- lmax={r['lmax']}: {ratio:.3f}")

if __name__ == "__main__":
    main()
