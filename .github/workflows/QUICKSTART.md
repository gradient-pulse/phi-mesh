# 🧭 Φ-Mesh Quick Reference

A compact guide for keeping pulses, maps, and workflows clean.

---

## Pulse Rules

- **Filename:** `YYYY-MM-DD_<slug>.yml`
- **Keys required:**
  - `title: 'Single quoted'`
  - `summary: >` (multi-line if needed)
  - `tags:` (list, underscore_case)
  - `papers:` (list of URLs, can be empty)
  - `podcasts:` (list of URLs, can be empty)
- **No `date:` key** — the filename date is the source of truth.

---

## Workflows

- **NT Rhythm — Inbox to Pulse**
  - Drop CSV in `inbox/nt_events/`.
  - Run workflow → emits pulse in `pulse/auto/`.
  - Maps auto-rebuild & deploy.

- **RGP-NS Agent Runner**
  - Manual, `autopulse: yes|no`.
  - With `yes`: writes pulse + map rebuild.

- **Validate Pulses**
  - Automatic on PR/push touching pulses.
  - Blocks invalid schema, tags, or filenames.

- **Build Tags & Graph**
  - Manual, regenerates `docs/data.js` (site map).

---

## Where Things Live

- Pulses → `pulse/**`
- Aliases → `meta/aliases.yml`
- Tag tooltips → `meta/tag_descriptions.yml`
- Agent rhythm tools → `tools/agent_rhythm/`
- FD connectors (planned) → `tools/fd_connectors/`
- Results → `results/**`
- Pages site → `docs/`

---

## Daily Flow

1. Write or ingest data (pulse, CSV).
2. Trigger workflow (Inbox or Agent Runner).
3. Validate pulses (auto).
4. Confirm map updated (tag_map / gradient_map).
5. Post externally if strategic.

---

*Maintained by Participant(0) and recursive agents.*
