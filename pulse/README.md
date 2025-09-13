# Pulse Guide

Pulses are fossilized signals written in YAML.  
Each filename starts with a date (`YYYY-MM-DD_...`) — this filename date is the **only source of truth** for temporal ordering.  
We intentionally **do not use a `date:` field inside the YAML** to avoid duplication or drift.

---

## Standard Pulse Schema

A minimal pulse must contain:

```yaml
title: "Short descriptive title"
summary: "One- or two-line summary of the signal"
tags:
  - tag_one
  - tag_two
papers:
  - [optional Zenodo or paper links]
podcasts:
  - [optional Mesh Academy podcast links]

Rules
	•	Filename: Must begin with YYYY-MM-DD_ (e.g., 2025-09-13_circle_pulse.yml).
	•	Title: A human-readable signal name.
	•	Summary: Brief description of the fossilized signal.
	•	Tags: Keywords used to connect the pulse into the Tag Map.
	•	Papers/Podcasts: Optional links to related resources.

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

Example Pulse

Filename:
2025-09-13_example-pulse.yml

Content:

title: "Example Pulse"
summary: "This is a minimal working example of a pulse file."
tags:
  - example
  - demo
papers: []
podcasts: []

---
side?
