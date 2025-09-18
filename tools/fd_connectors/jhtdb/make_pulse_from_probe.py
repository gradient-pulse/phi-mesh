#!/usr/bin/env python3
import argparse, json, os, datetime as dt, pathlib, re

def _slug(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "dataset"

def _basename_no_ext(p: str) -> str:
    s = (p or "").split("#",1)[0].split("?",1)[0]
    base = os.path.basename(s.rstrip("/"))
    return re.sub(r"\.(csv|json|txt|zip|xz|gz|bz2|tar)$","",base,flags=re.I)

def _ensure_dir(d: str) -> None:
    if d: os.makedirs(d, exist_ok=True)

def _next_batch(today: str, base: str, outdir: str) -> int:
    root = pathlib.Path(outdir)
    root.mkdir(parents=True, exist_ok=True)
    paths = sorted(root.glob(f"{today}_{base}_batch*.yml"))
    if not paths: return 1
    rx = re.compile(r"_batch(\d+)\.yml$")
    nums = []
    for p in paths:
        m = rx.search(p.name)
        if m: nums.append(int(m.group(1)))
    return (max(nums)+1) if nums else 1

def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _compute_hint(peaks) -> tuple[str,int,float]:
    ladder, dominance = 0, 1.0
    if isinstance(peaks, list) and peaks:
        ladder = len(peaks)
        try:
            p0 = float(peaks[0][1])
            p1 = float(peaks[1][1]) if len(peaks)>1 else 0.0
            dominance = (p0/p1) if p1>0 else (float("inf") if p0>0 else 1.0)
        except Exception:
            dominance = 1.0
    if ladder >= 3 and dominance >= 2.0:
        return "decisive", ladder, dominance
    if ladder >= 3 or (ladder >= 2 and dominance >= 1.5):
        return "strong", ladder, dominance
    if ladder >= 2 or dominance >= 1.1:
        return "weak", ladder, dominance
    return "undetermined", ladder, dominance

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flow", required=True)
    ap.add_argument("--x", type=float, required=True)
    ap.add_argument("--y", type=float, required=True)
    ap.add_argument("--z", type=float, required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--nsteps", type=int, required=True)
    ap.add_argument("--slug", default="isotropic")  # for filenames; not shown in pulse
    args = ap.parse_args()

    # Locate the analysis JSON we just wrote
    stem = f"{args.flow}__x{args.x}_y{args.y}_z{args.z}__t0_{args.t0}_dt{args.dt}_n{args.nsteps}"
    analysis = f"results/fd_probe/{stem}.analysis.json"
    A = _read_json(analysis) if os.path.isfile(analysis) else {}

    # Roll up values for summary
    n      = A.get("n", args.nsteps)
    mean_dt= A.get("dt", args.dt)  # analyzer’s dt == mean_dt for uniform series
    cv_dt  = A.get("cv_dt", 0.0)   # analyzer may not set this; fall back to 0
    peaks  = A.get("peaks") or []
    hint, ladder, dominance = _compute_hint(peaks)

    # Provenance + file naming
    ds_slug = _slug(_basename_no_ext(args.flow))
    source  = "jhtdb"
    base    = f"{ds_slug}_{source}"
    today   = dt.date.today().isoformat()
    outdir  = "pulse/auto"
    batch   = _next_batch(today, base, outdir)
    outpath = os.path.join(outdir, f"{today}_{base}_batch{batch}.yml")
    _ensure_dir(outdir)

    # Build strict YAML
    probe_dict = {
        "dataset": args.flow,
        "var": None,
        "xyz": [args.x, args.y, args.z],
        "window": [args.t0, args.t0 + (args.nsteps-1)*args.dt, args.dt],
    }
    title = "NT Rhythm — FD Probe"
    summary_lines = [
        f"NT rhythm probe on “{base}_batch{batch}” — n={n}, mean_dt={mean_dt}, cv_dt={cv_dt}.",
        f"Source: {source}. Probe: {json.dumps(probe_dict, ensure_ascii=False)}.",
        f"hint: {hint} — fundamental + harmonics (ladder={ladder}), dominance={dominance if dominance!=float('inf') else 1e9:.3g}",
    ]

    yaml_lines = []
    yaml_lines.append(f"title: '{title.replace(\"'\",\"’\")}'")
    yaml_lines.append("summary: >-")
    for line in summary_lines:
        yaml_lines.append(f"  {line}")
    yaml_lines.append("tags:")
    for t in ["nt_rhythm", "turbulence", "navier_stokes", "rgp"]:
        yaml_lines.append(f"  - {t}")
    yaml_lines.append("papers:")
    yaml_lines.append("  - https://doi.org/10.5281/zenodo.15830659")
    yaml_lines.append("podcasts:")
    yaml_lines.append("  - https://notebooklm.google.com/notebook/b7e25629-0c11-4692-893b-cd339faf1805?artifactId=39665e8d-fa5a-49d5-953e-ee6788133b4a")

    with open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")

    print(f"[pulse] wrote {outpath}")
    print(f"[pulse] analysis_json={os.path.abspath(analysis)}")

if __name__ == "__main__":
    main()
