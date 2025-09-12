def _probe_timeseries_from_netcdf(path: str, var: str, xyz: Tuple[float, float, float]) -> Timeseries:
    """
    Open NASA DNS NetCDF and interpolate var at spatial point (x,y,z) over time.
    Normalizes common dim/coord aliases to canonical names: t, x, y, z.
    Resolves var (u/v/w/p) case-insensitively (e.g., U,V,W).
    """
    if xr is None:
        raise ImportError("xarray is required for NetCDF probing")

    # Open file
    try:
        ds = xr.open_dataset(path, engine="netcdf4")
    except Exception:
        # Fallback to default engine if netcdf4 not available
        ds = xr.open_dataset(path)

    # 1) Normalize dims/coords → t,x,y,z
    alias_map = {
        "t": ["t", "time", "timesteps", "Time", "TIME"],
        "x": ["x", "xcoord", "xc", "X", "Xcoord", "XC"],
        "y": ["y", "ycoord", "yc", "Y", "Ycoord", "YC"],
        "z": ["z", "zcoord", "zc", "Z", "Zcoord", "ZC"],
    }
    rename_map: dict[str, str] = {}

    # Helper: if any alias exists as a dim or coord and canonical missing, plan a rename
    def pick_rename(canon: str) -> None:
        if canon in ds.dims or canon in ds.coords:
            return
        for a in alias_map[canon]:
            if a in ds.dims or a in ds.coords:
                rename_map[a] = canon
                return

    for canon in ["t", "x", "y", "z"]:
        pick_rename(canon)

    if rename_map:
        ds = ds.rename(rename_map)

    # After rename, assert we have the coords
    missing = [k for k in ["t", "x", "y", "z"] if (k not in ds.dims and k not in ds.coords)]
    if missing:
        raise KeyError(f"Missing required coords/dims after normalization: {missing}. "
                       f"Available dims={list(ds.dims)}, coords={list(ds.coords)}")

    # 2) Resolve variable name case-insensitively
    var_candidates = [var, var.lower(), var.upper(), var.capitalize()]
    vname = None
    for cand in var_candidates:
        if cand in ds.data_vars:
            vname = cand
            break
    if vname is None:
        # As a last resort, choose first data_var whose name (lower) equals u/v/w/p
        low = var.lower()
        for k in ds.data_vars:
            if k.lower() == low:
                vname = k
                break
    if vname is None:
        raise KeyError(f"Variable {var!r} not found. Available: {list(ds.data_vars)}")

    v = ds[vname]

    # 3) Interpolate at point (x,y,z) across all times
    # Ensure we have coordinate arrays on these axes
    for ax in ["t", "x", "y", "z"]:
        if ax not in v.coords and ax in ds.coords:
            v = v.assign_coords({ax: ds[ax]})

    # Time may be dimension or coordinate; keep vector over time
    # Typical orders: (t,z,y,x) or (t,y,x,z). xarray interps by name.
    try:
        vt = v.interp(x=xyz[0], y=xyz[1], z=xyz[2], method="linear")
    except Exception as e:
        ds.close()
        raise RuntimeError(f"Interpolation failed at xyz={xyz}: {e}")

    # Extract arrays
    t = ds["t"].values
    vals = vt.values

    # Close file
    ds.close()

    # 4) Sanity: coerce to 1-D time series and sort if needed
    t = np.asarray(t).reshape(-1)
    vals = np.asarray(vals).reshape(-1)

    # Some datasets store descending time; sort ascending
    if t.size > 1 and np.any(np.diff(t) < 0):
        idx = np.argsort(t)
        t = t[idx]
        vals = vals[idx]

    # Guard: remove NaNs produced by out-of-domain interp
    mask = np.isfinite(t) & np.isfinite(vals)
    if not np.any(mask):
        raise ValueError("All interpolated values are NaN/Inf — probe may be outside the domain.")
    t = t[mask]; vals = vals[mask]

    return Timeseries(t=t.astype(float).tolist(),
                      v=vals.astype(float).tolist())
