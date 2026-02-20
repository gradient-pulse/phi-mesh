#!/usr/bin/env python3
import json
import argparse
from pathlib import Path

def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def linspace(a: float, b: float, n: int):
    if n <= 1:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]

def find_aggregate_json(run_folder: Path) -> Path | None:
    # Prefer an "aggregate" json if present.
    cands = sorted(run_folder.glob("*aggregate*.json"))
    if cands:
        return cands[0]
    # Fallback: json containing D_stats + inputs + per_sim
    for p in sorted(run_folder.glob("*.json")):
        try:
            d = load_json(p)
            if "D_stats" in d and "inputs" in d and "per_sim" in d:
                return p
        except Exception:
            pass
    return None

def iter_per_sim_jsons(run_folder: Path):
    """
    Per-sim result jsons usually contain 'observed' with curves.
    We try to detect those robustly without relying on exact filenames.
    """
    for p in sorted(run_folder.glob("*.json")):
        try:
            d = load_json(p)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        # Exclude aggregate-like records
        if "D_stats" in d and "per_sim" in d:
            continue
        # Include anything that looks like a per-sim observed output
        obs = d.get("observed")
        if (isinstance(obs, dict) and ("v1_curve" in obs or "v0_curve" in obs)) or ("v1_curve" in d):
            yield p, d

def get_v1_curve(d: dict):
    if "v1_curve" in d and isinstance(d["v1_curve"], list):
        return d["v1_curve"]
    obs = d.get("observed", {})
    if isinstance(obs, dict) and "v1_curve" in obs and isinstance(obs["v1_curve"], list):
        return obs["v1_curve"]
    return None

def infer_sim_id(d: dict, filename: str) -> str:
    for k in ("sim_id", "sim", "simIdx"):
        if k in d:
            s = str(d[k])
            return s.zfill(3) if s.isdigit() else s
    # infer from filename fragments like "__sim000__"
    if "__sim" in filename:
        try:
            tail = filename.split("__sim", 1)[1]
            s = tail[:3]
            if s.isdigit():
                return s
        except Exception:
            pass
    return "unknown"

def peak_stats(v1_curve: list[float], nus: list[float]):
    peak_val = max(v1_curve)
    peak_idx = v1_curve.index(peak_val)
    nu_at_peak = nus[peak_idx] if 0 <= peak_idx < len(nus) else None
    return peak_val, peak_idx, nu_at_peak

