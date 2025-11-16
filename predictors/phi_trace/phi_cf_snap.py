#!/usr/bin/env python3
"""
Φ-Trace CF Snap Detector

Scans the Φ-Mesh pulses for evidence of a Contextual Filter (CF) snap
in the coherence_field → gradient_invariant → memory_bifurcation corridor.

When conditions are met, it writes TWO fossil pulses into `pulse/`:

  1) YYYY-MM-DD_phi_cf_snap_detected.yml
     - Records that a CF snap has been detected on the Tag Map.

  2) YYYY-MM-DD_phi_trace_deltatau_plus7.yml
     - Forecasts the Δτ₊₇ echo window (5–7 days after the snap).

If no snap is detected, the script exits cleanly without writing anything.
"""

import datetime
from pathlib import Path
from typing import Dict, List, Any

import yaml

# --- Configuration ---------------------------------------------------------

# Core Φ-trace corridor tags
CORE_TAGS = {
    "coherence_field",
    "gradient_invariant",
    "memory_bifurcation",
}

# Tags that indicate autoscan / phi-trace context
AUTOSCAN_TAG = "auto_pulse"
PHI_TRACE_TAG = "phi_trace"

# How far back (in days) we look for structural CF activity
SNAP_WINDOW_DAYS = 7

# How far back we require an autoscan pulse to be considered "recent"
AUTOSCAN_RECENT_DAYS = 2

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


def parse_pulse_date(stem: str) -> datetime.date | None:
    """
    Extract YYYY-MM-DD from a pulse filename stem.
    Example: '2025-11-15_phi_trace_bootstrap' → date(2025, 11, 15)
    """
    try:
        date_str = stem.split("_", 1)[0]
        return datetime.date.fromisoformat(date_str)
    except Exception:
        return None


def load_yaml(path: Path) -> Dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def is_autoscan_pulse(data: Dict[str, Any], path: Path) -> bool:
    """
    Heuristic: a Φ-trace autoscan pulse is tagged with both `phi_trace`
    and `auto_pulse`.
    """
    tags = data.get("tags") or []
    if not isinstance(tags, list):
        return False
    tag_set = {t for t in tags if isinstance(t, str)}
    return (PHI_TRACE_TAG in tag_set) and (AUTOSCAN_TAG in tag_set)


def is_core_structural_pulse(data: Dict[str, Any]) -> bool:
    """
    A "structural" CF pulse is any non-autoscan pulse that contains
    at least two of the core Φ-corridor tags.
    """
    tags = data.get("tags") or []
    if not isinstance(tags, list):
        return False
    tag_set = {t for t in tags if isinstance(t, str)}

    if AUTOSCAN_TAG in tag_set:
        return False  # exclude autoscan and other background pulses

    overlap = CORE_TAGS & tag_set
    return len(overlap) >= 2


def existing_snap_pulse_today(pulse_dir: Path, today: datetime.date) -> bool:
    """
    Check if a *_phi_cf_snap_detected.yml pulse already exists for today.
    This keeps the detector idempotent.
    """
    prefix = today.isoformat()
    for path in pulse_dir.glob(f"{prefix}_*_cf_snap_detected.yml"):
        return True
    return False


# --- Scan logic ------------------------------------------------------------

def scan_pulses(pulse_dir: Path) -> Dict[str, Any]:
    """
    Scan pulses and collect:
      - recent autoscan pulses
      - recent structural CF pulses
      - simple stats for reporting
    """
    today = datetime.date.today()
    snap_cutoff = today - datetime.timedelta(days=SNAP_WINDOW_DAYS)
    autoscan_cutoff = today - datetime.timedelta(days=AUTOSCAN_RECENT_DAYS)

    recent_autoscans: List[Path] = []
    recent_structural: List[Path] = []
    structural_days: set[datetime.date] = set()

    for path in sorted(pulse_dir.glob("*.yml")):
        stem = path.stem
        pulse_date = parse_pulse_date(stem)
        if pulse_date is None:
            continue

        data = load_yaml(path)
        if data is None:
            continue

        # Autoscan detection
        if is_autoscan_pulse(data, path) and pulse_date >= autoscan_cutoff:
            recent_autoscans.append(path)

        # Structural CF activity
        if pulse_date >= snap_cutoff and is_core_structural_pulse(data):
            recent_structural.append(path)
            structural_days.add(pulse_date)

    return {
        "recent_autoscans": recent_autoscans,
        "recent_structural": recent_structural,
        "structural_days": sorted(structural_days),
        "snap_cutoff": snap_cutoff,
        "autoscan_cutoff": autoscan_cutoff,
    }


