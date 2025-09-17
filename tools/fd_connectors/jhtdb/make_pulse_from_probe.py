#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
import yaml

FILENAME_MAX = 64  # hard cap for the whole filename

def slugify(raw: str) -> str:
    s = (raw or "fdprobe").lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)   # keep only safe chars
    s = re.sub(r"_+", "_", s).strip("_-") # collapse repeats / trim
    return s or "fdprobe"

def read_json(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--outdir", default="pulse")
    ap.add_argument("--date", required=True)   # YYYY-MM-DD
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--slug", default="fdprobe")
    args = ap.parse_args()

    meta = read_json(args.meta)
    ana  = read_json(args.analysis)

    # ---- dynamic slug cap so whole filename <= FILENAME_MAX ----
    safe_slug = slugify(args.slug)
    prefix = f"{args.date}_"
    suffix = f"_batch{args.batch}.yml"
    remaining = max(1, FILENAME_MAX - len(prefix) - len(suffix))
    safe_slug = safe_slug[:remaining]

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    fname = f"{prefix}{safe_slug}{suffix}"
    out_path = outdir / fname
    # ------------------------------------------------------------

    # links
    meta_rel = str(Path(args.meta).as_posix())
    ana_rel  = str(Path(args.analysis).as_posix())
    base = Path(args.meta).with_suffix("").with_suffix("")  # drop .meta.json
    cand = []
    for ext in (".csv.gz", ".parquet", ".csv"):
        p = Path("data/jhtdb") / (base.name + ext)
        if p.exists():
            cand.append(p.as_posix())

    title = f"NT Rhythm — FD Probe ({args.date})"
    point = meta.get("point") or {}
    flow  = meta.get("flow", "")
    n     = meta.get("nsteps", meta.get("n"))
    dt    = meta.get("dt")

    data = {
        "title": title,
        "date": args.date,
        "tags": ["navier_stokes", "turbulence", "nt_rhythm", "rgp", "experiments"],
        "summary": (
            f'NT rhythm probe on "{flow}" — n={n}, dt={dt}. '
            f'Probe: xyz=({point.get("x")}, {point.get("y")}, {point.get("z")}). '
            f'dominant_freq_hz≈{ana.get("dominant_freq_hz", 0)}.'
        ),
        "papers": [],
        "podcasts": [],
        "links": [meta_rel, ana_rel, *cand],
    }

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"wrote {out_path}")

if __name__ == "__main__":
    main()
