# Princeton Teaser – Receipt → Run Checklist

**Upon Receipt**
1. Verify files received (velocity + metadata).
2. Record hash, file size, date, sender.
3. Confirm variables (ux, uy, uz).
4. Confirm grid and spacing.

**Preparation**
5. Place files into `data/ingest/princeton_teaser/`.
6. Validate with sanity script (`python check_data.py`).
7. Ensure parameters match GOLD PATH defaults.

**Execution**
8. Run: `make run_harmonics RUN=princeton_teaser`
9. Review `results/princeton_teaser/report.md`
10. Compare summary to JHTDB baseline (same τ).

**Post-Processing**
11. Archive raw and processed data.
12. Prepare optional report pulse if results confirm harmonic resonance.
