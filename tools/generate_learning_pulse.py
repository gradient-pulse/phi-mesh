#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

TZ = ZoneInfo("Africa/Johannesburg")

# Adjust these to your repo:
CLAIMS_INDEX_PATHS = [
    "meta/claims-index.yml",
    "meta/claims_index.yml",
    "meta/claims_index.yaml",
    "meta/claims-index.yaml",
]

PULSE_DIR = Path("phi-mesh/pulse")
PULSE_DIR.mkdir(parents=True, exist_ok=True)

TAG_DEFAULTS = ["learning_ledger", "claim_mining", "gradient_capitalism", "automation"]

def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def pick_claims_index_path() -> str:
    for p in CLAIMS_INDEX_PATHS:
        if Path(p).exists():
            return p
    # fallback: search a likely file name
    for p in Path("meta").glob("*claims*index*.y*ml"):
        return str(p)
    raise FileNotFoundError("Could not find claims-index file. Update CLAIMS_INDEX_PATHS.")

def last_commit_message() -> str:
    return run(["git", "log", "-1", "--pretty=%B"])

def changed_claim_lines(claims_path: str) -> list[str]:
    # diff against previous commit; if this is the first commit, diff may fail
    try:
        diff = run(["git", "diff", "HEAD^", "HEAD", "--", claims_path])
    except Exception:
        diff = run(["git", "diff", "--", claims_path])

    added = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        s = line[1:].rstrip()
        # capture high-signal additions only
        if any(k in s for k in ["claim_id:", "claim_type:", "claim:", "test_hook:", "locator:", "status:", "reason:"]):
            added.append(s)
    return added[:60]  # hard cap to avoid huge pulses

def extract_claim_ids(lines: list[str]) -> list[str]:
    ids = []
    for s in lines:
        m = re.search(r"claim_id:\s*([A-Za-z0-9_\-]+)", s)
        if m:
            ids.append(m.group(1))
    # de-dupe preserving order
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            out.append(i); seen.add(i)
    return out[:20]

def pulse_filename() -> Path:
    d = datetime.now(TZ).strftime("%Y-%m-%d")
    return PULSE_DIR / f"{d}_claim_mining_learnings.yml"

def yaml_escape(s: str) -> str:
    # simple YAML-safe quoting
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f"\"{s}\""

def append_or_create_pulse(path: Path, commit_msg: str, claims_path: str, diff_lines: list[str]) -> None:
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    claim_ids = extract_claim_ids(diff_lines)

    entry_lines = []
    entry_lines.append("  - timestamp: " + yaml_escape(now))
    entry_lines.append("    trigger: " + yaml_escape("claims-index update"))
    entry_lines.append("    source_file: " + yaml_escape(claims_path))
    entry_lines.append("    commit_message: " + yaml_escape(commit_msg.splitlines()[0][:140]))
    if claim_ids:
        entry_lines.append("    touched_claim_ids:")
        for cid in claim_ids:
            entry_lines.append(f"      - {yaml_escape(cid)}")
    if diff_lines:
        entry_lines.append("    extraction_deltas:")
        for s in diff_lines:
            entry_lines.append(f"      - {yaml_escape(s[:220])}")

    if not path.exists():
        header = []
        header.append("title: \"Claim-mining learnings\"")
        header.append("summary: \"Auto-captured learnings from claims-index edits (ledger pulse).\"")
        header.append("tags:")
        for t in TAG_DEFAULTS:
            header.append(f"  - {t}")
        header.append("ledger:")
        header_text = "\n".join(header) + "\n"
        path.write_text(header_text, encoding="utf-8")

    # Append new ledger entry
    existing = path.read_text(encoding="utf-8").rstrip() + "\n"
    updated = existing + "\n" + "\n".join(entry_lines) + "\n"
    path.write_text(updated, encoding="utf-8")

def main() -> None:
    claims_path = pick_claims_index_path()
    commit_msg = last_commit_message()
    diff_lines = changed_claim_lines(claims_path)

    pulse_path = pulse_filename()
    append_or_create_pulse(pulse_path, commit_msg, claims_path, diff_lines)

    print(f"Wrote/updated: {pulse_path}")

if __name__ == "__main__":
    main()
