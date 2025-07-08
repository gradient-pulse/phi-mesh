import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Streamlit page config
# -------------------------------------------------
st.set_page_config(page_title="NT Metrics Dashboard", layout="centered")
st.title("NT Metrics Dashboard")

# -------------------------------------------------
# File upload
# -------------------------------------------------
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

# -------------------------------------------------
# Load CSV and display metrics
# -------------------------------------------------
df = pd.read_csv(uploaded)

if df.empty:
    st.warning("Uploaded file contains no data.")
    st.stop()

# Expecting a single-row CSV with 5 KPI columns
metrics = df.iloc[0]

st.subheader("Five KPI metrics")
st.dataframe(df)

# Horizontal bar chart
fig, ax = plt.subplots()
metrics.plot(kind="barh", ax=ax, color="skyblue")
ax.set_xlabel("Value")
st.pyplot(fig)
