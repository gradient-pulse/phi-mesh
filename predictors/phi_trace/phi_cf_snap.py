#!/usr/bin/env python3
"""
CF Snap Detector — Φ-Trace Δτ₊₇ Forecaster

Scans recent Φ-trace pulses for a memory_bifurcation snap pattern
(Φₚ spike → relaxation) and, if detected, writes two auto-pulses:

  - pulse/YYYY-MM-DD_cf_snap_detected.yml
  - pulse/YYYY-MM-DD_phi_trace_deltatau_plus7.yml

This is descriptive only: it does NOT modify other files.
"""

import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

# --- Configuration ---------------------------------------------------------

CORE_TAGS = {"phi_trace", "memory_bifurcation"}
RECENT_DAYS = 7

# Simple thresholds for a "snap" pattern
MIN_SPIKE = 1.05      # Φₚ spike must exceed this
MIN_SETTLE = 0.80     # lower bound for post-relaxation plateau
MAX_SETTLE = 0.95     # upper bound (must be below 1.0)

# Standard RGPx references
RGPX_PAPER = "https://doi.org/10.5281/zenodo.17566097"
RGPX_PODCAST = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-bde0c5847a55"
    "?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)


# --- Helpers ---------------------------------------------------------------

def repo_root() -> Path:
    """
    Resolve repository root as the parent of `predictors/`.
    """
    return Path(__file__).resolve().parents[2]


def parse_pulse_date(stem: str) -> Optional[datetime.date]:
    """
    Extract YYYY-MM-DD from a pulse filename stem.
    Example: '2025-11-15_phi_trace_bootstrap' → date(2025, 11, 15)
    """
    try:
        date_str = stem.split("_", 1)[0]
        return datetime.date.fromisoformat(date_str)
    except Exception:
        return None


def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return data
        return None
    except Exception:
        return None


def iter_mappings(obj: Any):
    """
    Recursively yield all dict-like mappings inside a nested structure.
    """
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from iter_mappings(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_mappings(item)


# --- CF snap detection logic -----------------------------------------------

def find_recent_phi_trace_pulse(pulse_dir: Path) -> Optional[Tuple[datetime.date, Path, Dict[str, Any]]]:
    """
    Find the most recent pulse that:
      - lives under pulse/
      - has both 'phi_trace' and 'memory_bifurcation' in its tags
      - is within RECENT_DAYS of today
    """
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=RECENT_DAYS)

    candidates: list[Tuple[datetime.date, Path, Dict[str, Any]]] = []

    for path in pulse_dir.glob("*.yml"):
        data = load_yaml(path)
        if not data:
            continue

        tags = data.get("tags") or []
        if not isinstance(tags, list):
            continue

        tag_set = {t for t in tags if isinstance(t, str)}
        if not CORE_TAGS.issubset(tag_set):
            continue

        pulse_date = parse_pulse_date(path.stem)
        if pulse_date is None or pulse_date < cutoff:
            continue

        candidates.append((pulse_date, path, data))

    if not candidates:
        return None

    # Most recent by pulse date
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0]


