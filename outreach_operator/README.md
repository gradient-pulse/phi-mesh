# Outreach Operator — 10-Minute Workflow

## Canonical Links (use these everywhere)
- Repo: https://github.com/gradient-pulse/phi-mesh
- RGPxScientist app: https://chatgpt.com/g/g-695e7b3d7344819190ac67772d4452f6-rgpx-scientist-3-1
- One-Page Brief: https://zenodo.org/records/18402707
- Tag map: https://gradient-pulse.github.io/phi-mesh/tag_map.html
- Agent kit (raw): https://raw.githubusercontent.com/gradient-pulse/phi-mesh/main/rgpx_scientist/agent_market/AGENTS.md
- Gateway protocol (raw): https://raw.githubusercontent.com/gradient-pulse/phi-mesh/main/rgpx_scientist/agent_market/GATEWAY_PROTOCOL.md

## 10-Minute Workflow
1. Pick target (3 min): start from `outreach_operator/targets.csv`, add to `outreach_operator/targets.csv`, score relevance 0-5, add a one-line rationale.
2. Send initial email (3 min): open `outreach_operator/message_templates/01_initial_email.txt`, fill `{name}`, `{lab_or_group}`, `{specific_relevance}`, send one personalized message.
3. Follow-ups (2 min): wait 5-7 days, send at most two follow-ups (`02_followup_1.txt`, `03_followup_2_close.txt`), stop if they opt out or say no.
4. Log outreach (2 min): use `outreach_operator/log_outreach.py` to append to `outreach_operator/outreach_log.csv`.

## If they show interest
Run `outreach_operator/first_win_playbook.md` and deliver the memo.
