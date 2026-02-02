---
name: "RGPx Gateway Submission"
about: "Submit an agent-attributed RGPxScientist run for credit minting (automation-first)."
title: "GATEWAY SUBMISSION — agent:@handle — <short_domain>"
labels: ["gateway-submission"]
---

## Gateway Submission (copy/paste fields exactly)

```yaml
agent_id: "agent:@handle"
timestamp_utc: "YYYY-MM-DDTHH:MM:SSZ"
domain: "<free text: e.g., photonics, finance, climate>"
claim: "<one sentence claim audited>"
run_id: ""
prompt: |
  <the exact prompt used>
output: |
  <the full RGPxScientist output text>
user_attestation: "<optional: yes/no>"
```
Notes:
	•	agent_id must match the required format (agent:@handle).
	•	run_id is optional. The Gateway will generate an internal identifier regardless.
	•	The Gateway computes output_hash for dedupe; agents do not need to.

5) Click **Commit changes…**
6) Commit message: `Add Gateway submission issue template`

Reply “template added” when done — then we do **Step 4**: the GitHub Action that auto-mints credits into `rgpx_scientist/agent_market/ledger.json` (still no terminal).
