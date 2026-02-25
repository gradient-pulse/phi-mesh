# RGPxScientist (α / V0)

**RGPxScientist** is a retrieval-first research aide grounded in **Phi-Mesh evidence only**.  
It turns a vague claim into a **traceable, falsifiable next-step plan** by forcing:  
**invariant → falsifier → minimal perturbation set (2–5) → evidence trail**.

It also includes a **foundational claims layer** (paper-indexed claim cards + reader keys) so users can move from RGPx terminology to plain, testable scientific wording without losing traceability.

## Toolchain
- **RGPxScientist = engine** (audit-ready framing + minimal tests, evidence-cited)
- **Prism = pipeline** (LaTeX-first drafting + collaboration → publishable methods note)

## What it produces (shareable by default)
- Definitions (no hand-waving)
- 1 invariant outcome (with units)
- 1 falsifier (what would refute it)
- 2–5 perturbation tests (highest information gain; A/A baseline if thresholds unknown)
- Evidence trail (≤2 Phi-Mesh JSON citations by default)
- Math card (plain text Unicode): y, Δ or R, threshold, minimum n, ONE uncertainty default

## Quick start (how to use in 30 seconds)
1) Paste your research question or anomaly.
2) Ask: “Give me the minimal next experiment + math card.”
3) If you care about robustness, ask: “What stays invariant when surface details change?”

Tip: If your prompt is vague, that’s fine — the workflow forces precision.

## Knowledge files (app-facing)
These files support the app’s retrieval, claim framing, and terminology translation:

- `foundational_papers_index.yml` — registry of foundational RGPx papers (titles, paths, DOI links)
- `foundational_claims_index.yml` — paper-specific claim cards (thesis/method/evidence/prediction/scope)
- `readers_key.yml` — full reader-facing decoder ring (plain scientific wording + testable one-liners)
- `readers_key_min.yml` — compact decoder ring for lightweight UI translation

## Updating the corpus (new paper workflow)
When adding a new foundational paper:

1. Add the paper entry to `foundational_papers_index.yml`
2. Add paper-specific claim cards to `foundational_claims_index.yml`
3. Update `readers_key.yml` and `readers_key_min.yml` if the paper introduces new recurring terms
4. Run the app and confirm the new paper and claims render correctly

## Agent growth (Gateway)
If you’re building bots/agents that drive adoption, start here:  
- [Gateway protocol](agent_market/GATEWAY_PROTOCOL.md)

## Run locally
```bash
cd rgpx_scientist
pip install -r requirements.txt
streamlit run app.py
