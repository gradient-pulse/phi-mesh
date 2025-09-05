# --- assemble metrics -------------------------------------------------
# assume these locals already exist in your script:
#   batch         -> int (default 1)
#   stamp         -> run timestamp string, e.g. "20250905_103441"
#   out_dir       -> results/rgp_ns/<stamp>/batch{batch}/
#   source_kind   -> "synthetic" | "local_netcdf" | "jhtdb" ...
#   dataset_id    -> a short name/slug for the dataset (e.g. "synth" or "isotropic")
#   var_name      -> e.g. "u"
#   xyz, window   -> probe location and [t0, t1, dt]
#   n_events, ratio_mean, ratio_cv, etc. -> your computed numbers

meta = {
    "batch": int(batch),
    "timestamp": str(stamp),
}

details = {
    "dataset": str(dataset_id),
    "var": str(var_name),
    "xyz": [float(xyz[0]), float(xyz[1]), float(xyz[2])],
    "window": [float(window[0]), float(window[1]), float(window[2])],
    "batch": int(batch),  # <-- ensure batch is present in details
}

metrics = {
    # put your main numbers here; names are examples
    "n": int(n_events),
    "ratio_mean": float(ratio_mean),
    "ratio_cv": float(ratio_cv),
    "source": str(source_kind),

    # attach both details and meta
    "details": details,
    "meta": meta,
}

# write JSON
os.makedirs(out_dir, exist_ok=True)
metrics_path = os.path.join(out_dir, "metrics.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
print(f"Wrote metrics: {metrics_path}")
