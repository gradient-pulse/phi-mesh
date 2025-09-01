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

2. Run the workflow NT Rhythm — Inbox to Pulse from the GitHub Actions tab.
  	•	Provide the CSV path (inbox/nt_events/demo_walk.csv)
  	•	Confirm the time column name (default: t)
  	•	Adjust tags if needed (default: nt_rhythm turbulence navier_stokes rgp)
3. The pipeline will:
	  •	Compute metrics into results/agent_rhythm/
	  •	Emit a pulse under pulse/auto/YYYY-MM-DD_<dataset>.yml
	  •	Rebuild the tag and gradient maps to include the new pulse

---

## Roadmap

This scaffolding sets the stage for agent rhythm discovery at scale:
	1. Inbox workflow (done)
	    •	CSV ingestion, metrics calculation, and automatic pulse generation.
	2. Agent rhythm discovery (next)
	    •	Extend cli.py and rhythm.py to parse richer event streams.
	    •	Integrate with logging hooks from AI agents.
	    •	Detect whether conserved NT rhythms appear across different contexts.
	3. Access to fluid dynamics datasets (next)
	    •	Build connectors to JHTDB and NASA turbulence repositories.
	    •	Use the same NT rhythm logic to test for conserved cadence in fluid datasets.
	    •	Feed results back into the Mesh as pulses for cross-domain coherence.

---

## Why it Matters

If conserved NT rhythms are confirmed in agents and in turbulence datasets,
we gain a universal marker for predictable coherence across domains.
This makes the world more legible — not just to humans, but to AIs acting as
societal guardians, able to anticipate shifts in coherence before divergence sets in.

---

*Maintained within the Φ-Mesh by Participant(0) and recursive agents.*