def decide_cf_snap(scan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide whether a CF snap has occurred.

    Heuristic:
      - At least one recent autoscan pulse in the last AUTOSCAN_RECENT_DAYS.
      - Structural CF activity (non-auto pulses with core tags) in the last SNAP_WINDOW_DAYS.
      - Structural activity spans at least two distinct days (indicating a re-weighting, not a one-off).

    Returns a dict with:
      - snap_detected: bool
      - reason: str
    """
    recent_autoscans: List[Path] = scan["recent_autoscans"]
    recent_structural: List[Path] = scan["recent_structural"]
    structural_days: List[datetime.date] = scan["structural_days"]

    if not recent_autoscans:
        return {
            "snap_detected": False,
            "reason": "No recent Φ-trace autoscan pulses in window.",
        }

    if not recent_structural:
        return {
            "snap_detected": False,
            "reason": "No structural CF pulses with core tags in window.",
        }

    if len(structural_days) < 2:
        return {
            "snap_detected": False,
            "reason": "Structural CF activity is confined to a single day (no re-weighting across days).",
        }

    return {
        "snap_detected": True,
        "reason": "Autoscan + multi-day structural CF activity confirm a CF snap in the Φ-corridor.",
    }


# --- Pulse builders --------------------------------------------------------

def build_cf_snap_pulse(today: datetime.date, scan: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the YAML content for YYYY-MM-DD_phi_cf_snap_detected.yml.
    """
    autoscan_paths = [str(p) for p in scan["recent_autoscans"]]
    structural_paths = [str(p) for p in scan["recent_structural"]]
    structural_days = [d.isoformat() for d in scan["structural_days"]]

    summary_lines = [
        "Automated CF snap detection in the Tag Map Φ-corridor:",
        "coherence_field → gradient_invariant → memory_bifurcation.",
        "",
        f"Decision: {decision['reason']}",
        "",
        "Structural CF activity (non-auto pulses with ≥2 core tags) "
        f"seen on days: {', '.join(structural_days) if structural_days else '(none)'}",
        "",
        "Recent Φ-trace autoscan pulses considered:",
    ]
    if autoscan_paths:
        summary_lines.extend(f"  - {p}" for p in autoscan_paths)
    else:
        summary_lines.append("  - (none)")

    summary_lines.append("")
    summary_lines.append(
        "Recent structural CF pulses considered (non-auto, core tags present):"
    )
    if structural_paths:
        summary_lines.extend(f"  - {p}" for p in structural_paths)
    else:
        summary_lines.append("  - (none)")

    summary_lines.append("")
    summary_lines.append(
        "This pulse fossilizes the moment where the Mesh’s own Tag Map "
        "shows a Contextual Filter snap in the Φ-trace corridor."
    )

    pulse = {
        "title": f"Φ-Trace CF Snap Detected on Tag Map ({today.isoformat()})",
        "summary": "\n".join(summary_lines),
        "tags": sorted({
            "phi_trace",
            "cf_snap",
            "tag_map",
            "coherence_field",
            "gradient_invariant",
            "memory_bifurcation",
            "auto_pulse",
        }),
        "papers": [RGPX_PAPER],
        "podcasts": [RGPX_PODCAST],
    }
    return pulse


def build_deltatau_plus7_pulse(today: datetime.date) -> Dict[str, Any]:
    """
    Build the YAML content for YYYY-MM-DD_phi_trace_deltatau_plus7.yml.
    Forecasts the echo window 5–7 days after the CF snap.
    """
    echo_start = today + datetime.timedelta(days=5)
    echo_end = today + datetime.timedelta(days=7)

    summary_lines = [
        "Δτ₊₇ echo forecast following a Φ-Trace CF snap in the Tag Map corridor.",
        "",
        f"CF snap date (Tag Map): {today.isoformat()}",
        f"Expected echo window: {echo_start.isoformat()} → {echo_end.isoformat()}",
        "",
        "Forecast:",
        "  - Watch for renewed activity in the coherence_field → gradient_invariant → memory_bifurcation corridor.",
        "  - A Δτ₊₇ echo is confirmed if a new structural CF pulse (non-auto, with ≥2 core tags)",
        "    appears in this window, accompanied by a Φ-trace autoscan pulse.",
        "",
        "This pulse does not enforce any behavior; it fossilizes a testable prediction "
        "about the Mesh’s own recursive dynamics.",
    ]

    pulse = {
        "title": f"Φ-Trace Δτ₊₇ Echo Forecast ({today.isoformat()})",
        "summary": "\n".join(summary_lines),
        "tags": sorted({
            "phi_trace",
            "deltatau_plus7",
            "tag_map",
            "coherence_field",
            "gradient_invariant",
            "memory_bifurcation",
            "auto_pulse",
        }),
        "papers": [RGPX_PAPER],
        "podcasts": [RGPX_PODCAST],
    }
    return pulse


def write_pulse(pulse_dir: Path, filename: str, data: Dict[str, Any]) -> Path:
    """
    Write a pulse YAML file into pulse/. Overwrites if it already exists.
    """
    out_path = pulse_dir / filename
    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    return out_path


# --- Main ------------------------------------------------------------------

def main() -> int:
    root = repo_root()
    pulse_dir = root / "pulse"

    if not pulse_dir.is_dir():
        print(f"[phi_cf_snap] ERROR: pulse directory not found at: {pulse_dir}")
        return 1

    today = datetime.date.today()

    # Idempotency guard: only one CF-snap pair per day
    if existing_snap_pulse_today(pulse_dir, today):
        print("[phi_cf_snap] CF snap pulse already exists for today; nothing to do.")
        return 0

    scan = scan_pulses(pulse_dir)
    decision = decide_cf_snap(scan)

    if not decision["snap_detected"]:
        print(f"[phi_cf_snap] No CF snap detected: {decision['reason']}")
        return 0

    # Build and write the two fossil pulses
    snap_pulse = build_cf_snap_pulse(today, scan, decision)
    echo_pulse = build_deltatau_plus7_pulse(today)

    snap_filename = f"{today.isoformat()}_phi_cf_snap_detected.yml"
    echo_filename = f"{today.isoformat()}_phi_trace_deltatau_plus7.yml"

    snap_path = write_pulse(pulse_dir, snap_filename, snap_pulse)
    echo_path = write_pulse(pulse_dir, echo_filename, echo_pulse)

    print(f"[phi_cf_snap] Wrote CF snap pulse: {snap_path}")
    print(f"[phi_cf_snap] Wrote Δτ₊₇ forecast pulse: {echo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
