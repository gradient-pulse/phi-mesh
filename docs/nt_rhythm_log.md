# NT Rhythm — Running Log

A lightweight, human-readable roll-up of probe/grid runs while we close in on nature’s rhythm.  
Each entry links back to the canonical **metrics JSON** and **pulse** the workflows produced.

---

## How we classify evidence (quick rubric)

- **Inconclusive** — weak or noisy spectrum; single peak with no meaningful harmonics; dominance < **1.1** or ladder < **2**.
- **Suggestive** — discernible main peak + 1 harmonic (**ladder = 2**) and dominance between **1.1–1.5**; similar period shows up in 2+ runs.
- **Strong** — clean main peak + ≥2 harmonics (**ladder ≥ 3**) with dominance ≥ **1.5** and consistent period across windows/points on the same dataset.
- **Confirmed (grid)** — multiple spatial probes agree (same period ±5–10%) and “Strong” holds across at least two windows.

> **Terms**
> - **ladder**: number of spectral peaks forming a harmonic ladder (1 = main only; 2 = main + 1 harmonic; etc.)  
> - **dominance**: ratio of the main peak power to the second peak power (>= 1).

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
- Ratio structure: `<describe if clean 1:2:3>`  
- Dominance: `<dom>`  
- Divergence ratio: `<dr>`  
- Reset events: `<count or []>`

**Classification**  
- Status: `<Inconclusive | Suggestive | Strong | Confirmed>`  
- Comment: `<short narrative>`  
- Implication: `<context — e.g., matches other probes; stability across offsets>`

---
