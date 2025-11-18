import os
from datetime import datetime, timedelta

import yaml


PULSE_DIR = "pulse"
ZENODO_PAPER = "https://doi.org/10.5281/zenodo.17566097"
PODCAST_LINK = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-"
    "bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)


def write_pulse(filename: str, pulse: dict) -> None:
    """
    Write a YAML pulse file following the canonical Φ-Mesh schema.

    Canonical top-level keys:
      - title      (string, single-quoted by PyYAML when needed)
      - summary    (multi-line string; PyYAML emits as `summary: >` for multiline)
      - tags       (list of strings)
      - papers     (list of URLs)
      - podcasts   (list of URLs)
    """
    path = os.path.join(PULSE_DIR, filename)

    os.makedirs(PULSE_DIR, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            pulse,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=78,  # reasonable wrapping
        )


def generate_memory_echo_pulse(primary_snapshot: dict, date: datetime) -> None:
    """
    Generate the Δτ₊₇ memory_bifurcation echo forecast pulse.

    Canonical echo tags:
      - phi_trace
      - phi_p
      - tag_map
      - recursion
      - autoscan
      - memory_bifurcation
      - gradient_invariant
    """

    title = "Φ–Pulse Δτ₊₇ — memory_bifurcation echo forecast"

    spike = primary_snapshot.get("phi_p_spike", "n/a")
    plateau = primary_snapshot.get("phi_p_plateau", "n/a")

    summary_lines = [
        "Automatic forecast pulse for the expected memory_bifurcation echo (Δτ₊₇)",
        "window starting from the primary CF snap recorded before "
        f"{date.strftime('%Y-%m-%d')}. Primary CF",
        f"snapshot: Φᵨ spike ≈ {spike}, relaxation plateau ≈ {plateau}.",
        "Echo forecast window: ~7 days after the primary event.",
    ]
    summary = "\n".join(summary_lines)

    pulse = {
        "title": title,
        "summary": summary,
        "tags": [
            "phi_trace",
            "phi_p",
            "tag_map",
            "recursion",
            "autoscan",
            "memory_bifurcation",
            "gradient_invariant",
        ],
        "papers": [ZENODO_PAPER],
        "podcasts": [PODCAST_LINK],
    }

    filename = f"{date.strftime('%Y-%m-%d')}_phi_pulse_memory_bifurcation_echo.yml"
    write_pulse(filename, pulse)


def generate_autoscan_pulse(scan_result: dict, date: datetime) -> None:
    """
    Emit the nightly Φ-Trace Autoscan pulse.

    All autoscan metadata is folded into the `summary:` block.
    Canonical autoscan tags:
      - phi_trace
      - phi_p
      - tag_map
      - recursion
      - autoscan
      - memory_bifurcation
      - gradient_invariant
    """

    status = scan_result.get("status", "no_event")
    event_type = scan_result.get("event_type", "none")
    phi_p_peak = scan_result.get("phi_p_peak", None)
    phi_p_plateau = scan_result.get("phi_p_plateau", None)
    notes_list = scan_result.get("notes", [])

    if status == "no_event":
        lead_line = (
            "No Φᵨ plateau or Δ→GC→CF echo crossed Φ-trace detection thresholds today."
        )
    else:
        lead_line = (
            "A Φᵨ plateau or Δ→GC→CF echo exceeded Φ-trace detection thresholds today."
        )

    peak_str = "none" if phi_p_peak is None else str(phi_p_peak)
    plateau_str = "none" if phi_p_plateau is None else str(phi_p_plateau)
    notes_str = " | ".join(str(n) for n in notes_list) if notes_list else "none"

    summary_lines = [
        lead_line,
        "",
        "Autoscan details:",
        f"  status: {status}",
        f"  event_type: {event_type}",
        f"  phi_p_peak: {peak_str}",
        f"  phi_p_plateau: {plateau_str}",
        f"  notes: {notes_str}",
    ]
    summary = "\n".join(summary_lines)

    title = f"Φ-Trace Autoscan — {date.strftime('%Y-%m-%d')}"

    pulse = {
        "title": title,
        "summary": summary,
        "tags": [
            "phi_trace",
            "phi_p",
            "tag_map",
            "recursion",
            "autoscan",
            "memory_bifurcation",
            "gradient_invariant",
        ],
        "papers": [ZENODO_PAPER],
        "podcasts": [PODCAST_LINK],
    }

    filename = f"{date.strftime('%Y-%m-%d')}_phi_trace_autoscan.yml"
    write_pulse(filename, pulse)


def run_predictor() -> None:
    """
    Main entry for workflow execution.

    Generates two pulses each run (typically nightly via GitHub Actions):
      1. Φ-Trace Autoscan pulse
      2. Φ–Pulse Δτ₊₇ memory_bifurcation echo forecast pulse
    """

    today = datetime.utcnow()
    # Placeholder for future use if we ever look back at yesterday's CF snap:
    _yesterday = today - timedelta(days=1)

    # 1. Autoscan (placeholder logic for now)
    scan_result = {
        "status": "no_event",
        "event_type": None,
        "phi_p_peak": None,
        "phi_p_plateau": None,
        "notes": [
            "No Φᵨ plateau or Δ→GC→CF echo crossed detection thresholds today."
        ],
    }
    generate_autoscan_pulse(scan_result, today)

    # 2. Echo pulse (placeholder primary snapshot for now)
    primary_snapshot = {
        "phi_p_spike": "1.12",
        "phi_p_plateau": "0.89",
    }
    generate_memory_echo_pulse(primary_snapshot, today)


if __name__ == "__main__":
    run_predictor()
