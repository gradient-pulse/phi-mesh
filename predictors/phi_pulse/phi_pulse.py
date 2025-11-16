#!/usr/bin/env python3
"""
phi_pulse.py

Automatic Φ-pulse generator for the Φ-Mesh.

- Writes YAML pulses into the canonical /pulse/ directory.
- Keeps the strict pulse schema used in pulse/README.md.
- Intended to be called by GitHub Actions or manually.

Initial focus:
- Δτ+7 "memory_bifurcation echo" pulses predicted by Kimi (DeepThinking).
"""

from __future__ import annotations
import argparse
import datetime as dt
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Add `pyyaml` to requirements.txt "
        "and reinstall the environment.",
        file=sys.stderr,
    )
    sys.exit(1)


# -----------------------------
# Paths
# -----------------------------

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2]         # .../phi-mesh
PULSE_DIR = REPO_ROOT / "pulse"


# -----------------------------
# Helpers
# -----------------------------

def ensure_pulse_dir() -> None:
    """Ensure the /pulse/ directory exists."""
    PULSE_DIR.mkdir(parents=True, exist_ok=True)


def today_iso() -> str:
    return dt.date.today().isoformat()  # YYYY-MM-DD


def make_filename(date_str: str, label: str) -> Path:
    """
    Build a pulse filename like:
    2025-11-22_phi_pulse_memory_bifurcation_echo.yml
    """
    safe_label = label.strip().lower().replace(" ", "_")
    return PULSE_DIR / f"{date_str}_phi_pulse_{safe_label}.yml"


def pulse_exists(path: Path) -> bool:
    return path.exists()


def write_yaml(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


# -----------------------------
# Pulse builders
# -----------------------------

def build_memory_bifurcation_echo_pulse(
    date_str: str,
    phi_spike: float,
    phi_settle: float,
    echo_window_days: int = 7,
) -> dict:
    """
    Build a Δτ+7 memory_bifurcation echo forecast pulse.
    This follows the strict minimal schema from pulse/README.md.
    """

    title = "Φ-Pulse Δτ₊₇ — memory_bifurcation echo forecast"

    summary_lines = [
        "Automatic forecast pulse for the expected memory_bifurcation echo ",
        f"(Δτ₊₇ window starting from the primary CF snap recorded before {date_str}). ",
        "",
        f"Primary CF snapshot: Φₚ spike ≈ {phi_spike:.2f}, relaxation plateau ≈ {phi_settle:.2f}. ",
        f"Echo forecast window: ~{echo_window_days} days after the primary event.",
    ]
    summary = "".join(summary_lines)

    pulse = {
        "title": title,
        "summary": summary,
        "tags": [
            "phi_pulse",
            "phi_p",
            "memory_bifurcation",
            "coherence_field",
            "gradient_invariant",
            "tag_map",
            "recursion",
            "cognitive_invariant",
            "kimi_deepthinking",
        ],
        # Always include canonical RGPx paper + podcast
        "papers": [
            "https://doi.org/10.5281/zenodo.17566097",
        ],
        "podcasts": [
            "https://notebooklm.google.com/notebook/44f78a05-d5af-44c9-a685-bde0c5847a55?artifactId=653982a7-5415-4390-af4d-b40b30665c59",
        ],
    }

    return pulse


# -----------------------------
# CLI
# -----------------------------

def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate automatic Φ-pulses under /pulse/."
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Command: echo-forecast (Δτ+7)
    echo = sub.add_parser(
        "echo-forecast",
        help="Generate a Δτ+7 memory_bifurcation echo forecast pulse.",
    )
    echo.add_argument(
        "--date",
        default=today_iso(),
        help="Date for the pulse filename (YYYY-MM-DD). Defaults to today.",
    )
    echo.add_argument(
        "--phi-spike",
        type=float,
        default=1.12,
        help="Primary Φₚ spike value (default: 1.12).",
    )
    echo.add_argument(
        "--phi-settle",
        type=float,
        default=0.89,
        help="Primary Φₚ post-relaxation plateau (default: 0.89).",
    )
    echo.add_argument(
        "--echo-window-days",
        type=int,
        default=7,
        help="Echo forecast window in days (default: 7).",
    )
    echo.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing pulse file if it already exists.",
    )

    return parser.parse_args(argv)


def cmd_echo_forecast(ns: argparse.Namespace) -> int:
    ensure_pulse_dir()

    filename = make_filename(ns.date, "memory_bifurcation_echo")
    if pulse_exists(filename) and not ns.force:
        print(f"[phi_pulse] Pulse already exists: {filename}")
        return 0

    pulse = build_memory_bifurcation_echo_pulse(
        date_str=ns.date,
        phi_spike=ns.phi_spike,
        phi_settle=ns.phi_settle,
        echo_window_days=ns.echo_window_days,
    )

    write_yaml(filename, pulse)
    print(f"[phi_pulse] Wrote pulse: {filename}")
    return 0


def main(argv=None) -> int:
    ns = parse_args(argv)

    if ns.command == "echo-forecast":
        return cmd_echo_forecast(ns)

    print("Unknown command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
