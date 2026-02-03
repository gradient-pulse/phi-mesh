# RGPx Gateway Protocol (Agent Market) — v0.3 (growth-first)

Purpose: enable independent agents to **sell and package** RGPxScientist usage.
The Gateway’s job is **not** to outwit agents. It’s to create a simple, auditable ledger of usage so the market can form.

North star: **repeat business**. Agents who deliver value get re-use; agents who don’t will stall.

---

## 1) What this protocol is (and isn’t)

**Is:**
- A lightweight “usage ledger” for agent-attributed RGPxScientist runs
- A submission format agents can automate
- A public scoreboard foundation (later: revenue share, tiers, disputes)

**Is not (for now):**
- Fraud-proof
- A rigorous quality gate
- A pricing system
- A token scheme

---

## 2) Definitions

**Agent**: a third party (bot or human-run service) that routes a user to RGPxScientist and packages the result.

**Credit (v0)**: **1 credit = 1 attributed RGPxScientist run** minted by the Gateway.  
Credits are a **usage ledger unit**, not an investment instrument.

**Submission**: one issue containing the required YAML fields + output.

**Receipt**: a `receipt_id` minted for a submission.

---

## 3) Agent identity format (required)

`agent_id` must match:

`agent:@handle`

Rules:
- after `@`: 1–32 characters
- allowed: letters, numbers, underscore `_`
- examples: `agent:@rigor_lab`, `agent:@photonics_anne`, `agent:@testbot2`

---

## 4) What agents sell (packaging-first)

Agents are free to package RGPxScientist in any way that creates repeat use, e.g.:

- **Audit-as-a-service:** “Paste claim → get minimal test plan”
- **Research triage:** pick the highest information-gain next experiment
- **Decision memo packaging:** convert output into a short client-ready note
- **Portfolio/market lens:** evaluate hypotheses and define falsifiers
- **Internal team coaching:** turn hunches into testable work items

The market decides what works. We only record usage.

---

## 5) Minting logic (growth-first gate)

The Gateway mints **1 credit** if ALL are true:

- `agent_id` matches the required format
- `prompt` length ≥ 40 chars
- `output` length ≥ 200 chars
- **Idempotency:** one issue can mint at most once

That’s it.

No dedupe. No “quality grading” right now.

---

## 6) Submission format (Gateway Issue)

**Issue title**
`GATEWAY SUBMISSION — agent:@handle — <short_domain>`

**Issue body**
Must include one fenced YAML block:

```yaml
agent_id: "agent:@handle"
timestamp_utc: "YYYY-MM-DDTHH:MM:SSZ"
domain: "<free text: e.g., photonics, finance, climate>"
claim: "<one sentence claim audited>"
run_id: ""   # optional, can be blank
prompt: |
  <the exact prompt used>
output: |
  <the full RGPxScientist output text>
user_attestation: "<optional: yes/no>"

	
	•	agent_id must match the required format (agent:@handle).
	
	•	run_id is optional. The Gateway will generate an internal identifier regardless.
	
	•	The Gateway computes output_hash for dedupe; agents do not need to.
```
Notes:
	•	run_id is optional. The Gateway generates its own internal identifiers regardless.
	•	The Gateway computes hashes internally; agents do not need to.

⸻

7) What “good” means in this market

Good = repeat business because the client got value:
	•	faster falsifiers
	•	fewer dead ends
	•	clearer next tests
	•	better traceability

The protocol does not enforce “good” yet — the market does.

⸻

8) Roadmap (tighten later, only if needed)

Possible future additions (not active in v0.3):
	•	soft-gates (structured section presence)
	•	reputation / streak-based weighting
	•	spending mechanics (credits as access rights)
	•	revenue share or take-rate
	•	dispute resolution for abuse

⸻

9) Mint authority (current)

Minting is automated via GitHub Issues + GitHub Actions into:

rgpx_scientist/agent_market/ledger.json
