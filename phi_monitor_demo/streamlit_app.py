import streamlit as st
import pandas as pd
from phi_utils import phi_from_csv
from dashboard import render_dashboard  # import is correct now

# ✅ This must be FIRST Streamlit command
st.set_page_config(page_title="Φ-Monitor", layout="centered")

st.title("Φ-Monitor demo")
up = st.file_uploader("Upload time-log CSV", type="csv")

if up:
    bytes_data = up.read()
    sigma, gc, phi = phi_from_csv(bytes_data)
    st.metric("Sigma (switches/hr)", f"{sigma:.2f}")
    st.metric("|GC| (focus min/hr)", f"{gc:.2f}")
    st.metric("Φ", f"{phi:.2f}")

    st.divider()
    render_dashboard(bytes_data)
