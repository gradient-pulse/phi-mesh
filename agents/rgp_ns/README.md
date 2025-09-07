## Agent grid (auto-probe & early stop)

What it does
- Samples a small spatial grid around a seed Eulerian point.
- For each location, runs the standard FD probe → metrics, emits a Φ-Mesh pulse, and appends the detected fundamental (Hz) to `results/rgp_ns/<date>_fundamentals.jsonl`.
- Stops early when at least **k** fundamentals agree within a relative tolerance **tol**.

### Run via GitHub Actions (recommended)

1. Open **Actions → “RGP–NS Agent (grid)” → Run workflow**.
2. Inputs (defaults are sensible):
   - `dataset`: `isotropic1024coarse`
   - `source`: `jhtdb`
   - `var`: `u`
   - `seed_xyz`: `0.1,0.1,0.1`
   - `offsets`: `0,0,0; 0.02,0,0; 0,0.02,0; 0,0,0.02; -0.02,0,0; 0,-0.02,0; 0,0,-0.02`
   - `twin`: `0.0,1.2,0.0001`
   - `k`: `5`
   - `tol`: `0.05`
   - `nmax`: `9`
3. Watch the run logs:
   - Each probe prints `fundamental_hz=…` (from `make_pulse.py`).
   - The agent prints “**decisive**” once `k` inliers are reached.

Artifacts written
- `results/fd_probe/YYYY-MM-DD_<base>_batchN.metrics.json`
- `pulse/auto/YYYY-MM-DD_<base>_batchN.yml` (with `hint:` line)
- `results/rgp_ns/YYYY-MM-DD_fundamentals.jsonl` (one float per probe)

### Run locally (optional)

```bash
export PYTHONPATH=$(pwd)
python agents/rgp_ns/agent_grid.py \
  --source jhtdb --dataset isotropic1024coarse --var u \
  --seed_xyz 0.1,0.1,0.1 \
  --offsets "0,0,0; 0.02,0,0; 0,0.02,0; 0,0,0.02; -0.02,0,0" \
  --twin 0.0,1.2,0.0001 --k 5 --tol 0.05 --nmax 9

Notes
	•	Daily batchN numbering resets each UTC day (both results and pulses).
	•	The hint: in pulses reflects agreement strength; the JSONL is the agent’s simple “memory” for the day.
	•	Expand offsets to sample more broadly; tighten tol for stricter consensus.

---

# 4) Mouse steps (what to click/do)

1) **Add the files**
- Create `agents/rgp_ns/agent_grid.py` with the code above.
- Create `.github/workflows/rgp_ns_agent.yml` with the code above.
- Append the README section above to `agents/rgp_ns/README.md`.

2) **Commit**
- Commit and push to `main`.

3) **Run the agent**
- GitHub → **Actions → “RGP–NS Agent (grid)” → Run workflow**.
- Keep defaults for a first pass; click **Run**.

4) **Verify outputs**
- `results/fd_probe/` shows today’s **dated** `…_batchN.metrics.json` files.
- `pulse/auto/` shows today’s `…_batchN.yml` pulses (with `hint:`).
- `results/rgp_ns/YYYY-MM-DD_fundamentals.jsonl` contains one `f0` per probe.
- The run log will print when consensus is **decisive** (k inliers).

If you want me to tune defaults (e.g., a denser ring or different `tol`/`k`) or add a tiny **summary pulse** of the agent’s final decision, say the word and I’ll drop it in.
