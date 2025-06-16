# File: phi_monitor_demo/dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from phi_utils import phi_from_csv

def render_dashboard(file_bytes):
    st.set_page_config(page_title="Φ Insight Dashboard", layout="centered")
    st.title("Φ Trend & UD Detection")

    st.markdown("""
    This dashboard visualizes your productivity entropy (Σ), gradient effort (|GC|), and the resulting Φ ratio.  
    Use this to monitor drift, spot Unity→Disunity thresholds, and optimize deep work alignment.
    """)

    # Ensure local log folder exists
    log_dir = "phi_monitor_demo/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Parse uploaded bytes
    sigma, gc, phi = phi_from_csv(file_bytes)

    # Store this session's reading
    df = pd.DataFrame([[pd.Timestamp.now(), sigma, gc, phi]],
                      columns=["Timestamp", "Sigma", "GC", "Phi"])

    log_path = os.path.join(log_dir, "phi_log.csv")
    if os.path.exists(log_path):
        existing = pd.read_csv(log_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(log_path, index=False)

    # Display Φ trend
    st.subheader("📈 Φ Over Time")
    if os.path.exists(log_path):
        data = pd.read_csv(log_path, parse_dates=["Timestamp"])
        fig, ax = plt.subplots()
        ax.plot(data["Timestamp"], data["Phi"], marker="o", label="Φ")
        ax.axhline(y=1.0, color="gray", linestyle="--", label="UD Threshold")
        ax.set_ylabel("Φ")
        ax.set_xlabel("Date")
        ax.legend()
        st.pyplot(fig)

        # Simple UD detection
        if data.shape[0] > 2:
            last_phi = data["Phi"].iloc[-1]
            prev_phi = data["Phi"].iloc[-2]
            if last_phi < prev_phi and last_phi < 1.0:
                st.error("⚠️ UD risk detected: Your Φ is trending down.")
            elif last_phi > prev_phi:
                st.success("✅ Φ recovery detected: system stabilizing.")

    st.markdown("""
    ---
    *Next steps*: Add GC sprint suggestions, detect turning points, and connect to agent workflows. Want this?  
    Click **Manage app → Invite collaborators → [gradientpulse@proton.me](mailto:gradientpulse@proton.me)** to support development.
    """)
