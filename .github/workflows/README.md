# Φ-Mesh Workflows

This repo uses a small set of GitHub Actions to keep the Tag Map clean and make **experiment → fossilization** predictable.

---

## Ground rules

- **Pulse filename:** `YYYY-MM-DD_<slug>.yml`
- **Minimal pulse keys:** `title`, `summary`, `tags`, `papers`, `podcasts`
  *(No `date:` key; the date is derived from the filename.)*
- **Tags:** `underscore_case`. New tags should always have a tooltip in `meta/tag_descriptions.yml`.

---

## Workflow catalog

### 1) Results Watch (RGP-NS)
**File:** `.github/workflows/results-watch.yml`  
**When:** automatic on push to `results/rgp_ns/**/summary.json`  
**What:** posts a compact summary (dataset, p, effect size, significant) to the run page so you know results landed.  
**Who:** agents/experimenters via result pushes.

---

### 2) RGP-NS Agent Runner
**File:** `.github/workflows/rgp-ns-agent-runner.yml`  
**When:** manual (`workflow_dispatch`)  
**Input:** `autopulse: yes|no` (gated by `ENABLE_AUTOPULSE=1` when `yes`)

- `autopulse: no` → compute results only (writes `results/rgp_ns/.../summary.json`)
- `autopulse: yes` → emits pulses to `pulse/auto/YYYY-MM-DD_<dataset>.yml`, rebuilds maps (`docs/data.js`), commits

**Who:** you (publisher) after reviewing Results Watch.

---

### 3) Validate Pulses
**File:** `.github/workflows/validate-pulses.yml`  
**When:** on PRs/pushes touching `pulse/**`  
**What:** enforces filename format, minimal schema, and tooltips.  
**Tip:** archives under `pulse/archive/**` are ignored (or enforce your own rule there).

---

### 4) Audit Missing Tooltips
**File:** `.github/workflows/audit-tooltips.yml` (if present)  
**When:** manual  
**What:** lists any tags in pulses without an entry in `meta/tag_descriptions.yml`.

---

### 5) Build Tags & Graph
**File:** `.github/workflows/build_tags_and_graph.yml`  
**When:** manual (ad-hoc)  
**What:** runs `generate_graph_data.py` to rebuild `docs/data.js` only.

---

### 6) Clean Pulses (schema normalizer)
**File:** `.github/workflows/clean-pulses.yml`  
**When:** manual, rarely  
**What:** normalizes legacy pulses to the minimal schema.  
⚠️ **Use with care**: review diffs.

---

### 7) One-time Mesh Maintenance
**File:** `.github/workflows/mesh-maintenance.yml`  
**When:** manual, exceptional changes only  
**What:** repo-wide hygiene tasks (aliases migrations, bulk renames).

---

### 8) Pages Build
**File:** GitHub’s `pages-build-deployment`  
**When:** automatic on pushes that update `docs/`  
**What:** publishes the Tag Map site. Any workflow that commits `docs/data.js` will trigger this.

---

### 9) NT Rhythm — Inbox → Pulse
**File:** `.github/workflows/nt_rhythm_inbox.yml`  
**When:** push to `inbox/nt_events/**.csv` or manual dispatch  
**What:** CSV → metrics → `pulse/auto/YYYY-MM-DD_<dataset>.yml` → rebuild maps.

Inputs (dispatch): CSV path, time column (default `t`), title, dataset slug, tags.  
On push mode the dataset slug derives from the file stem.

---

### 10) NT Rhythm — FD Probe → Pulse (JHTDB/NASA)
**File:** `.github/workflows/fd_probe.yml`  
**When:** manual  
**What:** calls `tools/fd_connectors/run_fd_probe.py` (JHTDB/NASA stub), computes NT metrics, emits a pulse, rebuilds maps.

Inputs: source (`jhtdb|nasa`), dataset, var, point `(x,y,z)`, `t0,t1,dt`, title, tags.  
Dev tip: set secret `JHTDB_OFFLINE=1` to use synthetic data until real API auth is wired.

---

### 11) Rebuild Maps (docs/data.js)
**File:** `.github/workflows/rebuild_maps.yml`  
**When:** manual  
**What:** just rebuilds `docs/data.js` from pulses and commits.

---

## Roles & flow

1. **Agent/Experimenter**
   - Pushes results or CSVs.
   - Results Watch confirms arrivals.
   - Inbox/FD workflows can fossilize into pulses and update the map.

2. **Publisher (you)**
   - Review Results Watch.
   - If publishing RGP-NS runs: **Agent Runner** → `autopulse: yes`.
   - For CSV/FD probes: run their workflows directly.
   - For tooltip/tag edits only: run **Rebuild Maps**.

---

## Guardrails

- 🚫 No cron jobs; everything is explicit (push or manual).  
- ✅ Only dedicated workflows emit pulses; validation enforces schema.  
- 🗂 Archives live under `pulse/archive/**`.  
- 🔒 Autopulse gated via `ENABLE_AUTOPULSE=1` in the Agent Runner.  
- 📜 The site rebuilds when `docs/data.js` changes (committed by workflows).

---

## Troubleshooting quickies

- **Pulse appears on GitHub but not on the site?**  
  Ensure a workflow rebuilt `docs/data.js` (or run **Rebuild Maps**). Check **Validate Pulses**.

- **“Tags missing tooltips” warning?**  
  Add one-liners in `meta/tag_descriptions.yml`, then run **Rebuild Maps**.

- **Unexpected/duplicate tags?**  
  Check `meta/aliases.yml` and browser console logs from `normalize_data.js`.

---

## Publishing checklist (fast)

1. Review Results Watch (if RGP-NS).  
2. Run **Agent Runner** (`autopulse: yes`) or **Inbox → Pulse** or **FD Probe → Pulse**.  
3. Confirm **Validate Pulses** is green.  
4. Verify the Tag Map updated.

## RGP–NS grid

Trigger **RGP–NS grid (JHTDB → agent runs → results + pulse)** to fan out agent runs across multiple probe points.

Inputs:
- **points** — newline-separated xyz triplets, e.g.

0.10,0.10,0.10
0.12,0.10,0.10

- **twin** — time window as `t0,t1,dt`, default `0.0,1.2,0.0001`.
- **title / tags** — forwarded to pulses.

Outputs:
- `results/rgp_ns/<timestamp>/batch1/*`
- `pulse/auto/YYYY-MM-DD_rgpnsgird_…yml` (from the agent)
- Tag map updates via normal map build.

agents/rgp_ns/README.md (add under “Run (dry test)”)

## Run via GitHub Actions (grid)

Use **RGP–NS grid** to run the agent across multiple JHTDB probe points.

1. Open *Actions → RGP–NS grid* → *Run workflow*.
2. Paste probe points (one per line), set `twin` if needed, run.
3. Results will appear under `results/rgp_ns/<timestamp>/batch1/`.
4. Each shard emits its own pulse in `pulse/auto/` (shows on the Tag Map).

