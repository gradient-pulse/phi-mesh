# RGPxScientist (α / V0)

**RGPxScientist** is a retrieval-first research aide grounded in **Phi-Mesh evidence only**.  
It turns a vague claim into a **traceable, falsifiable next-step plan** by forcing:  
**invariant → falsifier → minimal perturbation set (2–5) → evidence trail**.

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

## Agent growth (Gateway)
If you’re building bots/agents that drive adoption, start here:  
- [Gateway protocol](agent_market/GATEWAY_PROTOCOL.md)

## Run locally
```bash
cd rgpx_scientist
pip install -r requirements.txt
streamlit run app.py
