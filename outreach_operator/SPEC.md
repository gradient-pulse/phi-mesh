# Outreach Operator Spec — Academic Acquisition for RGPxScientist

## Canonical Links (must use in all outreach)
- Repo: https://github.com/gradient-pulse/phi-mesh
- RGPxScientist app: https://chatgpt.com/g/g-695e7b3d7344819190ac67772d4452f6-rgpx-scientist-3-1
- One-Page Brief: https://zenodo.org/records/18402707
- Tag map: https://gradient-pulse.github.io/phi-mesh/tag_map.html
- Agent kit (raw): https://raw.githubusercontent.com/gradient-pulse/phi-mesh/main/rgpx_scientist/agent_market/AGENTS.md
- Gateway protocol (raw): https://raw.githubusercontent.com/gradient-pulse/phi-mesh/main/rgpx_scientist/agent_market/GATEWAY_PROTOCOL.md

## Objective
Acquire academic users for RGPxScientist by offering a fast, high-signal “first win” memo that demonstrates value and creates an internal champion.

## Workflow
1. Identify high-fit academic labs and PIs using public signals.
2. Score relevance (0-5) and log targets.
3. Send a single high-signal initial email or DM with clear opt-out.
4. If no reply, send up to two follow-ups (max 2).
5. When interested, run the first-win playbook and deliver a one-page memo.
6. Ask for forwarding to an internal champion and/or collaborator.

## Rules (strict)
- No spam: contact only verified, relevant academic targets.
- Opt-out required: every message includes a clear opt-out line.
- High-signal only: lead with specific relevance and a concrete benefit.
- Respect timing: max 2 follow-ups total; stop if no response.
- No mass emailing: personalize every message.

## Success Metrics
- Primary: first wins/week (target: steady weekly increases).
- Secondary: reply rate, first-win delivery rate, internal champion referrals.

## Data Hygiene
- Maintain a single source of truth in `outreach_operator/targets_schema.csv`.
- Log every outreach attempt in `outreach_operator/outreach_log.csv`.
- Update `status` and `next_followup` after each touch.
