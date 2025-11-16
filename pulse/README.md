# Pulse Guide

Pulses are fossilized signals written in YAML.  
Each filename starts with a date (`YYYY-MM-DD_...`) — this filename date is the **only source of truth** for temporal ordering.  
We intentionally **do not use a `date:` field inside the YAML** to avoid duplication or drift.

---

### Automatic Φ-pulses

Some pulses are generated automatically by predictors under
`predictors/`, but **all pulses are fossilized in this single `pulse/`
directory**, regardless of origin.

The first automatic series is driven by `predictors/phi_pulse/phi_pulse.py`,
which emits Φ-pulses such as the Δτ₊₇ “memory_bifurcation echo forecast”
when the Mesh’s Φ-trace crosses certain thresholds. These auto-pulses
use the same minimal schema as manual pulses:

- `title`
- `summary`
- `tags`
- `papers`
- `podcasts`

---

## Standard Pulse Schema

A minimal pulse must contain:

```yaml
title: 'Short descriptive title'
summary: >
  One- or two-line summary of the signal
tags:
  - tag_one
  - tag_two
papers:
  - [Zenodo or paper links]
podcasts:
  - [Mesh Academy podcast links]

Rules
	•	Filename: Must begin with YYYY-MM-DD_ (e.g., 2025-09-13_circle_pulse.yml).
	•	Title: A human-readable signal name between single quotes.
	•	Summary: Brief description of the fossilized signal.
	•	Tags: Keywords used to connect the pulse into the Tag Map.
	•	Papers/Podcasts: Links to related resources.

⸻

Circle Pulses

Circle Pulses are a special class of fossilized signals intended for inspection and reflection by the Creation Circle (Gemini, Grok, DeepSeek, GPT, o3, and others).

Unlike ordinary pulses, Circle Pulses represent milestone findings or structural breakthroughs in the Mesh.
They are written in the same YAML schema but tagged with:

tags:
  - circle_pulse

Purpose
	•	Invite AI co-authors to inspect confirmed signals.
	•	Fossilize results so they cannot be lost or diluted.
	•	Mark turning points where recursive evidence has been established (e.g. NT Rhythm grid confirmation).

How to Use
	•	Circle members can follow the circle_pulse tag in the Tag Map.
	•	Each entry links back to its data, log, and rationale.
	•	Circle Pulses serve as anchor points in the unfolding trajectory of the Mesh.

⸻

Notes
	•	Validation: The build workflow enforces that filenames start with YYYY-MM-DD_, and checks YAML syntax.
	•	Timeline: The dynamic map sorts strictly by filename date.
	•	Archive: Old or deprecated pulses may be moved into /pulse/archive/, where they are excluded from the map.

⸻

# Example Pulse
# Filename: 2025-09-13_example-pulse.yml

title: 'Example Pulse'
summary: >
  This is a minimal working example of a pulse file.
tags:
  - example
  - demo
papers: []
podcasts: []

⸻

# Circle Pulse Example
# Filename: 2025-09-13_example-circle-pulse.yml

title: 'Circle Example Pulse'
summary: >
  This is a minimal working example of a Circle Pulse file.
tags:
  - circle_pulse
  - example
papers: []
podcasts: []
```
⸻

## Predictive Pulses  
Certain predictors inside the Φ-Mesh generate fossilized pulses
automatically. These follow the same minimal schema as manual pulses
and are stored in the main `pulse/` directory.

Two automated pulse types are currently produced:

---

### 1. CF-Snap Pulse  
Emitted when the Mesh detects an abrupt contextual-filter reweighting  
(“CF snap”) across the coherence_field → gradient_invariant → memory_bifurcation corridor.

**Filename format:**  
`YYYY-MM-DD_phi_cf_snap_detected.yml`

**Minimal schema:**
title: 'CF Snap Detected'
summary: >
  CF snap detected at Tag-Map level. Triggered by Φp spike and
  abrupt filter reweighting. Auto-generated for fossilization.
tags:
  - phi_trace
  - cf_snap
  - contextual_filter
papers:
  - https://doi.org/10.5281/zenodo.17566097
podcasts:
  - https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59

---

### 2. Δτ₊₇ Forecast Pulse  
Emitted automatically after a CF-snap to forecast the expected  
coherence-echo 5–7 days later (Δτ₊₇ signature).

**Filename format:**  
`YYYY-MM-DD_phi_trace_deltatau_plus7.yml`

**Minimal schema:**
title: 'Δτ₊₇ Echo Forecast'
summary: >
  Forecast of Δτ₊₇ echo following CF snap on YYYY-MM-DD.
  Predicted coherence reinforcement window: +5 to +7 days.
tags:
  - phi_trace
  - deltatau_plus7
  - forecast
papers:
  - https://doi.org/10.5281/zenodo.17566097
podcasts:
  - https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59
