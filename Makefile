# ---------- GOLD PATH shortcuts (Probe → Spectrum → Pulse) ----------

PY ?= python

## Show help
help:
	@echo "Targets:"
	@echo "  make jhtdb-probe   flow=<name> x=<float> y=<float> z=<float> t0=<s> dt=<s> n=<int> slug=<tag>"
	@echo "  make jhtdb-analyze meta=<path/to/*.meta.json> out=<results/...analysis.json>"
	@echo "  make jhtdb-pulse   flow=<name> x=<float> y=<float> z=<float> t0=<s> dt=<s> n=<int> slug=<tag>"
	@echo "  make hopkins-run   # local run via analysis/hopkins_probe/"
	@echo "  make princeton-run # local run via analysis/princeton_probe/ (once subset arrives)"

# 1) Dataset → series (JHTDB SOAP)
jhtdb-probe:
	$(PY) tools/fd_connectors/jhtdb/jhtdb_loader.py \
	  --flow $(flow) --x $(x) --y $(y) --z $(z) \
	  --t0 $(t0) --dt $(dt) --nsteps $(n) --slug $(slug)

# 2) Series → analysis (PSD + 1:2:3 ladder)
jhtdb-analyze:
	$(PY) tools/fd_connectors/jhtdb/analyze_probe.py --meta $(meta) --out $(out)

# 3) Analysis → pulse (Φ-Mesh pulse YAML)
jhtdb-pulse:
	$(PY) tools/fd_connectors/jhtdb/make_pulse_from_probe.py \
	  --flow $(flow) --x $(x) --y $(y) --z $(z) \
	  --t0 $(t0) --dt $(dt) --nsteps $(n) --slug $(slug)

# Local runners (reuse shared pipeline/)
hopkins-run:
	cd analysis/hopkins_probe && $(PY) run_pipeline.py

princeton-run:
	cd analysis/princeton_probe && $(PY) run_pipeline.py
