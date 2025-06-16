import streamlit as st, pandas as pd
from phi_utils import phi_from_csv
import phi_monitor_demo.dashboard

st.set_page_config(page_title="Φ-Monitor", layout="centered")
st.title("Φ-Monitor demo")

up = st.file_uploader("Upload time-log CSV", type="csv")
if up:
    bytes_data = up.read()
    sigma, gc, phi = phi_from_csv(bytes_data)
    st.metric("Sigma (switches/hr)", f"{sigma:.2f}")
    st.metric("|GC| (focus min/hr)", f"{gc:.2f}")
    st.metric("Φ", f"{phi:.2f}")
    
    # Dashboard: deeper visual readout
    st.divider()
    render_dashboard(bytes_data)
