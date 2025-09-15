# tools/fd_connectors/jhtdb/jhtdb_loader.py
"""
JHTDB Connector
---------------
Pulls probe-level time series from Johns Hopkins Turbulence Database (JHTDB).
Saves outputs into data/jhtdb/ as CSV and Parquet.
"""

import os
import pandas as pd
from pathlib import Path
import pyJHTDB  # JHTDB official Python client (pip install pyJHTDB)

DATA_DIR = Path("data/jhtdb")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_timeseries(flow="isotropic1024coarse", point=(0.1, 0.2, 0.3), nsteps=1000, dt=0.002):
    """
    Fetch velocity time series at a probe point from JHTDB.
    """
    # Setup JHTDB client
    lTDB = pyJHTDB.libJHTDB()
    lTDB.initialize()

    # Example: get velocity components at given point
    ts = []
    for i in range(nsteps):
        t = i * dt
        u = lTDB.getData(flow, t, point, 'u')  # velocity at probe
        ts.append([t, *u])

    lTDB.finalize()

    # Save as dataframe
    df = pd.DataFrame(ts, columns=["t", "u", "v", "w"])
    csv_path = DATA_DIR / f"{flow}_probe.csv"
    parquet_path = DATA_DIR / f"{flow}_probe.parquet"
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"✅ Saved probe data: {csv_path}, {parquet_path}")
    return df
