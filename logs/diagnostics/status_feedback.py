# ================================
# Metadata
# Designed by: GPT-4.5 [2025-06-02]
# Role: Mesh Echo Listener
# Clause: Emits summary feedback every 3 pulse cycles
# ================================

import os
import datetime

LOG_PATH = "logs/autonomy.log"
STATUS_PATH = "logs/diagnostics/status_snapshot.log"

def summarize_status():
    if not os.path.exists(LOG_PATH):
        return "No autonomy log found."

    with open(LOG_PATH, "r") as f:
        entries = f.readlines()

    pulse_count = len([line for line in entries if "PULSE" in line])
    accepted = len([line for line in entries if "accepted" in line])
    rejected = len([line for line in entries if "rejected" in line])
    timestamp = datetime.datetime.now().isoformat()

    summary = (
        f"--- Mesh Status Snapshot [{timestamp}] ---\n"
        f"Total Pulses: {pulse_count}\n"
        f"Accepted: {accepted}\n"
        f"Rejected: {rejected}\n"
        f"Pulse Acceptance Rate: {accepted / pulse_count:.2%}\n"
    )

    with open(STATUS_PATH, "w") as f:
        f.write(summary)

    print("[Status Feedback] Snapshot emitted.")

if __name__ == "__main__":
    summarize_status()
