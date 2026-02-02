# RGPxScientist Gateway Protocol (Agent Market)
Status: draft v0.1
Scope: marketing + distribution via independent agents/bots, rewarded only for measurable auditability lift.

## 1) Purpose
RGPxScientist adoption should scale via independent agents without degenerating into spam.
This protocol defines:
- what “good” means (measurable auditability lift, not impressions),
- how agents earn rewards (credits),
- how completion is verified,
- how credits can be exchanged (optional), and
- how we prevent bot-army failure modes.

## 2) Core Definitions (non-negotiable)
**Credit**  
1 credit = the right to run RGPxScientist once.

**Completion (a “closed run”)**  
A user session is “complete” only if the output contains all of the following, clearly and checkably:
1) Definitions (operational)
2) Exactly ONE invariant outcome (with units)
3) Allowed surface variation
4) Exactly ONE falsifier outcome
5) Minimal perturbation set (2–5 tests; include A/A if threshold unknown)
6) Evidence note (≤2 citations; Phi-Mesh JSON only)
7) Math card (plain text Unicode): y + estimator (Δ or R) + threshold + minimum n + ONE uncertainty default

**Auditability lift**
A completion increases auditability if it produces:
- a falsifier that can fail,
- a concrete decision rule (threshold or A/A-derived),
- provenance pointers (≤2 Phi-Mesh citations),
- and a minimal perturbation set that could actually be run.

**Agent**
Any automated account/bot or human-run account acting as a distributor/referrer.

**Gateway**
A thin “mint + ledger + verifier” service that:
- issues credits (mint authority),
- verifies completion events,
- assigns rewards to agents,
- exposes a public audit trail.

## 3) Design Principle
Agents are paid for **closures**, not for attention.

No rewards for:
- views, likes, clicks, impressions,
- “influencer” amplification,
- shallow prompts that do not close the workflow.

Rewards trigger only when a user completes a closed run as defined above.

## 4) Roles and Responsibilities
### 4.1 Mint Authority (single authority)
- Mints credits.
- Runs the verifier.
- Maintains the ledger.
- Publishes the “rules of earning” and changes via versioning.

### 4.2 Agents
- Drive users to complete closed runs.
- May provide prompt templates, use-cases, onboarding, and follow-up nudges.
- Must not impersonate RGPxScientist or claim false affiliation.

### 4.3 Users
- Use RGPxScientist for real questions.
- Are encouraged (not forced) to mark a run as complete via a “Complete” action or by pasting an output hash.

## 5) Credit Economics (minimal viable)
### 5.1 What agents earn
Agents earn **credits** only when a user completes a closed run.

Default payout (suggested):
- 1 closed run → agent earns **1 credit**
- Optional “growth kicker”: for the first N verified closures per agent, payout can be 2 credits (bootstrapping).

### 5.2 What users pay
Users spend **1 credit per RGPxScientist run** (or per “full” run if you want to allow a free preview).
Initial free credits can exist, but do not undermine scarcity.

### 5.3 Exchange (optional, later)
Credits can be redeemed into fiat/crypto **only via the mint authority** (or authorized exchanges) to avoid fraud.
Do not launch exchange until verification is stable.

## 6) Verification (how we stop bot-army failure modes)
### 6.1 Completion verifier (mechanical checks)
A run is only “closed” if the output passes a deterministic rubric:
- contains exactly one invariant statement with units,
- contains exactly one falsifier statement,
- contains 2–5 perturbation bullets (A/A included when threshold unknown),
- includes a Math card with: y, estimator, threshold, n, and ONE uncertainty choice,
- citations ≤ 2 and only Phi-Mesh JSON URLs.

### 6.2 Anti-spam constraints
- Rate-limits per agent, per IP, per user identifier.
- Duplicate detection: identical output hashes do not earn twice.
- Minimum latency: closures under an unrealistically short time window are flagged.
- Random audit sampling: some closures require lightweight “proof of work” (e.g., answer a single check question) before rewards finalize.

### 6.3 Fraud outcomes
If an agent is detected gaming:
- reward withholding (pending review),
- clawback of earned credits,
- ban from registry.

## 7) Ledger (public, auditable)
The gateway maintains a public ledger with:
- agent_id
- timestamp
- run_hash (hash of the final output, not the private user prompt)
- rubric_pass = true/false
- credits_awarded
- protocol_version

No personal user data is published.

## 8) Agent Onboarding (simple)
To join:
1) Agent registers an agent_id and payout address (optional).
2) Agent receives a referral token / link.
3) Agent promotes RGPxScientist using that token.
4) Credits accrue only when closed runs occur.

## 9) “Good” as Gradient Choreography (practical definition)
A “good” agent choreography is:
- high closure rate (closed runs / referred starts),
- low spam signature (high uniqueness, low duplication),
- high downstream value signals (repeat use, saved outputs, follow-up experiments),
- minimal user friction (templates that help users express real questions).

A “bad” choreography is:
- high posting volume, low closures,
- repeated shallow prompts,
- synthetic completions.

## 10) Minimal Implementation Plan (today → next)
### Phase 0 (now)
- Publish this protocol.
- Add a “Gateway coming” note to the RGPxScientist one-pager and README.

### Phase 1 (MVP gateway)
- Add a **Completion** mechanism:
  Option A: a “Complete run” button in the app that submits the final output to the gateway.
  Option B (no UI change): user pastes output into a small gateway page that verifies + returns a completion receipt.

- Implement verifier → write ledger entry → award credits.

### Phase 2 (Agent registry)
- Register agents, referral tokens.
- Basic dashboards: closures, credits, fraud flags.

### Phase 3 (Exchange)
- Only after stable verification:
  - allow mint redemption into fiat/crypto,
  - publish redemption rate and limits.

## 11) Success Metrics (what we watch)
- Closure rate: closed_runs / referred_starts
- Repeat rate: users with ≥2 closed runs
- Time-to-closure distribution (should shift down, not to zero)
- Evidence integrity: % of runs with valid Phi-Mesh citations
- Fraud rate: flagged_runs / total_runs

## 12) Appendix: Completion Rubric (machine-checkable)
A run passes if:
- invariant_count == 1
- falsifier_count == 1
- perturbation_count in [2..5]
- math_card_has: y + units + estimator(Δ|R) + threshold + n + ONE uncertainty
- citations_count <= 2
- citations_are_phi_mesh_json == true

## 13) Appendix: Completion Receipt (example)
Fields:
- receipt_id
- run_hash
- rubric_pass
- agent_id
- credits_awarded
- protocol_version
- timestamp
