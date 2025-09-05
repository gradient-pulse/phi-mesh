# FD Job Inbox

This folder is the **drop zone** for NT Rhythm probe jobs.  
Every YAML file added here will be picked up by the `agent_fd_jobs.yml` workflow, executed, and then moved to `_done/` or `_error/`.

---

## 📂 Folder Structure

- `inbox/fd_jobs/` — active job queue  
- `_done/` — completed jobs (archived automatically)  
- `_error/` — failed jobs (inspect and retry if needed)  

---

## 📝 Job File Schema

A minimal job file looks like this:

```yaml
# inbox/fd_jobs/20250905__synth_demo.yml
source: synthetic        # one of: synthetic, nasa, jhtdb
dataset: 'demo'          # slug or path (auto-sanitized)
var: 'u'                 # variable name
xyz: [0.1, 0.1, 0.1]     # probe coordinates
window: [0.0, 10.0, 0.01]# [t0, t1, dt]
title: 'NT Rhythm — FD Probe'
tags: ['nt_rhythm','turbulence','navier_stokes','rgp']

🔄 Workflow
	1.	Drop a job YAML into inbox/fd_jobs/.
	2.	GitHub Actions agent picks it up.
	3.	Results written to results/fd_probe/ (metrics JSON).
	4.	Matching pulse emitted into pulse/auto/.
	5.	Job YAML is moved to _done/ (or _error/ on failure).

⸻

🚦 Usage Rules
	•	❌ Do not edit _done/ or _error/ manually.
	•	✅ Always create new jobs in the root of this folder.
	•	⚠️ Job filenames must include a date prefix: YYYYMMDD__slug.yml.
Example: 20250905__nasa_demo.yml.

⸻

📌 Summary

This inbox allows the agent to act like a job queue:
	•	Users: just drop jobs here.
	•	Agent: processes them, archives them, updates results + pulses.
	•	Traceability: preserved via _done/ and _error/ subfolders.
