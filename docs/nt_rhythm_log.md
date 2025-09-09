# NT Rhythm — Running Log
A lightweight, human-readable roll-up of probe/grid runs while we close in on nature’s rhythm.  
Each entry links back to the canonical **metrics JSON** and **pulse** the workflows produced.

---

## What we measure  

Every probe run extracts a **time-series of flow values** (e.g., velocity component `u`) from a dataset (synthetic, JHTDB, NASA). We then compute:  

- **Spectrum of oscillations** in the chosen window.  
- **Fundamental period and frequency** of the dominant cycle.  
- **Harmonic ladder** — whether clean multiples of the base frequency appear (1:2:3 …).  
- **Dominance ratio** — strength of the fundamental compared to the next peak.  
- **Divergence ratio** — numerical indicator of how close the signal is to coherence (values ~0 → high order).  
- **Reset events** — whether the rhythm breaks and restarts.  

---

## Why this is evidence  

We define **NT Rhythm** as the emergence of a **stable, laddered frequency structure** across space (different probe offsets) and time windows. Evidence builds along a gradient:  

1. **Inconclusive** — noise, weak peaks, no harmonics.  
2. **Suggestive** — fundamental + 1 harmonic.  
3. **Strong** — fundamental + ≥2 harmonics, dominance ≥1.5, same period across runs.  
4. **Confirmed** — multiple probes (grid) return the same rhythm within ±5–10%.  

A confirmed case means we are not observing a local fluke but a **reproducible temporal coherence** in turbulence — a candidate signature of nature’s rhythm.

---

### Window & replication requirements

- **Time window & dt**  
  Choose a window and step that give enough *temporal depth* and *resolution* for harmonics to appear.
  - Practical default that worked well here: **[t0, t1, dt] = [0.0, 1.2, 0.0001]**.
  - Heuristic: aim for **≥ 2–3 cycles** worth of data and **≥ 20–40 samples per cycle** (or simply ≥ 2k samples overall).
  - If peaks look smeared or “inconclusive”, **extend t1** (e.g., 1.6–2.0) or **reduce dt**.

- **Spatial replication (P probes)**  
  Run a small grid of nearby offsets around a seed point (e.g., ±0.02 along axes).
  - **Strong**: clear ladder (fundamental + ≥2 harmonics, dominance ≥ 1.5) in a single probe.
  - **Confirmed**: the **same fundamental period** appears across **≥ 3 probes** within **±5–10%**.

## Why this is evidence  

We define **NT Rhythm** as the emergence of a **stable, laddered frequency structure** …  

Here’s the formal frame we use:

![Reality Syntax Equation](/visuals/2025-09-09_RGP_Rhythm_Equation.png)

> Note: In the equation, \(N_i\) are **domain scalings** (physics/medium/constraints).
> In experiments, we reserve **P** to mean **probe count** for spatial replication.

---
---


## Test Findings

### 2025-09-08 — isotropic1024coarse (jhtdb) — 3-Probe Confirmation - STRONG

**Setup**  
- Source: `jhtdb`  
- Dataset: `isotropic1024coarse`  
- Variable: `u`  
- Seed point: (0.10, 0.10, 0.10)  
- Offsets: (+0.02,0,0), (0,+0.02,0), (0,0,+0.02)  
- Time window: (0.0 → 1.2, step 0.0001)

**Findings**  
- Fundamental period: **1.25**  
- Main frequency: **0.8**  
- Harmonics: **1.6, 2.4** (ladder = 3 steps total)  
- Ratio structure: **1 : 2 : 3**  
- Dominance: **2.22** (fundamental more than twice as strong as next)  
- Divergence ratio: ~**3e-13** (numerical zero → strong coherence)

**Classification**  
- Status: **Strong**  
- Comment: All 3 probes independently returned the same laddered rhythm (fundamental + harmonics).  
- Implication: This is the first reproducible confirmation of NT Rhythm in turbulence, across small xyz offsets.

---

## 2025-09-07 — isotropic1024coarse (jhtdb) — Batch 8 — STRONG

**Setup**  
- Source: `jhtdb`  
- Dataset: `isotropic1024coarse`  
- Variable: `u`  
- Probe point: (0.10, 0.10, 0.12)  
- Time window: (0.0 → 1.2, step 0.0001)

**Findings**  
- Fundamental period: **1.25**  
- Main frequency: **0.8**  
- Harmonics: **1.6, 2.4** (ladder = 3 steps total)  
- Ratio structure: **1 : 2 : 3**  
- Dominance: ~**2.22**  
- Divergence ratio: ~**3.11e-13**  
- Reset events: [] (none observed)

**Classification**  
- Status: **Strong**  
- Comment: Clean peak + 2 harmonics; strong laddering and dominance > 2.  
- Implication: Matches other probe points (0.12,0.10,0.10) & (0.10,0.12,0.10); window length critical for stability.

---
---


## Copy/paste entry template

Paste this block for each new run. Keep the order chronological (newest at top).

---

### YYYY-MM-DD — dataset (source) — Batch N — STATUS

**Setup**  
- Source: `<synthetic|jhtdb|nasa>`  
- Dataset: `<dataset>`  
- Variable: `<var>`  
- Probe point: `<x,y,z>`  
- Time window: `[t0 → t1, step=dt]`

**Findings**  
- Fundamental period: `<period>`  
- Main frequency: `<f0>`  
- Harmonics: `<f1, f2, …>` (ladder = `<k>` steps total)  
- Ratio structure: `<explicitly note 1:2:3 if harmonics are clean multiples of f0, otherwise describe deviations>`  
- Dominance: `<dom>`  
- Divergence ratio: `<dr>`  
- Reset events: `<count or []>`

**Classification**  
- Status: `<Inconclusive | Suggestive | Strong | Confirmed>`  
- Comment: `<short narrative>`  
- Implication: `<context — e.g., matches other probes; stability across offsets>`
