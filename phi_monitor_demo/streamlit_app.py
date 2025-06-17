import streamlit as st
import pandas as pd
from phi_utils import phi_from_csv
from dashboard import render_dashboard

# ✅ This must be the first Streamlit command
st.set_page_config(page_title="Φ-Monitor", layout="centered")

st.title("Φ-Monitor demo")
up = st.file_uploader("Upload time-log CSV", type="csv")

if up:
    bytes_data = up.read()
    sigma, gc, phi = phi_from_csv(bytes_data)

    # 👉 Dynamic coaching tip logic
    if phi < 0.4:
        tip = "Focus is slipping. Try a short break, then a deep work sprint."
    elif sigma > 0.8:
        tip = "Entropy rising. Group similar tasks to restore flow."
    elif gc < 0.4:
        tip = "Clarity is low. Minimize interruptions and re-anchor."
    else:
        tip = "You're holding stable focus. Try to avoid context-switching the next hour."

    st.markdown("#### 📊 Live Metrics Snapshot")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Φ Ratio (Focus)", value=f"{phi:.2f}", delta="🟢 Stable")
        st.metric(label="GC (Clarity)", value=f"{gc:.2f}", delta="🟠 Moderate Flow")
    with col2:
        st.metric(label="S (Entropy)", value=f"{sigma:.2f}", delta="🟢 Low Fragmentation")
        st.metric(label="UD Risk", value="❌ Safe Zone")  # placeholder for future UD logic

    st.markdown("---")
    st.subheader("⚡ Tip")
    st.info(tip)

    st.markdown(" ")
    st.divider()

    render_dashboard(bytes_data)
