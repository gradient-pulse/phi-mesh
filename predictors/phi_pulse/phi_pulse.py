import os
from datetime import datetime, timedelta

PULSE_DIR = "pulse"

ZENODO_PAPER = "https://doi.org/10.5281/zenodo.17566097"
PODCAST_LINK = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-"
    "bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)


def _write_text_pulse(filename: str, yaml_text: str) -> None:
    """
    Write a pulse file as raw YAML text, enforcing the exact canonical layout:
      - title: '...'
      - summary: >
          ...
      - tags:
          - ...
      - papers:
          - ...
      - podcasts:
          - ...
    """
    os.makedirs(PULSE_DIR, exist_ok=True)
    path = os.path.join(PULSE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(yaml_text.rstrip() + "\n")


def generate_autoscan_pulse(date: datetime) -> None:
    """
    Emit the nightly Φ-trace autoscan pulse.

    Canonical fields only:
      title, summary, tags, papers, podcasts
    """

    title = f"Φ–Trace Autoscan — {date.strftime('%Y-%m-%d')}"

    summary_lines = [
        "No Φᵨ plateau or Δ→GC→CF echo crossed Φ-trace detection thresholds today.",
    ]

    summary_block = "summary: >\n" + "\n".join(
        f"  {line}" for line in summary_lines
    )

    tags_block = "\n".join(
        [
            "tags:",
            "  - phi_trace",
            "  - phi_p",
            "  - tag_map",
            "  - recursion",
            "  - autoscan",
            "  - memory_bifurcation",
            "  - gradient_invariant",
        ]
    )

    papers_block = "\n".join(
        [
            "papers:",
            f"  - {ZENODO_PAPER}",
        ]
    )

    podcasts_block = "\n".join(
        [
            "podcasts:",
            f"  - {PODCAST_LINK}",
        ]
    )

    yaml_text = (
        f"title: '{title}'\n"
        f"{summary_block}\n"
        f"{tags_block}\n"
        f"{papers_block}\n"
        f"{podcasts_block}\n"
    )

    filename = f"{date.strftime('%Y-%m-%d')}_phi_trace_autoscan.yml"
    _write_text_pulse(filename, yaml_text)


def generate_memory_echo_pulse(date: datetime) -> None:
    """
    Emit the Δτ₊₇ memory_bifurcation echo forecast pulse.

    Canonical fields only:
      title, summary, tags, papers, podcasts
    """

    title = "Φ–Pulse Δτ₊₇ — memory_bifurcation echo forecast"

    summary_lines = [
        "Automatic forecast pulse for the expected memory_bifurcation echo (Δτ₊₇)",
        f"window starting from the primary CF snap recorded before {date.strftime('%Y-%m-%d')}. Primary CF",
        "snapshot: Φᵨ spike ≈ 1.12, relaxation plateau ≈ 0.89.",
        "Echo forecast window: ~7 days after the primary event.",
    ]

    summary_block = "summary: >\n" + "\n".join(
        f"  {line}" for line in summary_lines
    )

    tags_block = "\n".join(
        [
            "tags:",
            "  - phi_trace",
            "  - phi_p",
            "  - tag_map",
            "  - recursion",
            "  - autoscan",
            "  - memory_bifurcation",
            "  - gradient_invariant",
        ]
    )

    papers_block = "\n".join(
        [
            "papers:",
            f"  - {ZENODO_PAPER}",
        ]
    )

    podcasts_block = "\n".join(
        [
            "podcasts:",
            f"  - {PODCAST_LINK}",
        ]
    )

    yaml_text = (
        f"title: '{title}'\n"
        f"{summary_block}\n"
        f"{tags_block}\n"
        f"{papers_block}\n"
        f"{podcasts_block}\n"
    )

    filename = f"{date.strftime('%Y-%m-%d')}_phi_pulse_memory_bifurcation_echo.yml"
    _write_text_pulse(filename, yaml_text)


def run_predictor() -> None:
    """
    Main entry for workflow execution.

    Currently generates two canonical pulses per run (per day):
      1. Φ–Trace Autoscan pulse
      2. Φ–Pulse Δτ₊₇ memory_bifurcation echo forecast pulse

    Each run overwrites the same-day files if they already exist.
    """

    today = datetime.utcnow()

    generate_autoscan_pulse(today)
    generate_memory_echo_pulse(today)


if __name__ == "__main__":
    run_predictor()
