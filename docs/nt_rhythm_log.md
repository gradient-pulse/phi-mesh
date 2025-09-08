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

## Copy/paste entry template

Paste this block for each new run. Keep the order chronological (newest at top).

```md
### YYYY-MM-DD — <dataset> (<source>) — batch <N> — <status>

- **Probe**: xyz=`<x,y,z>`; window=`[t0, t1, dt]`  
- **Period**: `<period>` s  | **BPM**: `<bpm>`  | **Main freq**: `<f0>` Hz  
- **Ladder**: `<k>` peaks  | **Dominance**: `<dom>`  
- **Divergence ratio**: `<dr>`  | **Resets**: `<count or []>`  
- **Hint**: `<inconclusive | weak | strong — clean peak + ... | confirmed>`
- **Artifacts**: [metrics JSON](results/<path-to-json>) · [pulse](pulse/auto/<filename>.yml)
- **Notes**: `<free text — e.g., consistent with batch N-1; grid shard (0.10,0.10,0.12) best; try longer window>`
