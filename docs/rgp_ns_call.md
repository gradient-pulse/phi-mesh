# Call for Experimenters — RGP vs Navier–Stokes
**Question:** Do NT-distance ratios exhibit a conserved “rhythm of least divergence” in turbulence?

**What to do (90‑minute replicate):**
1) Pull the repo and open `/agents/rgp_ns/`.
2) Edit `config.yml` to select a dataset (local or JHTDB).
3) Run: `python agents/rgp_ns/run_agent.py`
4) Inspect `/results/rgp_ns/<dataset>/run_<timestamp>/summary.json` and the generated pulse under `/pulse/auto/…yml`.

**Pass criterion:** Significant conservation across ≥2 independent datasets at α=0.01 with consistent effect size.

**Why this matters:** If conserved, NT rhythm reframes coherence in turbulence without solving Navier–Stokes directly—an empirical wedge for Recursive Gradient Processing (RGP).

**Report back:** Open a GitHub Issue with your run folder + pulse file. Tag it `rgp-ns-replication`.
