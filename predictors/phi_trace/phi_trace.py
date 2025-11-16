#!/usr/bin/env python3
"""
Φ-Trace Auto-Scan

Scans the Φ-Mesh pulses for evidence of an active Φ-trace cluster on the Tag Map,
focused on the coherence_fields → gradient_invariant → memory_bifurcation corridor.

Outputs an auto-generated pulse in:
  pulse/YYYY-MM-DD_phi_trace_autoscan.yml

This is descriptive only: it does NOT change any other files.
"""

import datetime
import os
from pathlib import Path

import yaml


# --- Configuration ---------------------------------------------------------

# Tags that define the Φ-trace / memory-bifurcation cluster
CORE_TAGS = {
    "coherence_field",       # generative layer
    "gradient_invariant",    # Φₚ / invariant surface
    "memory_bifurcation",    # CF-level snap + relaxation
}

AUX_TAGS = {
    "phi_trace",
    "phi_p",
    "tag_map",
    "hardware_decoherence",
    "turbulence_signature",
}

# How many days back we consider "recent" for cluster activity
RECENT_DAYS = 7

# Standard RGPx references (per your note)
RGPX_PAPER = "https://doi.org/10.5281/zenodo.17566097"
RGPX_PODCAST = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-bde0c5847a55"
    "?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)


# --- Helpers ---------------------------------------------------------------

def repo_root() -> Path:
    """
    Resolve repository root as the parent of `predictors/`.
    This works even if the script is moved between predictor subfolders.
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


def load_yaml(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


# --- Core logic ------------------------------------------------------------

def scan_pulses(pulse_dir: Path):
    """
    Scan all pulses and collect:
      - per-tag counts
      - last-seen date per tag
      - list of recent pulses participating in the Φ-trace cluster
    """
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=RECENT_DAYS)

    tag_counts: dict[str, int] = {}
    tag_last_seen: dict[str, datetime.date] = {}
    recent_cluster_files: list[Path] = []

    for path in sorted(pulse_dir.glob("*.yml")):
        data = load_yaml(path)
        if not isinstance(data, dict):
            continue

        tags = data.get("tags") or []
        if not isinstance(tags, list):
            continue

        stem = path.stem
        pulse_date = parse_pulse_date(stem)
        if pulse_date is None:
            continue

        # Update tag stats
        for t in tags:
            if not isinstance(t, str):
                continue
            tag_counts[t] = tag_counts.get(t, 0) + 1
            if t not in tag_last_seen or pulse_date > tag_last_seen[t]:
                tag_last_seen[t] = pulse_date

        # Check whether this pulse participates in the Φ-trace corridor
        tag_set = set(tags)
        if CORE_TAGS & tag_set and pulse_date >= cutoff:
            recent_cluster_files.append(path)

    return {
        "tag_counts": tag_counts,
        "tag_last_seen": tag_last_seen,
        "recent_cluster_files": recent_cluster_files,
    }


def determine_cluster_status(scan_result: dict) -> dict:
    """
    Decide whether a Φ-trace cluster is "active" based on recent pulses.
    """
    tag_counts = scan_result["tag_counts"]
    tag_last_seen = scan_result["tag_last_seen"]
    recent_files = scan_result["recent_cluster_files"]

    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=RECENT_DAYS)

    # Are all core tags present at least once in the whole history?
    core_present = all(t in tag_counts for t in CORE_TAGS)

    # Are all core tags active within the recent window?
    core_recent = all(
        (t in tag_last_seen and tag_last_seen[t] >= cutoff) for t in CORE_TAGS
    )

    cluster_active = core_present and core_recent and len(recent_files) > 0

    return {
        "cluster_active": cluster_active,
        "core_present": core_present,
        "core_recent": core_recent,
        "recent_files": [str(p) for p in recent_files],
    }


def build_auto_pulse(scan_result: dict, status: dict) -> dict:
    """
    Build the YAML structure for the auto-generated Φ-trace pulse.
    """
    today = datetime.date.today().isoformat()
    tag_counts = scan_result["tag_counts"]
    tag_last_seen = scan_result["tag_last_seen"]

    # Human-readable status line
    if status["cluster_active"]:
        state_line = (
            "Φ-trace cluster is ACTIVE: all core tags are present and have "
            f"recent activity within the last {RECENT_DAYS} days."
        )
    elif status["core_present"]:
        state_line = (
            "Φ-trace cluster is LATENT: core tags exist historically but lack "
            f"coherent activity in the last {RECENT_DAYS} days."
        )
    else:
        state_line = (
            "Φ-trace cluster not yet formed: one or more core tags have no "
            "pulses registered in the Mesh."
        )

    # Compact per-tag summary for core + aux tags
    def tag_line(t: str) -> str:
        count = tag_counts.get(t, 0)
        last = tag_last_seen.get(t)
        if last is None:
            return f"- {t}: 0 pulses (never seen)"
        return f"- {t}: {count} pulses (last seen {last.isoformat()})"

    tag_status_lines = [tag_line(t) for t in sorted(CORE_TAGS | AUX_TAGS)]

    recent_files = status["recent_files"]
    if recent_files:
        recent_block = (
            "Recent Φ-trace-related pulses:\n"
            + "\n".join(f"  - {p}" for p in recent_files)
        )
    else:
        recent_block = "Recent Φ-trace-related pulses:\n  - (none in window)"

    pulse = {
        "title": f"Φ-Trace Autoscan — Tag Map Cluster Status ({today})",
        "summary": (
            "Automated Φ-trace scan over existing pulses in the Φ-Mesh.\n"
            "\n"
            f"{state_line}\n"
            "\n"
            "Core & auxiliary tag status:\n"
            + "\n".join(tag_status_lines)
            + "\n\n"
            + recent_block
            + "\n\n"
            "This auto-pulse does not introduce new theory. It records how the "
            "Tag Map’s existing pulses currently populate the Φ-trace corridor "
            "(coherence_field → gradient_invariant → memory_bifurcation) and "
            "whether a live cross-domain cluster is present."
        ),
        "tags": sorted(
            {
                "phi_trace",
                "auto_pulse",
                "tag_map",
                "coherence_field",
                "gradient_invariant",
                "memory_bifurcation",
            }
        ),
        "papers": [RGPX_PAPER],
        "podcasts": [RGPX_PODCAST],
    }

    return pulse


def write_pulse(pulse_dir: Path, pulse_data: dict) -> Path:
    """
    Write the auto-pulse to pulse/YYYY-MM-DD_phi_trace_autoscan.yml.
    Overwrites any existing file for the same day (idempotent).
    """
    today = datetime.date.today().isoformat()
    filename = f"{today}_phi_trace_autoscan.yml"
    out_path = pulse_dir / filename

    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(pulse_data, f, sort_keys=False, allow_unicode=True)

    return out_path


def main() -> int:
    root = repo_root()
    pulse_dir = root / "pulse"

    if not pulse_dir.is_dir():
        print(f"[phi_trace] ERROR: pulse directory not found at: {pulse_dir}")
        return 1

    scan_result = scan_pulses(pulse_dir)
    status = determine_cluster_status(scan_result)
    pulse = build_auto_pulse(scan_result, status)
    out_path = write_pulse(pulse_dir, pulse)

    print(f"[phi_trace] Wrote auto Φ-trace pulse: {out_path}")
    print(f"[phi_trace] Cluster active: {status['cluster_active']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
