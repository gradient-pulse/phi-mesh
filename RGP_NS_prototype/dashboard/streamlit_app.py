import streamlit as st
import pandas as pd
from render_dashboard import render_dashboard      # same-folder import
# or (if Python complains again) use explicit relative import:
# from .render_dashboard import render_dashboard

# ✅ This must be the first Streamlit command
st.set_page_config(page_title="NT Metrics Dashboard", layout="centered")

st.title("NT Metrics Dashboard")

uploaded = st.file_uploader(
    "Upload KPI CSV (see results/kpi_columns.txt for schema)",
    type="csv",
)

if uploaded is None:
    st.markdown(
        """
        **No file yet.**

        • Download the [schema](https://github.com/gradient-pulse/phi-mesh/blob/main/results/kpi_columns.txt)  
        • Or grab the [example_KPI.csv](https://github.com/gradient-pulse/phi-mesh/blob/main/results/example_KPI.csv)  
          to test the dashboard layout.
        """
    )
    st.stop()

# Load the CSV into a DataFrame and render the dashboard
df = pd.read_csv(uploaded)
render_dashboard(df)
