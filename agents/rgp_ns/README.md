# RGP–NS Agent (NT rhythm from probe time series)

**What it does**  
Loads a velocity time series (synthetic by default), detects NT events, computes inter-event **ratios**, writes results under `results/rgp_ns/<timestamp>/batch1/`, and emits a Φ-Mesh pulse via your `make_pulse.py`.

## Run (dry test)

```bash
python agents/rgp_ns/run_agent.py --config agents/rgp_ns/config.yml

Outputs:
	•	results/rgp_ns/<stamp>/batch1/nt_ratio_summary.csv
	•	results/rgp_ns/<stamp>/batch1/meta.json
	•	results/rgp_ns/<stamp>/batch1/metrics.json (fed to make_pulse.py)
	•	a new pulse in pulse/auto/…yml

Switch to NetCDF later

Once you have a JHTDB (or other CFD) export in NetCDF/HDF5, edit agents/rgp_ns/config.yml:
dataset:
  kind: local_netcdf
  path: data/isotropic.nc
  u_var: u
  v_var: v
  w_var: w
  t_var: time

Then extend LocalNetCDFAdapter in data_io.py so that it yields
(probe_id, t, |u|) tuples. That’s the only place that needs touching.

Notes
	•	No SciPy dependency; peak detector is a simple prominence + min-separation rule.
	•	Keep your strict pulse style; titles are single-quoted in config.yml.
	•	Synthetic mode stays available forever as a dry-run baseline.

## JHTDB Live Mode (placeholder)

You can also run directly against the Johns Hopkins Turbulence Database (JHTDB).  
This requires a valid API token saved as a GitHub secret (`JHTDB_TOKEN`).

### Config
Set the dataset kind in `agents/rgp_ns/config.yml`:

```yaml
dataset:
  kind: jhtdb
  dataset: isotropic1024coarse   # or 'channel', 'mixing', etc.
  var: u
  xyz: [0.1, 0.1, 0.1]          # probe location
  window: [0.0, 10.0, 0.01]     # [t0, t1, dt]

Notes
	•	Current implementation uses the test token (≤4096 points per query).
	•	Replace with a personal token once approved by JHTDB.
	•	Agent wrapper (run_agent.py) will automatically fetch the token from secrets.
	•	Results + pulses appear under results/rgp_ns/<timestamp>/batchN/ as usual.
	•	This path is experimental — use NetCDF mode if you need bulk probes.
