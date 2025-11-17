import os
import yaml
from datetime import datetime, timedelta

PULSE_DIR = "pulse"
ZENODO_PAPER = "https://doi.org/10.5281/zenodo.17566097"
PODCAST_LINK = (
    "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-"
    "bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59"
)

# ---------------------------------------------------------------------------
# Custom YAML representer to ensure the EXACT Phi-Mesh canonical pulse format:
# - title → single-quoted
# - summary → emitted as a folded block (summary: >)
# - tags / papers / podcasts → plain scalars (NO quotes)
# ---------------------------------------------------------------------------

class PulseDumper(yaml.SafeDumper):
    pass


def represent_title(dumper, data):
    """Force single quotes for the title only."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


def represent_summary(dumper, data):
    """Force folded block literal for summary."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


# Register representers ONLY for the specific fields
PulseDumper.add_representer(str, yaml.SafeDumper.represent_str)  # default
PulseDumper.add_representer(type(None), yaml.SafeDumper.represent_none)

# Title and summary need special handling via key-based representation
def dict_representer(dumper, data):
    if "title" in data:
        data["title"] = yaml.scalarstring.SingleQuotedScalarString(data["title"])
    if "summary" in data:
        data["summary"] = yaml.scalarstring.FoldedScalarString(data["summary"])
    return yaml.SafeDumper.represent_dict(dumper, data)

PulseDumper.add_representer(dict, dict_representer)


# ---------------------------------------------------------------------------

def write_pulse(filename: str, pulse: dict):
    """Write pulse file with correct ordering and formatting."""
    path = os.path.join(PULSE_DIR, filename)
    
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            pulse,
            f,
            Dumper=PulseDumper,
            sort_keys=False,
            allow_unicode=True,
            width=78,
        )


# ---------------------------------------------------------------------------

def generate_memory_echo_pulse(primary_snapshot: dict, date: datetime):
    """Δτ₊₇ echo forecast pulse."""

    title = "Φ–Pulse Δτ₊₇ — memory_bifurcation echo forecast"

    summary = "\n".join([
        "Automatic forecast pulse for the expected memory_bifurcation echo (Δτ₊₇)",
        "window starting from the primary CF snap recorded before "
        f"{date.strftime('%Y-%m-%d')}. Primary CF",
        (
            f"snapshot: Φᵨ spike ≈ {primary_snapshot.get('phi_p_spike', 'n/a')}, "
            f"relaxation plateau ≈ {primary_snapshot.get('phi_p_plateau', 'n/a')}."
        ),
        "Echo forecast window: ~7 days after the primary event.",
    ])

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


# ---------------------------------------------------------------------------

def generate_autoscan_pulse(scan_result: dict, date: datetime):
    """Nightly autoscan pulse."""

    title = "Φ-Trace Autoscan"

    summary = (
        "No Φᵨ plateau or Δ→GC→CF echo crossed detection thresholds today."
        if scan_result.get("status") == "no_event"
        else "A Φᵨ plateau or Δ→GC→CF echo exceeded autoscan thresholds today."
    )

    autoscan_block = {
        "autoscan": {
            "date": date.strftime("%Y-%m-%d"),
            "status": scan_result.get("status", "no_event"),
            "event_type": scan_result.get("event_type"),
            "phi_p_peak": scan_result.get("phi_p_peak"),
            "phi_p_plateau": scan_result.get("phi_p_plateau"),
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


# ---------------------------------------------------------------------------

def run_predictor():
    """Main entry called by GitHub Actions."""

    today = datetime.utcnow()

    # AUTOSCAN — placeholder
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

    # ECHO — placeholder
    primary_snapshot = {
        "phi_p_spike": "1.12",
        "phi_p_plateau": "0.89",
    }

    generate_memory_echo_pulse(primary_snapshot, today)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_predictor()