def fmt(x, nd=4):
    if x is None:
        return ""
    return f"{x:.{nd}f}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs_dir", required=True,
                    help=".../topology_mf_v0_v1/controls/<control>/runs")
    ap.add_argument("--out_dir", default="",
                    help="Output directory (default: <runs_dir>/../summary_tables)")
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir).expanduser().resolve()
    if not runs_dir.exists():
        raise SystemExit(f"Not found: {runs_dir}")

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else runs_dir.parent / "summary_tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    sweep_rows = []
    peak_rows = []

    for run_folder in sorted([p for p in runs_dir.iterdir() if p.is_dir()]):
        agg_path = find_aggregate_json(run_folder)
        if not agg_path:
            continue

        agg = load_json(agg_path)
        inp = agg.get("inputs", {})
        ds = agg.get("D_stats", {})

        lmax = inp.get("lmax")
        if lmax is None:
            continue
        lmax = int(lmax)
        run_id = agg.get("run_id", run_folder.name)

        # ---- Sweep table row
        sweep_rows.append({
            "lmax": lmax,
            "run_id": run_id,
            "seed0": inp.get("seed0"),
            "nside": inp.get("nside"),
            "n_phase_sims": inp.get("n_phase_sims"),
            "sims_used": ",".join(inp.get("sims_used", [])),
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

        # ---- Peak extraction config
        n_nu = int(inp.get("n_nu", 61))
        nu_min = float(inp.get("nu_min", -3.0))
        nu_max = float(inp.get("nu_max", 3.0))
        nus = linspace(nu_min, nu_max, n_nu)

        per_sim_peaks = []
        for p, d in iter_per_sim_jsons(run_folder):
            v1 = get_v1_curve(d)
            if not v1:
                continue
            sim_id = infer_sim_id(d, p.name)
            pv, pi, pnu = peak_stats(v1, nus)
            per_sim_peaks.append((sim_id, pv, pi, pnu, p.name))

        # summarize peaks at run level
        if per_sim_peaks:
            peak_vals = [x[1] for x in per_sim_peaks]
            peak_idxs = [x[2] for x in per_sim_peaks]

            # mode of peak index (tie-break to smallest index)
            counts = {}
            for idx in peak_idxs:
                counts[idx] = counts.get(idx, 0) + 1
            mode_idx = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            mode_nu = nus[mode_idx] if 0 <= mode_idx < len(nus) else None

            peak_rows.append({
                "lmax": lmax,
                "run_id": run_id,
                "peak_mean": sum(peak_vals) / len(peak_vals),
                "peak_min": min(peak_vals),
                "peak_max": max(peak_vals),
                "mode_idx": mode_idx,
                "mode_nu": mode_nu,
                "per_sim": sorted(per_sim_peaks, key=lambda x: x[0])
            })
        else:
            peak_rows.append({
                "lmax": lmax,
                "run_id": run_id,
                "peak_mean": None,
                "peak_min": None,
                "peak_max": None,
                "mode_idx": None,
                "mode_nu": None,
                "per_sim": []
            })

    sweep_rows.sort(key=lambda r: r["lmax"])
    peak_rows.sort(key=lambda r: r["lmax"])

    # ----------------------------
    # Write sweep markdown
    # ----------------------------
    md = []
    md.append("# Gate 2B — ΛCDM end-to-end recon control (MF V0+V1): ℓmax sweep\n")
    md.append(f"- Runs scanned from: `{runs_dir}`\n")
    md.append("| lmax | run_id | seed0 | sims_used | D1_mean ± std | D1_min..max | Dmf_mean ± std | Dmf_min..max | D0_mean ± std |")
    md.append("|---:|---:|---:|---|---|---|---|---|---|")
    for r in sweep_rows:
        md.append(
            f"| {r['lmax']} | {r['run_id']} | {r['seed0']} | {r['sims_used']} | "
            f"{fmt(r['D1_mean'])} ± {fmt(r['D1_std'])} | {fmt(r['D1_min'])}..{fmt(r['D1_max'])} | "
            f"{fmt(r['Dmf_mean'])} ± {fmt(r['Dmf_std'])} | {fmt(r['Dmf_min'])}..{fmt(r['Dmf_max'])} | "
            f"{fmt(r['D0_mean'],6)} ± {fmt(r['D0_std'],6)} |"
        )

    md.append("\n## Derived: D1_mean / lmax\n")
    for r in sweep_rows:
        ratio = float(r["D1_mean"]) / float(r["lmax"])
        md.append(f"- lmax={r['lmax']}: {ratio:.3f}")

    out_sweep = out_dir / "gate2b_mf_v0_v1__lmax_sweep.md"
    out_sweep.write_text("\n".join(md) + "\n", encoding="utf-8")

    # ----------------------------
    # Write peak markdown
    # ----------------------------
    md2 = []
    md2.append("# Gate 2B — MF V0+V1: V1 peak summary (per run + per sim)\n")
    md2.append(f"- Runs scanned from: `{runs_dir}`\n")

    md2.append("## Per-run summary\n")
    md2.append("| lmax | run_id | peak(V1) mean | peak(V1) min..max | peak index (mode) | ν at peak (mode) |")
    md2.append("|---:|---:|---:|---:|---:|---:|")
    for r in peak_rows:
        md2.append(
            f"| {r['lmax']} | {r['run_id']} | {fmt(r['peak_mean'],3)} | "
            f"{fmt(r['peak_min'],3)}..{fmt(r['peak_max'],3)} | "
            f"{'' if r['mode_idx'] is None else r['mode_idx']} | {fmt(r['mode_nu'],3)} |"
        )

    md2.append("\n## Per-sim detail\n")
    for r in peak_rows:
        md2.append(f"### lmax={r['lmax']} (run {r['run_id']})\n")
        md2.append("| sim_id | v1_peak | peak_idx | ν_at_peak | source_json |")
        md2.append("|---:|---:|---:|---:|---|")
        for (sim_id, pv, pi, pnu, fname) in r["per_sim"]:
            md2.append(f"| {sim_id} | {pv:.3f} | {pi} | {pnu:.3f} | `{fname}` |")
        md2.append("")

    out_peaks = out_dir / "gate2b_mf_v0_v1__v1_peaks.md"
    out_peaks.write_text("\n".join(md2) + "\n", encoding="utf-8")

    print(f"Wrote: {out_sweep}")
    print(f"Wrote: {out_peaks}")

if __name__ == "__main__":
    main()
