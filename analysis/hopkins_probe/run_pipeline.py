from pathlib import Path
import yaml
import numpy as np

from pipeline import preprocess, spectrum, ladder, figures, utils

# replace with your own loader when ready
def load_hopkins(cfg):
    # Expect CSV in cfg['path'] with columns: t,u,v,w,Z (or adapt to your reader)
    import pandas as pd
    df = pd.read_csv(cfg["path"])
    t = df["t"].to_numpy()
    out = {cfg.get("probe_id", "hopkins:demo"): {}}
    for var in cfg.get("variables", ["u","v","w","Z"]):
        if var in df.columns:
            out[cfg.get("probe_id","hopkins:demo")][var] = (t, df[var].to_numpy())
    return out

cfg = yaml.safe_load(Path("config.yml").read_text())
tsmap = load_hopkins(cfg)

rows = []
for pid, series in tsmap.items():
    for var, (t, x) in series.items():
        xw = preprocess.apply(x, cfg.get("preprocess", {"detrend":"mean","window":"hann"}))
        dt = float(np.median(np.diff(t)))
        Pxx, f = spectrum.psd(xw, dt, cfg.get("fft", {"welch_segments": 4}))
        det = ladder.detect(f, Pxx, cfg.get("fft", {}))
        figures.plot_ts(t, x, pid, var, "results/fig")
        figures.plot_psd(f, Pxx, det, pid, var, "results/fig")
        rows.append(utils.pack_row(pid, var, det, cfg))

utils.write_table(rows, "results/tables/ratios.csv")
utils.write_log(cfg, "results/logs/run.log")
print("Done.")
