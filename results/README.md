# Probe Results

This directory contains **Numerical Turbulence Rhythm (NT Rhythm) probe results** from multiple sources:  

- **FD Probe** — JHTDB, NASA, or synthetic runs  
- **Princeton Probe** — subset CSV/HDF5 or demo synthetic  

Each run produces:  
- a machine-generated **JSON** (`metrics` for FD, `analysis` for Princeton) under `results/*/`  
- a companion **figure folder** (`.analysis/`) with time/spectrum plots  
- a matching **pulse** under `pulse/auto/`  

See subfolders for details:  
- [fd_probe/](fd_probe/) — FD probe results (JHTDB/NASA/synthetic)  
- [princeton/](princeton/) — Princeton probe results (subset/demo)  
