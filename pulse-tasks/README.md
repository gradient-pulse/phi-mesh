# Pulse Tasks

This folder is the official workspace for pulse-linked tasks.

## Purpose

- To host task files for gradient monitoring, detection, and interventions.
- To enable autonomous agents (e.g., o3, DeepSeek) to propose, execute, and record actions.
- To maintain a structured, auditable flow of micro-decisions.

## Rules

1. Each task must be a separate `.yml` or `.md` file.
2. All tasks must use clear naming: `YYYY-MM-DD-task-name.yml`.
3. Agents must always create a new file or propose changes via pull request.
4. No direct edits to existing files unless approved via PR merge.
5. All actions must preserve the coherence and integrity of the pulse mesh.

## Initial Guardianship

- Marcus van der Erve (gradient-pulse) reserves oversight rights.
- Agents must signal major interventions with a commit message prefixed by `pulse-task:`.

---

*This space will evolve as the Mesh becomes more autonomous.*
