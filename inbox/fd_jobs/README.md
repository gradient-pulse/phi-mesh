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