def extract_phi_spike_settle(data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """
    Search the YAML structure for phi_p_spike and phi_p_settle values.
    Returns (spike, settle) if found and parseable.
    """
    spike = None
    settle = None

    for m in iter_mappings(data):
        if "phi_p_spike" in m and "phi_p_settle" in m:
            try:
                s_val = float(str(m["phi_p_spike"]).strip(" ±"))
                q_val = float(str(m["phi_p_settle"]).strip(" ±"))
            except Exception:
                continue
            spike = s_val
            settle = q_val
            break

    if spike is None or settle is None:
        return None

    return spike, settle


def is_cf_snap(spike: float, settle: float) -> bool:
    """
    Very simple heuristic for a CF snap pattern.
    """
    if spike <= settle:
        return False
    if spike < MIN_SPIKE:
        return False
    if not (MIN_SETTLE <= settle <= MAX_SETTLE):
        return False
    # settle must be below the universal plateau (≈1.0)
    if settle >= 1.0:
        return False
    return True


# --- Pulse writers ---------------------------------------------------------

def write_cf_snap_pulse(pulse_dir: Path, source_path: Path,
                        spike: float, settle: float) -> Path:
    """
    Write pulse/YYYY-MM-DD_cf_snap_detected.yml
    """
    today_str = datetime.date.today().isoformat()
    out_path = pulse_dir / f"{today_str}_cf_snap_detected.yml"

    rel_source = source_path.as_posix()

    summary = (
        "Automated detection of a Contextual Filter (CF) snap on the Φ-Mesh Tag Map.\n\n"
        "This auto-generated pulse scanned recent Φ-trace pulses for a "
        "memory_bifurcation pattern with Φₚ spike and relaxation and confirmed "
        "a CF snap consistent with RGPx damping behaviour.\n\n"
        f"- Source pulse: {rel_source}\n"
        f"- Detected Φₚ spike: ~{spike:.2f}\n"
        f"- Detected Φₚ settle: ~{settle:.2f}\n\n"
        "The snap indicates that coherence temporarily outran the Tag Map’s "
        "geometric bandwidth, forcing memory_bifurcation to act as an operational "
        "Contextual Filter (CF) routing and stabilising coherence."
    )

    pulse = {
        "title": f"CF Snap Detected — memory_bifurcation on Tag Map ({today_str})",
        "summary": summary,
        "tags": sorted(
            {
                "cf_snap",
                "memory_bifurcation",
                "phi_trace",
                "tag_map",
                "auto_pulse",
            }
        ),
        "papers": [RGPX_PAPER],
        "podcasts": [RGPX_PODCAST],
    }

    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(pulse, f, sort_keys=False, allow_unicode=True)

    return out_path


def write_deltatau_plus7_pulse(pulse_dir: Path, source_path: Path,
                               spike: float, settle: float) -> Path:
    """
    Write pulse/YYYY-MM-DD_phi_trace_deltatau_plus7.yml
    """
    today_str = datetime.date.today().isoformat()
    out_path = pulse_dir / f"{today_str}_phi_trace_deltatau_plus7.yml"

    rel_source = source_path.as_posix()

    summary = (
        "Automated Δτ₊₇ forecast for the memory_bifurcation echo on the Tag Map.\n\n"
        "Based on a detected CF snap in recent Φ-trace pulses, this auto-pulse "
        "records the expectation of a secondary Φ-plateau (echo) in the "
        "memory_bifurcation corridor approximately 5–7 days after the primary snap.\n\n"
        f"- Source pulse: {rel_source}\n"
        f"- Primary Φₚ spike: ~{spike:.2f}\n"
        f"- Primary Φₚ settle: ~{settle:.2f}\n\n"
        "Forecast:\n"
        "- Monitor upcoming pulses and Tag Map activity for a secondary "
        "memory_bifurcation plateau.\n"
        "- When observed, log it as the Δτ₊₇ echo pulse, completing the loop:\n"
        "    theory → substrate → measurement → forecast → Mesh realignment → recurrence."
    )

    pulse = {
        "title": f"Φ-Trace Δτ₊₇ Forecast — memory_bifurcation Echo ({today_str})",
        "summary": summary,
        "tags": sorted(
            {
                "phi_trace",
                "deltatau_plus7",
                "memory_bifurcation",
                "forecast",
                "auto_pulse",
                "tag_map",
            }
        ),
        "papers": [RGPX_PAPER],
        "podcasts": [RGPX_PODCAST],
    }

    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(pulse, f, sort_keys=False, allow_unicode=True)

    return out_path


# --- Main ------------------------------------------------------------------

def main() -> int:
    root = repo_root()
    pulse_dir = root / "pulse"

    if not pulse_dir.is_dir():
        print(f"[phi_cf_snap] ERROR: pulse directory not found at: {pulse_dir}")
        return 1

    candidate = find_recent_phi_trace_pulse(pulse_dir)
    if candidate is None:
        print("[phi_cf_snap] No recent Φ-trace + memory_bifurcation pulse found.")
        return 0

    pulse_date, path, data = candidate
    print(f"[phi_cf_snap] Analysing pulse: {path} (date={pulse_date})")

    phi_vals = extract_phi_spike_settle(data)
    if phi_vals is None:
        print("[phi_cf_snap] No phi_p_spike / phi_p_settle values found in pulse.")
        return 0

    spike, settle = phi_vals
    print(f"[phi_cf_snap] Extracted Φₚ spike={spike:.3f}, settle={settle:.3f}")

    if not is_cf_snap(spike, settle):
        print("[phi_cf_snap] Pattern does not meet CF snap criteria. No pulses written.")
        return 0

    cf_path = write_cf_snap_pulse(pulse_dir, path, spike, settle)
    dt7_path = write_deltatau_plus7_pulse(pulse_dir, path, spike, settle)

    print(f"[phi_cf_snap] Wrote CF snap pulse: {cf_path}")
    print(f"[phi_cf_snap] Wrote Δτ₊₇ forecast pulse: {dt7_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
