# RGP–NS Agent (NT rhythm from probe time series)

**What it does**  
Loads a velocity time series (synthetic by default), detects NT events, computes inter-event **ratios**, writes results under `results/rgp_ns/<timestamp>/batch1/`, and emits a Φ-Mesh pulse via your `make_pulse.py`.

## Run (dry test)

```bash
python agents/rgp_ns/run_agent.py --config agents/rgp_ns/config.yml
