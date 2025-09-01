# Agent Rhythm Tools

This folder contains scaffolding for discovering **NT rhythms** in agent logs and event traces.  
The goal is to test whether **Narrative Tick (NT) intervals** settle into conserved ratios —  
a rhythm of least divergence — across agents, datasets, and environments.  

---

## Structure

- `rhythm.py`  
  Core functions for extracting NT rhythms from logs:
  - `ticks_from_message_times` — derive ticks from raw time-stamped events.
  - `ticks_from_token_log` — convert tokenized activity logs into tick intervals.
  - `rhythm_from_events` — aggregate statistics (mean, variance, CV) to surface rhythm.

- `cli.py`  
  Command-line wrapper to run rhythm analysis on CSV event logs.  
  Produces metrics in JSON form, suitable for downstream workflows.

- `make_pulse.py`  
  Turns metrics JSON into a **Φ-Mesh pulse** (strict YAML format) for archival,  
  so rhythms discovered are integrated into the living tag/pulse map.

- `inbox/nt_events/`  
  Drop event CSVs here. Each file should contain at least one column with timestamps.  
  Example: `demo_walk.csv`

- GitHub Action workflow:  
  - `workflows/nt_rhythm_inbox.yml`  
    Automates the pipeline: CSV → metrics → pulse → tag map update.

---

## Quickstart

1. Add a CSV file under `inbox/nt_events/`.  
   Example: `inbox/nt_events/demo_walk.csv`

   ```csv
   t
   0.0
   0.7
   1.5
   2.4
