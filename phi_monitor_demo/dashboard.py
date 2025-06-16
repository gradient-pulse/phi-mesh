# File: phi_monitor_demo/dashboard.py

import streamlit as st, pandas as pd, matplotlib.pyplot as plt
from phi_utils import phi_from_csv
import os

def render_dashboard():
    st.set_page_config(page_title="Φ Insight Dashboard", layout="centered")
    st.title("Φ Trend & UD Detection")

    st.markdown("""
    This dashboard visualizes your productivity entropy (Σ), gradient effort (|GC|), and the resulting Φ ratio.
    Use this to monitor drift, spot Unity→Disunity thresholds, and optimize deep work alignment.
    """)

    log_dir = "phi_monitor_demo/logs"
    os.makedirs(log_dir, exist_ok=True)

    uploaded = st.file_uploader("Upload today's time-log CSV", type="csv")

    if uploaded:
        bytes_data = uploaded.read()
        sigma, gc, phi = phi_from_csv(bytes_data)
        
        df = pd.DataFrame([[pd.Timestamp.now(), sigma, gc, phi]],
                          columns=["Timestamp", "Sigma", "GC", "Phi"])
        
        log_path = os.path.join(log_dir, "phi_log.csv")
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(log_path, index=False)

    log_file = os.path.join(log_dir, "phi_log.csv")
    if os.path.exists(log_file):
        data = pd.read_csv(log_file, parse_dates=["Timestamp"])
        st.subheader("📈 Φ Over Time")
        fig, ax = plt.subplots()
        ax.plot(data["Timestamp"], data["Phi"], marker="o", label="Φ")
        ax.axhline(y=1.0, color="gray", linestyle="--", label="UD Threshold")
        ax.set_ylabel("Φ")
        ax.set_xlabel("Date")
        ax.legend()
        st.pyplot(fig)

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
    Click **Manage app → Invite collaborators → gradientpulse@proton.me** to support development.
    """)
