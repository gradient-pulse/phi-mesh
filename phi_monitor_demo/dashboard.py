# File: phi_monitor_demo/dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from phi_utils import phi_from_csv

def render_dashboard(file_bytes):
    # Save time-log values
    sigma, gc, phi = phi_from_csv(file_bytes)

    # Create a new log row
    df = pd.DataFrame([[pd.Timestamp.now(), sigma, gc, phi]],
                      columns=["Timestamp", "Sigma", "GC", "Phi"])

    # Setup log file
    log_dir = "phi_monitor_demo/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "phi_log.csv")

    # Append or create log
    if os.path.exists(log_path):
        existing = pd.read_csv(log_path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(log_path, index=False)

    # Visualize trend
    st.subheader("📈 Φ Trend & UD Detection")
    try:
        data = pd.read_csv(log_path, parse_dates=["Timestamp"])
        fig, ax = plt.subplots()
        ax.plot(data["Timestamp"], data["Phi"], marker="o", label="Φ")
        ax.axhline(y=1.0, color="gray", linestyle="--", label="UD Threshold")
        ax.set_ylabel("Φ")
        ax.set_xlabel("Time")
        ax.legend()
        st.pyplot(fig)

        if len(data) > 1:
            last_phi = data["Phi"].iloc[-1]
            prev_phi = data["Phi"].iloc[-2]
            if last_phi < prev_phi and last_phi < 1.0:
                st.error("⚠️ UD risk detected: Φ is trending downward.")
            elif last_phi > prev_phi:
                st.success("✅ Φ recovery detected: system stabilizing.")
    except Exception as e:
        st.error(f"Error while parsing or logging: {str(e)}")
