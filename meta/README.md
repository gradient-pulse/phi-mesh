# Φ-Mesh Meta Framework

The `meta/` directory defines the coherence logic of the Φ-Mesh —  
how tags, pulses, and datasets are recursively classified and synthesized.

---

## 🌀 Recursive Gradient Phases (RGPx Cycles)

| Cycle | Symbol | Function | Description |
|-------|---------|-----------|--------------|
| **Cycle 1** | **Δ — Emergence** | Difference & initiation | Birth of new gradients, tension, discovery, potential. |
| **Cycle 2** | **GC — Resonance** | Alignment & rhythm | Rhythmic propagation, feedback, mutual adaptation. |
| **Cycle 3** | **CF — Integration / Closure** | Stability & attractors | Context formation, stabilization, integration of coherence. |
| **Open** | *(Unclassified)* | Undefined | Transitional or yet-to-be-aligned gradients. |

---

## 🧭 Tag Phase Logic

Phase assignment is derived from:
1. `meta/tag_phase_overrides.yml` — explicit mappings  
2. Heuristic inference by build scripts (Δ = initiation, GC = resonance, CF = closure)  
3. Manual curation during pulse creation

When uncertain, tags default to **Open** until the Mesh converges.

---

## ⚙️ Build Pipeline Overview

| Script | Purpose |
|--------|----------|
| **update_tag_index.py** | Extracts tags from pulses and updates `meta/tag_index.yml` |
| **build_tag_taxonomy_html.py** | Generates the visual taxonomy from `tag_taxonomy.yml` |
| **build_tag_browser.py** | Renders the interactive tag map |
| **generate_tag_map.py** | Links tags to pulses, papers, and podcasts |
| **tag_phase_overrides.yml** | Defines phase assignments (Δ / GC / CF) for selected tags |

---

## 🌐 Interpretation Principle

Recursive Gradient Processing (RGPx) treats every phenomenon as a loop:
