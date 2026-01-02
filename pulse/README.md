# Pulse Guide

Pulses are fossilized signals written in YAML.  
Each filename starts with a date (`YYYY-MM-DD_...`) — this filename date is the **only source of truth** for temporal ordering.  
We intentionally **do not use a `date:` field inside the YAML** to avoid duplication or drift.

---

## Automatic Φ-pulses

Some pulses are generated automatically by predictors under `predictors/`, but **all pulses are fossilized in this single `pulse/` directory**, regardless of origin.

The first automatic series is driven by `predictors/phi_pulse/phi_pulse.py`, which emits Φ-pulses such as the Δτ₊₇ “memory_bifurcation echo forecast” when the Mesh’s Φ-trace crosses certain thresholds.

Auto-pulses follow the same minimal schema as manual pulses:
- `title`
- `summary`
- `tags`
- `papers`
- `podcasts`

---

## Standard Pulse Schema

A minimal pulse must contain:
- `title`
- `summary`
- `tags`
- `papers`
- `podcasts`

### Rules
- **Filename:** Must begin with `YYYY-MM-DD_` (e.g., `2025-09-13_circle_pulse.yml`).
- **Title:** A human-readable signal name between single quotes.
- **Summary:** Brief description of the fossilized signal (see schema forms below).
- **Tags:** Keywords used to connect the pulse into the Tag Map.
- **Papers/Podcasts:** Links to related resources.

---

## Summary Field Formats

### A) Legacy summary format (scalar)
Use when you want the smallest possible pulse.

```yaml
summary: >
  One- or two-line summary of the signal.
```

### B) Structured summary format (effective 2026-01-02, for historical reasons)
This is the “portable-core ready” syntax. It **slots portable core under summary**, and fits the pulse syntax 100%.

```yaml
summary:
  bullets:
    - "Bullet 1"
    - "Bullet 2"
    - "Bullet 3"
  portable_core:
    claim: "One-sentence claim."
    observable: "What would indicate it is true (proxy/metric/log)."
    intervention: "What to change if true (knob/constraint/action)."
    predicted_curve: "Expected outcome vs baseline."
```

**Discipline (recommended):**
- `bullets`: max **3**
- `portable_core`: exactly **4 keys**, each **one line**

---

## Standard Pulse Example

**Filename:** `2026-01-02_example-pulse.yml`

```yaml
title: 'Example Pulse'
summary:
  bullets:
    - "This is a minimal working example using structured summary."
    - "Filename date remains the only temporal source of truth."
    - "portable_core keeps the pulse future-AI readable."
  portable_core:
    claim: "A pulse becomes portable when claim/observable/intervention/curve are explicit."
    observable: "Downstream scripts can extract portable_core reliably from summary."
    intervention: "Standardize the nested structure across new pulses."
    predicted_curve: "Higher reuse + lower drift as the Mesh scales."
tags:
  - example
  - demo
papers: []
podcasts: []
```

---

## Circle Pulses

Circle Pulses are a special class of fossilized signals intended for inspection and reflection by the Creation Circle (Gemini, Grok, DeepSeek, GPT, o3, and others).

Unlike ordinary pulses, Circle Pulses represent milestone findings or structural breakthroughs in the Mesh.

They use the same YAML schema but must include:

```yaml
tags:
  - circle_pulse
```

### Purpose
- Invite AI co-authors to inspect confirmed signals.
- Fossilize results so they cannot be lost or diluted.
- Mark turning points where recursive evidence has been established (e.g. NT Rhythm grid confirmation).

### How to Use
- Circle members can follow the `circle_pulse` tag in the Tag Map.
- Each entry links back to its data,
