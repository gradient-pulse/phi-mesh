# Tools

This folder contains helper scripts used by the Φ-Mesh workflows.

- **agent_rhythm/** — logic for agent-driven NT Rhythm analysis.  
- **fd_connectors/** — connectors for FD probe sources (JHTDB, Princeton, NASA, synthetic).  
  - Each connector subfolder (e.g. `jhtdb/`, `princeton/`) should contain an `__init__.py` to make it importable as a package.  
- **archive/** — deprecated or experimental tools, kept for reference.  
- **validate_pulses.py** — checks YAML pulses for schema consistency.  
- **__init__.py** — makes this folder a Python package (do not remove).  

---

## 📦 Packaging

- The presence of `__init__.py` files ensures that both `tools/` and its submodules (`fd_connectors/jhtdb`, `fd_connectors/princeton`, etc.) can be imported in Python workflows.  
- This symmetry prevents subtle import errors and keeps CI workflows stable.  

---

## 🧭 Policy

- ✅ Extend tools here only if scripts are shared across workflows.  
- ✅ Keep `archive/` for deprecated code — never delete history.  
- ❌ Do not remove `__init__.py` files, even if empty.  
