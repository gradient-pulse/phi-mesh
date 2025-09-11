# Φ-Mesh Workflows

This repo uses a small set of GitHub Actions to keep the Tag Map clean and make **experiment → fossilization** predictable.

---

## Ground rules

- **Pulse filename:** `YYYY-MM-DD_<slug>_batch#.yml`
- **Result filename:** `YYYY-MM-DD_<slug>_batch#.json`
- **Minimal pulse keys:** `title`, `summary`, `tags`, `papers`, `podcasts`
  *(No `date:` key; the date is derived from the filename.)*
- **Tags:** `underscore_case`. New tags should always have a tooltip in `meta/tag_descriptions.yml`.

---

## Workflow catalog

### 1) RGP-NS Grid
**File:** `.github/workflows/rgp-ns-grid.yml`  
**When:** manual (`workflow_dispatch`)  
**What:** runs the RGP-NS agent across multiple JHTDB/NASA probe points. Each shard writes results under `results/rgp_ns/.../batch#/` and emits an auto-pulse to `pulse/auto/`.

Inputs:
- **points** — newline-separated xyz triplets, e.g.

0.10,0.10,0.10

0.12,0.10,0.10

- **twin** — time window as `t0,t1,dt`, default `0.0,1.2,0.0001`.
- **title / tags** — forwarded to pulses.

Outputs:
- `results/rgp_ns/<timestamp>/batch#/*`
- `pulse/auto/YYYY-MM-DD_<slug>_batch#.yml`
- Map updates via normal build.

---

### 2) Validate Pulses
**File:** `.github/workflows/validate-pulses.yml`  
**When:** on PRs/pushes touching `pulse/**`  
**What:** enforces filename format, minimal schema, and tooltips.  
**Tip:** archives under `pulse/archive/**` are ignored (or enforce your own rule there).

---

### 3) Audit Missing Tooltips
**File:** `.github/workflows/audit-tooltips.yml` (if present)  
**When:** manual  
**What:** lists any tags in pulses without an entry in `meta/tag_descriptions.yml`.

---

### 4) Build Tags & Graph
**File:** `.github/workflows/build_tags_and_graph.yml`  
**When:** manual (ad-hoc)  
**What:** runs `generate_graph_data.py` to rebuild `docs/data.js`.  

*This replaces the older “Rebuild Maps” workflow (archived).*

---

### 5) Clean Pulses (schema normalizer)
**File:** `.github/workflows/clean-pulses.yml`  
**When:** manual, rarely  
**What:** normalizes legacy pulses to the minimal schema.  
⚠️ **Use with care**: review diffs.

---

### 6) One-time Mesh Maintenance
**File:** `.github/workflows/mesh-maintenance.yml`  
**When:** manual, exceptional changes only  
**What:** repo-wide hygiene tasks (aliases migrations, bulk renames).

---

### 7) Pages Build
**File:** GitHub’s `pages-build-deployment`  
**When:** automatic on pushes that update `docs/`  
**What:** publishes the Tag Map site. Any workflow that commits `docs/data.js` will trigger this.

---

## Roles & flow

1. **Agent/Experimenter**
   - Pushes results or CSVs.
   - Results Watch confirms arrivals.
   - Grid workflows fossilize into pulses and update the map.

2. **Publisher (you)**
   - Review Results Watch.
   - If publishing: run **RGP-NS Grid** (preferred).
   - For tooltip/tag edits only: run **Build Tags & Graph**.

---

## Guardrails

- 🚫 No cron jobs; everything is explicit (push or manual).  
- ✅ Only dedicated workflows emit pulses; validation enforces schema.  
- 🗂 Archives live under `pulse/archive/**`.  
- 📜 The site rebuilds when `docs/data.js` changes (committed by workflows).

---

## Troubleshooting quickies

- **Pulse appears on GitHub but not on the site?**  
  Ensure a workflow rebuilt `docs/data.js` (or run **Build Tags & Graph**). Check **Validate Pulses**.

- **“Tags missing tooltips” warning?**  
  Add one-liners in `meta/tag_descriptions.yml`, then run **Build Tags & Graph**.

- **Unexpected/duplicate tags?**  
  Check `meta/aliases.yml` and browser console logs from `normalize_data.js`.

---

## Publishing checklist (fast)

1. Review Results Watch.  
2. Run **RGP-NS Grid** (preferred).
3. Confirm **Validate Pulses** is green.  
4. Verify the Tag Map updated.

---

##Where Things Live

- Pulses → pulse/**
- Aliases → meta/aliases.yml
- Tag tooltips → meta/tag_descriptions.yml
- Agent rhythm tools → tools/agent_rhythm/
- FD connectors → tools/fd_connectors/
- Results → results/**
- Pages site → docs/

