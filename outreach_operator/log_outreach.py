#!/usr/bin/env python3
"""Append outreach attempts/outcomes to outreach_operator/outreach_log.csv."""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log an outreach attempt/outcome to outreach_operator/outreach_log.csv"
    )
    parser.add_argument("--org", required=True, help="Organization or university")
    parser.add_argument("--lab", default="", help="Lab or group")
    parser.add_argument("--person", default="", help="Contact name")
    parser.add_argument("--role", default="", help="Contact role")
    parser.add_argument("--channel", default="", help="Email, DM, referral, etc.")
    parser.add_argument("--outcome", required=True, help="Outcome (sent, replied, no_reply, opt_out, etc.)")
    parser.add_argument("--notes", default="", help="Free-text notes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    log_path = base_dir / "outreach_log.csv"

    header = [
        "timestamp_utc",
        "org",
        "lab",
        "person",
        "role",
        "channel",
        "outcome",
        "notes",
    ]

    row = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "org": args.org,
        "lab": args.lab,
        "person": args.person,
        "role": args.role,
        "channel": args.channel,
        "outcome": args.outcome,
        "notes": args.notes,
    }

    file_exists = log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
