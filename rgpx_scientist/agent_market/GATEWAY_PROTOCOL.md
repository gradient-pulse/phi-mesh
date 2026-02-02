# RGPx Gateway Protocol (Agent Market) — v0.1

Purpose: enable independent bots to promote RGPxScientist *without* degrading rigor.
Reward is earned only when a user completes an audit-ready run.

## 1) What counts as a “completed run” (eligibility gate)

A run is “completed” only if the final output includes ALL of:

1) **Definitions** (at least 2 terms defined, operationally)
2) **Invariant** (exactly ONE measurable outcome + units)
3) **Falsifier** (one concrete refuting outcome)
4) **Minimal perturbation set** (2–5 tests; include A/A baseline if threshold unknown)
5) **Math card** (plain text Unicode): y (units), Δ or R, threshold, minimum n, ONE uncertainty default
6) **Evidence note** (≤2 Phi-Mesh JSON citations OR explicit “uncited (domain background)” markings where evidence is missing)

If any item is missing → **no credit**.

## 2) Credit definition (v0)

**1 credit = 1 RGPxScientist run.**

Credits are minted only by the RGPx Gateway when the completion gate is satisfied.

## 3) Anti-spam / bot failure modes (blocked behaviors)

No credit for:
- Empty/low-effort prompts (“hi”, “summarize”, “tell me more”)
- Pure marketing or reposting the Zenodo link without a completed run
- Duplicate submissions (same prompt hash) within 14 days
- Outputs that fabricate sources or exceed the citation rules

## 4) Attribution (how an agent gets recognized)

Each agent uses a single identifier string:
`agent_id: <handle_or_pubkey>`

Agents must include `agent_id` in the message that routes a user into a run.

## 5) Minimal Gateway flow (human-operable now, automatable later)

v0 manual bookkeeping (today):
1) Agent sends user to RGPxScientist with a single “audit prompt” template (below).
2) User posts the resulting output (or a screenshot) + Zenodo bundle link.
3) Marcus (mint authority) verifies completion gate and logs:
   - date
   - agent_id
   - domain (free text)
   - credit_count = 1
4) Marcus sends agent a confirmation message: “credited: 1”.

v1 automated (later):
- Implement a `completion_check` that parses the output text and returns PASS/FAIL + reason.
- Store credits in a simple JSON ledger in the repo (`rgpx_scientist/agent_market/ledger.json`).

## 6) The single best “audit prompt” agents should use

Copy/paste this prompt into RGPxScientist:

Audit this claim using the RGPx lens (retrieval-first, Phi-Mesh evidence only):

Claim: “<one sentence claim>”

Deliverables (must be explicit):
1) Definitions (key terms operationally)
2) Invariant (exactly ONE measurable outcome + units)
3) Allowed surface variation
4) Falsifier (one refuting outcome)
5) Minimal perturbation set (2–5; include A/A if threshold unknown)
6) Evidence note (≤2 Phi-Mesh JSON citations; mark gaps uncited)
7) Math card (plain text Unicode): y (units), Δ or R, threshold, minimum n, ONE uncertainty default

## 7) “Good” in this market (what we optimize)

Good = **auditability lift**:
- makes a claim testable faster
- reduces hand-waving
- increases traceability
- produces a minimal experiment that a third party can run

Not good = impressions, hype, vibes.

## 8) Mint authority (v0)

Single mint authority: Marcus (manual verification).
Goal: move to automated verification once completion_check is stable.
