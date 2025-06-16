import io
import pandas as pd
import numpy as np

DISTRACT = {"Email", "Slack", "News", "Social"}

def phi_from_csv(file_bytes):
    df = pd.read_csv(io.StringIO(file_bytes.decode()))
    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])
    df["Duration"] = (df["End"] - df["Start"]).dt.total_seconds() / 60
    df["Switch"] = df["Activity"].shift() != df["Activity"]
    sigma = df["Switch"].sum() / ((df["End"].max() - df["Start"].min()).total_seconds() / 3600)
    focus_minutes = df[~df["Activity"].isin(DISTRACT)]["Duration"].sum()
    gc = focus_minutes / ((df["End"].max() - df["Start"].min()).total_seconds() / 3600)
    phi = gc / (sigma + 1e-5)
    return sigma, gc, phi
