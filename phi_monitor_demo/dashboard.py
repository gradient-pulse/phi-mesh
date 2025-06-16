# File: phi_monitor_demo/dashboard.py

import io
import streamlit as st, pandas as pd, matplotlib.pyplot as plt
import os

def render_dashboard(file_bytes):
    st.markdown("## Φ Trend & UD Detection")

    log_dir = "phi_monitor_demo/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Save this session’s Φ to cumulative log
    sigma, gc, phi = None, None, None  # Optional: make available for metrics
    df = pd.DataFrame([[pd.Timestamp.now(), None, None, None]],
                      columns=["Timestamp", "Sigma", "GC", "Phi"])
    try:
        df = pd.read_csv(io.StringIO(file_bytes.decode()))
        sigma = df.shape[0] / (df["End"].apply(pd.to_timedelta).sum().total_seconds() / 3600)
        gc = df["End"].apply(pd.to_timedelta).sum().total_seconds() / 60
        phi = gc / sigma if sigma != 0 else 0

        trend_row = pd.DataFrame([[pd.Timestamp.now(), sigma, gc, phi]],
                                 columns=["Timestamp", "Sigma", "GC", "Phi"])
        log_path = os.path.join(log_dir, "phi_log.csv")
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            df = pd.concat([existing, trend_row], ignore_index=True)
        else:
            df = trend_row
        df.to_csv(log_path, index=False)
    except Exception as e:
        st.error(f"Error while parsing or logging: {e}")
        return

    # Plot if log exists
    if os.path.exists(log_path):
        data = pd.read_csv(log_path, parse_dates=["Timestamp"])
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
