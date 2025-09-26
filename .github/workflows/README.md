# Φ-Mesh Workflows

A small set of GitHub Actions to keep **experiment → fossilization** predictable.

---

## Ground rules

- **Pulse filename:** `YYYY-MM-DD_<slug>_batch#.yml`  
- **Result filename:** `YYYY-MM-DD_<slug>_batch#.json`  
- **Minimal pulse keys:** `title`, `summary`, `tags`, `papers`, `podcasts`  
  *(No `date:` key; the date is derived from the filename.)*  
- **Tags:** `underscore_case`. New tags should always have a tooltip in `meta/tag_descriptions.yml`.

---

## Workflow catalog

### 1) GOLD PATH — Loader (Hopkins/Princeton) ✅

**File:** `.github/workflows/gold_path_loader.yml`  
**When:** manual (`workflow_dispatch`)  
**What:** runs the canonical Probe → Spectrum → Pulse pipeline.

- **Modes**  
  - `source=jhtdb` → pulls a single probe from JHTDB (SOAP), analyzes it, emits a pulse.  
  - `source=princeton` → ingests a local subset file, analyzes it, emits a pulse.  

- **Inputs (2 total)**  
  - `source`: `jhtdb | princeton`  
  - `params`: JSON blob parsed by the job (keeps us under the 10-input limit).  

- **Examples (paste in the params field)**  
  - JHTDB:  
    ```json
    {"flow":"isotropic1024coarse","x":0.1,"y":0.2,"z":0.3,"t0":0.0,"dt":0.0005,"nsteps":2400,"slug":"isotropic"}
    ```
  - Princeton:  
    ```json
    {"subset_path":"data/princeton/subset.h5","slug":"princeton_subset"}
    ```

- **Outputs**  
  - JHTDB raw series → `data/jhtdb/*.csv.gz` (+ `.meta.json`)  
  - Analysis → `results/fd_probe/*.analysis.json`  
  - Pulse → `pulse/auto/YYYY-MM-DD_<slug>_batch#.yml`

⸻

---

## 2) Validate Pulses

**File:** `.github/workflows/validate-pulses.yml`  
**When:** on PRs/pushes touching `pulse/**`  
**What:** enforces filename format + schema + tooltip checks.

---

## 3) Build Tags & Graph

**File:** `.github/workflows/build_tags_and_graph.yml`  
**When:** manual  
**What:** rebuilds `docs/data.js` for the Tag Map site.

---

## 4) Audit Missing Tooltips (optional)

**File:** `.github/workflows/audit-tooltips.yml`  
**When:** manual  
**What:** lists tags missing tooltips.

---

## 5) Clean Pulses (normalizer; use sparingly)

**File:** `.github/workflows/clean-pulses.yml`  
**When:** manual  
**What:** normalizes legacy pulses to the minimal schema.  

⚠️ **Archived:** RGP-NS Grid (legacy) → moved to archive or delete if unused. Superseded by the GOLD PATH, which is simpler and matches the current repo layout.

---

## Roles & Flow

1. **Experimenter** → Run **GOLD PATH** (Hopkins or Princeton).  
2. **Publisher** → If you only changed tags/tooltips, run **Build Tags & Graph**.

---

## Guardrails

- 🚫 No cron; everything is explicit (push or manual).  
- ✅ Only dedicated workflows emit pulses; validation enforces schema.  
- 🗂 Archives live under `pulse/archive/**`.  
- 📜 The site rebuilds when `docs/data.js` changes (committed by workflows).

---

## Troubleshooting Quickies

- **Pulse appears on GitHub but not on the site?**  
  → Ensure a workflow rebuilt `docs/data.js` (or run **Build Tags & Graph**).  
- **“Tags missing tooltips” warning?**  
  → Add one-liners in `meta/tag_descriptions.yml`, then rerun **Build Tags & Graph**.  
- **Unexpected/duplicate tags?**  
  → Check `meta/aliases.yml` and browser console logs from `normalize_data.js`.

---

## Where Things Live

- Pulses → `pulse/**`  
- Results → `results/**`  
- JHTDB data → `data/jhtdb/**`  
- Princeton subsets → `data/princeton/**`  
- GOLD PATH code →  
  - Loader/analyzer (Hopkins): `tools/fd_connectors/jhtdb/`  
  - Princeton runner: `analysis/princeton_probe/run_pipeline.py`  
- Shared analysis → `pipeline/`  
- Pages site → `docs/`
