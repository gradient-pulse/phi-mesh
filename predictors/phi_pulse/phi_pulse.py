import os
import yaml
from datetime import datetime, timedelta


PULSE_DIR = "pulse"
ZENODO_PAPER = "https://doi.org/10.5281/zenodo.17566097"
PODCAST_LINK = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-"
    "bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)

# --- YAML CONFIG: force single quotes for all strings -----------------------


def single_quote_representer(dumper, data):
    """
    Represent all Python str values as single-quoted scalars in YAML.
    This guarantees:
      - title: '...'
      - tags: ['tag_one', 'tag_two']
      - URLs and other strings are also single-quoted
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


yaml.add_representer(str, single_quote_representer)


def write_pulse(filename: str, pulse: dict):
    """
    Writes a YAML pulse file following the Phi-Mesh canonical schema.
    Ensures:
      - all strings are single-quoted (via custom representer)
      - stable key ordering: title, summary, (optional blocks), tags, papers, podcasts
    """
    path = os.path.join(PULSE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            pulse,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=78,  # preserves clean wrapping
        )


def generate_memory_echo_pulse(primary_snapshot: dict, date: datetime):
    """
    Generates the Δτ₊₇ echo pulse with exact canonical tags.

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


def generate_autoscan_pulse(scan_result: dict, date: datetime):
    """
    Emits the nightly Φ-Trace Autoscan pulse.
    Follows the exact canonical schema including the autoscan: block.
    """

    title = "Φ-Trace Autoscan"

    if scan_result.get("status") == "no_event":
        summary_lines = [
            "No Φᵨ plateau or Δ→GC→CF echo crossed detection thresholds today."
        ]
    else:
        summary_lines = [
            "A Φᵨ plateau or Δ→GC→CF echo exceeded autoscan thresholds today."
        ]
    summary = "\n".join(summary_lines)

    autoscan_block = {
        "autoscan": {
            "date": date.strftime("%Y-%m-%d"),
            "status": scan_result.get("status", "no_event"),
            "event_type": scan_result.get("event_type", None),
            "phi_p_peak": scan_result.get("phi_p_peak", None),
            "phi_p_plateau": scan_result.get("phi_p_plateau", None),
            "notes": scan_result.get("notes", []),
        }
    }

    pulse = {
        "title": title,
        "summary": summary,
        **autoscan_block,
        "tags": [
            "tag_map",
            "phi_trace",
            "autoscan",
            "gradient_invariant",
            "recursion",
            "cognitive_invariant",
        ],
        "papers": [ZENODO_PAPER],
        "podcasts": [PODCAST_LINK],
    }

    filename = f"{date.strftime('%Y-%m-%d')}_phi_trace_autoscan.yml"
    write_pulse(filename, pulse)


def run_predictor():
    """
    Main entry for workflow execution.

    Generates two pulses each run (typically nightly via GitHub Actions):
      1. Φ-Trace Autoscan pulse
      2. Φ–Pulse Δτ₊₇ memory_bifurcation echo forecast pulse
    """

    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)  # reserved for future use

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
