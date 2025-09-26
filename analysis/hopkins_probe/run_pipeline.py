from __future__ import annotations
import argparse
from pathlib import Path
from pipeline.io_loaders import load_series
from pipeline.preprocess import prep_1d
from pipeline.spectrum import rfft_spectrum, dominant_peak
from pipeline.ladder import ladder_1_2_3
from pipeline.figures import plot_time_and_spectrum
from pipeline.utils import save_json, ensure_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True, help="path to JHTDB .meta.json")
    ap.add_argument("--out",  required=True, help="output folder (results/fd_probe/...)")
    ap.add_argument("--component", default="u", help="which series (u|v|w|speed)")
    args = ap.parse_args()

    D = load_series("jhtdb", {"meta_path": args.meta})
    x = D["series"].get(args.component)
    if x is None:
        raise SystemExit(f"component '{args.component}' not found; have {list(D['series'].keys())}")

    P = prep_1d(D["t"], x)
    SP = rfft_spectrum(P["t"], P["x"], P["w"])
    dom = dominant_peak(SP["freq"], SP["power"], fmin=0.0)
    f0 = dom["freq"] if dom else None
    L = ladder_1_2_3(SP["freq"], SP["power"], f0) if f0 else None

    outdir = ensure_dir(args.out)
    figs = plot_time_and_spectrum(outdir, P["t"], {args.component: P["x"]}, SP["freq"], SP["power"], f0=f0)

    summary = {
        "label": D["label"],
        "component": args.component,
        "n": len(P["t"]),
        "dt": D["dt"],
        "dominant": dom,
        "ladder": L,
        "figures": figs,
    }
    save_json(Path(outdir) / "analysis.json", summary)
    print("✅ wrote:", (Path(outdir)/"analysis.json").as_posix())

if __name__ == "__main__":
    main()
