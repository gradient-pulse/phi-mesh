import streamlit as st, pandas as pd
import matplotlib.pyplot as plt
from phi_utils import phi_from_csv

st.title("Φ-Monitor demo")
up = st.file_uploader("Upload time-log CSV", type="csv")
if up:
    bytes_data = up.read()
    sigma, gc, phi = phi_from_csv(bytes_data)
    st.metric("Sigma (switches/hr)", f"{sigma:.2f}")
    st.metric("|GC| (focus min/hr)", f"{gc:.2f}")
    st.metric("Φ", f"{phi:.2f}")
