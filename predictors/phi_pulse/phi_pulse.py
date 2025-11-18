import os
from datetime import datetime, timedelta


PULSE_DIR = "pulse"
ZENODO_PAPER = "https://doi.org/10.5281/zenodo.17566097"
PODCAST_LINK = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-"
    "bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)


def ensure_pulse_dir():
    """Make sure the pulse/ directory exists."""
    os.makedirs(PULSE_DIR, exist_ok=True)


def write_pulse_file(
    filename: str,
    title: str,
    summary_lines: list[str],
    tags: list[str],
    autoscan_block: dict | None = None,
):
    """
    Write a YAML pulse file by hand so we control formatting exactly.

    Guarantees:
      - title is on one line and single-quoted
      - summary is emitted as a folded block (`summary: >`)
      - tags / papers / podcasts are standard YAML lists
      - optional `autoscan:` block is correctly indented
    """
    ensure_pulse_dir()
    path = os.path.join(PULSE_DIR, filename)

    lines: list[str] = []

    # Title
    lines.append(f"title: '{title}'")

    # Summary (folded block)
    lines.append("summary: >")
    for line in summary_lines:
        if line:
            lines.append(f"  {line}")
        else:
            lines.append("  ")

    # Optional autoscan: block
    if autoscan_block is not None:
        lines.append("autoscan:")
        lines.append(f"  date: {autoscan_block['date']}")
        lines.append(f"  status: {autoscan_block['status']}")
        lines.append(
            f"  event_type: {autoscan_block.get('event_type', 'null')}"
        )
        lines.append(
            "  phi_p_peak: "
            f"{autoscan_block.get('phi_p_peak', 'null')}"
        )
        lines.append(
            "  phi_p_plateau: "
            f"{autoscan_block.get('phi_p_plateau', 'null')}"
        )

        notes_lines = autoscan_block.get("notes_lines", [])
        if notes_lines:
            lines.append("  notes: >")
            for nline in notes_lines:
                if nline:
                    lines.append(f"    {nline}")
                else:
                    lines.append("    ")

    # Tags
    lines.append("tags:")
    for tag in tags:
        lines.append(f"  - {tag}")

    # Papers
    lines.append("papers:")
    lines.append(f"  - {ZENODO_PAPER}")

    # Podcasts
    lines.append("podcasts:")
    lines.append(f"  - {PODCAST_LINK}")

    content = "\n".join(lines) + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_memory_echo_pulse(primary_snapshot: dict, date: datetime):
    """
    Generate the Δτ₊₇ echo pulse using canonical tags and formatting.

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

    summary_lines = [
        "Automatic forecast pulse for the expected memory_bifurcation echo (Δτ₊₇)",
        "window starting from the primary CF snap recorded before "
        f"{date.strftime('%Y-%m-%d')}. Primary CF",
        (
            f"snapshot: Φᵨ spike ≈ {primary_snapshot.get('phi_p_spike', 'n/a')}, "
            f"relaxation plateau ≈ {primary_snapshot.get('phi_p_plateau', 'n/a')}."
        ),
        "Echo forecast window: ~7 days after the primary event.",
    ]

    tags = [
        "phi_trace",
        "phi_p",
        "tag_map",
        "recursion",
        "autoscan",
        "memory_bifurcation",
        "gradient_invariant",
    ]

    filename = f"{date.strftime('%Y-%m-%d')}_phi_pulse_memory_bifurcation_echo.yml"
    write_pulse_file(filename, title, summary_lines, tags)


def generate_autoscan_pulse(scan_result: dict, date: datetime):
    """
    Emit the nightly Φ-Trace Autoscan pulse.

    Title includes the date for human readability.
    """
    title = f"Φ-Trace Autoscan — {date.strftime('%Y-%m-%d')}"

    if scan_result.get("status") == "no_event":
        summary_lines = [
            "No Δ→GC→CF structures exceeded Φ-trace detection thresholds today."
        ]
    else:
        summary_lines = [
            "A Φᵨ plateau or Δ→GC→CF echo exceeded Φ-trace autoscan thresholds today."
        ]

    autoscan_block = {
        "date": date.strftime("%Y-%m-%d"),
        "status": scan_result.get("status", "no_event"),
        "event_type": scan_result.get("event_type", "null"),
        "phi_p_peak": scan_result.get("phi_p_peak", "null"),
        "phi_p_plateau": scan_result.get("phi_p_plateau", "null"),
        "notes_lines": scan_result.get(
            "notes",
            [
                "No Φᵨ plateau or Δ→GC→CF echo crossed detection thresholds today."
                if scan_result.get("status") == "no_event"
                else "Autoscan recorded a Φᵨ plateau / Δ→GC→CF echo above thresholds.",
            ],
        ),
    }

    tags = [
        "phi_trace",
        "phi_p",
        "tag_map",
        "recursion",
        "autoscan",
        "memory_bifurcation",
        "gradient_invariant",
    ]

    filename = f"{date.strftime('%Y-%m-%d')}_phi_trace_autoscan.yml"
    write_pulse_file(filename, title, summary_lines, tags, autoscan_block=autoscan_block)


def run_predictor():
    """
    Main entry for workflow execution.

    Generates two pulses each run:
      1. Φ-Trace Autoscan pulse
      2. Φ–Pulse Δτ₊₇ memory_bifurcation echo forecast pulse
    """
    today = datetime.utcnow()
    _yesterday = today - timedelta(days=1)  # reserved for future use

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

    # 2. Echo pulse (placeholder snapshot)
    primary_snapshot = {
        "phi_p_spike": "1.12",
        "phi_p_plateau": "0.89",
    }
    generate_memory_echo_pulse(primary_snapshot, today)


if __name__ == "__main__":
    run_predictor()
