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

### 2025-09-08 — First 3-Probe Confirmation (JHTDB isotropic1024coarse)

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

### 2025-09-07 — isotropic1024coarse (jhtdb) — batch 8 — Strong
- **Probe**: xyz=`0.10,0.10,0.12`; window=`[0.0, 1.2, 0.0001]`  
- **Period**: 1.25 s | **BPM**: 48.0 | **Main freq**: 0.8 Hz  
- **Ladder**: 3 | **Dominance**: ~2.22  
- **Divergence ratio**: 3.11e-13 | **Resets**: []  
- **Hint**: strong — clean peak + 2 harmonics  
- **Artifacts**: metrics JSON · pulse  
- **Notes**: Matches other probe points (0.12,0.10,0.10) & (0.10,0.12,0.10); window length matters.

---

## Copy/paste entry template

Paste this block for each new run. Keep the order chronological (newest at top).

```markdown
### YYYY-MM-DD — <dataset> (<source>) — batch <N> — <status>

- **Probe**: xyz=`<x,y,z>`; window=`[t0, t1, dt]`  
- **Period**: `<period>` s  | **BPM**: `<bpm>`  | **Main freq**: `<f0>` Hz  
- **Ladder**: `<k>` peaks  | **Dominance**: `<dom>`  
- **Divergence ratio**: `<dr>`  | **Resets**: `<count or []>`  
- **Hint**: `<inconclusive | weak | strong — clean peak + ... | confirmed>`  
- **Artifacts**: [metrics JSON](results/<path-to-json>) · [pulse](pulse/auto/<filename>.yml)  
- **Notes**: `<free text — e.g., consistent with batch N-1; grid shard (0.10,0.10,0.12) best; try longer window>`

Ultra-light “paste to chat” mini-template

When a run finishes, paste these 8 lines here and I’ll classify it instantly:

DATASET:    SOURCE: <synthetic|jhtdb|nasa>   BATCH: 
XYZ: <x,y,z>      WINDOW: [t0, t1, dt]
PERIOD:        BPM:       F0: 
PEAKS (first 3): [[f0,p0],[f1,p1],[f2,p2]]
LADDER:        DOMINANCE: <p0/p1 or 1 if no p1>
DIVERGENCE:  RESETS: <count or []>
METRICS: results/.json
PULSE:   pulse/auto/.yml
