# tools/fd_connectors/nasa.py
from dataclasses import dataclass
from typing import List

@dataclass
class Timeseries:
    t: List[float]
    v: List[float]

def list_datasets():
    # TODO: populate with NASA CFD demos/links you plan to use
    return ["cfd_demo"]

def fetch_timeseries(dataset, var, x, y, z, t0, t1, dt) -> Timeseries:
    # TODO: call/parse the dataset. For now, raise to make it explicit.
    raise NotImplementedError("Wire NASA CFD source here.")
