Φ-Mesh Workflows

This repo uses a small set of GitHub Actions to keep the Tag Map clean and make experiment → fossilization predictable.

Naming & schema (ground rules)
	•	Pulse filename: YYYY-MM-DD_<slug>.yml
	•	Minimal pulse keys: title, summary, tags, papers, podcasts
(No date: key; date is derived from filename.)
	•	Tags: underscore_case. New tags should have a tooltip in meta/tag_descriptions.yml.

⸻

Workflow catalog

1) RGP-NS Results Watch

File: .github/workflows/results-watch.yml
When to run: Automatic on push to results/rgp_ns/**/summary.json
What it does: Posts a compact summary (dataset, p, effect size, significant) to the run page so you know results landed.
Who triggers: Agents/experimenters indirectly via pushing results.

Use it to decide: whether to publish pulses (see Agent Runner below).

⸻

2) RGP-NS Agent Runner

File: .github/workflows/rgp-ns-agent-runner.yml
When to run: Manual (workflow_dispatch)
Inputs: autopulse: yes|no
Env gate: ENABLE_AUTOPULSE=1 is set only when autopulse: yes.
	•	autopulse: no → compute results only; writes results/rgp_ns/.../summary.json
	•	autopulse: yes → also writes validator-clean pulses to pulse/auto/
	•	Filenames: YYYY-MM-DD_<dataset>.yml
	•	No date: field
	•	Rebuilds docs/data.js and commits

Who triggers: You (publisher) after reviewing Results Watch.

⸻

3) Validate Pulses

File: .github/workflows/validate-pulses.yml
When to run: On PRs/Pushes touching pulse/**
What it does: Enforces filename format, minimal schema, and tooltips.
Tip: Archives under pulse/archive/** are ignored (or use the negated glob in the job).

⸻

4) Audit Missing Tooltips

When to run: Manual (ad-hoc)
What it does: Lists any tags in pulses without a tooltip entry in meta/tag_descriptions.yml.

⸻

5) Build Tags & Graph

When to run: Manual (or on demand from other jobs)
What it does: Runs generate_graph_data.py to rebuild docs/data.js without touching anything else.

⸻

6) Clean Pulses (minimal schema)

When to run: Manual, rarely
What it does: Normalizes legacy pulses to the minimal schema (no date:, URL lists only, etc.).
Use with care: View diffs before merging.

⸻

7) One-time Mesh Maintenance

When to run: Manual, exceptional changes only
What it does: Repo-wide hygiene tasks (aliases migrations, bulk renames). Keep disabled by default.

⸻

8) pages-build-deployment

When to run: Automatic (GitHub Pages)
What it does: Publishes docs/ to the Tag Map site. Usually triggered after Build Tags & Graph.

⸻

Roles & flow (who does what)
	1.	Agent/Experimenter
	•	Runs compute locally or via a PR that adds results.
	•	Results Watch will notify when summary.json files arrive.
	2.	Publisher (you)
	•	Review Results Watch summary (p, effect size, significant).
	•	If you want to fossilize, run RGP-NS Agent Runner with autopulse: yes.
	•	If not yet, run with autopulse: no (results only).
	•	Optionally run Build Tags & Graph if you’ve edited tag tooltips without new pulses.

⸻

Guardrails (so surprises don’t happen)
	•	No cron jobs. All workflows are manual or results-watch only.
	•	Only agents/rgp_ns/run_agent.py writes pulses. Tools under tools/ that once wrote pulses are archived.
	•	The agent exits unless ENABLE_AUTOPULSE=1 (set by the workflow when autopulse: yes).
	•	Validator ignores pulse/archive/** or requires hyphenated dates there too—choose one and keep it consistent.

⸻

Troubleshooting quickies
	•	Pulse edits not showing on the site?
Check that Validate Pulses is green. If validation fails, the site won’t rebuild.
	•	“Tags missing tooltips” warning?
Add one-liners in meta/tag_descriptions.yml. Rebuild Tags & Graph.
	•	Unexpected auto pulses?
Confirm no other workflow references tools/harvest_* and that only the Agent Runner runs the agent.

⸻

Publishing checklist (fast)
	1.	Review Results Watch summary (significance).
	2.	If publish: RGP-NS Agent Runner → autopulse: yes.
	3.	Ensure Validate Pulses is green.
	4.	Confirm the Tag Map updated (hover new tags for tooltips).
